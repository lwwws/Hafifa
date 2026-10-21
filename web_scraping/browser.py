import asyncio
import base64
import json
from pathlib import Path

from playwright.async_api import Browser, Error as PlaywrightError, async_playwright
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent


class ScraperSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SCRAPER_", frozen=True)

    input_file: Path = BASE_DIR / "input" / "urls.input"
    output_dir: Path = BASE_DIR / "output"
    browser_channel: str = "chrome"
    max_concurrent_pages: int = 5
    page_timeout_ms: int = 60_000


def read_urls(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()

    return [line.strip() for line in lines if line.strip()]


def write_browse_json(path: Path, html: str, resources: list[str], screenshot: bytes) -> None:
    data = {
        "html": html,
        "resources": resources,
        # JSON can't hold raw bytes, so the PNG is stored as base64 text.
        "screenshot": base64.b64encode(screenshot).decode("ascii"),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def browse(browser: Browser, semaphore: asyncio.Semaphore, url: str, out_dir: Path, timeout_ms: int) -> bool:
    """Open the URL and save its HTML, loaded resources and screenshot.

    Returns False instead of raising when the page fails to load, so one bad URL
    doesn't stop the others.
    """
    resources: list[str] = []

    try:
        async with semaphore, await browser.new_page() as page:
            # Subscribe before goto, otherwise the first requests are missed.
            page.on("request", lambda request: resources.append(request.url))
            await page.goto(url, timeout=timeout_ms)
            html = await page.content()
            out_dir.mkdir(parents=True, exist_ok=True)
            screenshot = await page.screenshot(path=out_dir / "screenshot.png")
    except PlaywrightError as error:
        print(f"Failed {url}: {error.message.splitlines()[0]}")
        return False

    write_browse_json(out_dir / "browse.json", html, resources, screenshot)
    print(f"Saved {url} to {out_dir.name}")

    return True


async def main() -> None:
    settings = ScraperSettings()
    urls = read_urls(settings.input_file)
    semaphore = asyncio.Semaphore(settings.max_concurrent_pages)

    async with (
        async_playwright() as playwright,
        await playwright.chromium.launch(channel=settings.browser_channel) as browser,
    ):
        tasks = [
            browse(browser, semaphore, url, settings.output_dir / f"url_{index}", settings.page_timeout_ms)
            for index, url in enumerate(urls, start=1)
        ]

        results = await asyncio.gather(*tasks)

    print(f"Done: {sum(results)}/{len(urls)} pages saved")


if __name__ == "__main__":
    asyncio.run(main())
