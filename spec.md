# Albert Cat Climber — Specification (Rounds 1–6)

## 1. Overview

Albert Cat Climber is a small 2D platformer based on the developer's black cat, Albert. The player guides Albert up a tower of kitchen cabinets. The goal is to reach the highest cabinet without falling.

Round 1 is deliberately small. It covers only the requirements R1–R8 from `problem.md`. Round 2 adds one feature, optional cat treats (R9–R14), described in section 8. R1–R8 are unchanged. Round 3 adds one feature, two horizontally moving cabinet drawers (R15–R20), described in section 9. R1–R14 behaviour is unchanged; the only Round 1 change is that two route cabinets become drawers (section 9.1). Round 4 replaces the compact tower with a large kitchen level, a camera that scrolls on both axes, and a longer route through four progressively harder sections (R21–R26), described in section 10. Albert's physics and the R1–R20 rules are unchanged; the level size, layout and the treat and drawer counts are revised (section 10.1). Round 5 adds visual-only kitchen animation and effects (R27–R32), described in section 11: looping decorations, landing dust and a treat sparkle. Gameplay is unchanged. Section 11.5 expands Round 5 with large background scenery (R33–R38): windows with animated outdoor views that change with height, curtains, plants, pictures and tiled panels. Round 6 adds 8 timed kitchen hazards (steam vents, hot burners and dripping taps) that knock Albert back (R39–R46), described in section 12. Physics, the layout, the camera and the win/lose rules are unchanged.

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

Round 2 lifts the "collectibles" exclusion for cat treats only (section 8). Round 3 lifts the "moving platforms" exclusion for horizontally moving drawers only (section 9; six of them from Round 4). Round 5 adds non-interactive decorations and particle effects only (section 11). Round 6 adds timed, static kitchen hazards with knockback only (section 12). Enemies, lives and checkpoints stay out of scope. Everything else above stays out of scope.

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
> **Revised in Round 4 (section 10):** the world is now 960×1080 with a four-section route, and the camera scrolls horizontally as well as vertically. The size and cabinet-count limits below applied to Rounds 1–3 only.

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
- The default level has exactly 5 treats. *(Revised in Round 4: 12 treats, see R24.)*
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
- The default level has exactly 2 drawers. *(Revised in Round 4: 6 drawers, see R25.)*
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
*(Revised in Round 4: "the cabinet below/above" a drawer now means its previous/next stop on `Level.route`, see R25.)*
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

## 10. Round 4 — Large kitchen level and two-axis camera (R21–R26)

### 10.1 Scope
- **In scope:**
  - a much larger kitchen level (960×1080, 3 screens wide × 6 tall);
  - a camera that scrolls horizontally and vertically;
  - a longer route through four progressively harder sections that reuses cabinets, treats and drawers;
  - 12 treats and 6 drawers.
- **Out of scope:** enemies, checkpoints, lives, vertical or other moving platforms, multiple levels, points/score, timers, sound or music, a minimap, camera smoothing or dead-zones, section banners or wall tints, extra menus, and any other feature not listed here.
- **Revisions to earlier rounds (approved):**
  - Section 4.1's "one vertical tower 2–3 screens tall with 10–12 cabinets" is replaced by R21. The R3 tests for those limits are removed.
  - The Round 1–3 layout (`_TOWER`, `_DRAWERS`, `_TREATS`) is replaced by the Round 4 layout.
  - R9's count of 5 treats becomes 12 (R24). All other R9 placement rules still apply.
  - R15's count of 2 drawers becomes 6 (R25). All other R15 rules still apply.
  - In R19, "the cabinet below/above a drawer" now means the drawer's previous/next stop on `Level.route`.
  - The R3 climbability check walks `Level.route` in order, instead of sorting cabinets by height, and uses the rise-dependent jump reach from section 10.2.
- **Unchanged:**
  - Albert's physics: `MOVE_SPEED` 100, `GRAVITY` 900, `JUMP_VELOCITY` 320, `MAX_FALL_SPEED` 400, and `physics.py` behaviour.
  - The R1–R20 rules: one-way platforms, win by landing on the highest cabinet, lose when falling below the world, restart, treat collection, the HUD, drawer motion and riding.
  - R7's 320×180 canvas with ×4 nearest-neighbour scaling, and the palette.

### 10.2 Decisions
| Topic | Decision |
|---|---|
| World | 960×1080 world pixels (`level.WORLD_WIDTH`, `level.WORLD_HEIGHT`). The world's left and right edges are the walls. There is no floor. |
| Start / goal | Albert starts on the counter `(16, 1060)`, 80×16, at the bottom-left. The goal is still the highest cabinet, `(100, 24)`, 40×16, near the top-left. |
| Route | `Level.route` lists every stop on the intended route in order, from the counter to the goal: cabinets (`Platform`) and `Drawer` definitions. It snakes up the kitchen. S1 runs right along the bottom, S2 runs left, S3 runs right, and S4 runs left to the goal. |
| Sections | `Platform` and `Drawer` gain a `section` field (default 1). Every route stop and side cabinet is tagged 1–4. |
| Side cabinets | Two short off-route cabinets (one in S3, one in S4) each hold a treat that needs a detour. They are the only cabinets not on the route. |
| Difficulty | Per section (route stops only):<br>• S1: cabinets 48–80 wide, gaps ≤ 22, rises ≤ 26, no drawers.<br>• S2: cabinets 32–40 wide, gaps ≤ 32, rises ≤ 36, 1 drawer at 35 px/s.<br>• S3: cabinets 24–32 wide, gaps ≤ 40, rises ≤ 40, 2 drawers at 45 px/s.<br>• S4: cabinets 24–40 wide, gaps ≤ 44, rises ≤ 42, 3 drawers at 50–55 px/s, including one drawer-to-drawer hop. |
| Jump reach (tests) | The rise limit is 0.9 × the max jump height (≈ 51 px). For a rise `r` (negative for a drop), horizontal reach = `margin × MOVE_SPEED × (v + √(v² − 2·GRAVITY·r)) / GRAVITY`, where `v = JUMP_VELOCITY`. Climbing checks use margin 0.85; "can't reach" checks use margin 1.0. |
| Camera | `Game.camera_x` and `Game.camera_y` centre Albert's hitbox on the 320×180 screen. Each axis is clamped to `[0, world size − screen size]`. Both are set on `restart()` and after every `update()`, with no smoothing. |
| Rendering | Every world object (wallpaper, cabinets, drawers, treats, Albert) is drawn offset by `(camera_x, camera_y)`. The wallpaper tiles on both axes. Objects outside the screen are skipped. The HUD and overlays stay fixed to the screen. |
| Treats | 12 treats: 2 in S1, 3 in S2, 3 in S3 (one on a side cabinet) and 4 in S4 (one on a side cabinet). Later sections put them on cabinet edges and side cabinets. |
| Drawers | 6 drawers: 0 in S1, 1 in S2, 2 in S3 and 3 in S4. They are 32×16, horizontal only, and follow the Round 3 motion, collision and riding rules. Speed is set per drawer and is always below `MOVE_SPEED`. |

