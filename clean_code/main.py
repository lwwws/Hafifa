import tkinter as tk

import pygame

from app import PlayerApp
from settings import WindowSettings


def main():
    pygame.init()

    settings = WindowSettings()
    window = tk.Tk()
    window.geometry(settings.window_size)
    window.title(settings.window_title)

    app = PlayerApp(window, settings)
    app.poll_music()
    window.mainloop()


if __name__ == "__main__":
    main()
