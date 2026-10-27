from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal
from urllib.error import HTTPError, URLError
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from py_eureka_client.eureka_client import EurekaClient

from demo.shared.eureka import create_eureka_client
from demo.shared.messaging import BrokerUnavailableError, RabbitEventBroker

ROUTING_KEY = "parcel.placed"


class ParcelCreate(BaseModel):
    id: str = Field(..., min_length=3, max_length=32)
    locker_id: str = Field(..., min_length=3, max_length=32)
    size: Literal["S", "M", "L"] = "M"


def create_app(
    eureka_client: EurekaClient | None = None,
    event_broker: Any | None = None,
) -> FastAPI:
    client = (
        eureka_client
        if eureka_client is not None
        else create_eureka_client("PARCEL-SERVICE", 8102)
    )
    broker = event_broker if event_broker is not None else RabbitEventBroker()
    parcels: dict[str, dict[str, Any]] = {}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.eureka_client = client
        app.state.event_broker = broker
        app.state.parcels = parcels
        try:
            await client.start()
            yield
        finally:
            try:
                await client.stop()
            finally:
                broker.close()

    app = FastAPI(title="Parcel Service", version="1.0.0", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "PARCEL-SERVICE"}

    @app.get("/delivery-check/{locker_id}")
    async def check_destination(locker_id: str) -> dict[str, object]:
        try:
            locker = await app.state.eureka_client.do_service(
                "LOCKER-SERVICE",
                f"/lockers/{locker_id}",
                return_type="json",
                timeout=3,
            )
        except HTTPError as exc:
            if exc.code == 404:
                raise HTTPException(
                    status_code=404, detail="Destination locker not found"
                ) from exc
            raise HTTPException(
                status_code=502, detail="Locker Service returned an HTTP error"
            ) from exc
        except (URLError, TimeoutError) as exc:
            raise HTTPException(
                status_code=503, detail="Locker Service is unavailable"
            ) from exc

        return {"destination": locker_id, "locker": locker}

    @app.get("/parcels")
    async def list_parcels() -> list[dict[str, Any]]:
        return list(parcels.values())

    @app.get("/parcels/{parcel_id}")
    async def get_parcel(parcel_id: str) -> dict[str, Any]:
        parcel = parcels.get(parcel_id)
        if parcel is None:
            raise HTTPException(status_code=404, detail="Parcel not found")
        return parcel

    @app.post("/parcels", status_code=status.HTTP_201_CREATED)
    async def create_parcel(payload: ParcelCreate) -> dict[str, Any]:
        if payload.id in parcels:
            raise HTTPException(status_code=409, detail="Parcel already exists")

        try:
            locker = await app.state.eureka_client.do_service(
                "LOCKER-SERVICE",
                f"/lockers/{payload.locker_id}",
                return_type="json",
                timeout=3,
            )
        except HTTPError as exc:
            if exc.code == 404:
                raise HTTPException(
                    status_code=404, detail="Destination locker not found"
                ) from exc
            raise HTTPException(
                status_code=502, detail="Locker Service returned an HTTP error"
            ) from exc
        except (URLError, TimeoutError) as exc:
            raise HTTPException(
                status_code=503, detail="Locker Service is unavailable"
            ) from exc

        if locker.get("status") != "online":
            raise HTTPException(
                status_code=409, detail="Destination locker is not online"
            )

        event = {
            "event_id": f"evt-{uuid.uuid4().hex[:12]}",
            "event_type": "ParcelPlaced",
            "parcel_id": payload.id,
            "locker_id": payload.locker_id,
            "size": payload.size,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            broker.publish(ROUTING_KEY, event)
        except BrokerUnavailableError as exc:
            raise HTTPException(
                status_code=503, detail="RabbitMQ broker is unavailable"
            ) from exc

        record = {
            "id": payload.id,
            "locker_id": payload.locker_id,
            "size": payload.size,
            "status": "placed",
            "last_event_id": event["event_id"],
        }
        parcels[payload.id] = record
        return record

    return app


app = create_app()
