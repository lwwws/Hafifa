import tkinter as tk

import pygame

from configs.settings import WindowSettings
from ui.app import PlayerApp


def main():
    pygame.init()

    settings = WindowSettings()
    window = tk.Tk()
    window.geometry(settings.window_size)
    window.title(settings.window_title)

    app = PlayerApp(window, settings)
    app.song_end_polling_loop()
    window.mainloop()


if __name__ == "__main__":
    main()
