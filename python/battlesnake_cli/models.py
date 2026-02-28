"""Data models for snake and game state."""

from dataclasses import dataclass
from subprocess import Popen


@dataclass
class Snake:
    """A running snake server process."""

    name: str
    proc: Popen
    port: int


@dataclass
class GameResult:
    """Result of a single game."""

    winner: str | None
    turns: int


@dataclass
class TestResults:
    """Aggregated results from multiple test games."""

    wins: dict[str, int]
    ties: int
    total_games: int
    turns_list: list[int]

    @property
    def avg_turns(self) -> float:
        return sum(self.turns_list) / len(self.turns_list) if self.turns_list else 0.0
