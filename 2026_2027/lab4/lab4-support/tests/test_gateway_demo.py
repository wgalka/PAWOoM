"""Integration tests: start Eureka, the LAB3 demo and the gateway first."""

import os

import httpx
import pytest


@pytest.fixture
def client():
    with httpx.Client(
        base_url=os.getenv("GATEWAY_URL", "http://127.0.0.1:8080"),
        timeout=10.0,
        trust_env=False,
    ) as http:
        yield http


def test_gateway_process_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "API-GATEWAY"}


def test_locker_route_and_header(client):
    response = client.get("/api/lockers/KRK-1024")
    assert response.status_code == 200
    assert response.json()["id"] == "KRK-1024"
    assert response.headers["x-gateway"] == "lab4"


def test_delivery_route_calls_dependency(client):
    response = client.get("/api/delivery-check/KRK-1024")
    assert response.status_code == 200
    assert response.json()["destination"] == "KRK-1024"
    assert response.json()["locker"]["id"] == "KRK-1024"


def test_domain_404_is_forwarded(client):
    response = client.get("/api/lockers/UNKNOWN")
    assert response.status_code == 404
    assert response.json() == {"detail": "Locker not found"}


def test_unknown_route_is_not_forwarded(client):
    response = client.get("/not-a-route")
    assert response.status_code == 404
    assert "x-gateway" not in response.headers
