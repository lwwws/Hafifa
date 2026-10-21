"""Tkinter user interface for the MP3 player, and the program's entry point."""

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog

import pygame
from mutagen import MutagenError

from playlist import Playlist
from song import Song
from player import Player

@dataclass(frozen=True)
class Settings:
    """Look and layout of the window."""

    window_title: str = "MP3 Music Player"
    window_size: str = "500x500"
    button_bg: str = "AntiqueWhite1"
    button_width: int = 40
    label_fg: str = "Black"
    label_bg: str = "ivory2"
    label_font: tuple[str, int] = ("Helvetica 12 bold italic", 10)
    playlist_width: int = 60


class PlayerApp(tk.Frame):
    """Main window: control buttons, a now-playing label and the playlist view.

    Holds no player logic of its own. Button handlers ask the Playlist which
    song to play and tell the Player to play it.
    """

    def __init__(self, master, settings: Settings):
        """Build the widgets inside `master`, the root Tk window."""
        super().__init__(master)
        self.settings = settings

        self.grid()
        self.playlist = Playlist()
        self.player = Player()

        # (label, handler) for each control button, top to bottom, one per row.
        buttons = [
            ("ADD TO LIST", self.add_songs),
            ("PLAY SONG", self.play_current),
            ("PAUSE/UNPAUSE", self.toggle_pause),
            ("PREVIOUS SONG", self.previous_song),
            ("NEXT SONG", self.next_song),
        ]
        for row, (text, command) in enumerate(buttons, start=1):
            tk.Button(self, text=text, command=command,
                      bg=settings.button_bg, width=settings.button_width).grid(row=row, column=0)

        self.status_label = tk.Label(self, fg=settings.label_fg,
                             bg=settings.label_bg, font=settings.label_font)
        self.status_label.grid(row=6, column=0)

        self.playlist_box = tk.Text(self, wrap=tk.WORD, width=settings.playlist_width)
        self.playlist_box.grid(row=8, column=0)

    def add_songs(self):
        """Ask the user for music files and add them to the playlist.

        Files whose tags can't be read are skipped and named in the status label.
        """
        skipped = []
        for path in filedialog.askopenfilenames():
            try:
                self.playlist.add(Song.from_file(path))
            except (MutagenError, OSError):
                skipped.append(Path(path).name)

        self.refresh_playlist_box()
        if skipped:
            self.status_label["text"] = "Couldn't read: " + ", ".join(skipped)

    def refresh_playlist_box(self):
        """Redraw the playlist view so it shows every song, numbered from 1."""
        self.playlist_box.delete("1.0", tk.END)
        for number, song in enumerate(self.playlist.songs, start=1):
            self.playlist_box.insert(tk.END, f"{number} : {song.title} - {song.artist}\n")

    def current_song_description(self):
        """Status label text for the current song, e.g. 'Now playing: Nr:2 Title - Artist'."""
        song = self.playlist.current()
        return f"Now playing: Nr:{self.playlist.index + 1} {song.title} - {song.artist}"

    def play_current(self):
        """Play the current song and show it in the status label.

        Does nothing if the playlist is empty. If pygame can't play the file,
        shows a message instead.
        """
        if self.playlist.is_empty():
            return
        song = self.playlist.current()
        try:
            self.player.play(song.path)
        except pygame.error:
            self.status_label["text"] = f"Can't play: {song.path.name}"
            return
        self.status_label["text"] = self.current_song_description()

    def check_music(self):
        """Move on to the next song if the current one has finished."""
        if self.player.song_finished():
            self.next_song()

    def toggle_pause(self):
        """Pause playback, or resume it if it's paused."""
        self.player.toggle_pause()

    def next_song(self):
        """Play the next song, wrapping around to the first after the last."""
        if self.playlist.is_empty():
            return
        self.playlist.next()
        self.play_current()

    def previous_song(self):
        """Play the previous song, wrapping around to the last before the first."""
        if self.playlist.is_empty():
            return
        self.playlist.previous()
        self.play_current()

    def poll_music(self):
        """Check for the end of the song, then schedule the next check."""
        self.check_music()
        # after() is a one-shot timer, so reschedule on every run to keep polling.
        self.after(100, self.poll_music)

def main():
    """Start pygame, build the window and run the tkinter event loop."""
    pygame.init()

    settings = Settings()
    window = tk.Tk()
    window.geometry(settings.window_size)
    window.title(settings.window_title)

    app = PlayerApp(window, settings)
    app.poll_music()      # start the repeating check
    window.mainloop()     # hand control to tkinter

if __name__ == "__main__":
    main()