### 10.3 Requirements and acceptance criteria

#### R21 — The level is a large kitchen spanning several screens in both directions
- The default world is 960×1080: at least 3 screens wide and 6 screens tall.
- Albert starts standing on the lowest cabinet, in the left third of the world.
- The goal is the unique highest cabinet.
- Every cabinet, drawer path and treat lies inside the world.

#### R22 — The camera scrolls horizontally and vertically
- When Albert is far from the world's edges, the camera centres his hitbox on both axes.
- The camera never shows anything outside the world on any of the four edges.
- When Albert moves along x or y, the camera follows on that axis.
- The camera is still valid (clamped, and centred where possible) in `WON` and `LOST`.
- `restart()` restores both axes to the starting view. Pressing restart during `PLAYING` doesn't change them.
- The HUD stays fixed to the screen whatever the camera position (R12).

#### R23 — The route runs through four progressively harder sections
- `Level.route` starts at the counter and ends at the goal. Its stops' sections run 1, 2, 3, 4 in order and never go back.
- Each stop on the route can be reached from the previous one: the rise is within the rise limit and the gap is within the reach for that rise. A drawer counts anywhere along its path.
- From one section to the next:
  - the largest gap and the largest rise never decrease;
  - the narrowest cabinet never gets wider;
  - the number of drawers and the fastest drawer speed never decrease;
  - each section is strictly harder than the one before on at least one of these.
- Over all cabinets, with drops allowed and full reach, the goal can't be reached without drawers but can be reached with them.

#### R24 — Treats are spread across the whole level
- The default level has exactly 12 treats: 2, 3, 3 and 4 in sections 1–4.
- R9's placement rules still hold.
- Each side cabinet holds a treat and can be reached from the route.
- R10–R14 are unchanged. The HUD shows `0/12` at the start.

#### R25 — Drawers recur throughout the level
- The default level has exactly 6 drawers: 0, 1, 2 and 3 in sections 1–4.
- Drawer speeds don't decrease from one section to the next, and every speed is above 0 and below `MOVE_SPEED`.
- Section 4 contains a drawer that directly follows another drawer on the route.
- R15–R19 still hold for each drawer, using its route neighbours:
  - when the previous (or next) stop is a cabinet, the drawer is in reach of it at one end of its path only;
  - a jump onto each drawer, and a jump off it to the next stop, each succeed at some moments and fail at others.

#### R26 — Earlier rules are unchanged by the bigger level
- The physics constants keep their Round 1 values.
- In the default level:
  - landing on the goal wins;
  - falling from a higher section onto a lower cabinet isn't a loss;
  - falling below y = 1080 loses.
- Restarting after a win or a loss resets Albert, both camera axes, the treats and the drawers.

### 10.4 Automated test plan (Round 4)
| Requirement | Test file | What the tests check |
|---|---|---|
| R21 | `tests/test_level_size.py` | 960×1080 world; ≥ 3×6 screens; start on the lowest cabinet at the left; unique highest goal; everything inside the world |
| R22 | `tests/test_camera.py` | Centred away from the edges; clamped at all four edges; follows on x and y; valid in WON/LOST; restart restores both axes |
| R23 | `tests/test_level_route.py` | Route starts at the counter and ends at the goal; sections in order; consecutive stops reachable; difficulty metrics are monotone and strictly increase; cabinets-only search can't reach the goal, but can with drawers |
| R24 | `tests/test_level_treats.py` | 12 treats; 2/3/3/4 per section; side cabinets hold treats and are reachable; HUD starts at `0/12` |
| R25 | `tests/test_level_drawers.py` | 6 drawers; 0/1/2/3 per section; speeds monotone and below MOVE_SPEED; a drawer-to-drawer hop in S4 |
| R26 | `tests/test_round4_rules.py` | Physics constants pinned; winning on the goal; falling to a lower section isn't a loss; falling out of the world loses; restart resets everything |
| R3, R6, R9, R11, R13, R15, R19 (revised) | existing files | Climbability walks `Level.route` with rise-dependent reach (the 10–12-cabinet and 2–3-screen tests are removed); the restart snapshot includes `camera_x`; treat and drawer counts become 12 and 6; R19 uses route neighbours, loops over all drawers and samples each drawer's full cycle |

No new modules are added. The shared jump-reach helpers live in `tests/conftest.py`.

## 11. Round 5 — Kitchen animation and visual effects (R27–R38)

### 11.1 Scope
- **In scope:**
  - an animation clock that counts updates;
  - a few fixed, looping kitchen decorations: steaming mugs, steaming pots and blinking appliance clocks;
  - a small dust puff when Albert lands;
  - a short sparkle when Albert collects a treat.
