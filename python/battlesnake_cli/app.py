"""Main CLI application using cmd.Cmd."""

from __future__ import annotations

import cmd
import readline

from .binary import setup_battlesnake
from .config import DEFAULT_TEST_GAMES, MAX_SNAKES
from .game_runner import GameRunner
from .models import GameResult
from .snake_manager import SnakeManager


class BattlesnakeCLI(cmd.Cmd):
    """Interactive CLI for managing Battlesnake servers and games."""

    prompt = "Command: "
    intro = "Welcome to snake runner\n    - use h for help\n    - Tab for autocomplete\n"

    def __init__(self):
        super().__init__()
        self.manager = SnakeManager()
        binary_path = setup_battlesnake()
        self.runner = GameRunner(binary_path)
        print()

    # Aliases
    def do_h(self, arg: str) -> None:
        """Alias for help."""
        self.do_help(arg)

    def do_s(self, arg: str) -> None:
        """Alias for start."""
        self.do_start(arg)

    def do_run(self, arg: str) -> None:
        """Alias for start."""
        self.do_start(arg)

    def do_S(self, arg: str) -> None:
        """Alias for stop."""
        self.do_stop(arg)

    def do_a(self, arg: str) -> None:
        """Alias for startall."""
        self.do_startall(arg)

    def do_A(self, arg: str) -> None:
        """Alias for stopall."""
        self.do_stopall(arg)

    def do_l(self, arg: str) -> None:
        """Alias for list."""
        self.do_list(arg)

    def do_g(self, arg: str) -> None:
        """Alias for game."""
        self.do_game(arg)

    def do_q(self, arg: str) -> None:
        """Alias for quickgame."""
        self.do_quickgame(arg)

    def do_t(self, arg: str) -> None:
        """Alias for test."""
        self.do_test(arg)

    def do_e(self, arg: str) -> bool:
        """Alias for exit."""
        return self.do_exit(arg)

    # Commands
    def do_start(self, arg: str) -> None:
        """Start snake: start [folder] [index]"""
        tokens = arg.split()
        if len(tokens) != 2:
            print("Error: incorrect amount of args\n")
            return

        snake_name = tokens[0]
        try:
            snake_ind = int(tokens[1]) - 1
        except ValueError:
            print(f"Error: incorrect index (use 1-{MAX_SNAKES})\n")
            return

        if snake_ind < 0 or snake_ind >= MAX_SNAKES:
            print(f"Error: incorrect index (use 1-{MAX_SNAKES})\n")
            return

        snake = self.manager.start(snake_name, snake_ind)
        if snake:
            print(f"Snake {snake_name} is active as Snake {snake_ind + 1}\n")
        else:
            print(f"Unable to start snake {snake_name}\n")

    def do_startall(self, arg: str) -> None:
        """Start multiple snakes: startall [folder, folder, ...]"""
        tokens = arg.split()
        if not tokens:
            print("No folder names provided\n")
            return

        snake_ind = 0
        seen: set[str] = set()
        for snake_name in tokens:
            if snake_ind >= MAX_SNAKES:
                print("Too many snakes provided")
                break
            if snake_name in seen:
                print("Notice: to start multiple instances of the same snake use start [snake folder] [index]")
                print(f"      (second instance of {snake_name} won't be started with startall)")
                continue
            seen.add(snake_name)

            snake = self.manager.start(snake_name, snake_ind)
            if snake:
                print(f"Snake {snake_name} is active at index {snake_ind + 1}")
                snake_ind += 1
            else:
                print(f"Unable to start snake {snake_name}")
        print()

    def do_stop(self, arg: str) -> None:
        """Stop snake: stop [index]"""
        tokens = arg.split()
        if len(tokens) != 1:
            print("Error: incorrect amount of args\n")
            return

        try:
            snake_ind = int(tokens[0]) - 1
        except ValueError:
            print(f"Error: incorrect index (use 1-{MAX_SNAKES})\n")
            return

        if snake_ind < 0 or snake_ind >= MAX_SNAKES:
            print(f"Error: incorrect index (use 1-{MAX_SNAKES})\n")
            return

        snake = self.manager.get(snake_ind)
        name = snake.name if snake else "?"
        if self.manager.stop(snake_ind):
            print(f"Snake {snake_ind + 1} : {name} stopped\n")
        else:
            print(f"Unable to stop snake {snake_ind + 1} : {name}\n")

    def do_stopall(self, arg: str) -> None:
        """Stop all active snakes."""
        results = self.manager.stop_all()
        if not results:
            print("No snakes running\n")
            return
        for i, name, success in results:
            if success:
                print(f"Stopped snake {i + 1} : {name}")
            else:
                print(f"Unable to stop snake {i + 1} : {name}")
        print()

    def do_list(self, arg: str) -> None:
        """List active snakes."""
        print("Snakes currently running:")
        for i, snake in self.manager.list_active():
            print(f"    - {i + 1} : {snake.name} ({snake.proc})")
        print()

    def do_game(self, arg: str) -> None:
        """Run game: game [count] or game [count] [indices...]"""
        tokens = arg.split()
        if not tokens:
            print("Error: number of snakes not provided\n")
            return

        try:
            amount = int(tokens[0])
        except ValueError:
            print("Error: incorrect number of snakes (expected 1-4)\n")
            return

        if amount < 1 or amount > 4:
            print("Error: incorrect number of snakes (expected 1-4)\n")
            return

        # Parse indices
        snake_inds: list[int] = []
        if len(tokens) == 1:
            snake_inds = list(range(amount))
        elif len(tokens) == amount + 1:
            for i in range(1, amount + 1):
                try:
                    idx = int(tokens[i]) - 1
                except ValueError:
                    print(f"Error: incorrect snake index: {tokens[i]} (expected 1-{MAX_SNAKES})\n")
                    return
                if idx < 0 or idx >= MAX_SNAKES:
                    print(f"Error: incorrect snake index: {tokens[i]} (expected 1-{MAX_SNAKES})\n")
                    return
                if not self.manager.is_active(idx):
                    print(f"Error: snake {idx + 1} is not active\n")
                    return
                snake_inds.append(idx)
        else:
            print(f"Error: incorrect number of args (expected {amount} indices)\n")
            return

        # Verify all snakes active
        snakes = []
        for idx in snake_inds:
            snake = self.manager.get(idx)
            if not snake:
                print(f"Error: snake {idx + 1} is not active\n")
                return
            snakes.append(snake)

        self.runner.play(snakes)
        print(f"Running game with {amount} snakes:")
        for idx, snake in zip(snake_inds, snakes):
            print(f"    - {idx + 1} : {snake.name} ({snake.proc})")

    def do_quickgame(self, arg: str) -> None:
        """Start snakes and run game: quickgame [folder, folder, ...]"""
        tokens = arg.split()
        if not tokens:
            print("No folder names provided\n")
            return

        if len(tokens) > 4:
            print("Error: maximum 4 snakes per game\n")
            return

        # Start all snakes
        snake_inds: list[int] = []
        snake_ind = 0
        seen: set[str] = set()

        for snake_name in tokens:
            if snake_name in seen:
                print(f"Notice: duplicate {snake_name} skipped")
                continue
            seen.add(snake_name)

            snake = self.manager.start(snake_name, snake_ind)
            if snake:
                print(f"Snake {snake_name} is active at index {snake_ind + 1}")
                snake_inds.append(snake_ind)
                snake_ind += 1
            else:
                print(f"Unable to start snake {snake_name}")

        if not snake_inds:
            print("No snakes started\n")
            return

        # Run game with started snakes
        snakes = [self.manager.get(idx) for idx in snake_inds]
        snakes = [s for s in snakes if s is not None]

        if snakes:
            self.runner.play(snakes)
            print(f"\nRunning game with {len(snakes)} snakes:")
            for idx, snake in zip(snake_inds, snakes):
                print(f"    - {idx + 1} : {snake.name}")

    def do_test(self, arg: str) -> None:
        """Run test games: test [count] [indices...] [num_games?]"""
        tokens = arg.split()
        if len(tokens) < 1:
            print("Error: number of snakes not provided\n")
            return

        try:
            amount = int(tokens[0])
        except ValueError:
            print("Error: incorrect number of snakes (expected 1-4)\n")
            return

        if amount < 1 or amount > 4:
            print("Error: incorrect number of snakes (expected 1-4)\n")
            return

        snake_inds: list[int] = []
        num_games = DEFAULT_TEST_GAMES

        if len(tokens) == 1:
            snake_inds = list(range(amount))
        elif len(tokens) == 1 + amount:
            for i in range(1, 1 + amount):
                try:
                    idx = int(tokens[i]) - 1
                except ValueError:
                    print(f"Error: invalid index {tokens[i]}\n")
                    return
                if idx < 0 or idx >= MAX_SNAKES or not self.manager.is_active(idx):
                    print(f"Error: snake {tokens[i]} not active\n")
                    return
                snake_inds.append(idx)
        elif len(tokens) == 2 + amount:
            for i in range(1, 1 + amount):
                try:
                    idx = int(tokens[i]) - 1
                except ValueError:
                    print(f"Error: invalid index {tokens[i]}\n")
                    return
                if idx < 0 or idx >= MAX_SNAKES or not self.manager.is_active(idx):
                    print(f"Error: snake {tokens[i]} not active\n")
                    return
                snake_inds.append(idx)
            try:
                num_games = int(tokens[1 + amount])
            except ValueError:
                print("Error: invalid number of games\n")
                return
        else:
            print(f"Error: expected {amount} indices (and optional game count)\n")
            return

        # Gather snakes
        snakes = []
        for idx in snake_inds:
            snake = self.manager.get(idx)
            if not snake:
                print(f"Error: snake {idx + 1} not active\n")
                return
            snakes.append(snake)

        print(f"Running {num_games} games...\n")

        def progress(game_num: int, total: int, result: GameResult, wins: dict[str, int]) -> None:
            winner_str = f"{result.winner} wins" if result.winner else "Tie"
            summary = ", ".join(f"{name}: {count}" for name, count in wins.items())
            game_num_width = len(str(total))
            left = f"Game {game_num:>{game_num_width}}/{total}: {winner_str} ({result.turns} turns)"
            print(f"{left:<45} | {summary}")

        results = self.runner.run_test(snakes, num_games, progress_callback=progress)

        # Final summary
        print(f"\n=== Results ({num_games} games) ===")
        for name, count in results.wins.items():
            pct = (count / num_games) * 100
            left = f"  {name}:"
            print(f"{left:<15} {count} wins ({pct:.1f}%)")
        if results.ties > 0:
            pct = (results.ties / num_games) * 100
            left = "  Ties:"
            print(f"{left:<15} {results.ties}      ({pct:.1f}%)")
        print(f"  Avg turns: {results.avg_turns:.1f}\n")

    def do_exit(self, arg: str) -> bool:
        """Stop all snakes and exit."""
        self._cleanup()
        return True

    def do_EOF(self, arg: str) -> bool:
        """Handle Ctrl+D."""
        print()
        self._cleanup()
        return True

    def _cleanup(self) -> None:
        """Stop all snakes before exit."""
        for i, name, success in self.manager.stop_all():
            if success:
                print(f"Stopped snake {i + 1} : {name}")
            else:
                print(f"Unable to stop snake {i + 1} : {name}")

    # Completers
    def complete_start(self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        tokens = line.split()
        if len(tokens) <= 2 and not line.endswith(" "):
            folders = self.manager.get_snake_folders()
            return [f for f in folders if f.startswith(text)]
        return []

    complete_s = complete_start
    complete_run = complete_start

    def complete_startall(self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        folders = self.manager.get_snake_folders()
        return [f for f in folders if f.startswith(text)]

    complete_a = complete_startall

    def complete_quickgame(self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        folders = self.manager.get_snake_folders()
        return [f for f in folders if f.startswith(text)]

    complete_q = complete_quickgame

    def default(self, line: str) -> None:
        """Handle unknown commands."""
        print("Command is not recognized\n")

    def emptyline(self) -> None:
        """Do nothing on empty line."""
        pass

    # Custom help
    def do_help(self, arg: str) -> None:
        """Print help message."""
        if arg:
            super().do_help(arg)
            return

        print("Available commands:")
        print("h | help\n    - print help")
        print(
            f"s | start | run [folder name] [index]\n"
            f"    - starts the snake from the given folder in the snakes/ directory as Snake <index>\n"
            f"      (available indices: 1-{MAX_SNAKES})\n"
            f"      (e.g. start BobSnake 1 - starts the snake in the snakes/BobSnake/ folder as Snake 1)"
        )
        print(
            f"a | startall [folder name, folder name, ...]\n"
            f"    - start given snakes at indices starting with 1\n"
            f"      (at most {MAX_SNAKES})"
        )
        print("S | stop [index]\n    - stop snake at given index")
        print("A | stopall\n    - stop all snakes that are currently active")
        print("l | list\n    - list all snakes that are currently active")
        print("g | game [number of snakes]\n    - start game with snakes at indices 1 to number of snakes")
        print("g | game [number of snakes] [index, index, ...]\n    - start game with snakes at given indices")
        print(
            "q | quickgame [folder name, folder name, ...]\n"
            "    - combination of startall and game\n"
            "      (starts given snakes at indices starting from 1 and runs a game with them)"
        )
        print(
            "t | test [number of snakes] [index, index, ...] [num games?]\n"
            "    - run multiple games (default 100) and show win statistics\n"
            "      (e.g. test 2 1 2 - runs 100 games with snakes 1 and 2)\n"
            "      (e.g. test 2 1 2 50 - runs 50 games)"
        )
        print("e | exit\n    - stop all snakes and exit the program")


def main() -> None:
    """Entry point for the CLI."""
    # Setup readline for better macOS compatibility
    if readline.__doc__ and "libedit" in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    cli = BattlesnakeCLI()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n")
        cli._cleanup()
