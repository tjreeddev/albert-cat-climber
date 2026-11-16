# Albert Cat Climber — Specification (Round 1)

## 1. Overview

Albert Cat Climber is a small 2D platformer based on the developer's black cat, Albert. The player guides Albert up a tower of kitchen cabinets. The goal is to reach the highest cabinet without falling.

Round 1 is deliberately small. It covers only the requirements R1–R8 from `problem.md`.

## 2. Scope

### In scope (Round 1)
- One hand-built level: a vertically scrolling tower of cabinets
- Left/right movement, jumping and gravity
- Landing on cabinets and climbing them
- Losing by falling below the world; winning by landing on the top cabinet
- Restarting after a win or a loss
- 16-bit-style pixel art, generated for this project
- Runs locally on the user's computer

### Out of scope (Round 1)
Collectibles, enemies, moving platforms, multiple levels, sound or music, power-ups, score/timer, menus beyond the win/lose overlay, save data, and anything else not required by `problem.md`.

## 3. Technical decisions

| Topic | Decision |
|---|---|
| Language / framework | Python 3 + Pygame, installed as the `pygame-ce` distribution (Community Edition; classic `pygame` has no Python 3.14 wheels). Code still uses `import pygame`. |
| Tests | pytest, running headlessly (`SDL_VIDEODRIVER=dummy`) |
| Internal resolution | 320×180 pixels |
| Window scale | ×4, whole-number scaling with nearest-neighbour filtering (no smoothing) |
| Update loop | Fixed timestep, 60 updates per second |
| Architecture | Game logic (physics, collisions, level, game state) in pure Python modules that don't import Pygame; rendering and input in a thin Pygame layer |
| Art | Claude creates the pixel-art sprites with a limited palette |
| Launch command | `python -m albert` |

## 4. Gameplay rules

### 4.1 World and camera
- The level is one vertical tower about 2–3 screens tall (roughly 360–540 world pixels) with about 10–12 cabinet platforms.
- Albert starts on a low counter at the bottom of the tower.
- There is **no floor** below the starting counter.
- The camera follows Albert up and down and stays inside the world bounds.
- Albert can't move past the left or right edge of the tower.

### 4.2 Controls
| Action | Keys |
|---|---|
| Move left | ← or A |
| Move right | → or D |
| Jump | Space, ↑ or W |
| Restart (only on the win/lose screen) | R or Enter |
| Quit | Esc or closing the window |

### 4.3 Game states
- `PLAYING`: normal play; input moves Albert.
- `WON`: Albert has landed on the highest cabinet. Gameplay input is ignored and a "You win" overlay is shown.
- `LOST`: Albert has fallen below the bottom of the world. Gameplay input is ignored and a "You lose" overlay is shown.

## 5. Requirements and acceptance criteria

### R1 — The player moves Albert left and right
- While PLAYING, holding left or right changes Albert's x position by `move_speed × dt` in that direction.
- With no horizontal input, Albert has no horizontal velocity and doesn't drift.
- Albert's x position is kept within the tower's left and right edges.

### R2 — Albert can jump and is affected by gravity
- Pressing jump while Albert is standing on a cabinet gives him a fixed upward velocity.
- Pressing jump while airborne has no effect (no double jump).
- While airborne, gravity increases Albert's downward velocity each update, up to a terminal falling speed.

### R3 — Albert lands on cabinets and uses them to climb
- Cabinets are **one-way platforms**. Albert collides with one only when moving downward and his feet cross its top surface from above.
- On landing, Albert's feet snap to the cabinet top, his vertical velocity becomes 0 and he counts as standing.
- Albert can jump up through a cabinet from below or the side without colliding.
- Walking off a cabinet's edge makes Albert start falling.
- The level layout must be climbable: each cabinet on the intended route is within Albert's maximum jump height and horizontal reach of the previous one.

### R4 — Falling below the playable area loses the game
- The playable area's bottom edge is the bottom of the world (below the starting counter).
- When Albert's top edge goes below the world's bottom edge, the state becomes `LOST`.
- Falling from a higher cabinet onto a lower one is **not** a loss.
- Once the state is `LOST`, movement and jump input are ignored.

### R5 — Reaching the highest cabinet wins the game
- The highest cabinet in the level is the goal platform.
- When Albert **lands on** the goal platform (by the R3 landing rule), the state becomes `WON`.
- Passing through it from below or touching its side doesn't win.
- Landing on any other cabinet doesn't win.
- Once the state is `WON`, movement and jump input are ignored.

### R6 — The player can restart after winning or losing
- In `WON` or `LOST`, pressing R or Enter restarts the game.
- Restarting restores the initial state: the starting position on the counter, zero velocity, standing, the starting camera position and the `PLAYING` state.
- Pressing the restart keys during `PLAYING` has no effect.

### R7 — 16-bit-style pixel art
- The game draws at 320×180 and scales the image up by a whole number with nearest-neighbour filtering, so pixels stay sharp.
- All sprites come from one declared, limited palette, with at most 16 colours per sprite.
- Required art:
  - Albert, a black cat with frames for idle, walking (2 frames) and jumping, facing either way
  - Cabinet platform tile(s)
  - A kitchen wall background
  - Simple pixel-style text for the win and lose overlays
- Whether the overall look fits the 16-bit style is judged by manual review.

### R8 — Runs on the user's own computer
- The game runs locally on Windows with Python 3 and pygame-ce installed. No network connection or server is needed.
- The only dependencies are `pygame-ce` (game, imported as `pygame`) and `pytest` (tests).
- `python -m albert` opens the game window.
- Headless, the game can initialise and run a few hundred frames of scripted input without errors.

## 6. Automated test plan

| Requirement | What the tests check |
|---|---|
| R1 | Left/right moves by speed×dt; no input means no drift; x stays within the tower edges |
| R2 | Jumping while standing sets upward velocity; jumping in the air does nothing; gravity increases downward speed up to the cap |
| R3 | Landing from above snaps Albert to the top; jumping up through a cabinet from below doesn't collide; walking off an edge starts a fall; the level layout is climbable |
| R4 | Going below the world bottom gives LOST; landing on a lower cabinet doesn't; input is ignored while LOST |
| R5 | Landing on the top cabinet gives WON; touching it from below or the side doesn't; other cabinets don't; input is ignored while WON |
| R6 | Restarting from WON or LOST restores the full initial state; restart does nothing while PLAYING |
| R7 | Resolution is 320×180; scale is a whole number; nearest-neighbour scaling; sprites use ≤16 colours from the palette; sprite sizes are as expected |
| R8 | Headless startup plus about 300 frames run without error; dependencies are only pygame-ce and pytest; no network modules are imported |

Visual quality (R7) and how the game feels to play are checked by hand.

## 7. Planned project layout

```
albert/
  __main__.py   # window, event loop, input mapping
  config.py     # resolution, scale, physics constants, palette
  physics.py    # player movement, gravity, jumping, platform collision (no pygame)
  level.py      # cabinet layout, start position, goal platform (no pygame)
  game.py       # game states, update, restart, win/lose checks, camera (no pygame)
  sprites.py    # pixel-art sprite definitions -> pygame Surfaces
  render.py     # drawing with camera offset, scaling, overlays
tests/
  test_movement.py, test_jump_gravity.py, test_platforms.py, test_lose.py,
  test_win.py, test_restart.py, test_art_style.py, test_runs_locally.py
requirements.txt
```