- **Out of scope:** decorations that collide with anything, random or physics-driven particles, screen shake, lighting or blending effects, Albert squash/stretch or new cat frames, parallax, weather (the clouds in the window views, R36, are scenery, not weather), sound or music, settings to turn effects off, and any other feature not listed here.
- **Visual only.** Round 5 doesn't change:
  - Albert's physics, speed, jump height or controls;
  - the cabinets, drawers, treats or `Level.route` from Round 4;
  - drawer motion or riding;
  - the camera;
  - treat collection, the treat count or the HUD;
  - win, lose or restart rules.

  R1–R26 keep holding as written.
- **Approved revisions to earlier rounds:**
  - New pure module `albert/effects.py` (no pygame). It holds particles and the animation-frame helper.
  - `Level` gains `decorations`, which is fixed, non-solid data. The Round 4 cabinet, drawer and treat layout is unchanged.

### 11.2 Decisions
| Topic | Decision |
|---|---|
| Animation clock | `Game.ticks` starts at 0 and goes up by 1 on every `update()` in every state: `PLAYING`, `WON` and `LOST`. `restart()` sets it to 0. It counts updates, not wall-clock time, so animation is deterministic. |
| Frame helper | `effects.anim_frame(ticks, frame_ticks, frame_count, phase=0)` returns `((ticks + phase) // frame_ticks) % frame_count`. Every looping animation chooses its frame with this helper only. `effects.decoration_frame(decoration, ticks)` applies it with the decoration's kind timing from `config.DECORATION_FRAMES` and its `phase`. |
| Decorations | `Level.decorations` is a list of `level.Decoration(kind, x, y, section, phase)` (default: empty). Its size comes from its kind. Decorations are never in `Level.platforms` and nothing collides with them. Default level: 8 decorations, 2 per section. A mug's or pot's `section` is the section of the cabinet it sits on. |
| Kinds and sizes | **Mug** (`"mug"`): 8×16. A cup in the bottom 8 rows with steam rising above it. 4 frames, 10 ticks each.<br>**Pot** (`"pot"`): 16×20. A pot in the bottom 10 rows with steam above it. 4 frames, 8 ticks each.<br>**Clock** (`"clock"`): 16×8. A wall-mounted appliance clock whose colon and digits light up and go dark. 2 frames, 30 ticks each. |
| Placement | **Mugs and pots** rest on a static cabinet: bottom = cabinet top, horizontally within the cabinet. They never sit on a drawer or the goal cabinet, and never overlap a treat or Albert's starting hitbox.<br>**Clocks** hang on the wall. They don't overlap any cabinet, drawer path or treat.<br>All decorations are inside the world. Each section has at least one steaming item (mug or pot), and all three kinds appear in the level. |
| Phase | Each decoration has a fixed `phase`, so decorations of the same kind don't animate in lockstep. |
| States | Decorations and particles keep animating in `WON` and `LOST`, behind the overlay. Drawers stay frozen there (R16). |
| Particles | `effects.Particle(kind, x, y, vx, vy, life)`. Every update, in every state, each particle moves by `velocity × dt` and loses 1 `life`. It is removed when `life` reaches 0. There is no gravity, no collision and no randomness. `Game.particles` holds them, at most `config.MAX_PARTICLES` = 48. When a new particle would exceed the limit, the oldest are dropped first. |
| Landing | Albert lands when he was not standing before this update's physics step and is standing after it, on a cabinet or a drawer, while `PLAYING`. Standing still, riding a drawer and the standing start after `restart()` are not landings. The landing that wins the game counts. |
| Spawning | `effects.dust_particles(player)` and `effects.sparkle_particles(treat)` return the new particles in order. `game.py` calls them through the module (`effects.dust_particles(...)`), so tests can replace them. New particles are appended to the end of `Game.particles`, so the oldest come first. |
| Landing dust | `DUST_COUNT` = 4 `"dust"` particles start at Albert's feet: y = bottom − 1, at x = left + 2, left + 4, right − 4 and right − 2. Their velocities are (−30, −10), (−15, −10), (15, −10) and (30, −10) px/s. They last `DUST_LIFE` = 12 ticks. Each is drawn as 1×1 `counter_shade`. |
| Treat sparkle | Each collected treat spawns `SPARKLE_COUNT` = 6 `"sparkle"` particles at the treat's centre. They move outward at `SPARKLE_SPEED` = 40 px/s at evenly spaced angles, starting straight up: particle k has velocity (40·sin θ, −40·cos θ) with θ = k × 360° / 6. They last `SPARKLE_LIFE` = 18 ticks. Each is drawn as a 3×3 plus sign in `brass`, centred on its rounded position, for the first half of its life. After that it is a 1×1 pixel in `text_white`. Dust is likewise drawn at its rounded position. Two treats collected on one frame give two sparkles. |
| Update order (while `PLAYING`) | Move drawers and carry Albert → physics → spawn dust on landing → collect treats and spawn sparkles → lose/win check → camera → step existing particles. New particles start stepping on the next update. In `WON`/`LOST`, `update` advances `ticks` and steps particles, then handles restart. |
| Restart | `restart()` sets `ticks` to 0 and clears `particles`. Pressing restart during `PLAYING` still does nothing (R6). |
| Draw order | Wallpaper → clocks → cabinets → drawers → mugs and pots → treats → Albert → particles → HUD → overlay. Decorations and particles are offset by the camera, and anything off-screen is skipped. |
| Art (R7 rules) | New sprites: `mug_0`–`mug_3`, `pot_0`–`pot_3` and `clock_0`–`clock_1`. They use palette colours only, at most 16 colours and no semi-transparent pixels. Steam uses `text_white` with a darker outline pixel where it crosses the light wallpaper. Existing colours are reused where possible, and at most 2 new palette colours are added. |
| Constants | These live in `config.py`:<br>• `MAX_PARTICLES`, `DUST_COUNT`, `DUST_LIFE`, `SPARKLE_COUNT`, `SPARKLE_LIFE` and `SPARKLE_SPEED`;<br>• `DECORATION_FRAMES`, a dict from kind to `(frame_ticks, frame_count)`: `{"mug": (10, 4), "pot": (8, 4), "clock": (30, 2)}`;<br>• `MUG_SIZE`, `POT_SIZE` and `CLOCK_SIZE` as `(width, height)` tuples, plus `DECORATION_SIZES` mapping each kind to its size.<br>Sprite keys are `f"{kind}_{frame}"`. |

