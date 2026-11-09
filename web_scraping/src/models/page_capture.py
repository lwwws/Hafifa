import base64

from pydantic import BaseModel, field_serializer


class PageCapture(BaseModel):
    html: str
    resources: list[str]
    screenshot: bytes

    @field_serializer("screenshot")
    def encode_screenshot(self, screenshot: bytes) -> str:
        return base64.b64encode(screenshot).decode("ascii")
