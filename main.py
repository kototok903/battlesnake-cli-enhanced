import os
import subprocess as sp
import sys

SNAKES_NUM = 8

# fmt: off
COMMAND_CODE = {
    "h": 0, "help": 0,
    "s": 1, "start": 1, "run": 1,
    "S": 2, "stop": 2,
    "l": 3, "list": 3,
    "g": 4, "game": 4,
    "e": 5, "exit": 5,
    "a": 6, "startall": 6,
    "A": 7, "stopall": 7,
    "q": 8, "quickgame": 8,
}
# fmt: on

game_timeout = 500

snakes = []


def main():
    for _ in range(SNAKES_NUM):
        snakes.append({"active": False})

    print("Welcome to snake runner\n    - use h for help\n")

    while True:
        tokens = input("Command: ").split()
        if len(tokens) == 0:
            continue

        code = COMMAND_CODE.get(tokens[0], COMMAND_CODE.get(tokens[0].lower(), -1))

        if code == COMMAND_CODE["help"]:
            print_help()
            print()

        elif code == COMMAND_CODE["start"]:
            if len(tokens) != 3:
                print("Error: incorrect amount of args\n")
                continue
            snake_ind = -1
            try:
                snake_ind = int(tokens[2]) - 1
            except ValueError:
                print("Error: incorrect index (use 1-8)\n")
                continue
            if snake_ind < 0 or snake_ind >= SNAKES_NUM:
                print("Error: incorrect index (use 1-8)\n")
                continue
            snake_name = tokens[1]
            if not run_snake(snake_name, snake_ind):
                print(f"Unable to start snake {snake_name}\n")
                continue
            print(f"Snake {snake_name} is active as Snake {snake_ind + 1}\n")

        elif code == COMMAND_CODE["startall"]:
            if len(tokens) == 1:
                print("No folder names provided\n")
                continue
            snake_ind, i = 0, 1
            for snake_name in tokens[1:]:
                if snake_ind >= SNAKES_NUM:
                    print("Too many snakes provided")
                    break
                if snake_name in tokens[:i]:
                    print("Notice: to start multiple instances of the same snake use start [snake folder] [index]")
                    print(f"      (second instance of {snake_name} won't be started with startall)")
                elif not run_snake(snake_name, snake_ind):
                    print(f"Unable to start snake {snake_name}")
                else:
                    print(f"Snake {snake_name} is active at index {snake_ind + 1}")
                    snake_ind += 1
                i += 1
            print()

        elif code == COMMAND_CODE["stop"]:
            if len(tokens) != 2:
                print("Error: incorrect amount of args\n")
                continue
            # get snake index
            snake_ind = -1
            try:
                snake_ind = int(tokens[1]) - 1
            except ValueError:
                print(f"Error: incorrect index (use 1-{SNAKES_NUM})\n")
                continue
            if snake_ind < 0 or snake_ind >= SNAKES_NUM:
                print(f"Error: incorrect index (use 1-{SNAKES_NUM})\n")
                continue
            # stop the snake
            name = snakes[snake_ind].get("name", "?")
            if not stop_snake(snake_ind):
                print(f"Unable to stop snake {snake_ind + 1} : {name}\n")
                continue
            print(f"Snake {snake_ind + 1} : {name} stopped\n")

        elif code == COMMAND_CODE["stopall"]:
            for i in range(SNAKES_NUM):
                if snakes[i]["active"]:
                    name = snakes[i].get("name", "?")
                    if not stop_snake(i):
                        print(f"Unable to stop snake {i + 1} : {name}")
                    else:
                        print(f"Stopped snake {i + 1} : {name}")
            print()

        elif code == COMMAND_CODE["list"]:
            print("Snakes currently running:")
            for i in range(SNAKES_NUM):
                if snakes[i]["active"]:
                    print(f"    - {i + 1} : {snakes[i]['name']} ({snakes[i]['proc']})")  # DEBUG
            print()

        elif code == COMMAND_CODE["game"]:
            if len(tokens) == 1:
                print("Error: number of snakes not provided\n")
                continue
            # get amount of snakes
            amount = -1
            try:
                amount = int(tokens[1])
            except ValueError:
                print("Error: incorrect number of snakes (expected 1-4)\n")
                continue
            if amount < 1 or amount > 4:
                print("Error: incorrect number of snakes (expected 1-4)\n")
                continue
            if len(tokens) != 2 and len(tokens) != amount + 2:
                print(f"Error: incorrect number of args (expected {amount} indices)\n")
                continue
            # get snake indices for the game
            snake_inds = []
            if len(tokens) == amount + 2:
                err = False
                for i in range(2, amount + 2):
                    snake_ind = -1
                    try:
                        snake_ind = int(tokens[i]) - 1
                    except ValueError:
                        print(f"Error: incorrect snake index: {tokens[i]} (expected 1-{SNAKES_NUM})\n")
                        err = True
                        break
                    if snake_ind < 0 or snake_ind >= SNAKES_NUM:
                        print(f"Error: incorrect snake index: {tokens[i]} (expected 1-{SNAKES_NUM})\n")
                        err = True
                        break
                    if not snakes[snake_ind]["active"]:
                        print(f"Error: snake {snake_ind + 1} is not active\n")
                        err = True
                        break
                    snake_inds.append(snake_ind)
                if err:
                    continue
            else:
                snake_inds = [i for i in range(amount)]
            # run game
            run_game(amount, snake_inds)
            print(f"Running game with {amount} snakes:")
            for i in snake_inds:
                print(f"    - {i + 1} : {snakes[i]['name']} ({snakes[i]['proc']})")  # DEBUG

        elif code == COMMAND_CODE["exit"]:
            for i in range(SNAKES_NUM):
                if snakes[i]["active"]:
                    name = snakes[i]["name"]
                    if not stop_snake(i):
                        print(f"Unable to stop snake {i + 1} : {name}")
                    else:
                        print(f"Stopped snake {i + 1} : {name}")
            break

        else:
            print("Command is not recognized\n")