### 11.3 Requirements and acceptance criteria

#### R27 — Animation is driven by a deterministic update clock
- `Game.ticks` is 0 after `Game()` and after `restart()`.
- Each `update()` adds exactly 1, in `PLAYING`, `WON` and `LOST`. On the update that restarts, `ticks` ends at 0.
- `anim_frame` follows the formula above. It loops with period `frame_ticks × frame_count`, and `phase` shifts it.
- Two games fed the same inputs have the same `ticks`, decoration frames and particles after every update.

#### R28 — The kitchen has fixed decorations in every section
- The default level has exactly 8 decorations, 2 in each of sections 1–4, and uses all three kinds.
- Each section has at least one mug or pot.
- The placement rules above hold.
- Decorations of the same kind don't all share a phase.
- Playing never changes `Level.decorations`.

#### R29 — Decorations loop through their animation frames
- A decoration's frame at tick `t` is `anim_frame(t, its kind's frame_ticks, its kind's frame_count, its phase)`. Over one full period, every frame is shown.
- In a headless render, a decoration's on-screen pixels differ between two ticks that give different frames. They are identical for two ticks that give the same frame.
- Decorations animate in `WON` and `LOST` as well as `PLAYING`.

#### R30 — Landing makes a small dust puff
- Landing on a cabinet or a drawer spawns exactly `DUST_COUNT` dust particles with the positions, velocities and life above.
- Standing still, walking along a cabinet, riding a drawer, jumping up through a cabinet, being in mid-air and the starting position after `restart()` spawn no dust.
- Dust moves by `velocity × dt` per update and is gone after `DUST_LIFE` updates.
- The landing that wins spawns dust.

#### R31 — Collecting a treat makes a sparkle
- Each collected treat spawns exactly `SPARKLE_COUNT` sparkle particles at its centre, moving outward at evenly spaced angles.
- Two treats collected on one frame give two sparkles.
- Edge-only touches, already-collected treats, and touches in `WON`/`LOST` spawn nothing, following R10.
- Sparkles are gone after `SPARKLE_LIFE` updates.
- The total number of particles never exceeds `MAX_PARTICLES`.

#### R32 — Effects are visual only and reset on restart
- A scripted run gives exactly the same gameplay state every update as the same run with no decorations and no particle spawning. The gameplay state is Albert, drawers, camera, game state, treats collected and the HUD text.
- Albert falls straight through a decoration's area, because decorations are not platforms.
- The physics constants keep their Round 1 values (R26).
- `restart()` from `WON` or `LOST` sets `ticks` to 0 and empties `particles`. Pressing restart during `PLAYING` changes neither.

### 11.4 Automated test plan (Round 5)
| Requirement | Test file | What the tests check |
|---|---|---|
| R27 | `tests/test_anim_clock.py` | Ticks start at 0; +1 per update in every state; restart resets; `anim_frame` formula, period and phase; two identical runs match |
| R28 | `tests/test_decorations.py` | 8 decorations, 2 per section; all kinds present; a steaming item per section; rest-on-cabinet and wall rules; no overlap with treats, the start or drawer paths; inside the world; phases vary; level data unchanged |
| R29 | `tests/test_decoration_anim.py` | Frame matches `anim_frame`; every frame appears per period; still animating in WON/LOST (pure). The headless pixel checks live in `test_art_style.py` |
| R30 | `tests/test_landing_dust.py` | Dust on cabinet and drawer landings; none when standing, walking, riding, rising through a cabinet, airborne or at restart; motion and lifetime; dust on the winning landing |
| R31 | `tests/test_treat_sparkle.py` | Sparkle count, centre and directions; two treats give two sparkles; nothing for edge touches, repeats or WON/LOST; lifetime; particle cap |
| R32 | `tests/test_visual_only.py` | Gameplay snapshots identical with and without decorations and effects; falling through a decoration; physics pinned; restart clears ticks and particles; restart during PLAYING doesn't |
| R7 (extended) | `tests/test_art_style.py` | Decoration frames are required sprites (palette, ≤ 16 colours, no semi-transparency) and match their kind's size; headless render pixels change between frames of a decoration (R29) |

`albert/effects.py` is the only new module. Like `config.py`, `physics.py`, `level.py` and `game.py`, it must not import pygame.

### 11.5 Round 5 expansion — Background scenery (R33–R38)

#### 11.5.1 Scope
- **In scope:**
  - large background scenery fixed to the kitchen wall: windows, tiled backsplash panels, framed pictures and hanging plants;
  - an animated outdoor view through every window, which changes with height: garden → town → city → sky;
  - slowly drifting clouds, plus one more motion per view;
  - curtains swaying on every window, and hanging plants that sway.
- **Out of scope:** parallax or any camera-dependent scrolling of the view, weather (rain or snow), a day/night cycle, lighting, scenery anyone can touch or stand on, and anything else not listed here.
- **Visual only.** Everything in 11.1 still applies. Scenery never collides with anything and never changes gameplay. R1–R32 still hold, and R27–R32 and their tests are unchanged.
- **Approved addition:** `Level.scenery`, fixed non-solid data in `level.py`, separate from `Level.decorations`.

