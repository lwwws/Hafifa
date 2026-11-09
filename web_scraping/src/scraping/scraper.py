import asyncio
import logging

from playwright.async_api import Browser
from playwright.async_api import Error as PlaywrightError

from configs.settings import ScraperSettings
from models.page_capture import PageCapture
from storage.page_capture_writer import PageCaptureWriter

logger = logging.getLogger(__name__)


class Scraper:
    """
    Loads pages in a shared browser and saves each one to its own folder:

        url_N/screenshot.png   the page as it looked after loading
        url_N/browse.json      {"html", "resources", "screenshot" (base64 PNG)}
    """

    def __init__(self, browser: Browser, writer: PageCaptureWriter, settings: ScraperSettings):
        self.browser = browser
        self.writer = writer
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

    async def capture_and_save(self, url: str, folder_name: str) -> bool:
        try:
            async with self.semaphore:
                capture = await self.capture(url)
        except PlaywrightError as error:
            logger.error(f"Failed {url}: {error.message.splitlines()[0]}")

            return False

        self.writer.write(capture, folder_name)
        logger.info(f"Saved {url} to {folder_name}")

        return True

    async def capture_and_save_all(self, urls: list[str]) -> int:
        saved_flags = await asyncio.gather(*(
            self.capture_and_save(url, f"url_{index}")
            for index, url in enumerate(urls, start=1)
        ))

        return sum(saved_flags)
