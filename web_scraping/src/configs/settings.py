from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SCRAPER_", frozen=True)

    input_file: Path = Path("input/urls.input")
    output_dir: Path = Path("output")
    screenshot_file: str = "screenshot.png"
    json_file: str = "browse.json"
    browser_channel: str = "chrome"
    max_concurrent_pages: int = 5
    page_timeout_ms: int = 60_000
