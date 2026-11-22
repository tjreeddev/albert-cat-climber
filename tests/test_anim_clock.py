"""R27 — Animation is driven by a deterministic update clock."""

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
START = (100, FLOOR[1] - config.PLAYER_HEIGHT)


def lose(game, run_frames):
    from albert.game import GameState

    game.player.y = game.level.world_height + 1
    game.player.on_ground = False
    run_frames(game, 1)
    assert game.state == GameState.LOST


def test_r27_ticks_start_at_zero(default_game):
    assert default_game.ticks == 0


def test_r27_ticks_go_up_by_one_per_update_while_playing(default_game, run_frames):
    for n in range(1, 6):
        run_frames(default_game, 1, right=True)
        assert default_game.ticks == n


def test_r27_ticks_keep_counting_when_lost(default_game, run_frames):
    lose(default_game, run_frames)
    before = default_game.ticks
    run_frames(default_game, 10)
    assert default_game.ticks == before + 10


def test_r27_ticks_keep_counting_when_won(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=(100, 400), add_decoy_goal=False)
    run_frames(game, 120)
    assert game.state == GameState.WON
    before = game.ticks
    run_frames(game, 10)
    assert game.ticks == before + 10


def test_r27_restart_sets_ticks_to_zero(default_game, run_frames):
    lose(default_game, run_frames)
    run_frames(default_game, 5)
    run_frames(default_game, 1, restart=True)
    assert default_game.ticks == 0
    default_game.restart()
    assert default_game.ticks == 0


@pytest.mark.parametrize(
    "ticks, frame_ticks, frame_count, phase, expected",
    [
        (0, 10, 4, 0, 0),
        (9, 10, 4, 0, 0),
        (10, 10, 4, 0, 1),
        (39, 10, 4, 0, 3),
        (40, 10, 4, 0, 0),
        (0, 10, 4, 15, 1),
        (29, 30, 2, 0, 0),
        (30, 30, 2, 0, 1),
        (60, 30, 2, 0, 0),
    ],
)
def test_r27_anim_frame_formula(ticks, frame_ticks, frame_count, phase, expected):
    from albert.effects import anim_frame

    assert anim_frame(ticks, frame_ticks, frame_count, phase) == expected
    assert anim_frame(ticks, frame_ticks, frame_count, phase) == ((ticks + phase) // frame_ticks) % frame_count


def test_r27_anim_frame_loops_with_period_frame_ticks_times_count():
    from albert.effects import anim_frame

    for t in range(200):
        assert anim_frame(t, 8, 4) == anim_frame(t + 32, 8, 4)


def test_r27_anim_frame_phase_shifts_the_loop():
    from albert.effects import anim_frame

    for t in range(100):
        assert anim_frame(t, 10, 4, phase=7) == anim_frame(t + 7, 10, 4)
    assert anim_frame(0, 10, 4) == 0  # phase defaults to 0


def _effects_snapshot(game):
    from albert.effects import decoration_frame

    frames = [decoration_frame(d, game.ticks) for d in game.level.decorations]
    particles = [(p.kind, p.x, p.y, p.vx, p.vy, p.life) for p in game.particles]
    return game.ticks, frames, particles


def test_r27_same_inputs_give_the_same_animation_and_particles(run_frames):
    from albert.game import Game

    a, b = Game(), Game()
    script = [dict(right=True)] * 30 + [dict(right=True, jump=True)] * 10 + [dict()] * 40 + [dict(left=True)] * 20
    for keys in script * 3:
        run_frames(a, 1, **keys)
        run_frames(b, 1, **keys)
        assert _effects_snapshot(a) == _effects_snapshot(b)
