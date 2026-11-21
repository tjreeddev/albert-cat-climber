"""R25 — Drawers recur throughout the level."""

from albert import config


def default_level():
    from albert.level import build_level

    return build_level()


def is_drawer(stop):
    from albert.level import Drawer

    return isinstance(stop, Drawer)


def test_r25_default_level_has_six_drawers():
    assert len(default_level().drawers) == 6


def test_r25_drawers_per_section_are_0_1_2_3():
    sections = [d.section for d in default_level().drawers]
    assert [sections.count(s) for s in (1, 2, 3, 4)] == [0, 1, 2, 3]


def test_r25_drawer_speeds_never_drop_between_sections():
    drawers = default_level().drawers
    for d in drawers:
        assert 0 < d.speed < config.MOVE_SPEED
    for a in drawers:
        for b in drawers:
            if a.section < b.section:
                assert a.speed <= b.speed, f"S{b.section} drawer slower than an S{a.section} drawer"


def test_r25_section_four_has_a_drawer_to_drawer_hop():
    route = default_level().route
    hops = [(a, b) for a, b in zip(route, route[1:]) if is_drawer(a) and is_drawer(b)]
    assert any(b.section == 4 for _, b in hops)
