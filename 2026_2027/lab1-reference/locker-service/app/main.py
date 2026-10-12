from fastapi import FastAPI, HTTPException, status

from app.models import (
    Compartment,
    CompartmentCreate,
    CompartmentStatusUpdate,
    Locker,
    LockerCreate,
)
from app.storage import ConflictError, InMemoryStore, NotFoundError


def create_app(store: InMemoryStore | None = None) -> FastAPI:
    app = FastAPI(
        title="Locker Service",
        description="Reference microservice for the first laboratory",
        version="1.0.0",
    )
    app.state.store = store or InMemoryStore()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "locker-service"}

    @app.get("/lockers", response_model=list[Locker])
    def list_lockers() -> list[Locker]:
        return app.state.store.list_lockers()

    @app.get("/lockers/{locker_id}", response_model=Locker)
    def get_locker(locker_id: str) -> Locker:
        try:
            return app.state.store.get_locker(locker_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/lockers", response_model=Locker, status_code=status.HTTP_201_CREATED)
    def add_locker(payload: LockerCreate) -> Locker:
        try:
            return app.state.store.add_locker(payload)
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/lockers/{locker_id}/compartments", response_model=list[Compartment])
    def list_compartments(locker_id: str) -> list[Compartment]:
        try:
            return app.state.store.list_compartments(locker_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/lockers/{locker_id}/compartments",
        response_model=Compartment,
        status_code=status.HTTP_201_CREATED,
    )
    def add_compartment(locker_id: str, payload: CompartmentCreate) -> Compartment:
        try:
            return app.state.store.add_compartment(locker_id, payload)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.patch("/compartments/{compartment_id}/status", response_model=Compartment)
    def update_compartment_status(
        compartment_id: str, payload: CompartmentStatusUpdate
    ) -> Compartment:
        try:
            return app.state.store.update_compartment_status(
                compartment_id, payload.status
            )
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return app


app = create_app()
