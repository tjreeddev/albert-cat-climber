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

import pytest  # noqa: E402

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
    """A Game using the real Round 1 level."""
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
