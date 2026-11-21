"""R9 — Cat treats are placed on selected cabinet platforms in the existing level."""

from albert import config


def default_level():
    from albert.level import build_level

    return build_level()


def cabinet_under(level, treat):
    """The cabinet whose top the treat rests on, within its width, or None."""
    for p in level.platforms:
        if treat.y + treat.height == p.y and p.x <= treat.x and treat.x + treat.width <= p.x + p.width:
            return p
    return None


def test_r9_default_level_has_twelve_treats():
    """Revised in Round 4 (spec.md 10.1): 5 treats became 12."""
    assert len(default_level().treats) == 12


def test_r9_treats_are_treat_size():
    for t in default_level().treats:
        assert (t.width, t.height) == (config.TREAT_SIZE, config.TREAT_SIZE)


def test_r9_each_treat_rests_on_top_of_a_cabinet():
    level = default_level()
    for t in level.treats:
        assert cabinet_under(level, t) is not None, f"treat at ({t.x}, {t.y}) is not resting on a cabinet"


def test_r9_no_treat_on_the_starting_counter_or_the_goal():
    level = default_level()
    counter = max(level.platforms, key=lambda p: p.y)
    for t in level.treats:
        cabinet = cabinet_under(level, t)
        assert cabinet is not counter, "treat on the starting counter"
        assert cabinet is not level.goal_platform, "treat on the goal cabinet"


def test_r9_at_most_one_treat_per_cabinet():
    level = default_level()
    cabinets = [id(cabinet_under(level, t)) for t in level.treats]
    assert len(set(cabinets)) == len(cabinets)


def test_r9_treats_are_inside_the_world():
    level = default_level()
    for t in level.treats:
        assert 0 <= t.x and t.x + t.width <= level.world_width
        assert 0 <= t.y and t.y + t.height <= level.world_height


def test_r9_custom_levels_have_no_treats_by_default(make_game):
    game = make_game([(0, 500, 320, 16)], start=(100, 486))
    assert game.level.treats == []
