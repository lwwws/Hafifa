from pathlib import Path

from models.page_capture import PageCapture


class PageCaptureWriter:
    def __init__(self, output_dir: Path, screenshot_file: str, json_file: str):
        self.output_dir = output_dir
        self.screenshot_file = screenshot_file
        self.json_file = json_file

    def write(self, capture: PageCapture, folder_name: str):
        folder = self.output_dir / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / self.screenshot_file).write_bytes(capture.screenshot)
        (folder / self.json_file).write_text(capture.model_dump_json(indent=2), encoding="utf-8")
