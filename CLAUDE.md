# CLAUDE.md — Albert Cat Climber

CSC299 project: a small 16-bit-style pixel-art platformer where Albert, the developer's black cat, climbs kitchen cabinets to reach the top.

## Source of truth
- `problem.md`: the original problem statement and requirements R1–R8. Don't edit it.
- `spec.md`: the detailed spec with decisions, defaults and acceptance criteria. Follow it. If something is ambiguous or seems to need a change, ask the user before departing from it.

## Scope rules (Rounds 1–6)
- Implement only what R1–R46 and `spec.md` require. R1–R8 (Round 1) are unchanged by Round 2; R1–R14 behaviour is unchanged by Round 3; R1–R20 rules and Albert's physics are unchanged by Round 4; R1–R26 are unchanged by Round 5; R1–R38 rules, physics, layout and camera are unchanged by Round 6.
- Round 2 adds one feature: optional cat treats (R9–R14, `spec.md` section 8). Cat treats are the only collectible.
- Round 3 adds one feature: horizontally moving cabinet drawers (R15–R20, `spec.md` section 9). They are the only moving platforms.
- Round 4 replaces the compact tower with a 960×1080 kitchen level, a camera that scrolls on both axes, and a four-section route of increasing difficulty with 12 treats and 6 drawers (R21–R26, `spec.md` section 10). This explicitly revises the old 2–3-screen / 10–12-cabinet limit.
- Round 5 is visual only (R27–R38, `spec.md` section 11). It adds looping kitchen decorations (mugs, pots, appliance clocks), landing dust and a treat sparkle (R27–R32). It also adds large background scenery (R33–R38, section 11.5): windows with animated outdoor views that change with height, curtains, plants, pictures and tiled panels. It must not change physics, controls, the layout, the camera, treat rules or win/lose/restart rules.
- Round 6 adds one feature: 8 timed, static kitchen hazards (steam vents, hot burners, dripping taps; R39–R46, `spec.md` section 12). Touching an active hazard causes a knockback, a 0.3 s left/right override and 1 s of invulnerability. It never causes an instant loss. Hazards are the only harmful objects. They are not enemies, and swinging or moving hazards are not in this round.
- Do **not** add other collectibles, enemies, lives, health, checkpoints, other moving platforms, multiple levels, sound or music, power-ups, points/score, timers, extra menus or other features unless the user asks. The treat count is not a score.
- Don't change the level layout beyond the approved Round 4 layout in `spec.md` section 10 without asking.
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
  - `albert/config.py`, `physics.py`, `level.py`, `game.py`, `effects.py` and `hazards.py` must not import pygame.
  - `albert/sprites.py`, `render.py` and `__main__.py` handle all Pygame drawing and input.
- `game.py` exposes a game-state object with `update(inputs, dt)` and `restart()`. Inputs are plain data such as left, right and jump flags, so tests can drive it without a window.
- Use a fixed timestep of 60 updates per second. Physics constants live in `config.py`.
- Cabinets are one-way platforms (they collide only when landing from above).
- Level route (Round 4): `Level.route` lists the intended stops (cabinets and drawer definitions) in order; `Platform` and `Drawer` carry a `section` (1–4).
- Camera (Round 4): `Game.camera_x` and `Game.camera_y` centre Albert, clamped to the world, no smoothing. Render offsets every world object by both; the HUD and overlays stay fixed to the screen.
- Losing means falling below the world's bottom; there is no floor. Winning means landing on the highest cabinet.
- Treats: `level.py` holds fixed treat positions (`Level.treats`); `game.py` tracks which were collected this run, and `restart()` clears that.
- Drawers: `level.py` holds fixed drawer definitions (`Level.drawers`, separate from `Level.platforms`); `game.py` keeps their moving state (`Game.drawers`) and `restart()` resets it. Drawers are one-way platforms and carry Albert while he stands on them.
- Effects (Round 5): `level.py` holds fixed, non-solid `Level.decorations`. `effects.py` holds `Particle` and `anim_frame`. `game.py` keeps `Game.ticks` (+1 every update, in every state) and `Game.particles`; `restart()` resets both. Animation uses update ticks only, never wall-clock time or randomness. Gameplay never reads effect state.
- Scenery (Round 5, section 11.5): `level.py` holds fixed, non-solid `Level.scenery`, separate from `Level.decorations`. Its animation comes from `effects.scroll_offset`, `anim_frame` and `scenery_anim` on `Game.ticks`. Render draws it straight after the wallpaper, behind everything else. Scenery never uses cabinet or drawer colours.
- Hazards (Round 6): `level.py` holds fixed `Level.hazards`. The pure module `hazards.py` gives `phase_of` and `hit_area`. `game.py` keeps `Game.hazard_ticks` (+1 per PLAYING update only, frozen in WON/LOST), `knockback_ticks`, `knockback_dir` and `invulnerable_ticks`; `restart()` resets them all. Hazards never read the visual `Game.ticks`.
- Each update while playing: advance the hazard clock and apply any knockback override to the inputs, then move drawers and carry Albert, then physics, then spawn landing dust, then collect treats and spawn sparkles, then check hazard hits, then check lose/win, then set the camera, then step the existing particles. In WON/LOST, advance ticks and step particles only.

## Art style (R7)
- Draw to a 320×180 internal surface, then scale it up by a whole number (×4) with nearest-neighbour filtering. Never use smooth scaling.
- Use one limited palette declared in `config.py`, with at most 16 colours per sprite.
- Albert is a black cat. Give him a dark outline or highlight colour so he stands out against the cabinets and wall.

## Testing conventions
- One test file per requirement: `tests/test_movement.py` (R1), `test_jump_gravity.py` (R2), `test_platforms.py` (R3), `test_lose.py` (R4), `test_win.py` (R5), `test_restart.py` (R6), `test_art_style.py` (R7), `test_runs_locally.py` (R8), `test_treat_placement.py` (R9), `test_treat_collect.py` (R10), `test_treat_count.py` (R11), `test_hud.py` (R12), `test_treat_restart.py` (R13), `test_treats_optional.py` (R14), `test_drawer_placement.py` (R15), `test_drawer_motion.py` (R16), `test_drawer_platforms.py` (R17), `test_drawer_ride.py` (R18), `test_drawer_route.py` (R19), `test_drawer_restart.py` (R20), `test_level_size.py` (R21), `test_camera.py` (R22), `test_level_route.py` (R23), `test_level_treats.py` (R24), `test_level_drawers.py` (R25), `test_round4_rules.py` (R26), `test_anim_clock.py` (R27), `test_decorations.py` (R28), `test_decoration_anim.py` (R29), `test_landing_dust.py` (R30), `test_treat_sparkle.py` (R31), `test_visual_only.py` (R32), `test_scenery.py` (R33), `test_scenery_coverage.py` (R34), `test_window_views.py` (R35), `test_outside_anim.py` (R36), `test_curtains_plants.py` (R37), `test_scenery_visual_only.py` (R38), `test_hazard_placement.py` (R39), `test_hazard_clock.py` (R40), `test_steam_vents.py` (R41), `test_burners.py` (R42), `test_drips.py` (R43), `test_knockback.py` (R44), `test_hazard_telegraph.py` (R45), `test_hazard_fairness.py` (R46).
- Name each test or docstring after the requirement it covers, e.g. `test_r4_falling_below_world_loses`.
- Test logic through the pure modules; only the R7, R8 and R12 (HUD drawing) tests touch Pygame. The R29, R35–R38 and R45 headless render checks live in `test_art_style.py`.
