from pathlib import Path

import pygame


class Player:
    SONG_END = pygame.USEREVENT + 1

    def __init__(self):
        if not pygame.get_init() or not pygame.mixer.get_init():
            raise RuntimeError("pygame must be initialized with pygame.init() before creating a Player")

        pygame.mixer.music.set_endevent(self.SONG_END)
        self.paused = False

    def play(self, path: Path) -> None:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.play()
        self.paused = False

    def toggle_pause(self) -> None:
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

        self.paused = not self.paused

    def song_finished(self) -> bool:
        # Reading events also clears pygame's queue, so only call this from one place.
        return any(event.type == self.SONG_END for event in pygame.event.get())
