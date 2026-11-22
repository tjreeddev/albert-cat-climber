# 0005 — Animation driven by update ticks, with no randomness

- **Round:** 5 (R27–R38)
- **Status:** Accepted. Still in effect.
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 5.
- **Evidence:** `spec.md` §11.1 (out of scope), §11.2 (Animation clock, Frame helper, Particles) and §11.5.2 (Animation); `albert/effects.py` (`anim_frame`, `scroll_offset`, `scenery_anim`); `tests/test_anim_clock.py`, `tests/test_visual_only.py` and `tests/test_scenery_visual_only.py`; commit `021d722`.

## Y-statement

In the context of **adding looping decorations, particles and animated window scenery to a game whose rules are checked by automated tests (Round 5)**,
facing **the risk that animation using wall-clock time or randomness would make test runs differ, and could leak into gameplay**,
we decided for **one counter, `Game.ticks` (+1 every update, in every state, reset on restart), with every frame, scroll and particle calculated from it by pure helpers in `effects.py`. Gameplay never reads effect state**,
and neglected **random or physics-driven particles, wall-clock timing, parallax, screen shake and lighting or blending effects** (`spec.md` §11.1 and §11.5.1 out of scope),
to achieve **effects that are exactly reproducible (R27, R36) and provably visual only (R32 and R38 compare gameplay with and without effects)**,
accepting **repeating, mechanical-looking animation with no random variation**.
