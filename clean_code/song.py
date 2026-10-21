from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
from pydantic import BaseModel

UNKNOWN_ARTIST = "Unknown artist"


class Song(BaseModel):
    path: Path
    title: str
    artist: str

    @classmethod
    def from_file(cls, path: str) -> "Song":
        file_path = Path(path)

        try:
            tags = EasyID3(file_path)
        except ID3NoHeaderError:
            tags = {}

        # EasyID3 stores each tag as a list of values, so take the first.
        title = tags.get("title", [file_path.stem])[0]
        artist = tags.get("artist", [UNKNOWN_ARTIST])[0]

        return cls(path=file_path, title=title, artist=artist)
