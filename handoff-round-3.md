# Handoff — Round 3: Moving cabinet drawers (R15–R20)

> **Reconstructed after development.** This handoff was written on 2026-11-22, after all seven rounds were finished, as final-project documentation. No handoff file existed at the end of Round 3. It is based only on what the repository records: commit `050b176`, `spec.md` section 9, the code and the tests at that commit. It does not claim to be a contemporaneous record.

## Round summary
- **Commit:** `050b176` "Add Round 3 moving cabinet drawers (R15–R20)", 2026-11-21.
- **Feature:** two pulled-out cabinet drawers that slide left and right. They are one-way platforms that carry Albert, and the route needs timed jumps onto and off them.
- **Requirements:** R15–R20 (`problem.md` "Round 3 requirements"; acceptance criteria in `spec.md` §9.3).
- **Workflow note:** the R15–R20 requirements (`spec.md` §9), the tests and the implementation were committed together in `050b176`. There is no separate earlier requirements commit for this round.

## What changed
- `albert/level.py`: the `Drawer` definition and `Level.drawers`, kept separate from `Level.platforms`. Round 1 cabinets 4 and 8 were removed from `_TOWER` and replaced by drawers A and B.
- `albert/game.py`: `Game.drawers` (moving state). Each update finds the drawer Albert stands on, moves the drawers, carries Albert, then runs physics. Drawers freeze in WON/LOST, and `restart()` resets them.
- `albert/physics.py`: drawers act as one-way landing surfaces, using the R3 rules.
- `albert/config.py`, `albert/sprites.py`, `albert/render.py`: `DRAWER_SPEED` and the drawer size, the drawer sprite and its drawing.
- `spec.md` §9 added; `CLAUDE.md` and `README.md` updated.

## Tests
- New: `test_drawer_placement.py` (R15), `test_drawer_motion.py` (R16), `test_drawer_platforms.py` (R17), `test_drawer_ride.py` (R18), `test_drawer_route.py` (R19), `test_drawer_restart.py` (R20).
- Changed: `test_platforms.py` (R3 climbability now counts drawers as route stops); `test_art_style.py` (drawer sprite).
- 143 test functions in `tests/` at this commit.

## Earlier requirements
- **R3:** the text is unchanged, but its climbability test now treats each drawer as a stop anywhere along its path, because two route cabinets became drawers.
- R1–R14 behaviour is otherwise unchanged.

## Decisions
- `docs/decisions/0002-drawers-are-separate-one-way-platforms.md`

## Notes for the next round (as evidenced by Round 4)
- Round 4 replaced the compact tower with a large level. It revised R15's count (2 → 6 drawers) and R19's meaning of "the cabinet below/above".
