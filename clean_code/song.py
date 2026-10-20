# song.py
from dataclasses import dataclass
from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

UNKNOWN_ARTIST = "Unknown artist"


@dataclass
class Song:
    path: Path
    title: str
    artist: str

    @classmethod
    def from_file(cls, path: str) -> "Song":
        """Read title and artist from the file's tags, with fallbacks if they're missing."""
        file_path = Path(path)
        try:
            tags = EasyID3(file_path)
        except ID3NoHeaderError: # the file has no tags at all
            tags = {}
        title = tags.get("title", [file_path.stem])[0]
        artist = tags.get("artist", [UNKNOWN_ARTIST])[0]
        return cls(file_path, title, artist)