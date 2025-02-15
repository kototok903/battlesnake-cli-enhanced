# Battlesnake CLI Enhanced
A modification built on top of official Battlesnake CLI. Designed to conveniently run multiple snakes on a local computer for testing and tournaments.
**At this moment only Python snakes are suppoerted**

## Dependencies
- Python
- Flask python package

## Usage
1. Clone the repository
    ```
    git clone https://github.com/kototok903/battlesnake-cli-enhanced.git
    ```

2. Install the official Battlesnake CLI ([BattlesnakeOfficial/rules](https://github.com/BattlesnakeOfficial/rules)) to this project's directory. Follow the instalation instructions in the [README](https://github.com/BattlesnakeOfficial/rules/blob/main/README.md). 
*After this step you should have a `rules` folder.*

3. Make sure you have Flask python package installed if you are using Battlesnake Python starter project (it uses Flask in `server.py`).
    ```
    pip install Flask
    ```

4. Download your snakes and put them into `snakes` folder. Download the whole ReplIt/GitHub projects, no need to adjust anything. 
*After this step you should have folders with your snakes in `snakes/` (e.g. `snakes/SnakeName1`, `snakes/SnakeName2`)*

5. Run the enhanced CLI
    ```
    python main.py
    ```
