from urllib.error import HTTPError, URLError

import pytest
from httpx import ASGITransport, AsyncClient

from demo.parcel_service.app.main import create_app


class FakeEurekaClient:
    def __init__(self, response=None, error=None):
        self.response = response or {
            "code": "KRK-1024",
            "status": "active",
            "free_compartments": 2,
        }
        self.error = error
        self.calls = []

    async def start(self):
        return None

    async def stop(self):
        return None

    async def do_service(self, service_name, path, return_type=None):
        self.calls.append((service_name, path, return_type))
        if self.error:
            raise self.error
        return self.response


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_delivery_check_discovers_locker_service_by_name():
    fake = FakeEurekaClient()
    app = create_app(eureka_client=fake)

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/delivery-check/KRK-1024")

    assert response.status_code == 200
    assert response.json()["locker"]["code"] == "KRK-1024"
    assert fake.calls == [("LOCKER-SERVICE", "/lockers/KRK-1024", "json")]


@pytest.mark.anyio
async def test_delivery_check_returns_service_unavailable_when_dependency_is_down():
    fake = FakeEurekaClient(error=URLError("connection refused"))
    app = create_app(eureka_client=fake)

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/delivery-check/KRK-1024")

    assert response.status_code == 503
    assert response.json()["detail"] == "Locker Service is unavailable"


@pytest.mark.anyio
async def test_delivery_check_preserves_not_found_from_dependency():
    error = HTTPError("http://locker/lockers/UNKNOWN", 404, "Not Found", {}, None)
    fake = FakeEurekaClient(error=error)
    app = create_app(eureka_client=fake)

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/delivery-check/UNKNOWN")

    assert response.status_code == 404
    assert response.json()["detail"] == "Destination locker not found"
