import asyncio
import logging
from pathlib import Path

from playwright.async_api import Browser
from playwright.async_api import Error as PlaywrightError

from page_capture import PageCapture
from settings import ScraperSettings

logger = logging.getLogger(__name__)


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
            page.on("request", lambda request: resources.append(request.url))
            await page.goto(url, timeout=self.settings.page_timeout_ms)
            html = await page.content()
            screenshot = await page.screenshot()

        return PageCapture(html=html, resources=resources, screenshot=screenshot)

    def save(self, capture: PageCapture, out_dir: Path):
        out_dir.mkdir(parents=True, exist_ok=True)
        capture.save(out_dir / self.settings.screenshot_file, out_dir / self.settings.json_file)

    async def try_capture_and_save(self, url: str, out_dir: Path) -> bool:
        try:
            async with self.semaphore:
                capture = await self.capture(url)
        except PlaywrightError as error:
            logger.error(f"Failed {url}: {error.message.splitlines()[0]}")
            return False

        self.save(capture, out_dir)
        logger.info(f"Saved {url} to {out_dir.name}")

        return True

    async def capture_and_save_all(self, urls: list[str]) -> int:
        saved_flags = await asyncio.gather(*(
            self.try_capture_and_save(url, self.settings.output_dir / f"url_{index}")
            for index, url in enumerate(urls, start=1)
        ))

        return sum(saved_flags)
