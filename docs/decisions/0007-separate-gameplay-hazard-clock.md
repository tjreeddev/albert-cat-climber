# 0007 — A separate hazard clock that freezes in WON/LOST

- **Round:** 6 (R39–R46)
- **Status:** Accepted. Still in effect.
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 6.
- **Evidence:** `spec.md` §12.1 (approved additions) and §12.2 (Hazard clock, Cycle); `albert/hazards.py` (`phase_of`, `hit_area`); `albert/game.py` (`hazard_ticks`); `tests/test_hazard_clock.py`; commit `c542338`.

## Y-statement

In the context of **timing hazard cycles (idle → warning → active) during play (Round 6)**,
facing **the Round 5 rule that gameplay never reads the visual `Game.ticks`, which keeps running in WON and LOST**,
we decided for **a separate gameplay clock, `Game.hazard_ticks`, that goes up only on PLAYING updates, freezes in WON/LOST and resets on restart. A pure `hazards.py` module calculates each hazard's phase and hit area from it**,
and neglected **reusing `Game.ticks` and random hazard timing** (`spec.md` §12.1 out of scope: random timing; §12.2: "Gameplay never reads `Game.ticks`"),
to achieve **deterministic, freezable hazard behaviour that tests can drive without Pygame (R40), while keeping R32 true**,
accepting **two separate clocks in `Game`, which must be kept apart**.
