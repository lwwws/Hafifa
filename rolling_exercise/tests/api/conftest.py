import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.configs.settings import ApiSettings
from tests.providers.settings import Setting


@pytest.fixture
def settings(tmp_path) -> ApiSettings:
    return ApiSettings(
        log_file_path=tmp_path / "test.log",
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        alert_aqi_threshold=Setting.ALERT_AQI_THRESHOLD,
        api_host=Setting.API_HOST,
        api_port=Setting.API_PORT,
        max_request_body_size_bytes=Setting.MAX_REQUEST_BODY_SIZE_BYTES,
    )


@pytest.fixture
def client(settings) -> TestClient:
    return TestClient(create_app(settings))
