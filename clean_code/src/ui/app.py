import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import pygame
from mutagen import MutagenError

from audio.player import Player
from configs.settings import WindowSettings
from models.playlist import Playlist
from models.song import Song


class PlayerApp(tk.Frame):
    def __init__(self, window: tk.Tk, settings: WindowSettings):
        super().__init__(window)
        self.settings = settings
        self.playlist = Playlist()
        self.player = Player()

        self.grid()
        self._create_buttons()
        self.status_label = self._create_status_label()
        self.playlist_box = self._create_playlist_box()

    def _create_buttons(self) -> None:
        buttons = [
            ("ADD TO LIST", self.add_songs),
            ("PLAY SONG", self.play_current),
            ("PAUSE/UNPAUSE", self.toggle_pause),
            ("PREVIOUS SONG", self.previous_song),
            ("NEXT SONG", self.next_song),
        ]

        for row, (text, command) in enumerate(buttons, start=1):
            button = tk.Button(self, text=text, command=command,
                               bg=self.settings.button_bg, width=self.settings.button_width)
            button.grid(row=row, column=0)

    def _create_status_label(self) -> tk.Label:
        status_label = tk.Label(self, fg=self.settings.label_fg,
                                bg=self.settings.label_bg, font=self.settings.label_font)
        status_label.grid(row=6, column=0)

        return status_label

    def _create_playlist_box(self) -> tk.Text:
        playlist_box = tk.Text(self, wrap=tk.WORD, width=self.settings.playlist_width)
        playlist_box.grid(row=8, column=0)

        return playlist_box

    def add_songs(self) -> None:
        skipped = []

        for path in filedialog.askopenfilenames():
            try:
                self.playlist.add(Song.from_file(path))
            except (MutagenError, OSError):
                skipped.append(Path(path).name)

        self.refresh_playlist_box()

        if skipped:
            self.status_label["text"] = f"Couldn't read: {', '.join(skipped)}"

    def refresh_playlist_box(self) -> None:
        self.playlist_box.delete("1.0", tk.END)

        for number, song in enumerate(self.playlist.songs, start=1):
            self.playlist_box.insert(tk.END, f"{number} : {song.title} - {song.artist}\n")

    def current_song_description(self) -> str:
        song = self.playlist.current()

        return f"Now playing: Nr:{self.playlist.index + 1} {song.title} - {song.artist}"

    def play_current(self) -> None:
        if self.playlist.is_empty():
            return

        song = self.playlist.current()

        try:
            self.player.play(song.path)
        except pygame.error:
            self.status_label["text"] = f"Can't play: {song.path.name}"
            return

        self.status_label["text"] = self.current_song_description()

    def check_music(self) -> None:
        if self.player.song_finished():
            self.next_song()

    def toggle_pause(self) -> None:
        self.player.toggle_pause()

    def next_song(self) -> None:
        if self.playlist.is_empty():
            return

        self.playlist.next()
        self.play_current()

    def previous_song(self) -> None:
        if self.playlist.is_empty():
            return

        self.playlist.previous()
        self.play_current()

    def song_end_polling_loop(self) -> None:
        self.check_music()
        # after() fires only once, so schedule the next check every time.
        self.after(100, self.song_end_polling_loop)
