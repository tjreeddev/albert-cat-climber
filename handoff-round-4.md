# Handoff — Round 4: Large kitchen level and two-axis camera (R21–R26)

> **Reconstructed after development.** This handoff was written on 2026-11-22, after all seven rounds were finished, as final-project documentation. No handoff file existed at the end of Round 4. It is based only on what the repository records: commit `83587e7`, `spec.md` section 10, the code and the tests at that commit. It does not claim to be a contemporaneous record.

## Round summary
- **Commit:** `83587e7` "Add Round 4 large kitchen level and two-axis camera (R21–R26)", 2026-11-21.
- **Feature:**
  - The compact tower became a 960×1080 kitchen (3 screens wide × 6 tall).
  - The camera scrolls on both axes.
  - The route runs through four progressively harder sections, with 12 treats and 6 drawers.
- **Requirements:** R21–R26 (`problem.md` "Round 4 requirements"; acceptance criteria in `spec.md` §10.3).
- **Workflow note:** the R21–R26 requirements and the revisions below (`spec.md` §10), the tests and the implementation were committed together in `83587e7`. There is no separate earlier requirements commit for this round.

## What changed
- `albert/level.py`:
  - a new 960×1080 layout;
  - `Level.route`, the ordered list of route stops;
  - a `section` field (1–4) on `Platform` and `Drawer`;
  - two side cabinets for detour treats;
  - 12 treats and 6 drawers.
- `albert/game.py`: `Game.camera_x` and `Game.camera_y` centre Albert, clamped to the world, with no smoothing.
- `albert/render.py`: every world object is offset by both camera axes, the wallpaper tiles on both axes, and off-screen objects are skipped.
- `tests/conftest.py`: shared jump-reach helpers that depend on the rise.
- `spec.md` §10 added, and §4.1 marked as revised. `CLAUDE.md` and `README.md` updated.

## Tests
- New: `test_level_size.py` (R21), `test_camera.py` (R22), `test_level_route.py` (R23), `test_level_treats.py` (R24), `test_level_drawers.py` (R25), `test_round4_rules.py` (R26).
- Changed for revised requirements: `test_platforms.py` (R3), `test_treat_placement.py` (R9), `test_drawer_placement.py` (R15), `test_drawer_route.py` (R19).
- Adjusted for the new layout and camera: `test_restart.py` (R6), `test_hud.py` (R12), `test_treat_count.py` (R11), `test_treat_restart.py` (R13), `test_drawer_restart.py` (R20).
- 177 test functions in `tests/` at this commit.

## Earlier requirements revised (by ID)
- **R3:** climbability is checked along `Level.route` with a rise-dependent reach. The spec's "2–3 screens, 10–12 cabinets" limits were removed, along with `test_r3_default_level_has_10_to_12_cabinets` and `test_r3_default_level_is_two_to_three_screens_tall`.
- **R9:** 5 treats became 12. The test was renamed to `test_r9_default_level_has_twelve_treats`.
- **R15:** 2 drawers became 6. The test was renamed to `test_r15_default_level_has_six_drawers`.
- **R19:** "the cabinet below/above a drawer" means its previous/next stop on `Level.route`.
- Albert's physics constants and the R1–R20 rules are unchanged; R26 pins them.

## Decisions
- `docs/decisions/0003-camera-centres-albert-without-smoothing.md`
- `docs/decisions/0004-explicit-ordered-route-with-sections.md`

## Notes for the next round (as evidenced by Round 5)
- Round 5 added visual-only effects and scenery without changing this layout or the camera. Its tests compare gameplay with and without the effects.
