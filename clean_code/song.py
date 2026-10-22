from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
from pydantic import BaseModel

UNKNOWN_ARTIST = "Unknown artist"


def _first_tag_value(tags: EasyID3 | dict, key: str, default: str) -> str:
    # EasyID3 stores each tag as a list of values, so take the first.
    return tags.get(key, [default])[0]


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

        return cls(
            path=file_path,
            title=_first_tag_value(tags, "title", file_path.stem),
            artist=_first_tag_value(tags, "artist", UNKNOWN_ARTIST),
        )
