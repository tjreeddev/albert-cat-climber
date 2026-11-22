# 0006 — Hazards cause knockback, not an instant loss

- **Round:** 6 (R39–R46)
- **Status:** Accepted. Still in effect.
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 6.
- **Evidence:** `spec.md` §12.1 (scope and unchanged rules) and §12.2 (Knockback, Invulnerability); `albert/game.py` (`knockback_ticks`, `knockback_dir`, `invulnerable_ticks`); `tests/test_knockback.py` and `tests/test_hazard_fairness.py`; commit `c542338`.

## Y-statement

In the context of **adding harmful kitchen hazards to the climb (Round 6)**,
facing **the R4 rule that losing means only falling below the world, and the project's exclusion of lives, health and checkpoints**,
we decided for **a hit that applies an upward knockback, overrides left/right input for 18 updates (0.3 s) while ignoring jump, and gives 60 updates (1 s) of invulnerability. A hazard can push Albert off a ledge, but it never ends the run directly**,
and neglected **instant-loss hazards, lives, health and checkpoints** (`spec.md` §12.1 out of scope),
to achieve **real danger without changing R4 or adding new lose conditions, with fairness that tests can verify (R46)**,
accepting **a short loss of control after a hit (a documented qualification of R1/R2), and that a knockback can still lead to a loss through R4**.
