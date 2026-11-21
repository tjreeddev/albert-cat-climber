"""R23 — The route runs through four progressively harder sections."""

from albert import config
from conftest import FULL_MARGIN, can_reach, reachable_from, side_gap


def default_level():
    from albert.level import build_level

    return build_level()


def is_drawer(stop):
    from albert.level import Drawer

    return isinstance(stop, Drawer)


def section_metrics(level, section):
    """Largest gap, largest rise, narrowest cabinet, drawer count and top drawer speed
    for the route stops in `section` (each jump counted in the section it lands in)."""
    route = level.route
    jumps = [(a, b) for a, b in zip(route, route[1:]) if b.section == section]
    stops = [s for s in route if s.section == section]
    cabinets = [s for s in stops if not is_drawer(s)]
    drawers = [s for s in stops if is_drawer(s)]
    return {
        "max_gap": max(side_gap(a, b) for a, b in jumps),
        "max_rise": max(a.y - b.y for a, b in jumps),
        "min_width": min(c.width for c in cabinets),
        "drawers": len(drawers),
        "top_speed": max((d.speed for d in drawers), default=0),
    }


def test_r23_route_starts_at_the_counter_and_ends_at_the_goal():
    level = default_level()
    counter = max(level.platforms, key=lambda p: p.y)
    assert level.route[0] is counter
    assert level.route[-1] is level.goal_platform
    x, y = level.start
    assert y + config.PLAYER_HEIGHT == counter.y


def test_r23_route_uses_the_level_cabinets_and_every_drawer():
    level = default_level()
    for stop in level.route:
        pool = level.drawers if is_drawer(stop) else level.platforms
        assert any(stop is s for s in pool)
    for d in level.drawers:
        assert any(d is s for s in level.route), "every drawer is on the route"


def test_r23_sections_run_one_to_four_in_order():
    sections = [s.section for s in default_level().route]
    assert sections == sorted(sections)
    assert sorted(set(sections)) == [1, 2, 3, 4]


def test_r23_each_route_stop_is_reachable_from_the_previous_one():
    route = default_level().route
    for i, (a, b) in enumerate(zip(route, route[1:])):
        assert can_reach(a, b), f"stop {i + 1} at ({b.y}) can't be reached from stop {i} at ({a.y})"


def test_r23_sections_never_get_easier():
    level = default_level()
    m = [section_metrics(level, s) for s in (1, 2, 3, 4)]
    for easier, harder in zip(m, m[1:]):
        assert harder["max_gap"] >= easier["max_gap"]
        assert harder["max_rise"] >= easier["max_rise"]
        assert harder["min_width"] <= easier["min_width"]
        assert harder["drawers"] >= easier["drawers"]
        assert harder["top_speed"] >= easier["top_speed"]


def test_r23_each_section_is_strictly_harder_on_some_measure():
    level = default_level()
    m = [section_metrics(level, s) for s in (1, 2, 3, 4)]
    for easier, harder in zip(m, m[1:]):
        assert (
            harder["max_gap"] > easier["max_gap"]
            or harder["max_rise"] > easier["max_rise"]
            or harder["min_width"] < easier["min_width"]
            or harder["drawers"] > easier["drawers"]
            or harder["top_speed"] > easier["top_speed"]
        ), f"{harder} is no harder than {easier}"


def test_r23_cabinets_alone_cannot_reach_the_goal():
    """Over all cabinets, drops allowed, full reach: no shortcut around the drawers."""
    level = default_level()
    counter = level.route[0]
    reached = reachable_from(counter, level.platforms, FULL_MARGIN)
    assert not any(p is level.goal_platform for p in reached)


def test_r23_cabinets_and_drawers_reach_the_goal():
    level = default_level()
    counter = level.route[0]
    reached = reachable_from(counter, list(level.platforms) + list(level.drawers), 0.85)
    assert any(p is level.goal_platform for p in reached)
