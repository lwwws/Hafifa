import asyncio
import logging
from pathlib import Path

from playwright.async_api import Browser, Error as PlaywrightError
from pydantic_settings import BaseSettings, SettingsConfigDict

from page_capture import PageCapture

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
    """Loads pages in a shared browser and saves each one to its own folder:

        url_N/screenshot.png   the page as it looked after loading
        url_N/browse.json      {"html", "resources", "screenshot" (base64 PNG)}
    """

    def __init__(self, browser: Browser, settings: ScraperSettings):
        self.browser = browser
        self.settings = settings
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_pages)

    async def capture(self, url: str) -> PageCapture:
        resources: list[str] = []

        async with await self.browser.new_page() as page:
            # Subscribe before goto
            page.on("request", lambda request: resources.append(request.url))
            await page.goto(url, timeout=self.settings.page_timeout_ms)
            html = await page.content()
            screenshot = await page.screenshot()

        return PageCapture(html=html, resources=resources, screenshot=screenshot)

    async def browse(self, url: str, out_dir: Path) -> bool:
        """Capture the URL and save it to out_dir.

        Returns False instead of raising when the page fails to load
        """
        try:
            async with self.semaphore:
                capture = await self.capture(url)
        except PlaywrightError as error:
            logger.error("Failed %s: %s", url, error.message.splitlines()[0])
            return False

        capture.save(out_dir)
        logger.info("Saved %s to %s", url, out_dir.name)

        return True

    async def browse_all(self, urls: list[str]) -> int:
        results = await asyncio.gather(*(
            self.browse(url, self.settings.output_dir / f"url_{index}")
            for index, url in enumerate(urls, start=1)
        ))

        # Return how many pages were saved successfully.
        return sum(results)
