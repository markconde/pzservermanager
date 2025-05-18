import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
    RCON_HOST = os.environ.get("RCON_HOST", "localhost")
    RCON_PORT = int(os.environ.get("RCON_PORT", 12345))
    RCON_PASSWORD = os.environ.get("RCON_PASSWORD", "changeme")
    SERVER_OPTIONS_FILE = os.path.join(
        os.environ.get("GAME_SERVER_CONFIG_FOLDER_PATH", "./config"),
        os.environ.get("GAME_SERVER_OPTIONS_FILENAME", "ServerOptions.ini"),
    )
