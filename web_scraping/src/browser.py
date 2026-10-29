import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

from configs.logging_config import configure_logging
from configs.settings import ScraperSettings
from scraping.scraper import Scraper

logger = logging.getLogger(__name__)


def read_urls(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()

    return [line.strip() for line in lines if line.strip()]


async def main():
    configure_logging()
    settings = ScraperSettings()
    urls = read_urls(settings.input_file)

    async with (
        async_playwright() as playwright,
        await playwright.chromium.launch(channel=settings.browser_channel) as browser,
    ):
        saved = await Scraper(browser, settings).capture_and_save_all(urls)

    logger.info(f"Done: {saved}/{len(urls)} pages saved")


if __name__ == "__main__":
    asyncio.run(main())
