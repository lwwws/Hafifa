from pydantic_settings import BaseSettings, SettingsConfigDict


class WindowSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PLAYER_", frozen=True)

    window_title: str = "MP3 Music Player"
    window_size: str = "500x500"
    button_bg: str = "AntiqueWhite1"
    button_width: int = 40
    label_fg: str = "Black"
    label_bg: str = "ivory2"
    label_font: tuple[str, int] = ("Helvetica 12 bold italic", 10)
    playlist_width: int = 60
