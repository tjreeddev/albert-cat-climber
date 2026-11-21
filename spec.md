# Albert Cat Climber — Specification (Rounds 1–3)

## 1. Overview

Albert Cat Climber is a small 2D platformer based on the developer's black cat, Albert. The player guides Albert up a tower of kitchen cabinets. The goal is to reach the highest cabinet without falling.

Round 1 is deliberately small. It covers only the requirements R1–R8 from `problem.md`. Round 2 adds one feature, optional cat treats (R9–R14), described in section 8. R1–R8 are unchanged. Round 3 adds one feature, two horizontally moving cabinet drawers (R15–R20), described in section 9. R1–R14 behaviour is unchanged; the only Round 1 change is that two route cabinets become drawers (section 9.1).

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

Round 2 lifts the "collectibles" exclusion for cat treats only (section 8). Round 3 lifts the "moving platforms" exclusion for two horizontally moving drawers only (section 9). Everything else above stays out of scope.

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

## 8. Round 2 — Cat treats (R9–R14)

### 8.1 Scope
- **In scope:** cat treats placed on the existing level, collecting them, a per-run treat count, a HUD showing it, and resetting treats on restart.
- **Out of scope:** enemies, moving platforms, multiple levels, power-ups, lives, checkpoints, sound or music, points/score, high scores, timers, save data, bonuses for collecting every treat, and any other feature not listed here.
- The treat count is the only number the game tracks. It is not a score.
- R1–R8 and the Round 1 cabinet layout (`_TOWER`) are unchanged. (Round 3 later replaces two cabinets with drawers; see section 9.1.)

