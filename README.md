# Albert Cat Climber

A small 16-bit-style pixel-art platformer starring Albert, a black cat, climbing a kitchen's cabinets. Start on the counter at the bottom-left of a big kitchen and climb to the highest cabinet near the top-left to win. Fall below the bottom of the kitchen and you lose. Landing back on a lower cabinet is fine, so a slip costs you height, not the run. Built as a CSC299 project.

## Features

- **Cabinet platforming.** Cabinets are one-way platforms: jump up through them from below and land on top.
- **A big scrolling kitchen.** The kitchen is 3 screens wide and 6 tall, and the camera follows Albert both sideways and up and down. The route zig-zags through four sections, each harder than the last, with narrower cabinets, longer gaps and faster drawers as you climb.
- **Cat treats.** Twelve fish-shaped treats are spread along the route, some on cabinet edges or side cabinets that need a detour. A counter in the corner shows how many you've collected. Treats are optional.
- **Moving drawers.** Six pulled-out drawers slide back and forth. Albert rides them while standing on them, and you'll need to time your jumps on and off, including one jump from a moving drawer straight onto another.
- **A living kitchen.**
  - Large windows show an animated outdoor view that changes as you climb: a garden, then town rooftops with chimney smoke, then a city skyline with blinking lights, and finally open sky with birds.
  - Curtains sway, clouds drift, mugs and pots steam, and appliance clocks blink.
  - Albert kicks up a puff of dust when he lands, and treats sparkle when collected.
- **Kitchen hazards.** Steam vents, hot burners and dripping taps run on fixed timing cycles and always flash a warning before they turn dangerous. Touching an active hazard doesn't end the run. It knocks Albert back with a short bounce and a moment without steering, then he flashes and is safe from hazards for a second. The real danger is being knocked off a ledge.
- **Title menu.** Start a game, check the controls, or quit, all over the animated kitchen.

## Controls

**Menu**

| Action | Keys |
|---|---|
| Move the selection | ↑ ↓ or W / S |
| Choose | Enter or Space |
| Back (quits from the title menu) | Esc or Backspace |

**In the game**

| Action | Keys |
|---|---|
| Move left / right | ← → or A / D |
| Jump | Space, ↑ or W |
| Restart (on the win/lose screen) | R or Enter |
| Back to the menu (on the win/lose screen) | M |
| Back to the menu (any time) | Esc |

Closing the window quits at any time.

## Setup

Requires **Python 3** (developed and tested with Python 3.14 on Windows). The only dependencies are listed in `requirements.txt`:

- `pygame-ce`, the Community Edition of Pygame. The code still uses `import pygame`. Don't also install classic `pygame`: it has no Python 3.14 wheels and conflicts with `pygame-ce`.
- `pytest`, which runs the automated tests.

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

There are **577 automated tests**, and all pass. They run headlessly, without opening a window. The tests in `tests/` are organised by requirement, R1–R53.

## Development

The game was built in seven rounds, each written up as requirements and tests before any code:

1. **The core platformer**: movement, jumping, one-way cabinets, winning and losing, restart, and the pixel-art look.
2. **Cat treats** and the treat counter.
3. **Moving drawers** that Albert can ride.
4. **The big kitchen**: a 960×1080 level, a camera that scrolls on both axes, and a four-section route.
5. **Animation and scenery**: steaming decorations, landing dust, treat sparkles, and large windows with outdoor views that change with height.
6. **Kitchen hazards** with warning cycles and knockback.
7. **The title menu** and controls screen.

See `problem.md` for the problem statement and the requirements for every round (R1–R53), and `spec.md` for the full specification. Each round from Round 2 on also has a `handoff-round-N.md`, and `docs/decisions/` holds the design decision records. The handoffs and decision records were reconstructed after development.
