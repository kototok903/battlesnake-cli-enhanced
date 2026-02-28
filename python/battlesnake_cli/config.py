"""Configuration constants and paths."""

from pathlib import Path

BASE_DIR = Path.cwd()
SNAKES_DIR = BASE_DIR / "snakes"
BIN_DIR = BASE_DIR / ".bin"

MAX_SNAKES = 8
BASE_PORT = 8000
GAME_TIMEOUT = 500
DEFAULT_TEST_GAMES = 100
