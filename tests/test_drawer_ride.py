"""R18 — Albert rides a moving drawer."""

import pytest

from albert import config

SPEED = 40.0
Y = 300


def riding_game(make_game, start_x=150, direction=1, min_x=100, max_x=250, albert_offset=8):
    """Albert standing on a drawer that slides along [min_x, max_x]."""
    d = dict(min_x=min_x, max_x=max_x, y=Y, speed=SPEED, start_x=start_x, start_direction=direction)
    return make_game([], start=(start_x + albert_offset, Y - config.PLAYER_HEIGHT), drawers=[d])


def test_r18_standing_albert_is_carried_by_the_drawer(make_game, run_frames):
    game = riding_game(make_game)
    d = game.drawers[0]
    offset = game.player.x - d.x
    run_frames(game, 30)
    assert d.x == pytest.approx(150 + SPEED * 30 / config.FPS)
    assert game.player.x - d.x == pytest.approx(offset)
    assert game.player.on_ground
    assert game.player.y + game.player.height == pytest.approx(Y)


def test_r18_carry_works_in_both_directions(make_game, run_frames):
    game = riding_game(make_game, start_x=200, direction=-1)
    x0 = game.player.x
    run_frames(game, 30)
    assert game.player.x == pytest.approx(x0 - SPEED * 30 / config.FPS)


def test_r18_walking_input_adds_to_the_carry(make_game, run_frames):
    game = riding_game(make_game, albert_offset=0)
    x0 = game.player.x
    run_frames(game, 6, right=True)
    expected = x0 + (SPEED + config.MOVE_SPEED) * 6 / config.FPS
    assert game.player.x == pytest.approx(expected)
    assert game.player.on_ground


def test_r18_albert_is_not_carried_in_the_air(make_game, run_frames):
    # Albert falls past a moving drawer's height but never stands on it.
    d = dict(min_x=100, max_x=250, y=Y, speed=SPEED, start_x=150, start_direction=1)
    game = make_game([], start=(20, Y - 40), drawers=[d])
    x0 = game.player.x
    run_frames(game, 20)
    assert game.player.x == x0


def test_r18_jumping_off_does_not_keep_the_drawer_speed(make_game, run_frames):
    game = riding_game(make_game)
    run_frames(game, 1, jump=True)
    assert not game.player.on_ground
    x_after_jump = game.player.x
    run_frames(game, 10)
    assert not game.player.on_ground
    assert game.player.x == x_after_jump


def test_r18_albert_is_clamped_at_the_wall_while_riding(make_game, run_frames):
    game = riding_game(make_game, start_x=0, direction=-1, min_x=-40, max_x=40, albert_offset=0)
    for _ in range(60):
        run_frames(game, 1)
        assert game.player.x == 0
    assert not game.player.on_ground, "the drawer should have slid out from under him"
