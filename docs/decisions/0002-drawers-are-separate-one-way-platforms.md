# 0002 — Drawers are separate, one-way, horizontal-only platforms

- **Round:** 3 (R15–R20)
- **Status:** Accepted. Still in effect, with the count revised to 6 drawers in Round 4 (R25).
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 3.
- **Evidence:** `spec.md` §9.1 and §9.2; `albert/level.py` (`Drawer`, `Level.drawers`); `albert/game.py` (`Game.drawers`); `tests/test_drawer_platforms.py` and `tests/test_drawer_ride.py`; commit `050b176`.

## Y-statement

In the context of **adding moving platforms to make the climb need timing (Round 3)**,
facing **the risk that moving objects would break the existing goal, cabinet-count and treat-placement checks, and the risk of new collision cases such as being pushed or crushed**,
we decided for **drawer definitions kept in `Level.drawers`, separate from `Level.platforms`, with their moving state in `Game.drawers`. They move only horizontally at a constant speed, follow exactly the R3 one-way rules, and carry Albert only while he stands on them**,
and neglected **vertical or other moving platforms, side pushing or crushing, treats on drawers, and storing drawers among the cabinets** (`spec.md` §9.1 out of scope; §9.2 data decision),
to achieve **unchanged R1–R14 behaviour and simple, deterministic drawer tests**,
accepting **that the game code has to handle two kinds of platforms, and that Albert doesn't keep the drawer's speed when he jumps**.
