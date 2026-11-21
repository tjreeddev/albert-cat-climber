"""R19 — The route requires timed drawer jumps.

Round 4 (spec.md 10.1): a drawer's "cabinet below/above" is now its previous/next
stop on `Level.route`, every drawer is checked, and reach depends on the rise.
"""

from albert import config
from albert.physics import is_standing_on
from conftest import FULL_MARGIN, can_reach, reachable_from

SAMPLE_STEP = 4  # frames between sampled jump times


def default_level():
    from albert.level import build_level

    return build_level()


def is_drawer(stop):
    from albert.level import Drawer

    return isinstance(stop, Drawer)


def drawer_at(d, x):
    from albert.level import Platform

    return Platform(x, d.y, d.width, d.height)


def neighbours(level, d):
    """The previous and next stops on the route."""
    i = next(i for i, s in enumerate(level.route) if s is d)
    return level.route[i - 1], level.route[i + 1]


def span_centre(stop):
    if is_drawer(stop):
        return (stop.min_x + stop.max_x + stop.width) / 2
    return stop.x + stop.width / 2


def test_r19_cabinets_alone_cannot_be_climbed():
    level = default_level()
    reached = reachable_from(level.route[0], level.platforms, FULL_MARGIN)
    assert not any(p is level.goal_platform for p in reached)


def test_r19_cabinets_and_drawers_can_be_climbed():
    route = default_level().route
    assert all(can_reach(a, b) for a, b in zip(route, route[1:]))


def test_r19_each_drawer_is_in_reach_of_its_cabinet_neighbours_at_one_end_only():
    level = default_level()
    checked = 0
    for d in level.drawers:
        before, after = neighbours(level, d)
        ends = [drawer_at(d, x) for x in (d.min_x, d.max_x)]
        if not is_drawer(before):
            near = [can_reach(before, e) for e in ends]
            far = [can_reach(before, e, FULL_MARGIN) for e in ends]
            assert sorted(near) == [False, True] and near == far, f"drawer at y={d.y} from previous: {far}"
            checked += 1
        if not is_drawer(after):
            near = [can_reach(e, after) for e in ends]
            far = [can_reach(e, after, FULL_MARGIN) for e in ends]
            assert sorted(near) == [False, True] and near == far, f"drawer at y={d.y} to next: {far}"
            checked += 1
    assert checked >= len(level.drawers)


# --- Simulated timed jumps on the real level ---


def _inputs(direction, jump=False):
    from albert.game import Inputs

    return Inputs(left=direction < 0, right=direction > 0, jump=jump)


def live(game, stop):
    """The object Albert actually stands on: the moving state for a drawer."""
    if is_drawer(stop):
        return game.drawers[next(i for i, d in enumerate(game.level.drawers) if d is stop)]
    return stop


def cycle_frames(d):
    """Frames for one full back-and-forth of drawer `d`."""
    return int(2 * (d.max_x - d.min_x) / d.speed * config.FPS) + 1


def jump_between(i, j, wait_frames):
    """Stand on route stop i, wait, then jump towards stop j holding the direction.
    Returns True if Albert lands on stop j."""
    from albert.game import Game, Inputs

    game = Game()
    a, b = game.level.route[i], game.level.route[j]
    on, target = live(game, a), live(game, b)
    direction = 1 if span_centre(b) > span_centre(a) else -1
    p = game.player
    if is_drawer(a):
        p.x = on.x + (on.width - p.width) / 2
    else:
        p.x = on.x + on.width - p.width if direction > 0 else on.x
    p.y, p.vx, p.vy, p.on_ground = on.y - p.height, 0, 0, True

    for _ in range(wait_frames):
        game.update(Inputs(), 1 / config.FPS)
    assert is_standing_on(p, on), "Albert should still be standing before the jump"

    game.update(_inputs(direction, jump=True), 1 / config.FPS)
    for _ in range(150):
        if p.on_ground:
            break
        game.update(_inputs(direction), 1 / config.FPS)
    return p.on_ground and is_standing_on(p, target)


def drawer_indexes(level):
    return [i for i, s in enumerate(level.route) if is_drawer(s)]


def test_r19_jumping_onto_each_drawer_depends_on_timing():
    level = default_level()
    assert drawer_indexes(level)
    for i in drawer_indexes(level):
        d = level.route[i]
        results = {jump_between(i - 1, i, n) for n in range(0, cycle_frames(d), SAMPLE_STEP)}
        assert results == {True, False}, f"drawer at y={d.y}: timing made no difference ({results})"


def test_r19_jumping_from_each_drawer_to_the_next_stop_depends_on_timing():
    level = default_level()
    assert drawer_indexes(level)
    for i in drawer_indexes(level):
        d = level.route[i]
        results = {jump_between(i, i + 1, n) for n in range(0, cycle_frames(d), SAMPLE_STEP)}
        assert results == {True, False}, f"drawer at y={d.y}: timing made no difference ({results})"
