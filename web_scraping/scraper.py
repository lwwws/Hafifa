import asyncio
import base64
import json
import logging
from pathlib import Path

from playwright.async_api import Browser, Error as PlaywrightError
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent

logger = logging.getLogger(__name__)


class ScraperSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SCRAPER_", frozen=True)

    input_file: Path = BASE_DIR / "input" / "urls.input"
    output_dir: Path = BASE_DIR / "output"
    browser_channel: str = "chrome"
    max_concurrent_pages: int = 5
    page_timeout_ms: int = 60_000


class Scraper:
    def __init__(self, browser: Browser, settings: ScraperSettings):
        self.browser = browser
        self.settings = settings
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_pages)

    async def browse(self, url: str, out_dir: Path) -> bool:
        """Open the URL and save its HTML, loaded resources and screenshot.

        Returns False instead of raising when the page fails to load, so one bad URL
        doesn't stop the others.
        """
        resources: list[str] = []

        try:
            async with self.semaphore, await self.browser.new_page() as page:
                page.on("request", lambda request: resources.append(request.url))
                await page.goto(url, timeout=self.settings.page_timeout_ms)
                html = await page.content()
                out_dir.mkdir(parents=True, exist_ok=True)
                screenshot = await page.screenshot(path=out_dir / "screenshot.png")
        except PlaywrightError as error:
            logger.error("Failed %s: %s", url, error.message.splitlines()[0])
            return False

        write_browse_json(out_dir / "browse.json", html, resources, screenshot)
        logger.info("Saved %s to %s", url, out_dir.name)

        return True

    async def browse_all(self, urls: list[str]) -> int:
        results = await asyncio.gather(*(
            self.browse(url, self.settings.output_dir / f"url_{index}")
            for index, url in enumerate(urls, start=1)
        ))

        # Return how many pages were saved successfully.
        return sum(results)


def write_browse_json(path: Path, html: str, resources: list[str], screenshot: bytes) -> None:
    data = {
        "html": html,
        "resources": resources,
        "screenshot": base64.b64encode(screenshot).decode("ascii"),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
