"""R3 — Albert can land on cabinet platforms and use them to climb upward."""

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)


def max_jump_height():
    return config.JUMP_VELOCITY**2 / (2 * config.GRAVITY)


def run_until_grounded(game, run_frames, max_frames=600):
    for _ in range(max_frames):
        run_frames(game, 1)
        if game.player.on_ground:
            return
    pytest.fail("Albert never landed")


def test_r3_falling_onto_a_cabinet_lands_on_its_top(make_game, run_frames):
    cabinet = (100, 300, 100, 16)
    game = make_game([cabinet], start=(130, 200))
    run_until_grounded(game, run_frames)
    assert game.player.y + game.player.height == pytest.approx(cabinet[1])
    assert game.player.vy == 0


def test_r3_fast_fall_does_not_pass_through_a_cabinet(make_game, run_frames):
    cabinet = (100, 4000, 100, 8)
    game = make_game([cabinet], start=(130, 100), world_height=5000)
    run_until_grounded(game, run_frames, max_frames=3000)
    assert game.player.y + game.player.height == pytest.approx(cabinet[1])


def test_r3_albert_stays_standing_on_a_cabinet(make_game, run_frames):
    game = make_game([FLOOR], start=(150, FLOOR[1] - config.PLAYER_HEIGHT))
    y0 = game.player.y
    run_frames(game, 120)
    assert game.player.on_ground
    assert game.player.y == pytest.approx(y0)


def test_r3_jump_height_allows_climbing_past_albert_height():
    assert max_jump_height() > config.PLAYER_HEIGHT + 16


def test_r3_albert_jumps_up_through_a_cabinet_and_lands_on_it(make_game, run_frames):
    # A cabinet just above Albert's head: one-way platforms let him jump
    # through it from below and land on top.
    cabinet_top = FLOOR[1] - config.PLAYER_HEIGHT - 10
    cabinet = (100, cabinet_top, 100, 8)
    game = make_game([FLOOR, cabinet], start=(130, FLOOR[1] - config.PLAYER_HEIGHT))

    run_frames(game, 1, jump=True)
    highest_feet = game.player.y + game.player.height
    for _ in range(180):
        run_frames(game, 1)
        highest_feet = min(highest_feet, game.player.y + game.player.height)

    assert highest_feet < cabinet_top, "Albert was blocked from below"
    assert game.player.on_ground
    assert game.player.y + game.player.height == pytest.approx(cabinet_top)


def test_r3_walking_off_an_edge_starts_a_fall(make_game, run_frames):
    cabinet = (100, 300, 60, 16)
    game = make_game([cabinet], start=(140, 300 - config.PLAYER_HEIGHT))
    y0 = game.player.y
    run_frames(game, 60, right=True)
    assert not game.player.on_ground
    assert game.player.y > y0


# --- Default level layout (R3 climbability). Round 4 (spec.md 10.1) replaced the
# 10-12 cabinet / 2-3 screen limits of section 4.1 with R21. ---


def test_r3_default_level_cabinets_are_inside_the_world():
    from albert.level import build_level

    level = build_level()
    for p in level.platforms:
        assert 0 <= p.x and p.x + p.width <= level.world_width
        assert 0 <= p.y and p.y + p.height <= level.world_height


def test_r3_default_level_starts_standing_on_the_lowest_cabinet():
    from albert.level import build_level

    level = build_level()
    lowest = max(level.platforms, key=lambda p: p.y)
    x, y = level.start
    assert y + config.PLAYER_HEIGHT == pytest.approx(lowest.y)
    assert lowest.x <= x and x + config.PLAYER_WIDTH <= lowest.x + lowest.width


def test_r3_default_level_is_climbable():
    """Each stop on the route is reachable with one jump from the previous one.

    Round 3: each moving drawer counts as a route stop anywhere along its path.
    Round 4: the route is `Level.route` in order (it runs sideways as well as up),
    and reach depends on the rise (spec.md 10.2).
    """
    from albert.level import build_level
    from conftest import RISE_LIMIT, jump_reach, side_gap

    route = build_level().route
    assert len(route) >= 2
    for a, b in zip(route, route[1:]):
        rise = a.y - b.y
        assert rise <= RISE_LIMIT, f"stop at y={b.y} is too high above y={a.y}"
        assert side_gap(a, b) <= jump_reach(rise), f"stop at y={b.y} is too far sideways from y={a.y}"
