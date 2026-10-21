from pathlib import Path
import pygame

class Player:
    """Plays one song at a time through pygame and reports when it ends."""

    SONG_END = pygame.USEREVENT + 1

    def __init__(self):
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.paused = False

    def play(self, path: Path) -> None:
        """Start playing a file. Raises pygame.error if the file can't be played."""
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.play(1, 0.0)
        self.paused = False

    def toggle_pause(self) -> None:
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused

    def song_finished(self) -> bool:
        """True if the current song ended since the last check."""
        return any(event.type == self.SONG_END for event in pygame.event.get())