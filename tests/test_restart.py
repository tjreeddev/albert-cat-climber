"""R6 — After winning or losing, the player can restart the game."""

import pygame
import pytest


def snapshot(game):
    p = game.player
    return (p.x, p.y, p.vx, p.vy, p.on_ground, game.camera_y)


def lose(game, run_frames):
    from albert.game import GameState

    game.player.y = game.level.world_height + 1
    game.player.on_ground = False
    run_frames(game, 1)
    assert game.state == GameState.LOST


def win(game, run_frames):
    from albert.game import GameState

    goal = game.level.goal_platform
    p = game.player
    p.x = goal.x + goal.width / 2 - p.width / 2
    p.y = goal.y - p.height - 5
    p.vx = p.vy = 0
    p.on_ground = False
    run_frames(game, 60)
    assert game.state == GameState.WON


def test_r6_restart_after_losing_restores_initial_state(default_game, run_frames):
    from albert.game import GameState

    initial = snapshot(default_game)
    lose(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert snapshot(default_game) == initial


def test_r6_restart_after_winning_restores_initial_state(default_game, run_frames):
    from albert.game import GameState

    initial = snapshot(default_game)
    win(default_game, run_frames)
    assert default_game.camera_y != initial[-1], "camera should have followed Albert up"
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert snapshot(default_game) == initial


def test_r6_initial_state_is_standing_still_on_the_start(default_game):
    x, y = default_game.level.start
    p = default_game.player
    assert (p.x, p.y) == (x, y)
    assert p.vx == 0 and p.vy == 0
    assert p.on_ground


def test_r6_restart_key_does_nothing_while_playing(default_game, run_frames):
    from albert.game import GameState

    run_frames(default_game, 20, right=True)
    run_frames(default_game, 1)  # settle: no keys held, so vx is 0 like in the restart frame
    moved = snapshot(default_game)
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert snapshot(default_game) == moved


def test_r6_game_is_playable_again_after_restart(default_game, run_frames):
    lose(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    x0 = default_game.player.x
    run_frames(default_game, 5, right=True)
    assert default_game.player.x > x0


def test_r6_restart_method_resets_the_game(default_game, run_frames):
    from albert.game import GameState

    initial = snapshot(default_game)
    lose(default_game, run_frames)
    default_game.restart()
    assert default_game.state == GameState.PLAYING
    assert snapshot(default_game) == initial


@pytest.mark.parametrize("key", [pygame.K_r, pygame.K_RETURN])
def test_r6_restart_keys_map_to_restart(key):
    from albert.__main__ import read_inputs

    assert read_inputs({key}).restart
