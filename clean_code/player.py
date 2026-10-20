from mutagen.easyid3 import EasyID3
import pygame

import tkinter as tk
from tkinter import filedialog

pygame.init()

global playlist
global paused
global current_index
global SONG_END
global playlist_box
global status_label

class PlayerApp(tk.Frame):
    def __init__(self,master):
        super(PlayerApp, self).__init__(master)
        global playlist_box, status_label, playlist, paused, current_index, SONG_END
        self.grid()
        b1 = tk.Button(self, text="ADD TO LIST",command=add_songs,bg='AntiqueWhite1',width=40)
        b1.grid(row=1,column=0)
        b2 = tk.Button(self, text="PLAY SONG",command=play_current,bg='AntiqueWhite1',width=40)
        b2.grid(row=2,column=0)
        b3 = tk.Button(self, text="PAUSE/UNPAUSE",command=toggle_pause,bg='AntiqueWhite1',width=40)
        b3.grid(row=3,column=0)
        b4 = tk.Button(self, text="PREVIOUS SONG",command=previous_song,bg='AntiqueWhite1',width=40)
        b4.grid(row=4,column=0)
        b5 = tk.Button(self, text="NEXT SONG",command=next_song,bg='AntiqueWhite1',width=40)
        b5.grid(row=5,column=0)

        status_label = tk.Label(self, fg='Black',font=('Helvetica 12 bold italic',10),bg='ivory2')
        status_label.grid(row=6,column=0)

        playlist_box = tk.Text(self,wrap=tk.WORD,width=60)
        playlist_box.grid(row=8,column=0)

        playlist = list()
        paused = False
        current_index = 0
        SONG_END = pygame.USEREVENT + 1
#################################################################################
def add_songs():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        directory = filedialog.askopenfilenames()
        for song_dir in directory:
            print(song_dir)
            playlist.append(song_dir)
        playlist_box.delete(0.0, tk.END)

        for key, item in enumerate(playlist):
            song = EasyID3(item)
            song_data = (str(key + 1) + ' : ' + song['title'][0] + ' - '
                         + song['artist'][0])
            playlist_box.insert(tk.END, song_data + '\n')
    except:
        pass
#################################################################################
def current_song_description():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        song = EasyID3(playlist[current_index])
        song_data = "Now playing: Nr:" + str(current_index + 1) + " " + \
                    str(song['title']) + " - " + str(song['artist'])
        return song_data
    except:
        pass
#################################################################################
def play_current():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        directory = playlist[current_index]
        pygame.mixer.music.load(directory)
        pygame.mixer.music.play(1, 0.0)
        pygame.mixer.music.set_endevent(SONG_END)
        paused = False
        status_label['text'] = current_song_description()
    except:
        pass
#################################################################################
def check_music():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        for event in pygame.event.get():
            if event.type == SONG_END:
                next_song()
    except:
        pass
#################################################################################
def toggle_pause():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        if paused:
            pygame.mixer.music.unpause()
            paused = False
        elif not paused:
            pygame.mixer.music.pause()
            paused = True
    except:
        pass
#################################################################################
def next_index():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        if current_index + 2 <= len(playlist):
            return current_index + 1
        else:
            return 0
    except:
        pass
#################################################################################
def next_song():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        current_index = next_index()
        play_current()
    except:
        pass
#################################################################################
def previous_index():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        if current_index - 1 >= 0:
            return current_index - 1
        else:
            return len(playlist) - 1
    except:
        pass
#################################################################################
def previous_song():
    global current_index, playlist, SONG_END, paused, status_label, playlist_box
    try:
        current_index = previous_index()
        play_current()
    except:
        pass


def main():
    window = tk.Tk()
    window.geometry("500x500")
    window.title("MP3 Music Player")
    app = PlayerApp(window)
    while True:
        # runs mainloop of program
        check_music()
        app.update()

if __name__ == "__main__":
    main()