#### 11.5.2 Decisions
| Topic | Decision |
|---|---|
| Data | `Level.scenery` is a list of `level.Scenery(kind, x, y, width, height, section, phase=0, view=None)` (default: empty). It is never in `Level.platforms` and nothing collides with it. `view` is set only for windows. |
| Kinds | **Window** (`"window"`): a large window of fixed size `WINDOW_SIZE` = 192×128. It has a `WINDOW_FRAME` = 4 px frame; the glass inside shows the outdoor view. A `CURTAIN_WIDTH` = 24 px curtain hangs over each side of the glass, full height.<br>**Tiles** (`"tiles"`): a static backsplash panel made of `TILE_SIZE` = 16 px tiles. Its width and height are multiples of 16, at least 64×32.<br>**Picture** (`"picture"`): a static framed picture, `PICTURE_SIZE` = 48×32.<br>**Plant** (`"plant"`): a hanging plant, `PLANT_SIZE` = 24×40. |
| Views | A window's `view` is set by its section: S1 `"garden"`, S2 `"town"`, S3 `"city"`, S4 `"sky"` (`config.VIEW_BY_SECTION`). Every view has a sky and drifting clouds, with:<br>• garden: a fence, trees and distant rooftops; the trees sway;<br>• town: rows of rooftops with chimneys; chimney smoke puffs;<br>• city: a skyline of tower blocks; their lit windows blink;<br>• sky: distant hills along the bottom; small birds glide across. |
| Amount | 4–6 large windows in the level, 1 or 2 per section, placed where many route views see them. Window centres get higher section by section: every S1 window's centre is lower than every S2 window's centre, and so on up to S4. The large windows and their outdoor views are the main feature, so the windows' total area exceeds the tiles' total area. Tiles, pictures and plants fill the remaining bare wall. |
| Section bands | A section's height band runs from the top of its highest cabinet or drawer to the bottom of its lowest one. In the default level: S1 858–1076, S2 596–838, S3 310–572, S4 24–284. Every window's centre lies inside its own section's band. Every other item is tagged with the section whose band is nearest its centre; inside a band the distance is 0, and an exact tie may use either section. |
| Coverage | For every stop on `Level.route` (a drawer at the middle of its path), take the camera view with Albert standing centred on the stop (R22 camera rule). Scenery covers at least 20% of that 320×180 view. Only windows and tiles count toward it; pictures and plants don't. Coverage is measured from the items' rectangles, which never overlap each other. In each section, at least half of these views show part of a window of that section. |
| Placement | Every scenery item is inside the world. Items don't overlap each other or any clock. They may sit behind cabinets, drawers, treats, mugs and pots, but at most 25% of a window's area may be behind cabinets or drawer paths. That share is the sum of its overlaps with cabinet rectangles and drawer-path rectangles, which never overlap each other (R15). Exact positions are chosen during implementation. |
| Animation | Driven only by `Game.ticks`:<br>• `effects.scroll_offset(ticks, ticks_per_px, loop_px, phase=0)` returns `((ticks + phase) // ticks_per_px) % loop_px`.<br>• Clouds drift right by 1 px every `CLOUD_TICKS_PER_PX` = 6 ticks (10 px/s) and wrap every `CLOUD_LOOP` = 160 px.<br>• Birds (sky view) glide 1 px every `BIRD_TICKS_PER_PX` = 3 ticks and wrap every `BIRD_LOOP` = 160 px.<br>• Looping frames use `anim_frame` with `config.SCENERY_FRAMES`: `{"garden": (45, 2), "town": (20, 3), "city": (50, 2), "curtain": (30, 4), "plant": (50, 2)}`. The four curtain frames show the art in the order `CURTAIN_SEQUENCE` = (0, 1, 2, 1), a gentle back-and-forth sway.<br>• Each item's `phase` offsets all of its animations, so windows don't move in lockstep.<br>• `effects.scenery_anim(item, ticks)` returns the item's animation state as a tuple of ints: window `(cloud_offset, view_frame, bird_offset, curtain_frame)`, where `curtain_frame` is the art frame (0–2) after `CURTAIN_SEQUENCE`, `view_frame` is 0 for sky, and `bird_offset` is 0 except for sky; plant `(frame,)`; tiles and picture `()`.<br>• Like decorations, scenery keeps animating in `WON` and `LOST` and resets on restart, because it follows `ticks`. |
| Draw order | Wallpaper → scenery (for a window: sky, clouds, the view and its animation, all clipped to the glass; then the frame and curtains) → clocks → cabinets → drawers → mugs and pots → treats → Albert → particles → HUD → overlay. Scenery is offset by the camera, and off-screen items are skipped. |
| Readability | Scenery must never look like something to stand on:<br>• No scenery sprite uses the cabinet and drawer colours `wood_light`, `wood_mid`, `wood_dark`, `counter_top` or `counter_shade`.<br>• Windows have no protruding sill.<br>• At most 10% of any scenery sprite's opaque pixels are darker than luminance 64, so black Albert stays easy to see. |
| Art (R7 rules) | Palette colours only, at most 16 colours per sprite, no semi-transparent pixels. Up to 8 new palette colours may be added for sky, foliage, roofs and buildings. Outdoor-view strips are drawn as tiles that wrap seamlessly at their loop width. Every scenery sprite key starts with `scn_`. These keys must exist: `scn_curtain_0`–`scn_curtain_2`, `scn_plant_0`–`scn_plant_1`, `scn_picture` (48×32), `scn_tile` (16×16), and at least one key starting with `scn_<view>_` for each of the four views. |

#### 11.5.3 Requirements and acceptance criteria

##### R33 — The kitchen has large background scenery
- `Level.scenery` uses all four kinds and has 4–6 windows, 1 or 2 per section. Window centres rise section by section.
- Each window's centre lies inside its section's band, and every other item carries the section nearest its centre.
- The windows' total area exceeds the tiles' total area.
- Sizes follow the table above.
- The placement rules above hold.
- Scenery items are never platforms.
- Playing never changes `Level.scenery`.

##### R34 — Scenery fills a large part of the screen everywhere on the route
- At every route-stop view, windows and tiles cover at least 20% of the screen.
- In each section, at least half of the route-stop views show part of one of that section's windows.

##### R35 — The view outside changes as Albert climbs
- Each window's `view` matches its section through `VIEW_BY_SECTION`.
- In a headless render at the same tick, the glass areas of the four views all differ from one another.

