# Albert Cat Climber

A small 16-bit-style pixel-art platformer starring Albert, a black cat, climbing the kitchen cabinets. Climb a big kitchen (3 screens wide and 6 tall) from the counter at the bottom-left to the highest cabinet near the top-left to win. If you fall below the bottom of the kitchen, you lose; falling back onto a lower cabinet is fine. CSC299 project, Rounds 1–4.

The camera follows Albert both sideways and up and down. The route zig-zags through four sections, each harder than the last:

1. **Counter run** (heading right): wide cabinets with short hops.
2. **Lower cabinets** (heading left): narrower cabinets, longer gaps and one slow drawer.
3. **Upper cabinets** (heading right): narrow cabinets and two drawers.
4. **Top shelves** (heading left): the narrowest cabinets, the longest gaps and three faster drawers, including a jump from one moving drawer straight onto another.

Twelve fish-shaped cat treats are spread along the way. The later ones sit on cabinet edges or on small side cabinets that need a detour. Touch a treat to collect it; the counter in the top-left corner shows how many you have (e.g. `2/12`). Treats are optional: you can win without them. Restarting puts every treat back and resets the counter to zero.

Six pulled-out drawers slide left and right. You can't skip them: each one is only within jumping range of the cabinet before it at one end of its slide, so wait for it to come close, jump on, ride it across, and jump off at the right moment.
- Albert moves with a drawer while standing on it, and you can still walk on it.
- He doesn't keep the drawer's movement once he jumps off.
- If a drawer carries him into a wall, it slides out from under him.

Restarting puts every drawer back where it started.

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

The tests run without opening a window. There is one test file per requirement (R1–R26) in `tests/`. See `problem.md` for the requirements and `spec.md` for the full specification.
