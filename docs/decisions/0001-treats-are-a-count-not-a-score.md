# 0001 — Treats are an optional count, not a score

- **Round:** 2 (R9–R14)
- **Status:** Accepted. Still in effect, with the count revised to 12 treats in Round 4 (R24).
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 2.
- **Evidence:** `spec.md` §8.1 and §8.2; `albert/game.py` (`treats_collected`, `hud_text`); `tests/test_treats_optional.py`; commit `c1502be`.

## Y-statement

In the context of **adding the first collectible to the climbing game (Round 2)**,
facing **the need to give players an optional extra goal without changing the R5 win rule or bringing in score features that are out of scope**,
we decided for **fixed cat treats whose only effect is a per-run `collected/total` count shown in the HUD; the count resets on restart and has no effect on winning**,
and neglected **points/score, high scores, timers, save data and bonuses for collecting every treat** (all explicitly out of scope in `spec.md` §8.1),
to achieve **a small, testable feature that keeps R1–R8 unchanged (R14: you can win with 0, some or all treats)**,
accepting **that collecting treats has no reward beyond the counter**.
