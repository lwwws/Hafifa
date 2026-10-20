# playlist.py
class Playlist:
    """Paths of the added songs and which one is current."""

    def __init__(self):
        self.paths: list[str] = []
        self.index = 0

    def add(self, path: str) -> None:
        self.paths.append(path)

    def is_empty(self) -> bool:
        return not self.paths

    def current(self) -> str:
        return self.paths[self.index]

    def next(self) -> str:
        self.index = (self.index + 1) % len(self.paths)
        return self.current()

    def previous(self) -> str:
        self.index = (self.index - 1) % len(self.paths)
        return self.current()