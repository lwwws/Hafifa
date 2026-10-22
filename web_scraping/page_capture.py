import base64
from pathlib import Path

from pydantic import BaseModel, field_serializer

SCREENSHOT_FILE = "screenshot.png"
JSON_FILE = "browse.json"


class PageCapture(BaseModel):
    html: str
    resources: list[str]
    screenshot: bytes

    @field_serializer("screenshot")
    def encode_screenshot(self, screenshot: bytes) -> str:
        # JSON can't hold raw bytes, so we store the PNG as base64 text
        return base64.b64encode(screenshot).decode("ascii")

    def save(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / SCREENSHOT_FILE).write_bytes(self.screenshot)
        (out_dir / JSON_FILE).write_text(self.model_dump_json(indent=2), encoding="utf-8")
