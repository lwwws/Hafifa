"""A single music file and the title and artist read from its tags."""

from dataclasses import dataclass
from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

# Shown when a file has no artist tag.
UNKNOWN_ARTIST = "Unknown artist"


@dataclass
class Song:
    """One music file with the title and artist to display for it."""

    path: Path
    title: str
    artist: str

    @classmethod
    def from_file(cls, path: str) -> "Song":
        """Read title and artist from the file's tags, with fallbacks if they're missing.

        A missing title falls back to the file name without its extension, and a
        missing artist to UNKNOWN_ARTIST. Raises a mutagen error or OSError if the
        file is corrupt or can't be opened.
        """
        file_path = Path(path)
        try:
            tags = EasyID3(file_path)
        except ID3NoHeaderError:  # the file has no tags at all
            tags = {}
        # EasyID3 stores every tag as a list of values, so take the first one.
        title = tags.get("title", [file_path.stem])[0]
        artist = tags.get("artist", [UNKNOWN_ARTIST])[0]
        return cls(file_path, title, artist)