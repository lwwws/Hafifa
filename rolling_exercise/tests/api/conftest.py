import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.configs.settings import ApiSettings


@pytest.fixture
def settings(tmp_path) -> ApiSettings:
    return ApiSettings(
        log_file_path=tmp_path / "test.log",
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        alert_aqi_threshold=300,
        api_host="127.0.0.1",
        api_port=8000,
        max_request_body_size_bytes=10_000,
    )


@pytest.fixture
def client(settings) -> TestClient:
    return TestClient(create_app(settings))
