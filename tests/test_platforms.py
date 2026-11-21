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


# --- Default level layout (spec.md 4.1 and R3 climbability) ---


def test_r3_default_level_has_10_to_12_cabinets():
    from albert.level import build_level

    assert 10 <= len(build_level().platforms) <= 12


def test_r3_default_level_is_two_to_three_screens_tall():
    from albert.level import build_level

    assert 360 <= build_level().world_height <= 540


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
    """Each cabinet, bottom to top, is reachable with one jump from the one below.

    Round 3: each moving drawer counts as a route stop anywhere along its path.
    """
    from albert.level import Platform, build_level

    level = build_level()
    stops = list(level.platforms) + [
        Platform(d.min_x, d.y, d.max_x + d.width - d.min_x, d.height) for d in level.drawers
    ]
    route = sorted(stops, key=lambda p: p.y, reverse=True)
    rise_limit = max_jump_height() * 0.9  # keep a safety margin
    reach_limit = config.MOVE_SPEED * (config.JUMP_VELOCITY / config.GRAVITY)

    for lower, upper in zip(route, route[1:]):
        rise = lower.y - upper.y
        gap = max(0, upper.x - (lower.x + lower.width), lower.x - (upper.x + upper.width))
        assert rise <= rise_limit, f"cabinet at y={upper.y} is too high above y={lower.y}"
        assert gap <= reach_limit, f"cabinet at y={upper.y} is too far sideways from y={lower.y}"
