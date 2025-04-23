import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    RCON_HOST = os.environ.get('RCON_HOST', 'localhost')
    RCON_PORT = int(os.environ.get('RCON_PORT'))
    RCON_PASSWORD = os.environ.get('RCON_PASSWORD', 'changeme')