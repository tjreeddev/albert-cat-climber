# 0004 — An explicit, ordered `Level.route` with sections 1–4

- **Round:** 4 (R21–R26)
- **Status:** Accepted. Still in effect. It revised how R3 and R19 are checked.
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 4.
- **Evidence:** `spec.md` §10.1 (revisions to earlier rounds) and §10.2 (Route, Sections, Difficulty, Jump reach); `albert/level.py` (`Level.route`, `section`); `tests/conftest.py` (reach helpers); `tests/test_level_route.py`; commit `83587e7`.

## Y-statement

In the context of **a level that zig-zags sideways across a large kitchen instead of going straight up (Round 4)**,
facing **the old R3 climbability check, which sorted cabinets by height and stopped making sense once the route ran sideways, and the need to prove the difficulty increases**,
we decided for **an explicit ordered `Level.route` from the counter to the goal, a `section` tag (1–4) on every cabinet and drawer, and a jump reach that depends on the rise. R3, R19 and R23 are checked along this route**,
and neglected **keeping the height-sorted climbability check and the "2–3 screens / 10–12 cabinets" limits** (removed by `spec.md` §10.1, along with their R3 tests),
to achieve **climbability and "each section is harder than the last" checks that are explicit and testable (R23)**,
accepting **that the route must be kept up to date by hand in `level.py`, and that R3, R9, R15 and R19 and their tests had to be revised**.