##### R36 — The outside view is always gently moving
- `scroll_offset` follows its formula, and `scenery_anim` follows the definitions above.
- For every window, the animation state changes at least once in any 60 updates. The clouds move in every view.
- Two games given the same inputs have the same scenery state after every update.
- Scenery keeps animating in `WON` and `LOST`.
- In a headless render, a window's glass pixels change between two ticks with different `cloud_offset`, and are identical for two ticks with the same animation state.

##### R37 — Curtains and hanging plants sway
- Every window's curtain frame cycles 0, 1, 2, 1 every 120 ticks.
- Every plant cycles through its 2 frames.
- The curtain sprites `scn_curtain_0`, `scn_curtain_1` and `scn_curtain_2` all differ, and the two plant sprites differ.

##### R38 — Scenery is visual only and stays behind gameplay
- A scripted run gives exactly the same gameplay state every update with and without scenery (the R32 comparison).
- Albert falls straight through a scenery item's area.
- In a headless render, every pixel where a cabinet, drawer, treat or Albert sprite is opaque looks the same with and without scenery behind it.
- The HUD pixels are identical with and without scenery.
- The readability rules above hold for every scenery sprite.

#### 11.5.4 Automated test plan (R33–R38)
| Requirement | Test file | What the tests check |
|---|---|---|
| R33 | `tests/test_scenery.py` | Kinds, sizes and counts; 1–2 windows per section, rising by section; inside the world; no overlaps with each other or clocks; at most 25% of each window hidden; not platforms; level data unchanged |
| R34 | `tests/test_scenery_coverage.py` | Coverage of at least 20% at every route-stop view; a window visible in at least half the views of each section |
| R35 | `tests/test_window_views.py` | View matches section (pure). The pixel check that the four views differ is in `test_art_style.py` |
| R36 | `tests/test_outside_anim.py` | `scroll_offset` formula; `scenery_anim` definitions; a change within every 60 ticks; deterministic; animates in WON/LOST. Pixel checks are in `test_art_style.py` |
| R37 | `tests/test_curtains_plants.py` | The curtain sequence 0, 1, 2, 1 and its period; plant frames. The sprite-difference check is in `test_art_style.py` |
| R38 | `tests/test_scenery_visual_only.py` | Gameplay identical with and without scenery; falling through scenery. The layering, HUD and readability pixel checks are in `test_art_style.py` |
| R7 (extended) | `tests/test_art_style.py` | Scenery sprites follow the palette, colour-count and transparency rules; the R35–R38 render checks |

No new modules. Scenery data lives in `level.py`, its animation helpers in `effects.py`, its sprites in `sprites.py` and its drawing in `render.py`.

## 12. Round 6 — Kitchen hazards (R39–R46)

### 12.1 Scope
- **In scope:** three kinds of static, timed kitchen hazards (steam vents, hot burners and dripping taps), 8 in the default level. Touching an active hazard knocks Albert back, takes away left/right control for a moment, and makes him briefly flash and unhittable.
- **Out of scope:** swinging or moving hazards (saved for a later round), enemies, lives, health, checkpoints, damage numbers, instant-loss hazards, hazards on drawers, random timing, sound or music, and anything else not listed here.
- **Unchanged:**
  - Albert's physics constants and `physics.py`;
  - the controls, except the approved 0.3 s left/right override after a hit;
  - the camera;
  - the cabinet, drawer and treat layout and `Level.route`;
  - drawer motion and riding;
  - treat collection and the HUD;
  - win, lose and restart rules;
  - every Round 5 decoration, effect and scenery item.
  
  Losing is still only falling below the world (R4). A knockback can lead to that, but a hazard never causes a loss directly.
- **Approved additions:**
  - `Level.hazards`, fixed hazard definitions;
  - a gameplay hazard clock, separate from the visual-only `Game.ticks`;
  - a new pure module `albert/hazards.py` (no pygame) for hazard timing and hit areas;
  - stovetop art on burner cabinets, with their collision unchanged.

