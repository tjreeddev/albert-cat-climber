"""R39 — The kitchen has 8 placed hazards."""

import pytest

from albert import config
from albert.level import Drawer, build_level

# spec.md 12.3, in Level.hazards order:
# (kind, section, x, top, idle, warning, active, phase, floor, cabinet (x, y, w))
EXPECTED = [
    ("drip", 1, 442, 900, 87, 60, 33, 0, 970, (420, 970, 48)),
    ("vent", 2, 722, 768, 90, 45, 45, 0, None, (712, 768, 36)),
    ("vent", 2, 300, 656, 90, 45, 45, 90, None, (292, 656, 32)),
    ("burner", 3, 70, 520, 120, 60, 60, 0, None, (64, 520, 28)),
    ("vent", 3, 696, 370, 90, 45, 45, 45, None, (690, 370, 28)),
    ("vent", 4, 560, 140, 60, 45, 45, 30, None, (556, 140, 24)),
    ("drip", 4, 886, 156, 27, 60, 33, 0, 226, (872, 226, 24)),
    ("burner", 4, 254, 56, 80, 60, 60, 0, None, (246, 56, 24)),
]


@pytest.fixture(scope="module")
def level():
    return build_level()


def overlap_area(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0, min(ay + ah, by + bh) - max(ay, by))


def hazard_areas(h):
    """Every area a hazard occupies or can hit (spec.md 12.2)."""
    if h.kind == "vent":
        vw, vh = config.VENT_SIZE
        return [(h.x, h.top - vh, vw, vh), (h.x + 2, h.top - 56, 12, 56)]
    if h.kind == "burner":
        return [(h.x, h.top - 1, config.BURNER_WIDTH, 1)]
    dw, _ = config.DROP_SIZE
    return [(h.x - 2, h.top - 8, 8, 8), (h.x, h.top, dw, h.floor - h.top)]


def hazard_cabinet(level, h):
    """The static cabinet a hazard belongs to (for a drip: the one under it)."""
    surface = h.floor if h.kind == "drip" else h.top
    width = config.DROP_SIZE[0] if h.kind == "drip" else config.BURNER_WIDTH
    for p in level.platforms:
        if p.y == surface and p.x <= h.x and h.x + width <= p.x + p.width:
            return p
    return None


def test_r39_hazard_constants_match_the_spec():
    assert config.VENT_SIZE == (16, 8)
    assert config.JET_SIZE == (12, 56)
    assert config.BURNER_WIDTH == 16
    assert config.DROP_SIZE == (4, 6)
    assert config.DRIP_SPEED == 2


def test_r39_default_level_has_the_8_hazards_of_the_spec(level):
    actual = [(h.kind, h.section, h.x, h.top, h.idle, h.warning, h.active, h.phase, h.floor) for h in level.hazards]
    assert actual == [e[:9] for e in EXPECTED]


def test_r39_hazards_per_section_and_kind(level):
    per_section = [sum(1 for h in level.hazards if h.section == s) for s in (1, 2, 3, 4)]
    assert per_section == [1, 2, 2, 3]
    kinds = [h.kind for h in level.hazards]
    assert (kinds.count("vent"), kinds.count("burner"), kinds.count("drip")) == (4, 2, 2)


def test_r39_drip_active_time_lands_the_drop_on_the_floor(level):
    for h in level.hazards:
        if h.kind == "drip":
            assert h.active == (h.floor - config.DROP_SIZE[1] - h.top) // config.DRIP_SPEED + 1


@pytest.mark.parametrize("index", range(8))
def test_r39_each_hazard_sits_on_its_static_route_cabinet(level, index):
    h = level.hazards[index]
    cab = hazard_cabinet(level, h)
    assert cab is not None, h
    assert (cab.x, cab.y, cab.width) == EXPECTED[index][9]
    assert any(cab is s for s in level.route), "the cabinet must be on the route"
    assert cab.section == h.section


def test_r39_no_hazard_on_the_goal_the_stop_before_it_or_the_counter(level):
    goal, before_goal, counter = level.route[-1], level.route[-2], level.route[0]
    assert goal is level.goal_platform
    for h in level.hazards:
        cab = hazard_cabinet(level, h)
        assert cab is not goal and cab is not before_goal and cab is not counter, h


def test_r39_no_hazard_touches_a_drawer_path(level):
    for h in level.hazards:
        for d in level.drawers:
            path = (d.min_x, d.y, d.max_x + d.width - d.min_x, d.height)
            for area in hazard_areas(h):
                assert overlap_area(area, path) == 0, (h, d)


def test_r39_no_hazard_touches_a_treat_or_decoration(level):
    others = [(t.x, t.y, t.width, t.height) for t in level.treats]
    others += [(d.x, d.y, *config.DECORATION_SIZES[d.kind]) for d in level.decorations]
    for h in level.hazards:
        for area in hazard_areas(h):
            for other in others:
                assert overlap_area(area, other) == 0, (h, other)


def test_r39_hazards_are_inside_the_world(level):
    for h in level.hazards:
        for x, y, w, hh in hazard_areas(h):
            assert 0 <= x and x + w <= level.world_width
            assert 0 <= y and y + hh <= level.world_height


def test_r39_hazards_are_not_platforms(level):
    for h in level.hazards:
        assert all(h is not p for p in level.platforms)
    assert not any(isinstance(s, Drawer) for s in level.hazards)


def test_r39_playing_never_changes_the_hazards(default_game, run_frames):
    def snapshot():
        return [
            (h.kind, h.x, h.top, h.section, h.idle, h.warning, h.active, h.phase, h.floor)
            for h in default_game.level.hazards
        ]

    before = snapshot()
    run_frames(default_game, 200, right=True, jump=True)
    default_game.restart()
    assert snapshot() == before
