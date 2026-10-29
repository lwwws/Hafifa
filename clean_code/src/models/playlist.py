from models.song import Song


class Playlist:
    def __init__(self):
        self.songs: list[Song] = []
        self.index = 0

    def add(self, song: Song) -> None:
        self.songs.append(song)

    def is_empty(self) -> bool:
        return not self.songs

    def current(self) -> Song:
        return self.songs[self.index]

    def next(self) -> Song:
        self.index = (self.index + 1) % len(self.songs)

        return self.current()

    def previous(self) -> Song:
        self.index = (self.index - 1) % len(self.songs)

        return self.current()
