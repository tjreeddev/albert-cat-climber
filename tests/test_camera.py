"""R22 — The camera scrolls horizontally and vertically."""

import pytest

from albert import config

SCREEN_W, SCREEN_H = config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT
WORLD = dict(world_width=960, world_height=1080)
FLOOR = (0, 500, 960, 16)
ON_FLOOR = FLOOR[1] - config.PLAYER_HEIGHT


def centred(game):
    p = game.player
    return (p.x + p.width / 2 - SCREEN_W / 2, p.y + p.height / 2 - SCREEN_H / 2)


def assert_in_world(game):
    assert 0 <= game.camera_x <= game.level.world_width - SCREEN_W
    assert 0 <= game.camera_y <= game.level.world_height - SCREEN_H


def test_r22_camera_centres_albert_away_from_the_edges(make_game):
    game = make_game([FLOOR], start=(472, ON_FLOOR), **WORLD)
    assert (game.camera_x, game.camera_y) == pytest.approx(centred(game))


def test_r22_camera_is_clamped_at_the_top_left(make_game):
    game = make_game([(0, 30, 40, 8)], start=(0, 30 - config.PLAYER_HEIGHT), **WORLD)
    assert (game.camera_x, game.camera_y) == (0, 0)


def test_r22_camera_is_clamped_at_the_bottom_right(make_game):
    game = make_game([(900, 1060, 60, 16)], start=(944, 1060 - config.PLAYER_HEIGHT), **WORLD)
    assert (game.camera_x, game.camera_y) == (960 - SCREEN_W, 1080 - SCREEN_H)


def test_r22_camera_follows_albert_horizontally(make_game, run_frames):
    game = make_game([FLOOR], start=(400, ON_FLOOR), **WORLD)
    x0, y0 = game.camera_x, game.camera_y
    run_frames(game, 30, right=True)
    assert game.camera_x == pytest.approx(x0 + (game.player.x - 400))
    assert game.camera_x > x0
    assert game.camera_y == pytest.approx(y0)


def test_r22_camera_follows_albert_vertically(make_game, run_frames):
    game = make_game([FLOOR], start=(472, 300), **WORLD)
    y0 = game.camera_y
    run_frames(game, 10)
    assert game.camera_y > y0
    assert game.camera_y == pytest.approx(centred(game)[1])


def test_r22_camera_stays_inside_the_world_while_playing(default_game, run_frames):
    for frame in range(600):
        run_frames(default_game, 1, right=(frame // 90) % 2 == 0, left=(frame // 90) % 2 == 1, jump=frame % 40 == 0)
        assert_in_world(default_game)


def test_r22_camera_is_valid_after_losing(default_game, run_frames):
    from albert.game import GameState

    default_game.player.y = default_game.level.world_height + 1
    default_game.player.on_ground = False
    run_frames(default_game, 1)
    assert default_game.state == GameState.LOST
    assert_in_world(default_game)
    assert default_game.camera_y == default_game.level.world_height - SCREEN_H


def test_r22_camera_is_valid_after_winning(default_game, run_frames):
    from albert.game import GameState

    goal = default_game.level.goal_platform
    p = default_game.player
    p.x, p.y = goal.x + goal.width / 2 - p.width / 2, goal.y - p.height - 5
    p.on_ground = False
    run_frames(default_game, 60)
    assert default_game.state == GameState.WON
    assert_in_world(default_game)
    cx, cy = centred(default_game)
    assert default_game.camera_x == pytest.approx(min(max(cx, 0), 960 - SCREEN_W))
    assert default_game.camera_y == pytest.approx(min(max(cy, 0), 1080 - SCREEN_H))


def test_r22_restart_restores_both_camera_axes(default_game, run_frames):
    start = (default_game.camera_x, default_game.camera_y)
    p = default_game.player
    p.x, p.y = 600, 400
    run_frames(default_game, 1)
    assert (default_game.camera_x, default_game.camera_y) != start
    default_game.restart()
    assert (default_game.camera_x, default_game.camera_y) == start
