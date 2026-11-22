# 0008 — A pure `menu.App` wraps `Game` without changing it

- **Round:** 7 (R47–R53)
- **Status:** Accepted. Still in effect. It revised R8 (tested as R53).
- **Record type:** Retrospective. Reconstructed on 2026-11-22 from the repository; not written during Round 7.
- **Evidence:** `spec.md` §13.1 (scope, approved revisions) and §13.2 (Presses, Update, Start gate, Backdrop); `albert/menu.py`; `albert/__main__.py` (`read_inputs`, `run`); `tests/test_menu_*.py`, `tests/test_return_to_menu.py` and `tests/test_runs_locally.py`; commit `31cc09b`.

## Y-statement

In the context of **adding a title menu and controls screen in front of the game (Round 7)**,
facing **the need to keep `Game` and R1–R46 unchanged, test menus without a window, and stop the key that picks START from also jumping or restarting**,
we decided for **a pure `menu.App` that owns the current `Game` (created fresh on START and discarded when leaving) and a backdrop `Game` that is never updated but whose ticks animate the menu. The app reacts only to key presses (held now, not held on the previous update), and a start gate sends empty inputs until all keys are released**,
and neglected **pause, settings, options, level select, mouse input and transitions** (`spec.md` §13.1 out of scope), and **putting menu state inside `Game`**,
to achieve **a menu that tests can drive through plain `Keys` data, while `Game` keeps behaving exactly like `Game()` (R47, R49)**,
accepting **that Esc no longer quits outright, which revises the Round 1 controls, and that the R8 entry-point test had to be revised (as R53)**.
