"""R2 — Albert can jump and is affected by gravity."""

import pygame
import pytest

from albert import config

FLOOR = (0, 500, 320, 16)


def dt():
    return 1 / config.FPS


def standing_game(make_game, x=150):
    return make_game([FLOOR], start=(x, FLOOR[1] - config.PLAYER_HEIGHT))


def airborne_game(make_game, world_height=1000):
    # Only a tiny ledge far to the left; Albert starts in open air.
    return make_game([(0, 900, 10, 8)], start=(200, 100), world_height=world_height)


def test_r2_physics_constants_are_positive():
    assert config.GRAVITY > 0
    assert config.JUMP_VELOCITY > 0
    assert config.MAX_FALL_SPEED > 0
    assert config.MOVE_SPEED > 0


def test_r2_albert_starts_standing(make_game):
    game = standing_game(make_game)
    assert game.player.on_ground


def test_r2_jump_while_standing_gives_upward_velocity(make_game, run_frames):
    game = standing_game(make_game)
    y0 = game.player.y
    run_frames(game, 1, jump=True)
    assert game.player.vy < 0
    assert game.player.vy == pytest.approx(-config.JUMP_VELOCITY, abs=config.GRAVITY * dt() + 1e-9)
    assert not game.player.on_ground
    assert game.player.y < y0


def test_r2_jump_in_mid_air_does_nothing(make_game, run_frames):
    game = standing_game(make_game)
    run_frames(game, 1, jump=True)
    run_frames(game, 5)
    vy_before = game.player.vy
    run_frames(game, 1, jump=True)
    assert game.player.vy == pytest.approx(vy_before + config.GRAVITY * dt())


def test_r2_jump_while_falling_does_nothing(make_game, run_frames):
    game = airborne_game(make_game)
    run_frames(game, 1, jump=True)
    assert game.player.vy > 0


def test_r2_gravity_increases_downward_speed_each_update(make_game, run_frames):
    game = airborne_game(make_game)
    speeds = []
    for _ in range(10):
        run_frames(game, 1)
        speeds.append(game.player.vy)
    for before, after in zip(speeds, speeds[1:]):
        assert after == pytest.approx(min(before + config.GRAVITY * dt(), config.MAX_FALL_SPEED))
    assert speeds[-1] > speeds[0]


def test_r2_falling_speed_is_capped(make_game, run_frames):
    game = airborne_game(make_game, world_height=1_000_000)
    for _ in range(600):
        run_frames(game, 1)
        assert game.player.vy <= config.MAX_FALL_SPEED + 1e-9
    assert game.player.vy == pytest.approx(config.MAX_FALL_SPEED)


def test_r2_jump_arc_returns_albert_to_the_ground(make_game, run_frames):
    game = standing_game(make_game)
    y0 = game.player.y
    run_frames(game, 1, jump=True)
    run_frames(game, 180)
    assert game.player.on_ground
    assert game.player.y == pytest.approx(y0)


@pytest.mark.parametrize("key", [pygame.K_SPACE, pygame.K_UP, pygame.K_w])
def test_r2_jump_keys_map_to_jump(key):
    from albert.__main__ import read_inputs

    assert read_inputs({key}).jump
