# Problem

I want to make a platforming game based on my black cat, Albert. The game will have him climb on cabinets in my home. I want the game to turn into a climbing challenge where the player tries to reach the top without falling.

## Initial requirements

R1. The player controls the cat and can move left and right

R2. Albert can jump and is affected by gravity

R3. Albert can land on cabinet platforms and use them to climb upward

R4. If Albert falls below the playable area, the player loses.

R5. The player wins by reaching the highest cabinet platform.

R6. After winning or losing, the player can restart the game.

R7. The game uses a 16 bit style pixel art appearance

R8. The game runs on the users own computer

---

> **Note on Rounds 2–7 (added 2026-11-22, after development).**
> During development, the Round 2–7 requirements were written only in `spec.md` (sections 8–13). They were committed together with each round's implementation and tests, in commits `c1502be` (Round 2), `050b176` (Round 3), `83587e7` (Round 4), `021d722` (Round 5), `c542338` (Round 6) and `31cc09b` (Round 7). `problem.md` was not updated at the time.
> The sections below were reconstructed afterwards from `spec.md`, the code and the tests, as final-project documentation. The requirement IDs and their meanings match `spec.md` and the test names exactly. No requirement here is new. The detailed acceptance criteria remain in `spec.md`.

## Round 2 requirements

Feature: optional cat treats (`spec.md` section 8). R1–R8 are unchanged.

R9. Cat treats are placed on selected cabinets: the level has 5 treats, each resting on top of a cabinet, never on the starting counter or the goal cabinet, and at most one per cabinet. *(Count revised in Round 4.)*

R10. Touching a treat collects it for the rest of the run, on a cabinet or in mid-air. A collected treat disappears, and a treat can't be collected twice in one run.

R11. The game tracks how many treats were collected this run, out of the level's fixed total.

R12. The HUD shows collected and total treats (for example `2/5`) in the top-left corner, fixed to the screen, in every game state.

R13. Restarting after a win or a loss restores every treat and resets the count to 0.

R14. Treats are optional: the player can win with none, some or all of them, and collecting every treat doesn't win by itself.

## Round 3 requirements

Feature: horizontally moving cabinet drawers (`spec.md` section 9).

R15. The level has two moving drawers, placed inside the world, between the starting counter and the goal, and never overlapping a cabinet. *(Count revised in Round 4.)*

R16. Drawers move horizontally back and forth at a constant speed between two fixed ends, deterministically. They move only while playing and freeze on the win and lose screens.

R17. Drawers are one-way platforms, following the same landing rules as cabinets in R3, and they never push Albert sideways.

R18. Albert rides a moving drawer while standing on it. Left/right input adds to that movement, but he is not carried in the air.

R19. The route requires timed drawer jumps: the goal can't be reached without the drawers, and each drawer is within jump reach of the cabinet below it at one end of its path only. *(Revised in Round 4.)*

R20. Drawers don't change the win, lose, treat or restart rules. Landing on a drawer never wins, and restarting resets the drawers.

Changes to earlier requirements in Round 3:
- **R3:** the requirement text is unchanged. Two Round 1 route cabinets were replaced by drawers, so the R3 climbability check now counts each drawer as a route stop anywhere along its path (`tests/test_platforms.py`, changed in `050b176`).

## Round 4 requirements

Feature: a large kitchen level with a camera that scrolls on both axes (`spec.md` section 10).

R21. The level is a large kitchen spanning several screens in both directions (960×1080, at least 3 screens wide and 6 tall). Albert starts on the lowest cabinet, and the goal is the single highest cabinet.

R22. The camera scrolls horizontally and vertically: it centres Albert, never shows anything outside the world, and keeps the HUD fixed to the screen.

R23. The route runs through four progressively harder sections. Each stop can be reached from the previous one, and gaps, rises, cabinet width and drawer count and speed get harder from section to section.

R24. Treats are spread across the whole level: 12 treats, 2, 3, 3 and 4 in sections 1–4, including treats on side cabinets that need a detour.

R25. Drawers recur throughout the level: 6 drawers, 0, 1, 2 and 3 in sections 1–4, with speeds that never decrease, including one jump from a drawer straight onto another drawer.

R26. Earlier rules are unchanged by the bigger level: the same physics, landing on the goal wins, falling below the world loses, and restart resets Albert, the camera, the treats and the drawers.

