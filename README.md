# Battlesnake CLI Enhanced

A modification built on top of official [Battlesnake CLI](https://github.com/BattlesnakeOfficial/rules?tab=readme-ov-file). Designed to conveniently run multiple snakes on a local computer for testing and tournaments.

## Supported Languages

- **Python** - snakes with `main.py`
- **Go** - snakes with `main.go`

## Dependencies

- Python 3.10+
- Flask python package (for Python snakes)
- Go (for Go snakes)

## Installation

1. Clone the repository

   ```
   git clone https://github.com/kototok903/battlesnake-cli-enhanced.git
   ```

2. Make sure you have Flask python package installed if you are using Battlesnake Python starter project (it uses Flask in `server.py`).

   ```
   pip install Flask
   ```

3. If you want to run Go snakes, make sure Go is installed ([golang.org/dl](https://golang.org/dl/)).

4. Download your snakes and put them into `snakes` folder. Download the whole ReplIt/GitHub projects, no need to adjust anything. Snake type is auto-detected by checking for `main.go` (Go) or `main.py` (Python).
   _After this step you should have folders with your snakes in `snakes/` (e.g. `snakes/SnakeName1`, `snakes/SnakeName2`)_

_Note: The official Battlesnake CLI binary will be auto-downloaded from [releases](https://github.com/BattlesnakeOfficial/rules/releases) on first run if not already installed._

## Usage

Run the enhanced CLI from the project root:

```
python -m python.battlesnake_cli
```

The tool allows you to run the snakes in `snakes` folder at some indices and run local games with snakes you started.

Use `start [SnakeFolder] [index]` to run the snake located in `snakes/SnakeFolder` at the given index. (One snake can be started at multiple indices.)

Use `game [AmountOfSnakes] [index, index, ...]` to run a local game where `AmountOfSnakes` is the amount of snakes in the game and indices are the indices of currently running snakes you want to be in the game (provide exactly `AmountOfSnakes` indices).
Alternatively, use `game [AmountOfSnakes]` to avoid providing indices and just run a game with snakes at indices from 1 to `AmountOfSnakes`.

Use `help` to see the full command list.

### Usage Example

Let's assume we have snakes `AlienSnake` and `BirdSnake` in the folder `snakes`.

Start the CLI:
```
python -m python.battlesnake_cli
```

First, we use `start AlienSnake 1` to start the AlienSnake as Snake 1.
Then, use `start BirdSnake 2` to start the BirdSnake as Snake 2.
Finally, we can use `game 2 1 2` to start a game with 2 snakes: Snake 1 and Snake 2 (which currently are AlienSnake and BirdSnake). The browser tab with the game, as well as a terminal, will open. _Note: reloading the browser tab will stop the website's access to the game and you won't be able to continue watching it in browser._

Now, let's assume we made some changes to AlienSnake's code.
Just use `start AlienSnake 1` to restart AlienSnake at index 1. Alternatively, we can use `start AlienSnake 3` to start the new code at index 3 and then use `game 2 1 3` to test our new AlienSnake against its old version.

Also, if you decide to test which of your snakes is stronger on average, use the `test` command to run big number of games and see results. For example, using `test 2 1 2 100` would simulate 100 games of AlienSnake against BirdSnake, and display the stats afterwards.

When we are done with coding for today, use `exit` to stop the CLI and all running snakes.
_Note: when you start the CLI again, no snakes will be running and you'll need to start them again._
