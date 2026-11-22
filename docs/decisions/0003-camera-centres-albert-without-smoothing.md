# 0003 — The camera centres Albert on both axes, with no smoothing

- **Round:** 4 (R21–R26)
- **Status:** Accepted. Still in effect.
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 4.
- **Evidence:** `spec.md` §10.1 (out of scope) and §10.2 (Camera, Rendering); `albert/game.py` (`camera_x`, `camera_y`); `tests/test_camera.py`; commit `83587e7`.

## Y-statement

In the context of **replacing the single vertical tower with a 960×1080 kitchen that is wider and taller than the 320×180 screen (Round 4)**,
facing **the need for the view to follow Albert sideways as well as up, while staying deterministic and testable without a window**,
we decided for **`Game.camera_x` and `Game.camera_y`, which centre Albert's hitbox and are clamped to the world on each axis. They are set on `restart()` and after every `update()`, and every world object is drawn offset by both while the HUD stays fixed to the screen**,
and neglected **camera smoothing, dead-zones and a minimap** (`spec.md` §10.1 out of scope),
to achieve **a camera that is a pure function of Albert's position, so tests can check it exactly (R22) and restart restores it exactly**,
accepting **a camera that moves rigidly with every one of Albert's movements, rather than the softer feel smoothing would give**.
