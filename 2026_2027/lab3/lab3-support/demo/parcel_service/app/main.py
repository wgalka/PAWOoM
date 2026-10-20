from contextlib import asynccontextmanager
from urllib.error import HTTPError, URLError

from fastapi import FastAPI, HTTPException
from py_eureka_client.eureka_client import EurekaClient

from demo.shared.eureka import create_eureka_client


def create_app(eureka_client: EurekaClient | None = None) -> FastAPI:
    client = eureka_client or create_eureka_client("PARCEL-SERVICE", 8102)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.eureka_client = client
        await client.start()
        try:
            yield
        finally:
            await client.stop()

    app = FastAPI(title="Parcel Service", version="1.0.0", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "PARCEL-SERVICE"}

    @app.get("/delivery-check/{locker_code}")
    async def check_destination(locker_code: str) -> dict[str, object]:
        try:
            locker = await app.state.eureka_client.do_service(
                "LOCKER-SERVICE",
                f"/lockers/{locker_code}",
                return_type="json",
            )
        except HTTPError as exc:
            if exc.code == 404:
                raise HTTPException(
                    status_code=404, detail="Destination locker not found"
                ) from exc
            raise HTTPException(
                status_code=502, detail="Locker Service returned an HTTP error"
            ) from exc
        except URLError as exc:
            raise HTTPException(
                status_code=503, detail="Locker Service is unavailable"
            ) from exc

        return {"destination": locker_code, "locker": locker}

    return app


app = create_app()
