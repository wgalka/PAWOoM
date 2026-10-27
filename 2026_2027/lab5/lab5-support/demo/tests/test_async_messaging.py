from urllib.error import HTTPError

import pytest
from httpx import ASGITransport, AsyncClient

from demo.locker_service.app.main import QUEUE_NAME, create_app as create_locker_app
from demo.parcel_service.app.main import ROUTING_KEY, create_app as create_parcel_app
from demo.shared.messaging import InMemoryEventBroker


class FakeEurekaClient:
    def __init__(self, response=None, error=None):
        self.response = (
            response
            if response is not None
            else {
                "id": "KRK-1024",
                "name": "Galeria",
                "address": "Dluga 10",
                "city": "Krakow",
                "status": "online",
                "placed_parcels_count": 0,
            }
        )
        self.error = error
        self.calls = []
        self.starts = 0
        self.stops = 0

    async def start(self):
        self.starts += 1

    async def stop(self):
        self.stops += 1

    async def do_service(self, service_name, path, return_type=None, timeout=None):
        self.calls.append((service_name, path, return_type, timeout))
        if self.error:
            raise self.error
        return self.response


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_parcel_creation_publishes_domain_event_and_locker_consumes_it():
    broker = InMemoryEventBroker()
    fake_eureka = FakeEurekaClient()

    locker_app = create_locker_app(eureka_client=fake_eureka, event_broker=broker)
    parcel_app = create_parcel_app(eureka_client=fake_eureka, event_broker=broker)

    async with locker_app.router.lifespan_context(locker_app), parcel_app.router.lifespan_context(parcel_app):
        async with (
            AsyncClient(transport=ASGITransport(app=parcel_app), base_url="http://parcel") as parcel_client,
            AsyncClient(transport=ASGITransport(app=locker_app), base_url="http://locker") as locker_client,
        ):
            create_resp = await parcel_client.post(
                "/parcels",
                json={"id": "PCK-101", "locker_id": "KRK-1024", "size": "M"},
            )
            assert create_resp.status_code == 201
            assert create_resp.json()["status"] == "placed"
            assert len(broker.published) == 1
            routing_key, event = broker.published[0]
            assert routing_key == ROUTING_KEY
            assert event["event_type"] == "ParcelPlaced"
            assert event["parcel_id"] == "PCK-101"

            # Przed skonsumowaniem wiadomości licznik w Locker Service wynosi 0
            before_resp = await locker_client.get("/lockers/KRK-1024")
            assert before_resp.json()["placed_parcels_count"] == 0

            # Pobranie i przetworzenie wiadomości z kolejki
            consume_resp = await locker_client.post("/events/consume")
            assert consume_resp.status_code == 200
            assert consume_resp.json()["consumed_messages"] == 1

            after_resp = await locker_client.get("/lockers/KRK-1024")
            assert after_resp.json()["placed_parcels_count"] == 1


@pytest.mark.anyio
async def test_consumer_is_idempotent_for_duplicate_event_id():
    broker = InMemoryEventBroker()
    fake_eureka = FakeEurekaClient()
    locker_app = create_locker_app(eureka_client=fake_eureka, event_broker=broker)

    duplicate_event = {
        "event_id": "evt-dup-001",
        "event_type": "ParcelPlaced",
        "parcel_id": "PCK-202",
        "locker_id": "KRK-1024",
        "size": "S",
        "occurred_at": "2026-10-27T10:00:00+00:00",
    }

    async with locker_app.router.lifespan_context(locker_app):
        broker.publish(ROUTING_KEY, duplicate_event)
        broker.publish(ROUTING_KEY, duplicate_event)

        async with AsyncClient(transport=ASGITransport(app=locker_app), base_url="http://locker") as locker_client:
            consume_resp = await locker_client.post("/events/consume")
            assert consume_resp.status_code == 200
            assert consume_resp.json()["consumed_messages"] == 2
            assert consume_resp.json()["unique_events_processed"] == 1

            locker_resp = await locker_client.get("/lockers/KRK-1024")
            assert locker_resp.json()["placed_parcels_count"] == 1


@pytest.mark.anyio
async def test_offline_locker_or_missing_locker_does_not_publish_event():
    broker = InMemoryEventBroker()
    offline_eureka = FakeEurekaClient(
        response={
            "id": "KRK-2048",
            "name": "Dworzec",
            "address": "Pawia 5",
            "city": "Krakow",
            "status": "offline",
            "placed_parcels_count": 0,
        }
    )
    parcel_app = create_parcel_app(eureka_client=offline_eureka, event_broker=broker)

    async with parcel_app.router.lifespan_context(parcel_app):
        async with AsyncClient(transport=ASGITransport(app=parcel_app), base_url="http://parcel") as parcel_client:
            conflict_resp = await parcel_client.post(
                "/parcels",
                json={"id": "PCK-303", "locker_id": "KRK-2048", "size": "L"},
            )
            assert conflict_resp.status_code == 409
            assert broker.published == []


@pytest.mark.anyio
async def test_broker_outage_returns_503_and_does_not_leave_unconfirmed_parcel():
    broker = InMemoryEventBroker(down=True)
    fake_eureka = FakeEurekaClient()
    parcel_app = create_parcel_app(eureka_client=fake_eureka, event_broker=broker)

    async with parcel_app.router.lifespan_context(parcel_app):
        async with AsyncClient(transport=ASGITransport(app=parcel_app), base_url="http://parcel") as parcel_client:
            resp = await parcel_client.post(
                "/parcels",
                json={"id": "PCK-404", "locker_id": "KRK-1024", "size": "M"},
            )
            assert resp.status_code == 503
            list_resp = await parcel_client.get("/parcels")
            assert list_resp.json() == []


@pytest.mark.anyio
async def test_missing_destination_locker_returns_404_without_publishing():
    broker = InMemoryEventBroker()
    error = HTTPError("http://locker/lockers/UNKNOWN", 404, "Not Found", {}, None)
    fake_eureka = FakeEurekaClient(error=error)
    parcel_app = create_parcel_app(eureka_client=fake_eureka, event_broker=broker)

    async with parcel_app.router.lifespan_context(parcel_app):
        async with AsyncClient(transport=ASGITransport(app=parcel_app), base_url="http://parcel") as parcel_client:
            resp = await parcel_client.post(
                "/parcels",
                json={"id": "PCK-505", "locker_id": "UNKNOWN", "size": "S"},
            )
            assert resp.status_code == 404
            assert broker.published == []
            assert fake_eureka.starts == fake_eureka.stops == 1