### 12.2 Decisions
| Topic | Decision |
|---|---|
| Data | `Level.hazards` is a list of `level.Hazard(kind, x, top, section, idle, warning, active, phase=0, floor=None)` (default: empty). `kind` is `"vent"`, `"burner"` or `"drip"`. `top` is the top of the cabinet the hazard is on; for a drip it is the y where the drop starts, and `floor` is the top of the cabinet below it. Hazards are never in `Level.platforms` and are not solid. |
| Hazard clock | `Game.hazard_ticks` starts at 0 and is reset to 0 by `restart()`. At the start of each update while `PLAYING`, three things happen in order: `hazard_ticks` goes up by 1 (that value is used for the whole update); `invulnerable_ticks` goes down by 1 if it is positive; and if `knockback_ticks` is positive, the inputs are overridden (see Knockback) and it goes down by 1. It doesn't change in `WON` or `LOST`. Gameplay never reads `Game.ticks` (R32 still holds). |
| Cycle | `cycle = idle + warning + active`. With `t = (hazard_ticks + phase) % cycle`, `hazards.phase_of(hazard, hazard_ticks)` returns `"idle"` when `t < idle`, `"warning"` when `idle ≤ t < idle + warning`, and `"active"` otherwise. Only `"active"` can hit. |
| Steam vent | A `VENT_SIZE` = 16×8 vent sits on the cabinet at `(x, top − 8)`. While active, its jet's hit area is `(x + 2, top − 56, 12, 56)`: 12 px wide, from the cabinet top up 56 px. Albert is hit when his hitbox overlaps it with positive area, standing or in mid-air. |
| Hot burner | A `BURNER_WIDTH` = 16 px stovetop strip on the cabinet top from `x` to `x + 16`. While active, Albert is hit when he is standing (`on_ground`) on that cabinet and his hitbox overlaps the strip horizontally with positive length. Passing through or jumping over the cabinet is safe. |
| Dripping tap | A tap hangs at `(x − 2, top − 8)`, 8×8. During the warning a drop forms at the tap in 3 growing sizes, which can't hit. While active, a `DROP_SIZE` = 4×6 drop falls at `DRIP_SPEED` = 2 px per update (120 px/s). In active update k (0, 1, …) the drop's top-left is `(x, top + 2k)`. `active` equals `(floor − 6 − top) / 2 + 1`, so the drop's last active position rests exactly on `floor` (it splashes there). Albert is hit when his hitbox overlaps the drop with positive area. |
| Hit check | `hazards.hit_area(hazard, hazard_ticks)` returns the hit rectangle `(x, y, w, h)` while active, or `None` otherwise. For a burner it is the strip `(x, top − 1, 16, 1)`, together with the standing rule above. |
| Update order (while `PLAYING`) | Hazard clock, invulnerability and knockback countdowns → move drawers and carry Albert → physics → landing dust → collect treats and sparkles → hazard hits → lose/win check → camera. **The win takes priority:** on an update where Albert lands on the goal, no hazard hit is applied. |
| Knockback | On a hit:<br>• `player.vy = −KNOCKBACK_SPEED` (180 px/s) and `on_ground = False`;<br>• `Game.knockback_dir` is +1 if Albert's centre x ≥ the hit area's centre x, otherwise −1;<br>• `Game.knockback_ticks = KNOCKBACK_TICKS` (18, 0.3 s);<br>• `Game.invulnerable_ticks = INVULNERABLE_TICKS` (60, 1 s).<br>On each of the next 18 `PLAYING` updates, left/right comes from `knockback_dir` instead of the input, and jump is ignored. Albert is clamped at the walls as usual. |
| Invulnerability | Hits are checked only when `invulnerable_ticks` is 0. After a hit on update U, updates U+1 to U+59 can't hit, and update U+60 (when the count reaches 0) can hit again. |
| Hit effect | A hit spawns `HIT_PUFF_COUNT` = 6 `"puff"` particles at Albert's centre through `effects.puff_particles(player)` (visual only). Their velocities follow the sparkle formula at 30 px/s, they last 15 ticks, and each is drawn 1×1 `text_white`. |
| Flashing | While `invulnerable_ticks > 0`, Albert isn't drawn on updates where `(invulnerable_ticks // 4) % 2 == 1`. |
| States and restart | Hazards, knockback and invulnerability freeze in `WON` and `LOST`. `restart()` sets `hazard_ticks`, `knockback_ticks` and `invulnerable_ticks` to 0. |
| Telegraph art | Two new palette colours, `warn_orange` and `warn_red`, are used only by hazard sprites; no decoration or scenery sprite uses them.<br>• **Vent:** idle is a dark-grey vent with an unlit light. Warning alternates two "rattle" frames every 6 ticks, with `warn_red` lit and small sputters. Active is a solid jet at least 10 px wide (2 frames every 6 ticks), much bigger than the 1–2 px decorative steam wisps.<br>• **Burner:** idle coils are grey; warning coils are `warn_orange`; active coils are `warn_red`, with a 2-frame shimmer every 8 ticks.<br>• **Drip:** the tap carries a `warn_red` collar while the drop forms; the falling drop is drawn in sky blue with a white highlight.<br>Sprite keys: `hz_vent_idle`, `hz_vent_warn_0/1`, `hz_jet_0/1`, `hz_burner_idle`, `hz_burner_warn`, `hz_burner_hot_0/1`, `hz_tap`, `hz_tap_warn`, `hz_drop_form_0..2`, `hz_drop`. |
| Draw order | Wallpaper → scenery → clocks → cabinets, with burner strips drawn on their cabinet tops → drawers → mugs and pots → vents, taps and forming drops → treats → jets and falling drops → Albert → particles → HUD → overlay. |
| Constants | `config.py` holds `VENT_SIZE`, `JET_SIZE` (12, 56), `BURNER_WIDTH`, `DROP_SIZE`, `DRIP_SPEED`, `KNOCKBACK_SPEED`, `KNOCKBACK_TICKS`, `INVULNERABLE_TICKS`, `HIT_PUFF_COUNT` and the two warning colours. |

### 12.3 Default hazards
Every hazard sits on a static cabinet on `Level.route`, never on the goal cabinet, the starting counter or a drawer. Counts per section are 1, 2, 2 and 3.

| # | Section | Kind | Cabinet `(x, y, w)` | Hazard `x` | Other fields | `idle / warning / active` (cycle) | Phase |
|---|---|---|---|---|---|---|---|
| H1 | 1 | drip (teaching) | (420, 970, 48) | 442 | top 900, floor 970 | 87 / 60 / 33 (180) | 0 |
| H2 | 2 | vent | (712, 768, 36) | 722 | top 768 | 90 / 45 / 45 (180) | 0 |
| H3 | 2 | vent | (292, 656, 32) | 300 | top 656 | 90 / 45 / 45 (180) | 90 |
| H4 | 3 | burner | (64, 520, 28) | 70 | top 520 | 120 / 60 / 60 (240) | 0 |
| H5 | 3 | vent | (690, 370, 28) | 696 | top 370 | 90 / 45 / 45 (180) | 45 |
| H6 | 4 | vent | (556, 140, 24) | 560 | top 140 | 60 / 45 / 45 (150) | 30 |
| H7 | 4 | drip | (872, 226, 24) | 886 | top 156, floor 226 | 27 / 60 / 33 (120) | 0 |
| H8 | 4 | burner | (246, 56, 24) | 254 | top 56 | 80 / 60 / 60 (200) | 0 |

None of these overlaps a treat, decoration or drawer path. Per section, the shortest cycle never gets longer and the hazard count never goes down. The goal cabinet and the stop before it, (180, 40), have no hazards, so the final jump to the goal is hazard-free. `Level.hazards` lists H1–H8 in this order.

### 12.4 Requirements and acceptance criteria

#### R39 — The kitchen has 8 placed hazards
- The default level has exactly 8 hazards, 1/2/2/3 in sections 1–4: 4 vents, 2 burners and 2 drips, as in 12.3.
- Each vent and burner lies horizontally within a static route cabinet of its section, with `top` equal to that cabinet's top. Each drip's `floor` is such a cabinet's top, and its drop lies within the cabinet.
- No hazard is on the goal cabinet, the route stop just before the goal, the starting counter or a drawer path.
- No hazard's areas (vent, jet, burner strip, tap, drop path) overlap a treat or decoration.
- Everything lies inside the world, and playing never changes `Level.hazards`.

