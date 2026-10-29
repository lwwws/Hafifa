import base64
from pathlib import Path

from pydantic import BaseModel, field_serializer


class PageCapture(BaseModel):
    html: str
    resources: list[str]
    screenshot: bytes

    @field_serializer("screenshot")
    def encode_screenshot(self, screenshot: bytes) -> str:
        return base64.b64encode(screenshot).decode("ascii")

    def save(self, screenshot_path: Path, json_path: Path):
        screenshot_path.write_bytes(self.screenshot)
        json_path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
