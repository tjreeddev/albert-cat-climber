# CLAUDE.md — Albert Cat Climber

CSC299 project: a small 16-bit-style pixel-art platformer where Albert, the developer's black cat, climbs kitchen cabinets to reach the top.

## Source of truth
- `problem.md`: the original problem statement and requirements R1–R8. Don't edit it.
- `spec.md`: the detailed spec with decisions, defaults and acceptance criteria. Follow it. If something is ambiguous or seems to need a change, ask the user before departing from it.

## Round 1 scope rules
- Implement only what R1–R8 and `spec.md` require.
- Do **not** add collectibles, enemies, moving platforms, multiple levels, sound or music, power-ups, score/timers, extra menus or other features unless the user asks.
- Keep the code small and readable.

## Workflow
- Work in stages and stop for the user's review at each one: docs → tests → game logic → art/rendering → playtest.
- Don't create files outside the current stage without approval.
- Write tests before the logic they cover, so they fail first.
- Commit only when the user asks.

## Tech stack
- Python 3 + Pygame; pytest for tests.
- Dependencies are limited to `pygame-ce` and `pytest` (listed in `requirements.txt`).
- `pygame-ce` is the Community Edition of Pygame, used because classic `pygame` has no Python 3.14 wheels. Always write `import pygame` in code; never add the classic `pygame` package as a dependency.

## Commands
- Install: `pip install -r requirements.txt`
- Run the game: `python -m albert`
- Run tests: `pytest`. Tests must run headlessly, with `SDL_VIDEODRIVER=dummy` set in the tests or conftest.

## Architecture
- Keep game logic separate from Pygame:
  - `albert/config.py`, `physics.py`, `level.py` and `game.py` must not import pygame.
  - `albert/sprites.py`, `render.py` and `__main__.py` handle all Pygame drawing and input.
- `game.py` exposes a game-state object with `update(inputs, dt)` and `restart()`. Inputs are plain data such as left, right and jump flags, so tests can drive it without a window.
- Use a fixed timestep of 60 updates per second. Physics constants live in `config.py`.
- Cabinets are one-way platforms (they collide only when landing from above).
- Losing means falling below the world's bottom; there is no floor. Winning means landing on the highest cabinet.

## Art style (R7)
- Draw to a 320×180 internal surface, then scale it up by a whole number (×4) with nearest-neighbour filtering. Never use smooth scaling.
- Use one limited palette declared in `config.py`, with at most 16 colours per sprite.
- Albert is a black cat. Give him a dark outline or highlight colour so he stands out against the cabinets and wall.

## Testing conventions
- One test file per requirement: `tests/test_movement.py` (R1), `test_jump_gravity.py` (R2), `test_platforms.py` (R3), `test_lose.py` (R4), `test_win.py` (R5), `test_restart.py` (R6), `test_art_style.py` (R7), `test_runs_locally.py` (R8).
- Name each test or docstring after the requirement it covers, e.g. `test_r4_falling_below_world_loses`.
- Test logic through the pure modules; only the R7 and R8 tests touch Pygame.
