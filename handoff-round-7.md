# Handoff — Round 7: Title menu and controls screen (R47–R53)

> **Reconstructed after development.** This handoff was written on 2026-11-22, after all seven rounds were finished, as final-project documentation. No handoff file existed at the end of Round 7. It is based only on what the repository records: commit `31cc09b` (plus the README-only commit `e53d4e6`), `spec.md` section 13, the code and the tests at that commit. It does not claim to be a contemporaneous record.

## Round summary
- **Commits:**
  - `31cc09b` "Add Round 7 title menu and controls screen (R47–R53)", 2026-11-22;
  - `e53d4e6` "Update README for the finished game (Rounds 1–7)", 2026-11-22.
- **Feature:**
  - a title menu with START, CONTROLS and QUIT, shown at startup over the animated kitchen;
  - a controls screen;
  - Esc during a game, or M on the win/lose screen, returns to the menu;
  - Esc on the menu quits.
- **Requirements:** R47–R53 (`problem.md` "Round 7 requirements"; acceptance criteria in `spec.md` §13.3).
- **Workflow note:** the R47–R53 requirements (`spec.md` §13), the tests and the implementation were committed together in `31cc09b`. There is no separate earlier requirements commit for this round.

## What changed
- `albert/menu.py` (new, pure):
  - `Keys`, `Screen`, `App` and `OPTIONS`, plus every menu string;
  - `App` reacts only to key presses (held now, not held on the previous update);
  - `App` owns the current `Game`, and a backdrop `Game` that is never updated but whose `ticks` animate the menu.
- `albert/__main__.py`: `read_inputs` maps keys to `Keys`, and `run()` drives and returns an `App`. Esc is no longer handled by the event loop.
- `albert/render.py`, `albert/sprites.py`: `draw_app`, the menu and controls panels, full A–Z font glyphs, and the overlay hint `R RESTART   M MENU`.
- `spec.md` §13 added, and §4.2 revised; `CLAUDE.md` updated. `README.md` was updated for the finished game in `e53d4e6`.

## Tests
- New: `test_menu_start.py` (R47), `test_menu_navigation.py` (R48), `test_menu_actions.py` (R49), `test_controls_screen.py` (R50), `test_return_to_menu.py` (R51), `test_menu_screen.py` (R52).
- Changed:
  - `test_runs_locally.py`: R8 revised as R53, with the headless run going through the menu.
  - `test_art_style.py`: menu render and font checks for R52.
- 394 test functions in `tests/` at this commit. `pytest` reports 577 tests after parametrisation, all passing.

## Earlier requirements revised (by ID)
- **R8 (revised, as R53):** the game still runs locally with `python -m albert`, but it starts on the title menu, and `run()` returns the `App`.
- **Round 1 controls (`spec.md` §4.2):** Esc no longer quits outright. M is added on the win/lose screen.
- **R6:** the restart keys are unchanged. Only the overlay hint text changed.
- `Game` and R1–R46 are otherwise unchanged.

## Decisions
- `docs/decisions/0008-pure-menu-app-separate-from-game.md`

## Notes for any later round
- `spec.md` §13.1 leaves pause, settings, level select, sound and mouse input out of scope.
