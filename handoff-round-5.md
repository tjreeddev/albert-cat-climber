# Handoff — Round 5: Kitchen animation, effects and background scenery (R27–R38)

> **Reconstructed after development.** This handoff was written on 2026-11-22, after all seven rounds were finished, as final-project documentation. No handoff file existed at the end of Round 5. It is based only on what the repository records: commit `021d722`, `spec.md` section 11 (including the 11.5 scenery expansion), the code and the tests at that commit. It does not claim to be a contemporaneous record.

## Round summary
- **Commit:** `021d722` "Add Round 5 animated kitchen effects and background scenery (R27–R38)", 2026-11-22.
- **Feature (visual only):**
  - looping decorations: steaming mugs and pots, and blinking appliance clocks;
  - landing dust and treat sparkles;
  - large background scenery: windows with animated outdoor views that change with height (garden → town → city → sky), curtains, plants, pictures and tiled panels.
- **Requirements:** R27–R38 (`problem.md` "Round 5 requirements"; acceptance criteria in `spec.md` §11.3 and §11.5.3).
- **Workflow note:** the R27–R38 requirements (`spec.md` §11), the tests and the implementation were committed together in `021d722`. R33–R38 were a scenery expansion of the same round, also in that commit. There is no separate earlier requirements commit for this round.

## What changed
- `albert/effects.py` (new, pure): `Particle`, `anim_frame`, `scroll_offset`, `scenery_anim`, and the dust and sparkle spawners.
- `albert/level.py`: fixed, non-solid `Level.decorations` (8) and `Level.scenery`.
- `albert/game.py`:
  - `Game.ticks` goes up by 1 on every update, in every state.
  - `Game.particles`, capped at `MAX_PARTICLES`.
  - Dust is spawned on landing and sparkles on collecting a treat.
  - `restart()` resets both `ticks` and `particles`.
- `albert/config.py`, `albert/sprites.py`, `albert/render.py`: effect constants, the decoration and `scn_*` scenery sprites, new palette colours, and scenery drawn straight after the wallpaper.
- `spec.md` §11 added; `CLAUDE.md` updated.

## Tests
- New:
  - `test_anim_clock.py` (R27), `test_decorations.py` (R28), `test_decoration_anim.py` (R29), `test_landing_dust.py` (R30), `test_treat_sparkle.py` (R31), `test_visual_only.py` (R32);
  - `test_scenery.py` (R33), `test_scenery_coverage.py` (R34), `test_window_views.py` (R35), `test_outside_anim.py` (R36), `test_curtains_plants.py` (R37), `test_scenery_visual_only.py` (R38).
- Extended: `test_art_style.py`, with the headless render checks for R29 and R35–R38.
- 287 test functions in `tests/` at this commit.

## Earlier requirements
- No earlier requirement was revised. The physics, layout, camera, treat rules and win/lose/restart rules are unchanged. R32 and R38 check this by running the same gameplay with and without the effects.

## Decisions
- `docs/decisions/0005-tick-driven-deterministic-animation.md`

## Notes for the next round (as evidenced by Round 6)
- Round 6 hazards needed their own gameplay clock (`hazard_ticks`), because `Game.ticks` keeps running in WON/LOST and gameplay must never read it.
