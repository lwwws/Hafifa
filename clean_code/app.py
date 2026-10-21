"""Tkinter user interface for the MP3 player, and the program's entry point."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import pygame
from mutagen import MutagenError

from playlist import Playlist
from song import Song
from player import Player

class PlayerApp(tk.Frame):
    """Main window: control buttons, a now-playing label and the playlist view.

    Holds no player logic of its own. Button handlers ask the Playlist which
    song to play and tell the Player to play it.
    """

    def __init__(self, master):
        """Build the widgets inside `master`, the root Tk window."""
        super(PlayerApp, self).__init__(master)

        self.grid()
        self.playlist = Playlist()
        self.player = Player()

        b1 = tk.Button(self, text="ADD TO LIST",command=self.add_songs,bg='AntiqueWhite1',width=40)
        b1.grid(row=1,column=0)
        b2 = tk.Button(self, text="PLAY SONG",command=self.play_current,bg='AntiqueWhite1',width=40)
        b2.grid(row=2,column=0)
        b3 = tk.Button(self, text="PAUSE/UNPAUSE",command=self.toggle_pause,bg='AntiqueWhite1',width=40)
        b3.grid(row=3,column=0)
        b4 = tk.Button(self, text="PREVIOUS SONG",command=self.previous_song,bg='AntiqueWhite1',width=40)
        b4.grid(row=4,column=0)
        b5 = tk.Button(self, text="NEXT SONG",command=self.next_song,bg='AntiqueWhite1',width=40)
        b5.grid(row=5,column=0)

        self.status_label = tk.Label(self, fg='Black',font=('Helvetica 12 bold italic',10),bg='ivory2')
        self.status_label.grid(row=6,column=0)

        self.playlist_box = tk.Text(self,wrap=tk.WORD,width=60)
        self.playlist_box.grid(row=8,column=0)

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
    window = tk.Tk()
    window.geometry("500x500")
    window.title("MP3 Music Player")
    app = PlayerApp(window)
    app.poll_music()      # start the repeating check
    window.mainloop()     # hand control to tkinter

if __name__ == "__main__":
    main()