### 8.2 Decisions
| Topic | Decision |
|---|---|
| Number of treats | 5 in the default level |
| Treat size | 8×8 world pixels (`config.TREAT_SIZE`); the hitbox matches the sprite |
| Placement | At most one treat per cabinet; never on the starting counter or the goal cabinet; each treat rests on its cabinet's top (treat bottom = cabinet top) and lies within the cabinet's width. Some sit near a cabinet edge so collecting them is a deliberate step. |
| Touch rule | Albert's hitbox and the treat's hitbox overlap with positive area (strict inequalities; touching edges don't count). Touching in mid-air counts. |
| Update order | Each `update` while `PLAYING`: physics step → collect treats → lose/win check. A treat touched on the winning frame counts. |
| States | Treats are collected only while `PLAYING`, never in `WON` or `LOST`. |
| A "run" | From the start or a restart until the next restart |
| Data | `Level.treats` holds fixed treat positions (default: none). The game keeps the set of treats collected this run; `restart()` clears it. Logic stays in `level.py` and `game.py` (no pygame). |
| HUD | A treat icon followed by `collected/total` (e.g. `2/5`) on a small dark panel in the top-left corner of the screen. It is fixed to the screen (not the camera) and is shown in every state, including the win and lose screens. |
| Font | The 5×5 pixel font gains the digits `0–9` and `/`. |
| Art (R7 rules) | The treat is a small fish-shaped cat treat. It uses only palette colours (two new treat colours are added), at most 16 colours and no semi-transparent pixels, with a dark outline so it stands out against the cabinets and wall. |

### 8.3 Requirements and acceptance criteria

#### R9 — Cat treats are placed on selected cabinets
- The default level has exactly 5 treats.
- Each treat rests on top of a cabinet and lies horizontally within it.
- No treat is on the starting counter or the goal cabinet, and no two treats share a cabinet.
- All treats are inside the world bounds and are `TREAT_SIZE`×`TREAT_SIZE`.

#### R10 — Touching a treat collects it for the rest of the run
- While `PLAYING`, when Albert's hitbox overlaps a treat's hitbox (positive area), the treat is collected.
- This works both on a cabinet and in mid-air. Touching edges only doesn't collect.
- A collected treat is no longer drawn (`Game.visible_treats()` excludes it) until the next restart.
- A treat can't be collected twice in one run. Several treats touched on the same frame are all collected.
- No treats are collected in `WON` or `LOST`.

#### R11 — The game tracks treats collected this run
- `Game.treats_collected` starts at 0 and goes up by exactly 1 per treat collected.
- `Game.treats_total` equals the number of treats in the level and never changes.
- A treat touched on the frame Albert wins is counted.

#### R12 — The HUD shows collected and total treats
- `hud_text(game)` (pure, in `game.py`) returns `"<collected>/<total>"`, e.g. `"0/5"`.
- The HUD is drawn in the top-left corner, fixed to the screen whatever the camera position.
- It is drawn in `PLAYING`, `WON` and `LOST`, and its pixels change when the count changes.
- Every character the HUD can show has a glyph in the pixel font.

#### R13 — Restarting restores treats and resets the count
- Restarting after winning or losing sets the count to 0 and makes every treat visible again.
- Pressing restart during `PLAYING` still does nothing (R6), including to treats.
- Playing never changes the level's treat definitions.

#### R14 — Treats are optional
- Landing on the goal wins with 0 treats, or with only some of them.
- Collecting every treat without landing on the goal doesn't win.
- Nothing extra happens when all treats are collected.

### 8.4 Automated test plan (Round 2)
| Requirement | Test file | What the tests check |
|---|---|---|
| R9 | `tests/test_treat_placement.py` | Count of 5; each treat rests within a cabinet; not on the counter or goal; one per cabinet; inside the world; correct size |
| R10 | `tests/test_treat_collect.py` | Walking and jumping into treats collects them; edge touch doesn't; collected treats aren't visible; no double collection; nothing in WON/LOST; two treats on one frame |
| R11 | `tests/test_treat_count.py` | Starts at 0; +1 per treat; total is fixed; treat on the winning frame counts |
| R12 | `tests/test_hud.py` | `hud_text` format; font has every HUD glyph; HUD pixels change with the count; HUD is fixed to the screen; drawn in every state |
| R13 | `tests/test_treat_restart.py` | Restart after losing or winning restores treats and count; restart during PLAYING doesn't; level treat data never changes |
| R14 | `tests/test_treats_optional.py` | Win with 0 or some treats; collecting all treats doesn't win |
| R7 (extended) | `tests/test_art_style.py` | `"treat"` is added to the required sprites so the palette, colour-count and transparency checks cover it; the treat sprite matches `TREAT_SIZE` |

No new modules are added; section 7's layout still applies, plus the six test files above.

## 9. Round 3 — Moving cabinet drawers (R15–R20)

### 9.1 Scope
- **In scope:** two cabinet drawers that slide left and right as one-way platforms, Albert riding them, and the timed jumps they create on the climbing route.
- **Out of scope:** vertical or other moving platforms, more than two drawers, treats on drawers, crushing or pushing, enemies, multiple levels, lives, checkpoints, sound or music, power-ups, points/score, timers, and any other feature not listed here.
- **Layout change (approved):** Round 1 cabinets 4 `(186, 342)` and 8 `(64, 160)` are removed from `_TOWER` and replaced by drawers that slide around those spots. The tower now has 10 static cabinets (still within section 4.1's 10–12). No treat moves and the goal cabinet is unchanged; only the cabinet indexes in `_TREATS` are renumbered.
- R1–R14 behaviour is otherwise unchanged. The R3 climbability check (`test_r3_default_level_is_climbable`) now counts each drawer as a stop on the route, anywhere along its path. The R3 requirement text is unchanged.

### 9.2 Decisions
| Topic | Decision |
|---|---|
| Data | `Level.drawers` holds fixed drawer definitions (`level.Drawer`; default: none), kept separate from `Level.platforms`, so `goal_platform`, the cabinet count and the R9 treat checks only see cabinets. The game keeps each drawer's moving state in `Game.drawers` (same order). |
| Drawer | `Drawer(min_x, max_x, y, width, height, speed, start_x, start_direction)`. Size is `DRAWER_WIDTH`×`DRAWER_HEIGHT` (32×16, matching the sprite). `y` never changes. Its left edge slides between `min_x` and `max_x`. |
| Motion | Constant `speed` (default `config.DRAWER_SPEED` = 40 px/s, slower than Albert's 100). Each update moves it `speed × dt` in its direction; on reaching or passing an end it stops at that end and reverses. |
| Default drawers | A: `min_x` 150, `max_x` 222, `y` 342, starts at x 186 moving right. B: `min_x` 30, `max_x` 100, `y` 160, starts at x 64 moving left. |
| Update order (while `PLAYING`) | Find the drawer Albert is standing on (if any) → move drawers → carry Albert by that drawer's movement → physics step against cabinets and drawers → collect treats → lose/win check. |
| Riding | While standing on a drawer, Albert's x changes by the drawer's movement that frame, clamped to the tower walls. Left/right input adds to it. He is not carried in the air and his jump doesn't keep the drawer's speed. |
| Collision | Drawers are one-way platforms with exactly the R3 rules. They never push Albert sideways. |
| States | Drawers move only while `PLAYING`; they freeze in `WON` and `LOST`. `restart()` puts every drawer back at its `start_x` and `start_direction`. |
| Win / lose / treats | Landing on a drawer never wins (the goal is still the highest cabinet). Falling off a drawer out of the world loses (R4). Drawers hold no treats and don't affect the treat count or HUD. |
| Art (R7 rules) | A 32×16 drawer front with a light top lip, a panel and a centred brass handle, using only existing palette colours, at most 16 colours and no semi-transparent pixels. |

### 9.3 Requirements and acceptance criteria

#### R15 — The level has two moving drawers
- The default level has exactly 2 drawers.
- Each drawer's whole path (from `min_x` to `max_x + width`) is inside the world.
- Each drawer is below the goal cabinet and above the starting counter.
- No drawer's path overlaps a cabinet.

#### R16 — Drawers move horizontally back and forth
- Each update while `PLAYING` moves a drawer by `speed × dt` in its direction.
- It reverses at `min_x` and `max_x` and never leaves its range.
- Its `y` never changes.
- The same number of updates always gives the same positions.
- Drawers don't move in `WON` or `LOST`.

#### R17 — Drawers are one-way platforms
- Albert lands on a drawer from above: feet snap to its top, vertical velocity becomes 0 and he counts as standing.
- He can jump up through a drawer from below.
- A drawer never pushes him from the side.
- He falls if he walks off a drawer or it slides out from under him.
- A fast fall can't pass through a drawer.

#### R18 — Albert rides a moving drawer
- While he stands on a drawer, his x changes by the drawer's movement that frame.
- Left/right input adds to that movement.
- He isn't carried while in the air, and his jump doesn't keep the drawer's speed.
- He is clamped at the tower walls, so a drawer can slide out from under him there.

#### R19 — The route requires timed drawer jumps
- Without the drawers, the cabinets can't be climbed to the goal.
- With each drawer somewhere along its path, the route can be climbed.
- At one end of its path each drawer is within jump reach of the cabinet below it; at the other end it is out of reach.
- In the default level, a jump onto each drawer, and from each drawer to the next cabinet, succeeds at some moments and fails at others.

#### R20 — Drawers don't change the win, lose, treat or restart rules
- Landing on a drawer never wins.
- Falling off a drawer and out of the world loses (R4).
- Treats and the HUD aren't affected by drawers.
- Restarting after a win or a loss resets the drawers; pressing restart during `PLAYING` still does nothing.
- Playing never changes the level's drawer definitions.

### 9.4 Automated test plan (Round 3)
| Requirement | Test file | What the tests check |
|---|---|---|
| R15 | `tests/test_drawer_placement.py` | Exactly 2 drawers; paths inside the world; below the goal and above the counter; no overlap with cabinets; drawer-sized |
| R16 | `tests/test_drawer_motion.py` | speed × dt per update; reverses at both ends; never out of range; fixed y; deterministic; frozen in WON and LOST |
| R17 | `tests/test_drawer_platforms.py` | Landing snaps to the top; jumping through from below; no side push; falling when it slides away or Albert walks off; no tunnelling on a fast fall |
| R18 | `tests/test_drawer_ride.py` | Carried while standing; input adds to the carry; not carried in the air; no inherited speed; clamped at the walls |
| R19 | `tests/test_drawer_route.py` | Not climbable without drawers; climbable with them; reach changes along each path; simulated jumps succeed at some moments and fail at others |
| R20 | `tests/test_drawer_restart.py` | Drawer never wins; falling off loses; restart resets drawers; nothing during PLAYING; level data unchanged; treats unaffected |
| R3 (updated) | `tests/test_platforms.py` | The climbability test counts drawers as route stops |
| R7 (extended) | `tests/test_art_style.py` | `"drawer"` is a required sprite (palette, colour-count and transparency checks) and matches the drawer size |

No new modules are added; section 7's layout still applies, plus the six test files above.
