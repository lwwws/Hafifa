import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

from scraper import Scraper, ScraperSettings

logger = logging.getLogger(__name__)


def read_urls(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()

    return [line.strip() for line in lines if line.strip()]


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = ScraperSettings()
    urls = read_urls(settings.input_file)

    async with (
        async_playwright() as playwright,
        await playwright.chromium.launch(channel=settings.browser_channel) as browser,
    ):
        saved = await Scraper(browser, settings).browse_all(urls)

    logger.info("Done: %d/%d pages saved", saved, len(urls))


if __name__ == "__main__":
    asyncio.run(main())
