import json
import os
import platform
import readline
import subprocess as sp
import sys
import tarfile
import urllib.request

SNAKES_NUM = 8
SNAKES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snakes")
BIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bin")
BATTLESNAKE_PATH = None


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

# Commands to autocomplete snake folder names
SNAKE_COMMANDS = {"start", "run", "s", "startall", "a", "quickgame", "q"}

GAME_TIMEOUT = 500

snakes = []


def get_snake_folders():
    """Returns list of valid snake folder names."""
    if not os.path.isdir(SNAKES_DIR):
        return []
    return [name for name in os.listdir(SNAKES_DIR) if os.path.isdir(os.path.join(SNAKES_DIR, name))]


def completer(text, state):
    """Tab completer for commands and snake folder names."""
    line = readline.get_line_buffer()
    tokens = line.split()

    # First token: complete commands
    if not tokens or (len(tokens) == 1 and not line.endswith(" ")):
        commands = list(COMMAND_CODE.keys())
        matches = [c + " " for c in commands if c.startswith(text)]
    # Subsequent tokens after snake commands: complete snake folders
    elif tokens[0].lower() in SNAKE_COMMANDS:
        folders = get_snake_folders()
        matches = [f + " " for f in folders if f.startswith(text)]
    else:
        matches = []

    return matches[state] if state < len(matches) else None


def setup_completer():
    readline.set_completer(completer)
    readline.set_completer_delims(" ")
    # macOS uses libedit, which needs different syntax
    if readline.__doc__ and "libedit" in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")


def main():
    setup_battlesnake()
    setup_completer()
    print()

    for _ in range(SNAKES_NUM):
        snakes.append({"active": False})

    print("Welcome to snake runner\n    - use h for help\n    - Tab for autocomplete\n")

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


def download_battlesnake():
    """Download battlesnake binary to .bin folder. Returns path or None."""
    system = platform.system()
    machine = platform.machine()

    arch_map = {"AMD64": "x86_64", "aarch64": "arm64"}
    arch = arch_map.get(machine, machine)

    binary_name = "battlesnake.exe" if system == "Windows" else "battlesnake"

    # Query GitHub API for latest release
    api_url = "https://api.github.com/repos/BattlesnakeOfficial/rules/releases/latest"
    try:
        with urllib.request.urlopen(api_url) as response:
            release = json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to query GitHub API: {e}")
        return None

    # Find matching asset (pattern: battlesnake_VERSION_SYSTEM_ARCH.tar.gz)
    search_suffix = f"_{system}_{arch}.tar.gz"
    download_url = None
    filename = None
    for asset in release.get("assets", []):
        if asset["name"].endswith(search_suffix):
            download_url = asset["browser_download_url"]
            filename = asset["name"]
            break

    if not download_url:
        print(f"No release found for {system}_{arch}")
        return None

    os.makedirs(BIN_DIR, exist_ok=True)
    archive_path = os.path.join(BIN_DIR, filename)
    binary_path = os.path.join(BIN_DIR, binary_name)

    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(download_url, archive_path)

        print("Extracting...")
        with tarfile.open(archive_path, "r:gz") as t:
            t.extract(binary_name, BIN_DIR)

        os.chmod(binary_path, 0o755)
        os.remove(archive_path)
        return binary_path

    except Exception as e:
        print(f"Failed to download battlesnake: {e}")
        return None


def setup_battlesnake():
    """Find or install battlesnake. Returns path or exits."""
    global BATTLESNAKE_PATH

    # Check Go installation
    try:
        gopath = sp.check_output(["go", "env", "GOPATH"], text=True).strip()
        go_bin = os.path.join(gopath, "bin", "battlesnake")
        if os.path.isfile(go_bin):
            print(f"Battlesnake Go package detected at {go_bin}")
            BATTLESNAKE_PATH = go_bin
            return
    except (sp.CalledProcessError, FileNotFoundError):
        pass

    # Check local .bin
    local_bin = os.path.join(BIN_DIR, "battlesnake")
    if os.path.isfile(local_bin):
        print("Battlesnake binary detected in .bin/")
        BATTLESNAKE_PATH = local_bin
        return

    # Need to install
    print("Battlesnake CLI not found. Installing...")
    path = download_battlesnake()
    if path:
        print(f"Battlesnake installed to {path}")
        BATTLESNAKE_PATH = path
    else:
        print("Could not install battlesnake. Please install manually:")
        print("  go install github.com/BattlesnakeOfficial/rules/cli/battlesnake@latest")
        print("Or download into .bin folder from: https://github.com/BattlesnakeOfficial/rules/releases")
        sys.exit(1)


def detect_snake_type(folder):
    """Returns 'go', 'python', or None"""
    if os.path.isfile(f"{folder}/main.go"):
        return "go"
    if os.path.isfile(f"{folder}/main.py"):
        return "python"
    return None


def run_snake(snake_name, snake_ind):
    folder = os.path.join(SNAKES_DIR, snake_name)
    if not os.path.isdir(folder):
        print(f"Error: folder {snake_name} not found")
        return False

    snake_type = detect_snake_type(folder)
    if not snake_type:
        print(f"Error: no main.go or main.py found in {snake_name}")
        return False

    if snakes[snake_ind]["active"]:
        snakes[snake_ind]["proc"].kill()
        print(f"Stopped previous Snake {snake_ind + 1} : {snakes[snake_ind]['name']}")

    env = os.environ.copy()
    env["PORT"] = str(8000 + snake_ind)

    if snake_type == "go":
        cmd = ["go", "run", "."]
    else:
        cmd = [sys.executable, "main.py"]

    snakes[snake_ind]["name"] = snake_name
    snakes[snake_ind]["proc"] = sp.Popen(cmd, cwd=folder, env=env)  # , stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    snakes[snake_ind]["active"] = True

    return True


def stop_snake(snake_ind):
    if not snakes[snake_ind]["active"]:
        return False

    snakes[snake_ind]["proc"].kill()
    snakes[snake_ind]["active"] = False

    return True


def run_game(amount, snake_inds, seed=None):
    cmd = [BATTLESNAKE_PATH, "play", "-W", "11", "-H", "11"]
    for i in snake_inds:
        cmd += ["--name", snakes[i]["name"], "--url", f"http://127.0.0.1:{8000 + i}"]
    cmd += ["-g", "solo" if amount == 1 else "standard"]
    cmd += ["-v", "-c"]
    if seed is not None:
        cmd += ["-r", seed]
    cmd += ["-t", str(GAME_TIMEOUT), "--browser"]

    sp.Popen(cmd)


if __name__ == "__main__":
    main()