Changes to earlier requirements in Round 4 (`spec.md` section 10.1; tests changed in `83587e7`):
- **R3 (revised):** climbability is now checked along `Level.route` in order, with a jump reach that depends on the rise, instead of sorting cabinets by height. The Round 1 spec limits "a tower 2–3 screens tall with 10–12 cabinets" were **removed**, along with their tests `test_r3_default_level_has_10_to_12_cabinets` and `test_r3_default_level_is_two_to_three_screens_tall`.
- **R9 (revised):** the default level has **12** treats instead of 5 (see R24). All other R9 placement rules still apply. The test `test_r9_default_level_has_five_treats` became `test_r9_default_level_has_twelve_treats`.
- **R15 (revised):** the default level has **6** drawers instead of 2 (see R25). All other R15 rules still apply. The test `test_r15_default_level_has_two_drawers` became `test_r15_default_level_has_six_drawers`.
- **R19 (revised):** "the cabinet below/above a drawer" now means the drawer's previous/next stop on `Level.route`, and every drawer is checked (`tests/test_drawer_route.py`).

## Round 5 requirements

Feature: visual-only kitchen animation, effects and background scenery (`spec.md` section 11, including the section 11.5 expansion). These requirements must not change gameplay.

R27. Animation is driven by a deterministic update clock (counting updates, not wall-clock time) that runs in every game state and resets on restart.

R28. The kitchen has fixed decorations in every section: 8 non-solid mugs, pots and appliance clocks, 2 per section.

R29. Decorations loop through their animation frames, including on the win and lose screens.

R30. Landing on a cabinet or drawer makes a small dust puff.

R31. Collecting a treat makes a sparkle.

R32. Effects are visual only and reset on restart: with or without decorations and particles, gameplay is identical.

R33. The kitchen has large background scenery: windows, tiled panels, framed pictures and hanging plants, with 1–2 windows per section.

R34. Scenery fills a large part of the screen everywhere on the route: at least 20% of every route-stop view is windows or tiles.

R35. The view outside the windows changes as Albert climbs: garden, then town, then city, then sky.

R36. The outside view is always gently moving, for example drifting clouds, puffing chimney smoke, blinking city lights and gliding birds.

R37. Curtains and hanging plants sway.

R38. Scenery is visual only and stays behind gameplay objects. It never looks like a platform and never changes gameplay.

No earlier requirement was revised in Round 5.

## Round 6 requirements

Feature: timed, static kitchen hazards (`spec.md` section 12).

R39. The kitchen has 8 placed hazards (4 steam vents, 2 hot burners and 2 dripping taps; 1, 2, 2 and 3 in sections 1–4) on route cabinets, never on the goal, the stop before it, the starting counter or a drawer.

R40. Hazards follow a deterministic gameplay clock that advances only while playing, freezes on the win and lose screens, and resets on restart.

R41. Steam vents: an active jet hits Albert when he is in it, standing, jumping or falling.

R42. Hot burners: an active burner hits Albert only when he is standing on its strip.

R43. Dripping taps: a drop forms during the warning and can't hit then. The falling drop hits Albert if it touches him.

R44. A hit causes knockback, a 0.3-second left/right control override and 1 second of invulnerability. A hit never causes an instant loss.

R45. Hazards are clearly telegraphed by a warning phase of at least 0.75 s before they become active, and they look different from the decorations.

R46. The route stays beatable with fair timing, and the earlier rules are unchanged.

Changes to earlier requirements in Round 6 (`spec.md` section 12.1):
- **R1 and R2 (qualified):** for 18 updates (0.3 s) after a hazard hit, left/right input is replaced by the knockback direction and jump is ignored (R44). At all other times, R1 and R2 are unchanged.
- **R4 is unchanged:** losing still happens only by falling below the world. A knockback can cause such a fall, but a hazard never causes a loss directly.

## Round 7 requirements

Feature: a title menu and controls screen (`spec.md` section 13).

R47. The game starts on a title menu with START selected. The game itself still begins in the playing state once started.

R48. The menu is navigated with single key presses (up/down, wrapping). Holding a key acts only once.

R49. The menu options START a fresh game, show the CONTROLS screen, or QUIT. Pressing Esc on the menu also quits.

R50. The controls screen lists the keys, and Esc or Enter goes back to the menu.

R51. Leaving a game returns to the menu: Esc at any time, or M on the win/lose screen. R/Enter still restarts on the win/lose screen.

R52. The menu screens are drawn over the animated kitchen.

R53. The entry point drives the app: `python -m albert` opens the title menu, maps keys to menu and game input, and a scripted run through the menu into a game runs without errors.

Changes to earlier requirements in Round 7 (`spec.md` section 13.1; tests changed in `31cc09b`):
- **R8 (revised, as R53):** the game still runs locally with `python -m albert`, but it now opens on the title menu. The headless run in `tests/test_runs_locally.py` goes through the menu, and `run()` returns the app instead of a game.
- **Esc no longer quits the game outright** (a change to the Round 1 controls in `spec.md` section 4.2): during a game it returns to the menu, and only Esc on the menu quits. Closing the window still quits at once.
- **R6:** the restart keys are unchanged. The win/lose overlay's hint becomes `R RESTART   M MENU`.
