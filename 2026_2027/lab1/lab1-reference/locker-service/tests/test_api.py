import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.storage import InMemoryStore


@pytest.fixture
def client():
    with TestClient(create_app(InMemoryStore())) as test_client:
        yield test_client


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "locker-service"


def test_list_seeded_lockers(client) -> None:
    response = client.get("/lockers")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "KRK-1024"


def test_get_missing_locker_returns_404(client) -> None:
    response = client.get("/lockers/UNKNOWN")
    assert response.status_code == 404
    assert "UNKNOWN" in response.json()["detail"]


def test_create_locker_and_reject_duplicate_without_changing_state(client) -> None:
    payload = {
        "id": "WAW-0001",
        "name": "Warszawa Centrum",
        "address": "ul. Testowa 1",
        "city": "Warszawa",
    }
    response = client.post("/lockers", json=payload)
    assert response.status_code == 201
    stored = client.get("/lockers/WAW-0001")
    assert stored.status_code == 200
    assert stored.json() == {**payload, "status": "online"}
    before = client.get("/lockers").json()

    duplicate = client.post("/lockers", json={**payload, "city": "Gdańsk"})
    assert duplicate.status_code == 409
    assert "already exists" in duplicate.json()["detail"]
    assert client.get("/lockers").json() == before


def test_valid_status_transitions_are_visible_in_subsequent_reads(client) -> None:
    for new_status in ["reserved", "occupied", "free", "out_of_service", "free"]:
        response = client.patch(
            "/compartments/KRK-1024-L1/status", json={"status": new_status}
        )
        assert response.status_code == 200
        assert response.json()["status"] == new_status
        compartments = client.get("/lockers/KRK-1024/compartments").json()
        compartment = next(item for item in compartments if item["id"] == "KRK-1024-L1")
        assert compartment["status"] == new_status


def test_invalid_status_is_rejected_without_changing_state(client) -> None:
    before = client.get("/lockers/KRK-1024/compartments").json()
    response = client.patch(
        "/compartments/KRK-1024-L1/status",
        json={"status": "broken-value"},
    )
    assert response.status_code == 422
    assert any(error["loc"] == ["body", "status"] for error in response.json()["detail"])
    assert client.get("/lockers/KRK-1024/compartments").json() == before


def test_forbidden_transition_is_rejected_without_changing_state(client) -> None:
    reserved = client.patch(
        "/compartments/KRK-1024-L1/status", json={"status": "reserved"}
    )
    assert reserved.status_code == 200
    before = client.get("/lockers/KRK-1024/compartments").json()
    response = client.patch(
        "/compartments/KRK-1024-L1/status", json={"status": "out_of_service"}
    )
    assert response.status_code == 409
    assert "reserved" in response.json()["detail"]
    assert "out_of_service" in response.json()["detail"]
    assert client.get("/lockers/KRK-1024/compartments").json() == before


def test_same_status_is_allowed_without_changing_state(client) -> None:
    before = client.get("/lockers/KRK-1024/compartments").json()
    response = client.patch(
        "/compartments/KRK-1024-L1/status", json={"status": "free"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "free"
    assert client.get("/lockers/KRK-1024/compartments").json() == before


def test_missing_compartment_returns_404_without_changing_state(client) -> None:
    before = client.get("/lockers/KRK-1024/compartments").json()
    response = client.patch("/compartments/UNKNOWN/status", json={"status": "reserved"})
    assert response.status_code == 404
    assert "UNKNOWN" in response.json()["detail"]
    assert client.get("/lockers/KRK-1024/compartments").json() == before


def test_new_application_has_its_own_initial_state(client) -> None:
    response = client.patch(
        "/compartments/KRK-1024-L1/status", json={"status": "reserved"}
    )
    assert response.status_code == 200
    with TestClient(create_app()) as other_client:
        compartments = other_client.get("/lockers/KRK-1024/compartments").json()
        assert all(item["status"] == "free" for item in compartments)
    original = client.get("/lockers/KRK-1024/compartments").json()
    assert next(item for item in original if item["id"] == "KRK-1024-L1")["status"] == "reserved"
