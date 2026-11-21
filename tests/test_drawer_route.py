"""R19 — The route requires timed drawer jumps."""

from albert import config
from albert.physics import is_standing_on

RISE_LIMIT = config.JUMP_VELOCITY**2 / (2 * config.GRAVITY) * 0.9  # same margin as the R3 test
REACH_LIMIT = config.MOVE_SPEED * (config.JUMP_VELOCITY / config.GRAVITY)


def default_level():
    from albert.level import build_level

    return build_level()


def gap(a, b):
    return max(0, b.x - (a.x + a.width), a.x - (b.x + b.width))


def climbable(stops):
    route = sorted(stops, key=lambda p: p.y, reverse=True)
    return all(
        lower.y - upper.y <= RISE_LIMIT and gap(lower, upper) <= REACH_LIMIT
        for lower, upper in zip(route, route[1:])
    )


def path_stop(d):
    from albert.level import Platform

    return Platform(d.min_x, d.y, d.max_x + d.width - d.min_x, d.height)


def drawer_at(d, x):
    from albert.level import Platform

    return Platform(x, d.y, d.width, d.height)


def cabinet_below(level, d):
    return min((p for p in level.platforms if p.y > d.y), key=lambda p: p.y)


def cabinet_above(level, d):
    return max((p for p in level.platforms if p.y < d.y), key=lambda p: p.y)


def centre(x, width):
    return x + width / 2


def test_r19_cabinets_alone_cannot_be_climbed():
    assert not climbable(default_level().platforms)


def test_r19_cabinets_and_drawers_can_be_climbed():
    level = default_level()
    assert climbable(list(level.platforms) + [path_stop(d) for d in level.drawers])


def test_r19_each_drawer_is_in_reach_at_one_end_only():
    level = default_level()
    for d in level.drawers:
        below = cabinet_below(level, d)
        assert below.y - d.y <= RISE_LIMIT
        reach = [gap(below, drawer_at(d, x)) <= REACH_LIMIT for x in (d.min_x, d.max_x)]
        assert sorted(reach) == [False, True], f"drawer at y={d.y}: reach at its ends is {reach}"


# --- Simulated timed jumps on the real level ---

PERIOD = 240  # frames; longer than any default drawer's full back-and-forth cycle
SAMPLE_STEP = 4


def jump_and_land(game, direction, max_frames=150):
    """Jump while holding `direction` until Albert lands or the game ends."""
    from albert.game import GameState

    game.update(_inputs(direction, jump=True), 1 / config.FPS)
    for _ in range(max_frames):
        if game.player.on_ground or game.state != GameState.PLAYING:
            return
        game.update(_inputs(direction), 1 / config.FPS)


def _inputs(direction, jump=False):
    from albert.game import Inputs

    return Inputs(left=direction < 0, right=direction > 0, jump=jump)


def place_on(player, platform, x):
    player.x, player.y = x, platform.y - player.height
    player.vx = player.vy = 0
    player.on_ground = True


def wait(game, frames):
    from albert.game import Inputs

    for _ in range(frames):
        game.update(Inputs(), 1 / config.FPS)


def jump_onto_drawer(index, wait_frames):
    from albert.game import Game

    game = Game()
    spec = game.level.drawers[index]
    below = cabinet_below(game.level, spec)
    direction = 1 if centre(spec.min_x, spec.max_x + spec.width - spec.min_x) > centre(below.x, below.width) else -1
    edge = below.x + below.width - game.player.width if direction > 0 else below.x
    place_on(game.player, below, edge)
    wait(game, wait_frames)
    jump_and_land(game, direction)
    return game.player.on_ground and is_standing_on(game.player, game.drawers[index])


def jump_off_drawer(index, wait_frames):
    from albert.game import Game

    game = Game()
    spec, moving = game.level.drawers[index], game.drawers[index]
    above = cabinet_above(game.level, spec)
    direction = 1 if centre(above.x, above.width) > centre(spec.min_x, spec.max_x + spec.width - spec.min_x) else -1
    place_on(game.player, moving, moving.x + (moving.width - game.player.width) / 2)
    wait(game, wait_frames)
    assert is_standing_on(game.player, moving), "Albert should still be riding the drawer"
    jump_and_land(game, direction)
    return game.player.on_ground and is_standing_on(game.player, above)


def test_r19_jumping_onto_each_drawer_depends_on_timing():
    for index in range(2):
        results = {jump_onto_drawer(index, n) for n in range(0, PERIOD, SAMPLE_STEP)}
        assert results == {True, False}, f"drawer {index}: timing made no difference ({results})"


def test_r19_jumping_from_each_drawer_to_the_next_cabinet_depends_on_timing():
    for index in range(2):
        results = {jump_off_drawer(index, n) for n in range(0, PERIOD, SAMPLE_STEP)}
        assert results == {True, False}, f"drawer {index}: timing made no difference ({results})"
