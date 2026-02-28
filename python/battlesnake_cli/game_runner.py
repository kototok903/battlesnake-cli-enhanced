"""Game execution using battlesnake binary."""

from __future__ import annotations

import re
import subprocess as sp
from pathlib import Path

from .config import DEFAULT_TEST_GAMES, GAME_TIMEOUT
from .models import GameResult, Snake, TestResults


class GameRunner:
    """Handles battlesnake binary interaction for running games."""

    def __init__(self, binary_path: Path):
        self.binary = binary_path

    def _build_base_cmd(self, snakes: list[Snake]) -> list[str]:
        """Build base command with snake names and URLs."""
        cmd = [str(self.binary), "play", "-W", "11", "-H", "11"]
        for snake in snakes:
            cmd += ["--name", snake.name, "--url", f"http://127.0.0.1:{snake.port}"]
        cmd += ["-g", "solo" if len(snakes) == 1 else "standard"]
        return cmd

    def play(self, snakes: list[Snake], browser: bool = True, seed: str | None = None) -> None:
        """Run a game with browser visualization."""
        cmd = self._build_base_cmd(snakes)
        cmd += ["-v", "-c"]
        if seed is not None:
            cmd += ["-r", seed]
        cmd += ["-t", str(GAME_TIMEOUT)]
        if browser:
            cmd += ["--browser"]
        sp.Popen(cmd)

    def play_headless(self, snakes: list[Snake]) -> GameResult:
        """Run single game without browser, return result."""
        cmd = self._build_base_cmd(snakes)
        cmd += ["-t", str(GAME_TIMEOUT)]

        result = sp.run(cmd, capture_output=True, text=True)

        # Parse: "Game completed after 123 turns. Snake1 was the winner."
        # Note: battlesnake CLI logs to stderr
        match = re.search(r"Game completed after (\d+) turns\. (.+) was the winner\.", result.stderr)
        if match:
            return GameResult(winner=match.group(2), turns=int(match.group(1)))

        # No winner (tie or error) - try to get turns at least
        turns_match = re.search(r"Game completed after (\d+) turns", result.stderr)
        turns = int(turns_match.group(1)) if turns_match else 0
        return GameResult(winner=None, turns=turns)

    def run_test(
        self,
        snakes: list[Snake],
        num_games: int = DEFAULT_TEST_GAMES,
        progress_callback: callable | None = None,
    ) -> TestResults:
        """Run multiple games and return aggregated results."""
        wins: dict[str, int] = {s.name: 0 for s in snakes}
        turns_list: list[int] = []
        ties = 0

        for game_num in range(1, num_games + 1):
            result = self.play_headless(snakes)
            turns_list.append(result.turns)

            if result.winner:
                wins[result.winner] = wins.get(result.winner, 0) + 1
            else:
                ties += 1

            if progress_callback:
                progress_callback(game_num, num_games, result, wins)

        return TestResults(wins=wins, ties=ties, total_games=num_games, turns_list=turns_list)
