"""R26 — Earlier rules are unchanged by the bigger level."""

import pytest

from albert import config


def test_r26_physics_constants_keep_their_round_1_values():
    assert config.MOVE_SPEED == 100.0
    assert config.GRAVITY == 900.0
    assert config.JUMP_VELOCITY == 320.0
    assert config.MAX_FALL_SPEED == 400.0
    assert (config.PLAYER_WIDTH, config.PLAYER_HEIGHT) == (16, 14)


def test_r26_landing_on_the_goal_wins(default_game, run_frames):
    from albert.game import GameState

    goal = default_game.level.goal_platform
    p = default_game.player
    p.x, p.y = goal.x + goal.width / 2 - p.width / 2, goal.y - p.height - 5
    p.on_ground = False
    run_frames(default_game, 60)
    assert default_game.state == GameState.WON


def test_r26_falling_from_a_higher_section_onto_a_lower_cabinet_is_not_a_loss(default_game, run_frames):
    from albert.game import GameState

    counter = default_game.level.route[0]
    p = default_game.player
    p.x, p.y = counter.x + counter.width / 2 - p.width / 2, counter.y - 300
    p.on_ground = False
    run_frames(default_game, 120)
    assert default_game.state == GameState.PLAYING
    assert p.on_ground
    assert p.y + p.height == pytest.approx(counter.y)


def test_r26_falling_out_of_the_bottom_of_the_world_loses(default_game, run_frames):
    from albert.game import GameState

    level = default_game.level
    p = default_game.player
    p.x, p.y = level.world_width - p.width, level.world_height - 120  # nothing below the bottom-right corner
    p.on_ground = False
    run_frames(default_game, 120)
    assert default_game.state == GameState.LOST


def snapshot(game):
    p = game.player
    drawers = [(d.x, d.direction) for d in game.drawers]
    return (p.x, p.y, p.vx, p.vy, p.on_ground, game.camera_x, game.camera_y, game.treats_collected, drawers)


def test_r26_restart_after_winning_resets_albert_camera_treats_and_drawers(default_game, run_frames):
    from albert.game import GameState

    initial = snapshot(default_game)
    run_frames(default_game, 200)  # drawers move
    for t in default_game.level.treats[:4]:
        p = default_game.player
        p.x, p.y, p.vx, p.vy = t.x, t.y + t.height - p.height, 0, 0
        run_frames(default_game, 1)
    goal = default_game.level.goal_platform
    p = default_game.player
    p.x, p.y = goal.x + goal.width / 2 - p.width / 2, goal.y - p.height - 5
    p.on_ground = False
    run_frames(default_game, 60)
    assert default_game.state == GameState.WON
    assert snapshot(default_game) != initial
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert snapshot(default_game) == initial
