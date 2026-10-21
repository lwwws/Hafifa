"""The ordered list of songs and which one is current."""

from song import Song

class Playlist:
    """Songs in the order they were added, plus the position of the current one.

    Pure logic: no GUI and no audio. Next and previous wrap around at the ends.
    """

    def __init__(self):
        self.songs: list[Song] = []
        self.index = 0  # position of the current song in self.songs

    def add(self, song: Song) -> None:
        """Append a song to the end of the playlist."""
        self.songs.append(song)

    def is_empty(self) -> bool:
        """True if no songs have been added yet."""
        return not self.songs

    def current(self) -> Song:
        """The current song. Raises IndexError if the playlist is empty."""
        return self.songs[self.index]

    def next(self) -> Song:
        """Move to the next song, wrapping to the first after the last, and return it.

        Raises ZeroDivisionError if the playlist is empty, so check is_empty() first.
        """
        self.index = (self.index + 1) % len(self.songs)
        return self.current()

    def previous(self) -> Song:
        """Move to the previous song, wrapping to the last before the first, and return it.

        Raises ZeroDivisionError if the playlist is empty, so check is_empty() first.
        """
        self.index = (self.index - 1) % len(self.songs)
        return self.current()