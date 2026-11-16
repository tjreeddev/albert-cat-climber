"""R1 — The player controls the cat and can move left and right."""

import pygame
import pytest

from albert import config

FLOOR = (0, 500, 320, 16)


def standing_game(make_game, x=150):
    return make_game([FLOOR], start=(x, FLOOR[1] - config.PLAYER_HEIGHT))


def dt():
    return 1 / config.FPS


def test_r1_holding_right_moves_albert_right(make_game, run_frames):
    game = standing_game(make_game)
    x0 = game.player.x
    run_frames(game, 1, right=True)
    assert game.player.x == pytest.approx(x0 + config.MOVE_SPEED * dt())


def test_r1_holding_left_moves_albert_left(make_game, run_frames):
    game = standing_game(make_game)
    x0 = game.player.x
    run_frames(game, 1, left=True)
    assert game.player.x == pytest.approx(x0 - config.MOVE_SPEED * dt())


def test_r1_no_input_means_no_horizontal_drift(make_game, run_frames):
    game = standing_game(make_game)
    x0 = game.player.x
    run_frames(game, 30)
    assert game.player.x == pytest.approx(x0)
    assert game.player.vx == 0


def test_r1_releasing_the_key_stops_albert_immediately(make_game, run_frames):
    game = standing_game(make_game)
    run_frames(game, 10, right=True)
    x_after_moving = game.player.x
    run_frames(game, 1)
    assert game.player.x == pytest.approx(x_after_moving)
    assert game.player.vx == 0


def test_r1_albert_cannot_leave_left_edge(make_game, run_frames):
    game = standing_game(make_game, x=2)
    run_frames(game, 60, left=True)
    assert game.player.x == pytest.approx(0)


def test_r1_albert_cannot_leave_right_edge(make_game, run_frames):
    game = standing_game(make_game, x=320 - config.PLAYER_WIDTH - 2)
    run_frames(game, 60, right=True)
    assert game.player.x + game.player.width == pytest.approx(320)


@pytest.mark.parametrize("key", [pygame.K_LEFT, pygame.K_a])
def test_r1_left_keys_map_to_left(key):
    from albert.__main__ import read_inputs

    inputs = read_inputs({key})
    assert inputs.left and not inputs.right


@pytest.mark.parametrize("key", [pygame.K_RIGHT, pygame.K_d])
def test_r1_right_keys_map_to_right(key):
    from albert.__main__ import read_inputs

    inputs = read_inputs({key})
    assert inputs.right and not inputs.left
