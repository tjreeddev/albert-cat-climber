"""R40 — Hazards follow a deterministic, freezable gameplay clock."""

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
START = (40, FLOOR[1] - config.PLAYER_HEIGHT)


def hazard(**kw):
    from albert.level import Hazard

    args = dict(kind="vent", x=150, top=500, section=1, idle=10, warning=5, active=5)
    args.update(kw)
    return Hazard(**args)


def lose(game, run_frames):
    from albert.game import GameState

    game.player.y = game.level.world_height + 1
    game.player.on_ground = False
    run_frames(game, 1)
    assert game.state == GameState.LOST


def test_r40_hazard_clock_starts_at_zero(default_game):
    assert default_game.hazard_ticks == 0
    assert default_game.knockback_ticks == 0
    assert default_game.invulnerable_ticks == 0


def test_r40_hazard_clock_counts_playing_updates(default_game, run_frames):
    for n in range(1, 6):
        run_frames(default_game, 1)
        assert default_game.hazard_ticks == n


def test_r40_hazard_clock_freezes_when_lost(default_game, run_frames):
    lose(default_game, run_frames)
    frozen = default_game.hazard_ticks
    run_frames(default_game, 30)
    assert default_game.hazard_ticks == frozen


def test_r40_hazard_clock_freezes_when_won(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=(100, 400), add_decoy_goal=False)
    run_frames(game, 120)
    assert game.state == GameState.WON
    frozen = game.hazard_ticks
    run_frames(game, 30)
    assert game.hazard_ticks == frozen


def test_r40_restart_resets_the_hazard_clock(default_game, run_frames):
    run_frames(default_game, 20)
    lose(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert default_game.hazard_ticks == 0


@pytest.mark.parametrize(
    "t, phase, expected",
    [(0, 0, "idle"), (9, 0, "idle"), (10, 0, "warning"), (14, 0, "warning"), (15, 0, "active"),
     (19, 0, "active"), (20, 0, "idle"), (0, 12, "warning"), (0, 16, "active"), (45, 0, "idle")],
)
def test_r40_phase_of_follows_the_formula(t, phase, expected):
    from albert.hazards import phase_of

    assert phase_of(hazard(phase=phase), t) == expected


def test_r40_phase_loops_with_the_cycle_and_phase_shifts_it():
    from albert.hazards import phase_of

    h, shifted = hazard(), hazard(phase=7)
    for t in range(200):
        assert phase_of(h, t) == phase_of(h, t + 20)
        assert phase_of(shifted, t) == phase_of(h, t + 7)


def _hazard_state(game):
    from albert.hazards import phase_of

    p = game.player
    return (
        game.hazard_ticks,
        [phase_of(h, game.hazard_ticks) for h in game.level.hazards],
        game.knockback_ticks,
        game.knockback_dir,
        game.invulnerable_ticks,
        (p.x, p.y, p.vx, p.vy, p.on_ground),
    )


def _vent_level(make_game):
    # An always-active vent right of the start, so walking right gets hit.
    vent = dict(kind="vent", x=100, top=500, section=1, idle=30, warning=10, active=20)
    return make_game([FLOOR], start=START, hazards=[vent])


def test_r40_same_inputs_give_the_same_hazard_state(make_game, run_frames):
    a, b = _vent_level(make_game), _vent_level(make_game)
    script = [dict(right=True)] * 40 + [dict(left=True, jump=True)] * 10 + [dict(right=True)] * 60
    for keys in script * 2:
        run_frames(a, 1, **keys)
        run_frames(b, 1, **keys)
        assert _hazard_state(a) == _hazard_state(b)


def test_r40_hazards_ignore_the_visual_clock(make_game, run_frames):
    a, b = _vent_level(make_game), _vent_level(make_game)
    script = [dict(right=True)] * 40 + [dict()] * 40 + [dict(right=True)] * 60
    for n, keys in enumerate(script):
        b.ticks = 7919 * (n + 3)  # scramble the visual-only animation clock
        run_frames(a, 1, **keys)
        run_frames(b, 1, **keys)
        assert _hazard_state(a) == _hazard_state(b)
