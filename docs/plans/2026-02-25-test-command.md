# Test Command Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `test` command that runs multiple games and reports win statistics.

**Architecture:** New `run_test()` function runs games sequentially via `subprocess.run()`, parses stdout for winner/turns, accumulates stats, prints progress and summary.

**Tech Stack:** Python, subprocess, regex

---

### Task 1: Add Command Code Entry

**Files:**
- Modify: `main.py:16-28` (COMMAND_CODE dict)

**Step 1: Add test command mapping**

Add to COMMAND_CODE dict:
```python
"t": 9, "test": 9,
```

**Step 2: Verify syntax**

Run: `python -m py_compile main.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add test command code mapping"
```

---

### Task 2: Create run_test_game Helper

**Files:**
- Modify: `main.py` (add function after `run_game`)

**Step 1: Add run_test_game function**

This function runs a single game and returns (winner, turns):

```python
def run_test_game(snake_inds):
    """Run single game, return (winner_name, num_turns) or (None, num_turns) for tie."""
    import re
    
    cmd = [BATTLESNAKE_PATH, "play", "-W", "11", "-H", "11"]
    for i in snake_inds:
        cmd += ["--name", snakes[i]["name"], "--url", f"http://127.0.0.1:{8000 + i}"]
    cmd += ["-g", "solo" if len(snake_inds) == 1 else "standard"]
    cmd += ["-t", str(GAME_TIMEOUT)]
    
    result = sp.run(cmd, capture_output=True, text=True)
    
    # Parse: "Game completed after 563 turns. Snom-Go was the winner."
    match = re.search(r"Game completed after (\d+) turns\. (.+) was the winner\.", result.stdout)
    if match:
        return match.group(2), int(match.group(1))
    
    # No winner (tie or error) - try to get turns at least
    turns_match = re.search(r"Game completed after (\d+) turns", result.stdout)
    turns = int(turns_match.group(1)) if turns_match else 0
    return None, turns
```

**Step 2: Verify syntax**

Run: `python -m py_compile main.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add run_test_game helper function"
```

---

### Task 3: Create run_test Function

**Files:**
- Modify: `main.py` (add function after `run_test_game`)

**Step 1: Add run_test function**

```python
DEFAULT_TEST_GAMES = 100

def run_test(snake_inds, num_games=DEFAULT_TEST_GAMES):
    """Run multiple games and print results."""
    wins = {snakes[i]["name"]: 0 for i in snake_inds}
    turns_list = []
    
    print(f"Running {num_games} games...\n")
    
    for game_num in range(1, num_games + 1):
        winner, turns = run_test_game(snake_inds)
        turns_list.append(turns)
        
        if winner:
            wins[winner] = wins.get(winner, 0) + 1
        
        # Progress line
        winner_str = f"{winner} wins" if winner else "Tie"
        summary = ", ".join(f"{name}: {count}" for name, count in wins.items())
        print(f"Game {game_num}/{num_games}: {winner_str} ({turns} turns) | {summary}")
    
    # Final summary
    print(f"\n=== Results ({num_games} games) ===")
    for name, count in wins.items():
        pct = (count / num_games) * 100
        print(f"  {name}: {count} wins ({pct:.1f}%)")
    avg_turns = sum(turns_list) / len(turns_list) if turns_list else 0
    print(f"  Avg turns: {avg_turns:.1f}\n")
```

**Step 2: Verify syntax**

Run: `python -m py_compile main.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add run_test function for batch games"
```

---

### Task 4: Add Command Handler in main_loop

**Files:**
- Modify: `main.py:91-234` (main_loop function, add elif block before exit handler)

**Step 1: Add test command handler**

Add this elif block before the `elif code == COMMAND_CODE["exit"]:` line:

```python
        elif code == COMMAND_CODE["test"]:
            if len(tokens) < 2:
                print("Error: number of snakes not provided\n")
                continue
            # Parse amount of snakes
            try:
                amount = int(tokens[1])
            except ValueError:
                print("Error: incorrect number of snakes (expected 1-4)\n")
                continue
            if amount < 1 or amount > 4:
                print("Error: incorrect number of snakes (expected 1-4)\n")
                continue
            
            # Determine expected token count: test [amount] [indices...] [num_games?]
            # Minimum: 2 (test + amount) -> uses indices 1..amount
            # With indices: 2 + amount
            # With indices + games: 3 + amount
            
            snake_inds = []
            num_games = DEFAULT_TEST_GAMES
            
            if len(tokens) == 2:
                # test [amount] -> use indices 1..amount
                snake_inds = list(range(amount))
            elif len(tokens) == 2 + amount:
                # test [amount] [indices...]
                snake_inds = []
                for i in range(2, 2 + amount):
                    try:
                        idx = int(tokens[i]) - 1
                    except ValueError:
                        print(f"Error: invalid index {tokens[i]}\n")
                        break
                    if idx < 0 or idx >= SNAKES_NUM or not snakes[idx]["active"]:
                        print(f"Error: snake {tokens[i]} not active\n")
                        break
                    snake_inds.append(idx)
                if len(snake_inds) != amount:
                    continue
            elif len(tokens) == 3 + amount:
                # test [amount] [indices...] [num_games]
                snake_inds = []
                for i in range(2, 2 + amount):
                    try:
                        idx = int(tokens[i]) - 1
                    except ValueError:
                        print(f"Error: invalid index {tokens[i]}\n")
                        break
                    if idx < 0 or idx >= SNAKES_NUM or not snakes[idx]["active"]:
                        print(f"Error: snake {tokens[i]} not active\n")
                        break
                    snake_inds.append(idx)
                if len(snake_inds) != amount:
                    continue
                try:
                    num_games = int(tokens[2 + amount])
                except ValueError:
                    print("Error: invalid number of games\n")
                    continue
            else:
                print(f"Error: expected {amount} indices (and optional game count)\n")
                continue
            
            # Verify all snakes active
            all_active = True
            for idx in snake_inds:
                if not snakes[idx]["active"]:
                    print(f"Error: snake {idx + 1} not active\n")
                    all_active = False
                    break
            if not all_active:
                continue
            
            run_test(snake_inds, num_games)
```

**Step 2: Verify syntax**

Run: `python -m py_compile main.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add test command handler in main_loop"
```

---

### Task 5: Update Help Text

**Files:**
- Modify: `main.py:236-260` (print_help function)

**Step 1: Add test command help**

Add these lines before the exit help line:

```python
    print(
        "t | test [number of snakes] [index, index, ...] [num_games?]\n"
        "    - run multiple games (default 100) and show win statistics\n"
        "      (e.g. test 2 1 2 - runs 100 games with snakes 1 and 2)\n"
        "      (e.g. test 2 1 2 50 - runs 50 games)"
    )
```

**Step 2: Verify syntax**

Run: `python -m py_compile main.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add test command to help text"
```

---

### Task 6: Manual Test

**Step 1: Start the CLI**

Run: `python main.py`

**Step 2: Start two snakes**

```
startall Snake1 Snake2
```
(Replace Snake1/Snake2 with actual folder names in your snakes/ directory)

**Step 3: Run test command**

```
test 2 1 2 5
```
Expected: 5 games run, progress shown, final summary with wins and avg turns

**Step 4: Test shorthand**

```
test 2
```
Expected: 100 games with snakes at indices 1 and 2

**Step 5: Commit final**

```bash
git add -A
git commit -m "feat: complete test command implementation"
```