#### R40 — Hazards follow a deterministic, freezable gameplay clock
- `hazard_ticks` is 0 at the start and after `restart()`. It goes up by 1 per `PLAYING` update and stays unchanged in `WON` and `LOST`.
- `phase_of` follows 12.2 and loops with period `cycle`, and `phase` shifts it.
- Two games given the same inputs have the same hazard phases, knockback and invulnerability state after every update.
- Hazards don't depend on `Game.ticks`: changing `Game.ticks` changes no hazard result.

#### R41 — Steam vents
- When active, the jet's hit area is exactly as in 12.2. In idle and warning, `hit_area` is `None`.
- Standing in the jet, or jumping or falling through it, while active hits Albert. Standing next to it doesn't, and touching only an edge doesn't.
- Albert passes through the vent box; it isn't a platform.

#### R42 — Hot burners
- While active, standing on the cabinet over the strip hits Albert.
- These don't hit: standing on the same cabinet clear of the strip, being in mid-air above it, jumping up through the cabinet, and standing there while idle or warning.
- The cabinet's collision is the same as a normal cabinet's.

#### R43 — Dripping taps
- During the warning the drop can't hit. While active, the drop's position follows 12.2, and its last active position rests on `floor`.
- A falling drop touching Albert hits him, standing or in mid-air. The drop never hits during idle.

#### R44 — Knockback, control override and invulnerability
- A hit sets `vy`, `on_ground`, `knockback_dir`, `knockback_ticks` and `invulnerable_ticks` as in 12.2.
- For the next 18 `PLAYING` updates, left/right input is replaced by `knockback_dir` and jump is ignored. From the 19th, input works normally.
- The 59 updates after a hit can't hit. The 60th can.
- If Albert lands on the goal on the same update as a hit would happen, the game is won and no hit is applied.
- A hit spawns 6 puff particles. Treats, the treat count and the HUD are unchanged by hits.
- A knockback that carries Albert out of the world loses through R4, and only through R4.
- Restart clears the knockback and invulnerability, and the restart rules for R6, R13, R20, R26 and R32 still hold.

#### R45 — Hazards are clearly telegraphed and look different from decorations
- Every hazard's warning lasts at least 45 updates (0.75 s) and comes directly before its active phase.
- The `hz_*` sprites in 12.2 exist and follow R7: palette colours only, at most 16 colours, no semi-transparency.
- Every warning-state sprite uses `warn_orange` or `warn_red`, and no decoration (`mug_*`, `pot_*`, `clock_*`) or scenery (`scn_*`) sprite uses either.
- An active jet has at least 10 opaque columns, while a decorative steam frame has at most 2 opaque `text_white` columns per row.
- In a headless render, a hazard's pixels differ between idle, warning and active. Albert is hidden on flashing updates and drawn otherwise.

#### R46 — The route stays beatable, and earlier rules are unchanged
- Every hazard's cycle has a non-active run of at least 75 updates (1.25 s): idle plus warning.
- **Crossing test:** for each hazard, the default level is used with only that hazard in it. Albert stands on the previous route stop: at its edge nearest the hazard cabinet, or centred on it if it is a drawer. A drawer neighbour is placed at its end nearest the hazard cabinet, moving away from that end. The hazard clock is set so the next update is the first update of the cycle (t = 0).
- **The script:** wait `w0` updates, then jump toward the hazard cabinet, holding that direction until Albert lands on it. Then walk toward the next stop for `w1` updates, then jump toward it, holding that direction until he lands on it.
- **Values:** `(w0, w1)` is (0, 0) for every hazard except H7, which uses (50, 12).
- **Pass:** Albert ends standing on the next stop, with no hit and still `PLAYING`. Starting at the same point in 3 consecutive cycles gives the same result and the same number of updates.
- Removing all hazards doesn't change how R1–R38 gameplay behaves in their tests' scenarios.
- The physics constants keep their Round 1 values. Landing on the goal still wins, and falling below the world still loses.

### 12.5 Automated test plan (Round 6)
| Requirement | Test file | What the tests check |
|---|---|---|
| R39 | `tests/test_hazard_placement.py` | Count and kinds per section; the 12.3 data; on static route cabinets; not on the goal, counter or drawers; no overlap with treats or decorations; inside the world; data unchanged |
| R40 | `tests/test_hazard_clock.py` | Clock starts at 0, advances only while PLAYING, frozen in WON/LOST, reset by restart; `phase_of` formula, period and phase; deterministic; independent of `Game.ticks` |
| R41 | `tests/test_steam_vents.py` | Jet area; hit when standing, rising or falling in it; no hit beside it, on an edge, or while idle/warning; vent not solid |
| R42 | `tests/test_burners.py` | Hit standing on the strip while active; no hit clear of the strip, mid-air, rising through, or while idle/warning; collision unchanged |
| R43 | `tests/test_drips.py` | No hit while forming; drop path formula; last position rests on the floor; hit standing or in mid-air; no hit while idle |
| R44 | `tests/test_knockback.py` | The hit sets each value; 18-update override then normal control; jump ignored; 60-update invulnerability; can be hit again afterwards; puffs; treats/HUD unaffected; out-of-world only via R4; restart clears everything |
| R45 | `tests/test_hazard_telegraph.py` (pure parts) and `tests/test_art_style.py` (sprites and renders) | Sprite rules; warning colours used only by hazards; jet width and wisp width; idle, warning and active pixels differ; flashing |
| R46 | `tests/test_hazard_fairness.py` | Non-active run of at least 75; scripted crossing at every hazard over 3 cycles; earlier scenarios unchanged without hazards; physics pinned |

`albert/hazards.py` is the only new module. It must not import pygame.
