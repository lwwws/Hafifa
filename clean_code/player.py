"""Audio playback through pygame's music mixer."""

from pathlib import Path
import pygame

class Player:
    """Plays one song at a time through pygame and reports when it ends.

    pygame must be initialized (pygame.init()) before creating a Player.
    """

    # Custom pygame event type that the mixer posts when a song finishes.
    SONG_END = pygame.USEREVENT + 1

    def __init__(self):
        # A setting, not an action: pygame posts SONG_END after every song from now on.
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.paused = False

    def play(self, path: Path) -> None:
        """Start playing a file. Raises pygame.error if the file can't be played."""
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.play(1, 0.0)
        self.paused = False

    def toggle_pause(self) -> None:
        """Pause if playing, resume if paused."""
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused

    def song_finished(self) -> bool:
        """True if the current song ended since the last check.

        This empties pygame's event queue, so call it from one place only.
        """
        return any(event.type == self.SONG_END for event in pygame.event.get())