def print_help():
    print("Available commands:")
    print("h | help\n    - print help")
    print(
        f"s | start | run [folder name] [index]\n"
        f"    - starts the snake from the given folder in the snakes/ directory as Snake <index>\n"
        f"      (available indices: 1-{SNAKES_NUM})\n"
        f"      (e.g. start BobSnake 1 - starts the snake in the snakes/BobSnake/ folder as Snake 1)"
    )
    print(
        f"a | startall [folder name, folder name, ...]\n"
        f"    - start given snakes at indices starting with 1\n"
        f"      (at most {SNAKES_NUM})"
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
    print("e | exit\n    - stop all snakes and exit the program")


def change_snake_port(snake_name, snake_ind):
    """Sets the port of a snake in snake_name folder to (8000 + snake_ind)"""

    server_file = f"snakes/{snake_name}/server.py"
    if not os.path.isfile(server_file):
        print(f"Error: file {server_file} not found")
        return False

    server_file_contents = ""

    with open(server_file, "r") as f:
        server_file_contents = f.read()

    port_marker = 'int(os.environ.get("PORT", "'
    marker_pos = server_file_contents.find(port_marker)
    if marker_pos == -1:
        print("Error: unknown server.py format, please edit manually")
        return False

    port_start = marker_pos + len(port_marker)
    port_end = server_file_contents.index('"', port_start)
    server_file_contents = server_file_contents[:port_start] + str(8000 + snake_ind) + server_file_contents[port_end:]

    with open(server_file, "w") as f:
        f.write(server_file_contents)

    return True


def run_snake(snake_name, snake_ind):
    if not os.path.isdir(f"snakes/{snake_name}"):
        print(f"Error: folder {snake_name} not found")
        return False

    if not change_snake_port(snake_name, snake_ind):
        print("Unable to change port")
        return False

    main_file = f"snakes/{snake_name}/main.py"
    if not os.path.isfile(main_file):
        print(f"Error: file {main_file} not found")
        return False

    if snakes[snake_ind]["active"]:
        snakes[snake_ind]["proc"].kill()
        print(f"Stopped previous Snake {snake_ind + 1} : {snakes[snake_ind]['name']}")

    snakes[snake_ind]["name"] = snake_name
    snakes[snake_ind]["proc"] = sp.Popen([sys.executable, main_file])  # , stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    snakes[snake_ind]["active"] = True

    return True


def stop_snake(snake_ind):
    if not snakes[snake_ind]["active"]:
        return False

    snakes[snake_ind]["proc"].kill()
    snakes[snake_ind]["active"] = False

    return True


def run_game(amount, snake_inds, seed=None):
    cmd = ["battlesnake", "play", "-W", "11", "-H", "11"]
    for i in snake_inds:
        cmd += ["--name", snakes[i]["name"], "--url", f"http://127.0.0.1:{8000 + i}"]
    cmd += ["-g", "solo" if amount == 1 else "standard"]
    cmd += ["-v", "-c"]
    if seed is not None:
        cmd += ["-r", seed]
    cmd += ["-t", str(game_timeout), "--browser"]

    try:
        sp.Popen(cmd)
    except FileNotFoundError:
        print("Error: 'battlesnake' command not found. Is the CLI installed?")


if __name__ == "__main__":
    main()
