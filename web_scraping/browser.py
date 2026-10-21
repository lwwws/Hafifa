import asyncio
import base64
import json
from pathlib import Path

from playwright.async_api import Browser, Error as PlaywrightError, async_playwright

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "input" / "urls.input"
OUTPUT_DIR = BASE_DIR / "output"
MAX_CONCURRENT_PAGES = 5
PAGE_TIMEOUT_MS = 60_000


def read_urls(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()

    return [line.strip() for line in lines if line.strip()]


def write_browse_json(path: Path, html: str, resources: list[str], screenshot: bytes) -> None:
    """Write the page data to a JSON file, with the screenshot encoded as base64."""
    data = {
        "html": html,
        "resources": resources,
        "screenshot": base64.b64encode(screenshot).decode("ascii"),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def browse(browser: Browser, semaphore: asyncio.Semaphore, url: str, out_dir: Path) -> bool:
    """Open the URL and save its HTML, loaded resources and screenshot.

    Returns False instead of raising when the page fails to load, so one bad URL
    doesn't stop the others.
    """
    resources: list[str] = []

    try:
        async with semaphore, await browser.new_page() as page:
            page.on("request", lambda request: resources.append(request.url))
            await page.goto(url, timeout=PAGE_TIMEOUT_MS)
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
    urls = read_urls(INPUT_FILE)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)

    async with async_playwright() as playwright:
        async with await playwright.chromium.launch(channel="chrome") as browser:
            tasks = [
                browse(browser, semaphore, url, OUTPUT_DIR / f"url_{index}")
                for index, url in enumerate(urls, start=1)
            ]

            results = await asyncio.gather(*tasks)

    print(f"Done: {sum(results)}/{len(urls)} pages saved")



if __name__ == "__main__":
    asyncio.run(main())