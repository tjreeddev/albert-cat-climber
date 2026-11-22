# Handoff — Round 6: Kitchen hazards (R39–R46)

> **Reconstructed after development.** This handoff was written on 2026-11-22, after all seven rounds were finished, as final-project documentation. No handoff file existed at the end of Round 6. It is based only on what the repository records: commit `c542338`, `spec.md` section 12, the code and the tests at that commit. It does not claim to be a contemporaneous record.

## Round summary
- **Commit:** `c542338` "Add Round 6 kitchen hazards with warning cycles and knockback (R39–R46)", 2026-11-22.
- **Feature:**
  - 8 static, timed hazards: 4 steam vents, 2 hot burners and 2 dripping taps.
  - Each runs an idle → warning → active cycle.
  - Touching an active hazard causes knockback, a 0.3 s left/right override and 1 s of invulnerability. It never causes an instant loss.
- **Requirements:** R39–R46 (`problem.md` "Round 6 requirements"; acceptance criteria in `spec.md` §12.4; default hazards in §12.3).
- **Workflow note:** the R39–R46 requirements (`spec.md` §12), the tests and the implementation were committed together in `c542338`. There is no separate earlier requirements commit for this round.

## What changed
- `albert/hazards.py` (new, pure): `phase_of` and `hit_area`.
- `albert/level.py`: `Hazard` and `Level.hazards`, H1–H8.
- `albert/game.py`:
  - `hazard_ticks` advances only in PLAYING updates;
  - `knockback_ticks`, `knockback_dir` and `invulnerable_ticks`;
  - hits are checked after treat collection, and a win on the same update takes priority over a hit;
  - `restart()` resets all of them.
- `albert/effects.py`: the hit puff particles.
- `albert/config.py`, `albert/sprites.py`, `albert/render.py`:
  - hazard constants;
  - the `warn_orange` and `warn_red` colours, used only by hazard sprites;
  - the `hz_*` sprites and Albert's flashing while invulnerable.
- `spec.md` §12 added; `CLAUDE.md` updated.

## Tests
- New: `test_hazard_placement.py` (R39), `test_hazard_clock.py` (R40), `test_steam_vents.py` (R41), `test_burners.py` (R42), `test_drips.py` (R43), `test_knockback.py` (R44), `test_hazard_telegraph.py` (R45), `test_hazard_fairness.py` (R46).
- Changed:
  - `test_drawer_route.py` (R19) uses a hazard-free level to measure drawer timing only, without knockbacks.
  - `tests/conftest.py` gained `hazard_free_level`.
  - `test_art_style.py` gained the hazard sprite and render checks.
- 355 test functions in `tests/` at this commit.

## Earlier requirements
- **R1/R2 (qualified):** for 18 updates after a hit, left/right comes from the knockback direction and jump is ignored. Otherwise they are unchanged.
- **R4 is unchanged:** a loss still happens only by falling below the world.
- The physics constants, layout, camera and win/restart rules are unchanged. R46 checks that removing the hazards leaves earlier scenarios unchanged.

## Decisions
- `docs/decisions/0006-hazards-knock-back-instead-of-instant-loss.md`
- `docs/decisions/0007-separate-gameplay-hazard-clock.md`

## Notes for the next round (as evidenced by Round 7)
- Swinging or moving hazards were explicitly left out of scope (`spec.md` §12.1). Round 7 added a menu instead and did not touch `Game`.
