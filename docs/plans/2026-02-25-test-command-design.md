# Test Command Design

Batch testing command to run multiple games and aggregate results.

## Command Syntax

```
t | test [num_snakes] [index, index, ...] [num_games?]
```

- `test 2 1 2` — 100 games (default) with snakes at indices 1 and 2
- `test 2 1 2 50` — 50 games
- `test 2` — 100 games with snakes at indices 1-2 (shorthand)

## Output Format

Per game:
```
Game 1/100: Snom-Go wins (87 turns) | Snom-Go: 1, AlienSnake: 0
Game 2/100: AlienSnake wins (124 turns) | Snom-Go: 1, AlienSnake: 1
```

Final summary:
```
=== Results (100 games) ===
  Snom-Go: 58 wins (58.0%)
  AlienSnake: 42 wins (42.0%)
  Avg turns: 103.4
```

## Implementation

### Approach
Parse stdout from `battlesnake play` command. Last line format:
```
INFO 17:20:21.911663 Game completed after 563 turns. Snom-Go was the winner.
```

Regex: `r"Game completed after (\d+) turns\. (.+) was the winner\."`

### Changes to main.py

1. Add to `COMMAND_CODE`: `"t": 9, "test": 9`
2. Add `run_test(amount, snake_inds, num_games)` function:
   - Use `subprocess.run()` (blocking) instead of `Popen`
   - No `-v`, `--browser` flags (silent mode)
   - Parse stdout for winner/turns
   - Track: wins dict, turns list
   - Print progress after each game
3. Add command handler in `main_loop()` (similar to `game` command)
4. Update `print_help()` with test command docs

### Edge Cases
- Ties / no winner
- Timeouts
- Solo games (always win)

## Future Enhancements
- `quicktest` command (like `quickgame` — auto-start snakes)
- Parallel execution (after Go port)
