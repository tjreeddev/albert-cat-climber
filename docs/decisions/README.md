# Decision records

These are architecture decision records in the **Y-statement** format:

> In the context of *‹use case›*, facing *‹concern›*, we decided for *‹option›* and neglected *‹other options›*, to achieve *‹quality›*, accepting *‹downside›*.

> **Retrospective records.** All of these records were reconstructed on 2026-11-22, after development finished, as final-project documentation. During development, the decisions themselves were recorded only in the "Decisions" and "Scope" tables of `spec.md` and in the code and tests. Each record cites that evidence. The "neglected" options are only those that `spec.md` explicitly puts out of scope or rejects. None of these records claims to have been written during its round.

| # | Round | Decision |
|---|---|---|
| [0001](0001-treats-are-a-count-not-a-score.md) | 2 | Treats are an optional count, not a score |
| [0002](0002-drawers-are-separate-one-way-platforms.md) | 3 | Drawers are separate, one-way, horizontal-only platforms |
| [0003](0003-camera-centres-albert-without-smoothing.md) | 4 | The camera centres Albert on both axes, with no smoothing |
| [0004](0004-explicit-ordered-route-with-sections.md) | 4 | An explicit, ordered `Level.route` with sections 1–4 |
| [0005](0005-tick-driven-deterministic-animation.md) | 5 | Animation driven by update ticks, with no randomness |
| [0006](0006-hazards-knock-back-instead-of-instant-loss.md) | 6 | Hazards cause knockback, not an instant loss |
| [0007](0007-separate-gameplay-hazard-clock.md) | 6 | A separate hazard clock that freezes in WON/LOST |
| [0008](0008-pure-menu-app-separate-from-game.md) | 7 | A pure `menu.App` wraps `Game` without changing it |
