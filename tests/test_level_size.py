"""R21 — The level is a large kitchen spanning several screens in both directions."""

import pytest

from albert import config
from conftest import stop_rect


def default_level():
    from albert.level import build_level

    return build_level()


def test_r21_world_is_960_by_1080():
    level = default_level()
    assert (level.world_width, level.world_height) == (960, 1080)


def test_r21_world_is_at_least_three_screens_wide_and_six_tall():
    level = default_level()
    assert level.world_width >= 3 * config.INTERNAL_WIDTH
    assert level.world_height >= 6 * config.INTERNAL_HEIGHT


def test_r21_albert_starts_on_the_lowest_cabinet_in_the_left_third():
    level = default_level()
    lowest = max(level.platforms, key=lambda p: p.y)
    x, y = level.start
    assert y + config.PLAYER_HEIGHT == pytest.approx(lowest.y)
    assert lowest.x <= x and x + config.PLAYER_WIDTH <= lowest.x + lowest.width
    assert x + config.PLAYER_WIDTH <= level.world_width / 3


def test_r21_goal_is_the_unique_highest_cabinet():
    level = default_level()
    top = min(p.y for p in level.platforms)
    assert level.goal_platform.y == top
    assert sum(1 for p in level.platforms if p.y == top) == 1


def test_r21_everything_is_inside_the_world():
    level = default_level()
    things = list(level.platforms) + list(level.drawers)
    rects = [stop_rect(s) for s in things] + [(t.x, t.y, t.width, t.height) for t in level.treats]
    for x, y, w, h in rects:
        assert 0 <= x and x + w <= level.world_width, (x, y)
        assert 0 <= y and y + h <= level.world_height, (x, y)
