"""R24 — Treats are spread across the whole level."""

from conftest import can_reach


def default_level():
    from albert.level import build_level

    return build_level()


def cabinet_under(level, treat):
    for p in level.platforms:
        if treat.y + treat.height == p.y and p.x <= treat.x and treat.x + treat.width <= p.x + p.width:
            return p
    return None


def side_cabinets(level):
    return [p for p in level.platforms if not any(p is s for s in level.route)]


def test_r24_default_level_has_twelve_treats():
    assert len(default_level().treats) == 12


def test_r24_treats_per_section_are_2_3_3_4():
    level = default_level()
    sections = [cabinet_under(level, t).section for t in level.treats]
    assert [sections.count(s) for s in (1, 2, 3, 4)] == [2, 3, 3, 4]


def test_r24_side_cabinets_each_hold_a_treat():
    level = default_level()
    sides = side_cabinets(level)
    assert sides, "the level has off-route side cabinets"
    holders = [cabinet_under(level, t) for t in level.treats]
    for p in sides:
        assert any(p is h for h in holders), f"side cabinet at ({p.x}, {p.y}) has no treat"


def test_r24_side_cabinets_can_be_reached_from_the_route_and_left_again():
    level = default_level()
    route_cabinets = [s for s in level.route if s in level.platforms]
    for p in side_cabinets(level):
        assert any(can_reach(r, p) for r in route_cabinets), f"can't reach side cabinet at ({p.x}, {p.y})"
        assert any(can_reach(p, r) for r in route_cabinets), f"stuck on side cabinet at ({p.x}, {p.y})"


def test_r24_hud_starts_at_zero_of_twelve(default_game):
    from albert.game import hud_text

    assert hud_text(default_game) == "0/12"
