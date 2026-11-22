"""R34 — Scenery fills a large part of the screen everywhere on the route."""

import pytest

from albert import config
from albert.level import Drawer, build_level

SCREEN_W, SCREEN_H = config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT


@pytest.fixture(scope="module")
def level():
    return build_level()


def stop_view(level, stop):
    """The camera view (x, y, w, h) with Albert standing centred on `stop` (R22 rule).
    A drawer counts at the middle of its path."""
    if isinstance(stop, Drawer):
        centre_x = (stop.min_x + stop.max_x + stop.width) / 2
    else:
        centre_x = stop.x + stop.width / 2
    centre_y = stop.y - config.PLAYER_HEIGHT / 2
    x = min(max(centre_x - SCREEN_W / 2, 0), level.world_width - SCREEN_W)
    y = min(max(centre_y - SCREEN_H / 2, 0), level.world_height - SCREEN_H)
    return (x, y, SCREEN_W, SCREEN_H)


def overlap_area(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0, min(ay + ah, by + bh) - max(ay, by))


def coverage(level, view):
    """Share of the view covered by windows and tiles (pictures and plants don't count).
    Scenery items never overlap each other (R33), so their areas simply add up."""
    big = [s for s in level.scenery if s.kind in ("window", "tiles")]
    return sum(overlap_area(view, (s.x, s.y, s.width, s.height)) for s in big) / (SCREEN_W * SCREEN_H)


def test_r34_route_has_stops_to_check(level):
    assert len(level.route) > 40


def test_r34_windows_and_tiles_cover_a_fifth_of_every_route_stop_view(level):
    low = []
    for i, stop in enumerate(level.route):
        c = coverage(level, stop_view(level, stop))
        if c < 0.20:
            low.append((i, round(c, 3)))
    assert not low, f"route stops with less than 20% windows and tiles: {low}"


@pytest.mark.parametrize("section", [1, 2, 3, 4])
def test_r34_half_of_each_sections_views_show_its_window(level, section):
    windows = [s for s in level.scenery if s.kind == "window" and s.section == section]
    stops = [s for s in level.route if s.section == section]
    seeing = sum(
        1
        for stop in stops
        if any(overlap_area(stop_view(level, stop), (w.x, w.y, w.width, w.height)) > 0 for w in windows)
    )
    assert windows
    assert seeing * 2 >= len(stops), f"only {seeing} of {len(stops)} views show a section {section} window"
