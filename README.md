# Albert Cat Climber

A small 16-bit-style pixel-art platformer starring Albert, a black cat, climbing the kitchen cabinets. Jump from cabinet to cabinet up a three-screen tower and land on the highest one to win. If you fall below the bottom of the tower, you lose. CSC299 project, Rounds 1–3.

Five fish-shaped cat treats sit on cabinets along the way. Touch one to collect it; the counter in the top-left corner shows how many you have (e.g. `2/5`). Treats are optional: you can win without them. Restarting puts every treat back and resets the counter to zero.

Two pulled-out drawers slide slowly left and right partway up the tower. You can't skip them: each one is only within jumping range at one end of its slide, so wait for it to come close, jump on, ride it across, and jump off at the right moment. Albert moves with a drawer while standing on it (you can still walk on it), but not once he jumps off. If a drawer carries him into a wall, it slides out from under him. Restarting puts both drawers back where they started.

## Controls

| Action | Keys |
|---|---|
| Move left / right | ← → or A / D |
| Jump | Space, ↑ or W |
| Restart (on the win/lose screen) | R or Enter |
| Quit | Esc or close the window |

## Setup

Requires **Python 3** (developed and tested with Python 3.14 on Windows). The only dependencies are in `requirements.txt`:

- `pygame-ce`: the Community Edition of Pygame. The code still uses `import pygame`. Don't also install classic `pygame`, which has no Python 3.14 wheels and conflicts with `pygame-ce`.
- `pytest`: runs the automated tests.

From the project folder (Windows PowerShell or Command Prompt), run these once:

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

## Run the game

```
.venv\Scripts\python -m albert
```

## Run the tests

```
.venv\Scripts\python -m pytest
```

The tests run without opening a window. There is one test file per requirement (R1–R20) in `tests/`. See `problem.md` for the requirements and `spec.md` for the full specification.
