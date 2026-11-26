from fastapi import FastAPI
from starlette.middleware.body_limit import RequestBodyLimitMiddleware

from src.api import health_router, upload_router
from src.api.exception_handlers import handle_invalid_csv_file
from src.configs.settings import ApiSettings
from src.db.database import create_session_factory
from src.errors import InvalidCsvFileError


def create_app(settings: ApiSettings) -> FastAPI:
    app = FastAPI(title="Air Quality API")
    app.state.settings = settings
    app.state.session_factory = create_session_factory(settings.database_url)
    _include_routers(app)
    _add_exception_handlers(app)
    app.add_middleware(RequestBodyLimitMiddleware, max_body_size=settings.max_request_body_size_bytes)

    return app


def _include_routers(app: FastAPI):
    app.include_router(health_router.router)
    app.include_router(upload_router.router)


def _add_exception_handlers(app: FastAPI):
    app.add_exception_handler(InvalidCsvFileError, handle_invalid_csv_file)
