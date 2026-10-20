from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from py_eureka_client.eureka_client import EurekaClient

from demo.shared.eureka import create_eureka_client


LOCKERS = {
    "KRK-1024": {"code": "KRK-1024", "status": "active", "free_compartments": 2}
}


def create_app(eureka_client: EurekaClient | None = None) -> FastAPI:
    client = eureka_client or create_eureka_client("LOCKER-SERVICE", 8101)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.eureka_client = client
        await client.start()
        try:
            yield
        finally:
            await client.stop()

    app = FastAPI(title="Locker Service", version="1.0.0", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "LOCKER-SERVICE"}

    @app.get("/lockers/{locker_code}")
    async def get_locker(locker_code: str) -> dict[str, str | int]:
        locker = LOCKERS.get(locker_code)
        if locker is None:
            raise HTTPException(status_code=404, detail="Locker not found")
        return locker

    return app


app = create_app()
