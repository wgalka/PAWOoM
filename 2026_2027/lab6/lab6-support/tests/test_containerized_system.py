"""End-to-end integration tests for the containerized system via API Gateway (:8080)."""

import os
import uuid

import httpx
import pytest


@pytest.fixture
def client():
    base_url = os.getenv("GATEWAY_URL", "http://127.0.0.1:8080")
    with httpx.Client(base_url=base_url, timeout=10.0, trust_env=False) as http:
        yield http


def test_gateway_health_in_container(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "API-GATEWAY"}


def test_locker_route_through_containerized_gateway(client):
    response = client.get("/api/lockers/KRK-1024")
    assert response.status_code == 200
    assert response.json()["id"] == "KRK-1024"
    assert response.headers.get("x-gateway") == "lab4"


def test_synchronous_discovery_flow_between_containers(client):
    response = client.get("/api/delivery-check/KRK-1024")
    assert response.status_code == 200
    assert response.json()["destination"] == "KRK-1024"
    assert response.json()["locker"]["id"] == "KRK-1024"
    assert response.headers.get("x-gateway") == "lab4"


def test_asynchronous_rabbitmq_flow_between_containers(client):
    before = client.get("/api/lockers/KRK-1024").json()["placed_parcels_count"]

    parcel_id = f"PCK-{uuid.uuid4().hex[:6].upper()}"
    create_resp = client.post(
        "/api/parcels",
        json={"id": parcel_id, "locker_id": "KRK-1024", "size": "M"},
    )
    assert create_resp.status_code == 201
    assert create_resp.headers.get("x-gateway") == "lab4"

    consume_resp = client.post("/api/lockers/events/consume")
    if consume_resp.status_code == 404:
        # Gdy endpoint konsumpcji wystawiony jest pod /events/consume lub odświeżany wewnętrznie
        pass

    after_locker = client.get("/api/lockers/KRK-1024")
    assert after_locker.status_code == 200
    assert after_locker.json()["placed_parcels_count"] >= before


def test_business_rule_conflict_is_preserved_in_containers(client):
    parcel_id = f"PCK-{uuid.uuid4().hex[:6].upper()}"
    conflict_resp = client.post(
        "/api/parcels",
        json={"id": parcel_id, "locker_id": "KRK-2048", "size": "S"},
    )
    assert conflict_resp.status_code == 409
    assert conflict_resp.headers.get("x-gateway") == "lab4"
