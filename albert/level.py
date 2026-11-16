"""The cabinet tower level. Pure Python: must not import pygame."""

from dataclasses import dataclass

from albert import config


@dataclass(eq=False)
class Platform:
    """A cabinet. Its top surface is at `y`; Albert lands on it from above."""

    x: float
    y: float
    width: float
    height: float


@dataclass
class Level:
    platforms: list
    world_width: int
    world_height: int
    start: tuple  # (x, y) top-left of Albert at the start

    @property
    def goal_platform(self):
        """R5: the highest cabinet (smallest y) is the goal."""
        return min(self.platforms, key=lambda p: p.y)


# (x, y, width, height), bottom to top. Each cabinet is one jump from the one
# below it. Difficulty comes from the layout, not the physics: narrow 32 px
# cabinets, rises of 44-48 px (max jump ~57 px), side gaps of 28-34 px, and the
# route switches direction twice, so jumps must be aimed and timed.
_TOWER = [
    (16, 524, 80, 16),  # starting counter
    (124, 480, 32, 16),  # climb right...
    (188, 434, 32, 16),
    (252, 390, 48, 16),  # ...to the right wall
    (186, 342, 32, 16),  # turn back left
    (124, 298, 32, 16),
    (60, 252, 32, 16),
    (0, 208, 32, 16),  # left wall
    (64, 160, 32, 16),  # turn back right
    (128, 116, 32, 16),
    (194, 70, 32, 16),
    (258, 26, 40, 16),  # goal: the highest cabinet
]

WORLD_WIDTH = config.INTERNAL_WIDTH
WORLD_HEIGHT = 540


def build_level():
    platforms = [Platform(*spec) for spec in _TOWER]
    counter = platforms[0]
    start = (32, counter.y - config.PLAYER_HEIGHT)
    return Level(platforms=platforms, world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT, start=start)
