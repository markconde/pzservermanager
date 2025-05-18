import json
from pathlib import Path

COMMANDS_PATH = Path(__file__).parent / "commands.json"

with open(COMMANDS_PATH, encoding="utf-8") as f:
    commands = json.load(f)
