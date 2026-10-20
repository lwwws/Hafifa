from mutagen.easyid3 import EasyID3
import pygame

import tkinter as tk
from tkinter import filedialog

from playlist import Playlist

SONG_END = pygame.USEREVENT + 1



class PlayerApp(tk.Frame):
    def __init__(self, master):
        super(PlayerApp, self).__init__(master)

        self.grid()
        self.playlist = Playlist()
        self.paused = False

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
        try:
            directory = filedialog.askopenfilenames()
            for song_dir in directory:
                print(song_dir)
                self.playlist.add(song_dir)
            self.playlist_box.delete(0.0, tk.END)

            for key, item in enumerate(self.playlist.paths):
                song = EasyID3(item)
                song_data = (str(key + 1) + ' : ' + song['title'][0] + ' - '
                            + song['artist'][0])
                self.playlist_box.insert(tk.END, song_data + '\n')
        except:
            pass

    def current_song_description(self):
        try:
            song = EasyID3(self.playlist.current())
            song_data = "Now playing: Nr:" + str(self.playlist.index + 1) + " " + \
                        str(song['title']) + " - " + str(song['artist'])
            return song_data
        except:
            pass

    def play_current(self):
        try:
            path = self.playlist.current()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(1, 0.0)
            pygame.mixer.music.set_endevent(SONG_END)
            self.paused = False
            self.status_label['text'] = self.current_song_description()
        except:
            pass

    def check_music(self):
        try:
            for event in pygame.event.get():
                if event.type == SONG_END:
                    self.next_song()
        except:
            pass

    def toggle_pause(self):
        try:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
            elif not self.paused:
                pygame.mixer.music.pause()
                self.paused = True
        except:
            pass

    def next_song(self):
        if self.playlist.is_empty():
            return
        self.playlist.next()
        self.play_current()

    def previous_song(self):
        if self.playlist.is_empty():
            return
        self.playlist.previous()
        self.play_current()


def main():
    pygame.init()
    window = tk.Tk()
    window.geometry("500x500")
    window.title("MP3 Music Player")
    app = PlayerApp(window)
    while True:
        # runs mainloop of program
        app.check_music()
        app.update()

if __name__ == "__main__":
    main()