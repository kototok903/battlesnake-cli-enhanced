# Battlesnake CLI Enhanced

A modification built on top of official Battlesnake CLI. Designed to conveniently run multiple snakes on a local computer for testing and tournaments.

## Supported Languages

- **Python** - snakes with `main.py`
- **Go** - snakes with `main.go`

## Dependencies

- Python
- Flask python package (for Python snakes)
- Go (for Go snakes)

## Installation

1. Clone the repository

   ```
   git clone https://github.com/kototok903/battlesnake-cli-enhanced.git
   ```

2. Install the official Battlesnake CLI ([BattlesnakeOfficial/rules](https://github.com/BattlesnakeOfficial/rules)) into this project's directory. Follow the instalation instructions in the [README](https://github.com/BattlesnakeOfficial/rules/blob/main/README.md).
   _After this step you should have a `rules` folder._

3. Make sure you have Flask python package installed if you are using Battlesnake Python starter project (it uses Flask in `server.py`).

   ```
   pip install Flask
   ```

4. If you want to run Go snakes, make sure Go is installed ([golang.org/dl](https://golang.org/dl/)).

5. Download your snakes and put them into `snakes` folder. Download the whole ReplIt/GitHub projects, no need to adjust anything. Snake type is auto-detected by checking for `main.go` (Go) or `main.py` (Python).
   _After this step you should have folders with your snakes in `snakes/` (e.g. `snakes/SnakeName1`, `snakes/SnakeName2`)_

## Usage

Run the enhanced CLI

```
python main.py
```

The tool allows you to run the snakes in `snakes` folder at some indecies and run local games with snakes you started.

Use `start [SnakeFolder] [index]` to run the snake located in `snakes/SnakeFolder` at the given index. (One snake can be started at multiple indecies.)

Use `game [AmountOfSnakes] [index, index, ...]` to run a local game where `AmountOfSnakes` is the amount of snakes in the game and idecies are the idecies of currently running snakes you want to be in the game (provide exactly `AmountOfSnakes` indecies).
Alternatively, use `game [AmountOfSnakes]` to avoid providing indecies and just run a game with snakes at indecies from 1 to `AmountOfSnakes`.

Use `help` to see the full command list.

### Usage Example

Let's assume we have snakes `AlienSnake` and `BirdSnake` in the folder `snakes`.

Use `python main.py` to start the CLI.

First, we use `start AlienSnake 1` to start the AlienSnake as Snake 1.
Then, use `start BirdSnake 2` to start the BirdSnake as Snake 2.
Finally, we can use `game 2 1 2` to start a game with 2 snakes: Snake 1 and Snake 2 (which currently are AlienSnake and BirdSnake). The browser tab with the game, as well as a terminal, will open. _Note: reloading the browser tab will stop the website's access to the game and you won't be able to continue watching it in browser._

Now, let's assume we made some changes to AlienSnake's code.
Just use `start AlienSnake 1` to restart AlienSnake at index 1. Alternatively, we can use `start AlienSnake 3` to start the new code at index 3 and then use `game 2 1 3` to test our new AlienSnake against its old version.

When we are done with coding for today, use `exit` to stop the CLI and all running snakes.
_Note: when you start the CLI again, no snakes will be running and you'll need to start them again._
