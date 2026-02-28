"""Snake process lifecycle management."""

from __future__ import annotations

import os
import signal
import subprocess as sp
import sys
from pathlib import Path

from .config import BASE_PORT, MAX_SNAKES, SNAKES_DIR
from .models import Snake


class SnakeManager:
    """Manages snake server processes."""

    def __init__(self, max_snakes: int = MAX_SNAKES, base_port: int = BASE_PORT):
        self.max_snakes = max_snakes
        self.base_port = base_port
        self._snakes: dict[int, Snake | None] = {i: None for i in range(max_snakes)}

    def get_snake_folders(self) -> list[str]:
        """Returns list of valid snake folder names."""
        if not SNAKES_DIR.is_dir():
            return []
        return [name for name in os.listdir(SNAKES_DIR) if (SNAKES_DIR / name).is_dir()]

    def _detect_snake_type(self, folder: Path) -> str | None:
        """Returns 'go', 'python', or None."""
        if (folder / "main.go").is_file():
            return "go"
        if (folder / "main.py").is_file():
            return "python"
        return None

    def start(self, name: str, index: int) -> Snake | None:
        """Start a snake at given index. Returns Snake or None on failure."""
        if index < 0 or index >= self.max_snakes:
            print(f"Error: invalid index (use 1-{self.max_snakes})")
            return None

        folder = SNAKES_DIR / name
        if not folder.is_dir():
            print(f"Error: folder {name} not found")
            return None

        snake_type = self._detect_snake_type(folder)
        if not snake_type:
            print(f"Error: no main.go or main.py found in {name}")
            return None

        # Stop existing snake at this index
        if self._snakes[index] is not None:
            old_name = self._snakes[index].name
            self.stop(index)
            print(f"Stopped previous Snake {index + 1} : {old_name}")

        env = os.environ.copy()
        port = self.base_port + index
        env["PORT"] = str(port)

        if snake_type == "go":
            cmd = ["go", "run", "."]
        else:
            cmd = [sys.executable, "main.py"]

        proc = sp.Popen(
            cmd, cwd=folder, env=env, stdout=sp.DEVNULL, stderr=sp.DEVNULL, start_new_session=True
        )

        snake = Snake(name=name, proc=proc, port=port)
        self._snakes[index] = snake
        return snake

    def stop(self, index: int) -> bool:
        """Stop snake at given index. Returns True if stopped."""
        if index < 0 or index >= self.max_snakes:
            return False

        snake = self._snakes[index]
        if snake is None:
            return False

        # Kill entire process group (needed for `go run` which spawns child processes)
        try:
            os.killpg(snake.proc.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            snake.proc.kill()

        self._snakes[index] = None
        return True

    def stop_all(self) -> list[tuple[int, str, bool]]:
        """Stop all active snakes. Returns list of (index, name, success)."""
        results = []
        for i in range(self.max_snakes):
            snake = self._snakes[i]
            if snake is not None:
                name = snake.name
                success = self.stop(i)
                results.append((i, name, success))
        return results

    def get(self, index: int) -> Snake | None:
        """Get snake at index, or None if not active."""
        if index < 0 or index >= self.max_snakes:
            return None
        return self._snakes[index]

    def list_active(self) -> list[tuple[int, Snake]]:
        """List all active snakes as (index, snake) tuples."""
        return [(i, s) for i, s in self._snakes.items() if s is not None]

    def is_active(self, index: int) -> bool:
        """Check if snake at index is active."""
        return self.get(index) is not None
