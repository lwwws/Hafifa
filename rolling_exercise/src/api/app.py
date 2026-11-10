from fastapi import FastAPI

from src.api import health_router
from src.configs.settings import ApiSettings


def create_app(settings: ApiSettings) -> FastAPI:
    app = FastAPI(title="Air Quality API")
    app.state.settings = settings

    app.include_router(health_router.router)

    return app
