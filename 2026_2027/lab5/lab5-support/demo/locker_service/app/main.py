from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from py_eureka_client.eureka_client import EurekaClient

from demo.shared.eureka import create_eureka_client
from demo.shared.messaging import BrokerUnavailableError, RabbitEventBroker

QUEUE_NAME = "locker.parcel-events"
ROUTING_KEY = "parcel.placed"


def _initial_lockers() -> dict[str, dict[str, Any]]:
    return {
        "KRK-1024": {
            "id": "KRK-1024",
            "name": "Galeria",
            "address": "Dluga 10",
            "city": "Krakow",
            "status": "online",
            "placed_parcels_count": 0,
        },
        "KRK-2048": {
            "id": "KRK-2048",
            "name": "Dworzec",
            "address": "Pawia 5",
            "city": "Krakow",
            "status": "offline",
            "placed_parcels_count": 0,
        },
    }


def create_app(
    eureka_client: EurekaClient | None = None,
    event_broker: Any | None = None,
) -> FastAPI:
    client = (
        eureka_client
        if eureka_client is not None
        else create_eureka_client("LOCKER-SERVICE", 8101)
    )
    broker = event_broker if event_broker is not None else RabbitEventBroker()

    lockers = _initial_lockers()
    processed_event_ids: set[str] = set()
    event_history: dict[str, list[dict[str, Any]]] = {
        locker_id: [] for locker_id in lockers
    }

    def handle_parcel_placed(event: dict[str, Any]) -> None:
        event_id = str(event.get("event_id") or "")
        locker_id = str(event.get("locker_id") or "")
        if not event_id or not locker_id:
            raise ValueError("Missing event_id or locker_id in event payload")
        if event_id in processed_event_ids:
            return
        locker = lockers.get(locker_id)
        if locker is None:
            raise LookupError(f"Unknown locker_id: {locker_id}")
        processed_event_ids.add(event_id)
        locker["placed_parcels_count"] += 1
        event_history.setdefault(locker_id, []).append(event)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.eureka_client = client
        app.state.event_broker = broker
        app.state.lockers = lockers
        app.state.processed_event_ids = processed_event_ids
        app.state.event_history = event_history
        try:
            try:
                broker.bind_queue(QUEUE_NAME, ROUTING_KEY)
            except BrokerUnavailableError:
                pass
            await client.start()
            yield
        finally:
            try:
                await client.stop()
            finally:
                broker.close()

    app = FastAPI(title="Locker Service", version="1.0.0", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "LOCKER-SERVICE"}

    @app.get("/lockers/{locker_id}")
    async def get_locker(locker_id: str) -> dict[str, Any]:
        locker = lockers.get(locker_id)
        if locker is None:
            raise HTTPException(status_code=404, detail="Locker not found")
        return locker

    @app.get("/lockers/{locker_id}/events")
    async def get_locker_events(locker_id: str) -> dict[str, Any]:
        locker = lockers.get(locker_id)
        if locker is None:
            raise HTTPException(status_code=404, detail="Locker not found")
        return {
            "locker_id": locker_id,
            "placed_parcels_count": locker["placed_parcels_count"],
            "events": event_history.get(locker_id, []),
        }

    @app.post("/events/consume")
    async def consume_events(request: Request) -> dict[str, Any]:
        try:
            consumed = request.app.state.event_broker.consume_available(
                QUEUE_NAME, handle_parcel_placed
            )
        except BrokerUnavailableError as exc:
            raise HTTPException(
                status_code=503, detail="RabbitMQ broker is unavailable"
            ) from exc
        except (ValueError, LookupError) as exc:
            raise HTTPException(
                status_code=422, detail=f"Invalid event payload: {exc}"
            ) from exc
        return {
            "queue": QUEUE_NAME,
            "consumed_messages": consumed,
            "unique_events_processed": len(processed_event_ids),
        }

    return app


app = create_app()
