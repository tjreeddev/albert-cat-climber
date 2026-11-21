"""R15 — The level has two moving drawers."""

from albert import config


def default_level():
    from albert.level import build_level

    return build_level()


def path_rect(d):
    """The area a drawer sweeps: (x, y, width, height)."""
    return (d.min_x, d.y, d.max_x + d.width - d.min_x, d.height)


def overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def test_r15_default_level_has_two_drawers():
    assert len(default_level().drawers) == 2


def test_r15_drawers_are_drawer_size():
    for d in default_level().drawers:
        assert (d.width, d.height) == (config.DRAWER_WIDTH, config.DRAWER_HEIGHT)


def test_r15_drawer_paths_are_inside_the_world():
    level = default_level()
    for d in level.drawers:
        x, y, w, h = path_rect(d)
        assert d.min_x < d.max_x
        assert 0 <= x and x + w <= level.world_width
        assert 0 <= y and y + h <= level.world_height


def test_r15_drawers_start_inside_their_path_moving_one_way():
    for d in default_level().drawers:
        assert d.min_x <= d.start_x <= d.max_x
        assert d.start_direction in (-1, 1)
        assert d.speed > 0


def test_r15_drawers_are_below_the_goal_and_above_the_counter():
    level = default_level()
    counter = max(level.platforms, key=lambda p: p.y)
    for d in level.drawers:
        assert level.goal_platform.y < d.y < counter.y


def test_r15_drawer_paths_do_not_overlap_cabinets():
    level = default_level()
    for d in level.drawers:
        for p in level.platforms:
            assert not overlaps(path_rect(d), (p.x, p.y, p.width, p.height)), (
                f"drawer at y={d.y} overlaps cabinet at ({p.x}, {p.y})"
            )


def test_r15_drawers_are_not_cabinets():
    """Drawers live in Level.drawers, so the goal and cabinet checks only see cabinets."""
    level = default_level()
    for d in level.drawers:
        assert d not in level.platforms
        assert level.goal_platform is not d


def test_r15_game_has_moving_state_for_each_drawer(default_game):
    assert len(default_game.drawers) == len(default_game.level.drawers)
    for state, d in zip(default_game.drawers, default_game.level.drawers):
        assert (state.x, state.y, state.width, state.height) == (d.start_x, d.y, d.width, d.height)
        assert state.direction == d.start_direction


def test_r15_custom_levels_have_no_drawers_by_default(make_game):
    game = make_game([(0, 500, 320, 16)], start=(100, 486))
    assert game.level.drawers == []
    assert game.drawers == []
