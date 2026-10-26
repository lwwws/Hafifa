import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

from scraper import Scraper
from settings import ScraperSettings

logger = logging.getLogger(__name__)


def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


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
