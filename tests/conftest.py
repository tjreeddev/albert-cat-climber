"""Shared pytest setup for Albert Cat Climber.

Runs Pygame headlessly and provides small helpers for building custom test
levels and stepping the game.

Coordinate convention (from spec.md): world pixels, y grows downward,
positions are top-left corners. Platform(x, y, width, height) has its top
surface at `y`.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math  # noqa: E402

import pytest  # noqa: E402

from albert import config  # noqa: E402

# --- Jump reach (spec.md 10.2), shared by the layout tests ---
# Import with `from conftest import ...`.

MAX_JUMP_HEIGHT = config.JUMP_VELOCITY**2 / (2 * config.GRAVITY)
RISE_LIMIT = MAX_JUMP_HEIGHT * 0.9  # safety margin for climbing checks
CLIMB_MARGIN = 0.85  # "can reach" checks
FULL_MARGIN = 1.0  # "can't reach" checks


def jump_reach(rise, margin=CLIMB_MARGIN):
    """Horizontal distance Albert covers in a jump that ends `rise` px higher
    (negative for a drop), or -1 if the rise is out of jump height."""
    v, g = config.JUMP_VELOCITY, config.GRAVITY
    if rise > MAX_JUMP_HEIGHT:
        return -1
    return margin * config.MOVE_SPEED * (v + math.sqrt(v * v - 2 * g * rise)) / g


def stop_rect(stop):
    """(x, y, width, height) of a cabinet, or of a drawer's whole path."""
    from albert.level import Drawer

    if isinstance(stop, Drawer):
        return (stop.min_x, stop.y, stop.max_x + stop.width - stop.min_x, stop.height)
    return (stop.x, stop.y, stop.width, stop.height)


def side_gap(a, b):
    ax, _, aw, _ = stop_rect(a)
    bx, _, bw, _ = stop_rect(b)
    return max(0, bx - (ax + aw), ax - (bx + bw))


def can_reach(a, b, margin=CLIMB_MARGIN):
    """One jump from standing on `a` can land on `b` (drawers anywhere along their path)."""
    rise = a.y - b.y
    rise_ok = rise <= (RISE_LIMIT if margin < 1 else MAX_JUMP_HEIGHT)
    return rise_ok and side_gap(a, b) <= jump_reach(rise, margin)


def reachable_from(start, stops, margin):
    """Every stop reachable from `start` by a chain of jumps (drops allowed)."""
    seen, todo = [start], [start]
    while todo:
        a = todo.pop()
        for b in stops:
            if not any(b is s for s in seen) and can_reach(a, b, margin):
                seen.append(b)
                todo.append(b)
    return seen

# A small, high platform placed in the top-left corner of custom test levels so
# that it is the goal (highest) platform and the platforms under test are not.
DECOY_GOAL = (0, 0, 8, 4)


@pytest.fixture
def make_game():
    """Build a Game on a custom Level.

    platforms: list of (x, y, width, height) tuples
    start:     (x, y) top-left of Albert at the start
    add_decoy_goal: add DECOY_GOAL so none of `platforms` is the goal
    treats:    optional list of (x, y) top-left treat positions (Round 2)
    drawers:   optional list of dicts of level.Drawer keyword arguments (Round 3)
    """

    def _make(
        platforms, start, world_width=320, world_height=1000, add_decoy_goal=True, treats=(), drawers=()
    ):
        from albert.game import Game
        from albert.level import Level, Platform

        extra = {}
        if treats:
            from albert.level import Treat

            extra["treats"] = [Treat(*t) for t in treats]
        if drawers:
            from albert.level import Drawer

            extra["drawers"] = [Drawer(**d) for d in drawers]
        specs = list(platforms) + ([DECOY_GOAL] if add_decoy_goal else [])
        level = Level(
            platforms=[Platform(*p) for p in specs],
            world_width=world_width,
            world_height=world_height,
            start=start,
            **extra,
        )
        return Game(level=level)

    return _make


@pytest.fixture
def default_game():
    """A Game using the real default level."""
    from albert.game import Game

    return Game()


@pytest.fixture
def run_frames():
    """Advance a game by `frames` fixed-timestep updates with the given keys held.

    Keys are Inputs fields: left, right, jump, restart.
    """

    def _run(game, frames=1, **keys):
        from albert import config
        from albert.game import Inputs

        inputs = Inputs(**keys)
        for _ in range(frames):
            game.update(inputs, 1 / config.FPS)

    return _run
