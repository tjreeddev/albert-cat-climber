"""R46 — The route stays beatable, and earlier rules are unchanged.

Crossing test (spec.md R46): with only one hazard in the default level, Albert
stands on the previous route stop (at its edge nearest the hazard's cabinet, or
centred on a drawer). Drawer neighbours wait at their end nearest that cabinet,
moving away from it. The hazard clock is set so the next update is t = 0. He
waits w0 updates, jumps to the hazard's cabinet holding that direction until he
lands, walks toward the next stop for w1 updates, then jumps to it holding that
direction until he lands.
"""

import pytest

from albert import config
from albert.level import Drawer, build_level
from albert.physics import is_standing_on

DT = 1 / config.FPS
CROSSING_WAITS = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0), 4: (0, 0), 5: (0, 0), 6: (50, 12), 7: (0, 0)}  # H1-H8


def centre(stop):
    if isinstance(stop, Drawer):
        return (stop.min_x + stop.max_x + stop.width) / 2
    return stop.x + stop.width / 2


def cabinet_index(level, h):
    surface = h.floor if h.kind == "drip" else h.top
    for i, s in enumerate(level.route):
        if not isinstance(s, Drawer) and s.y == surface and s.x <= h.x < s.x + s.width:
            return i
    raise AssertionError(f"no route cabinet for {h}")


def live(game, stop):
    if isinstance(stop, Drawer):
        return game.drawers[next(i for i, d in enumerate(game.level.drawers) if d is stop)]
    return stop


def cross(index, cycle_number):
    """Run the R46 crossing for hazard `index`. Returns (updates taken, hit?, finished?)."""
    from albert.game import Game, GameState, Inputs

    level = build_level()
    h = level.hazards[index]
    level.hazards = [h]
    game = Game(level=level)
    i = cabinet_index(level, h)
    prev, cab, nxt = level.route[i - 1], level.route[i], level.route[i + 1]

    for stop in (prev, nxt):
        if isinstance(stop, Drawer):
            d = live(game, stop)
            d.x = stop.max_x if centre(cab) > centre(stop) else stop.min_x
            d.direction = -1 if d.x == stop.max_x else 1

    p = game.player
    on = live(game, prev)
    toward_cab = 1 if centre(cab) > centre(prev) else -1
    toward_next = 1 if centre(nxt) > centre(cab) else -1
    if isinstance(prev, Drawer):
        p.x = on.x + (on.width - p.width) / 2
    else:
        p.x = on.x + on.width - p.width if toward_cab > 0 else on.x
    p.y, p.vx, p.vy, p.on_ground = on.y - p.height, 0, 0, True

    cycle = h.idle + h.warning + h.active
    game.hazard_ticks = (-h.phase - 1) % cycle + cycle_number * cycle  # next update: t == 0

    updates, hit = 0, False

    def step(direction=0, jump=False):
        nonlocal updates, hit
        game.update(Inputs(left=direction < 0, right=direction > 0, jump=jump), DT)
        updates += 1
        hit = hit or game.invulnerable_ticks > 0

    w0, w1 = CROSSING_WAITS[index]
    for _ in range(w0):
        step()
    step(toward_cab, jump=True)
    for _ in range(150):
        if p.on_ground:
            break
        step(toward_cab)
    on_cab = p.on_ground and is_standing_on(p, cab)
    for _ in range(w1):
        step(toward_next)
    step(toward_next, jump=True)
    for _ in range(150):
        if p.on_ground:
            break
        step(toward_next)
    finished = on_cab and p.on_ground and is_standing_on(p, live(game, nxt)) and game.state == GameState.PLAYING
    return updates, hit, finished


def test_r46_every_hazard_has_a_safe_run_of_at_least_75_updates():
    for h in build_level().hazards:
        assert h.idle + h.warning >= 75, h


@pytest.mark.parametrize("index", range(8))
def test_r46_each_hazard_can_be_crossed_in_its_safe_window(index):
    results = [cross(index, k) for k in range(3)]
    updates, hit, finished = results[0]
    assert finished, f"H{index + 1}: crossing did not reach the next stop"
    assert not hit, f"H{index + 1}: Albert was hit during the crossing"
    assert results == [results[0]] * 3, f"H{index + 1}: crossing differs between cycles {results}"


def test_r46_physics_constants_are_unchanged():
    assert (config.MOVE_SPEED, config.GRAVITY, config.JUMP_VELOCITY, config.MAX_FALL_SPEED) == (100.0, 900.0, 320.0, 400.0)


def test_r46_landing_on_the_goal_still_wins_and_falling_out_still_loses(default_game, run_frames):
    from albert.game import GameState

    goal = default_game.level.goal_platform
    p = default_game.player
    p.x, p.y, p.on_ground = goal.x + goal.width / 2 - p.width / 2, goal.y - p.height - 5, False
    run_frames(default_game, 60)
    assert default_game.state == GameState.WON
    default_game.restart()
    p = default_game.player
    p.y, p.on_ground = default_game.level.world_height + 1, False
    run_frames(default_game, 1)
    assert default_game.state == GameState.LOST


def test_r46_the_final_jump_to_the_goal_is_hazard_free():
    level = build_level()
    before_goal = level.route[-2]
    for h in level.hazards:
        assert cabinet_index(level, h) != len(level.route) - 2, f"{h} sits on {before_goal}"
