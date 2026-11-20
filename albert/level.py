"""The cabinet tower level. Pure Python: must not import pygame."""

from dataclasses import dataclass, field

from albert import config


@dataclass(eq=False)
class Platform:
    """A cabinet. Its top surface is at `y`; Albert lands on it from above."""

    x: float
    y: float
    width: float
    height: float


@dataclass(eq=False)
class Treat:
    """A cat treat (R9). Its position is fixed; the game tracks collection."""

    x: float
    y: float
    width: float = config.TREAT_SIZE
    height: float = config.TREAT_SIZE


@dataclass
class Level:
    platforms: list
    world_width: int
    world_height: int
    start: tuple  # (x, y) top-left of Albert at the start
    treats: list = field(default_factory=list)  # R9 (Round 2)

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

# R9: treats as (cabinet index in _TOWER, x). Each rests on its cabinet's top.
# Never on the counter (0) or the goal (11); two sit near a cabinet edge.
_TREATS = [
    (2, 200),  # centred
    (3, 290),  # far right edge of the right-wall cabinet
    (5, 136),  # centred
    (7, 2),  # far left edge of the left-wall cabinet
    (9, 140),  # centred
]

WORLD_WIDTH = config.INTERNAL_WIDTH
WORLD_HEIGHT = 540


def build_level():
    platforms = [Platform(*spec) for spec in _TOWER]
    counter = platforms[0]
    start = (32, counter.y - config.PLAYER_HEIGHT)
    treats = [Treat(x, platforms[i].y - config.TREAT_SIZE) for i, x in _TREATS]
    return Level(
        platforms=platforms, world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT, start=start, treats=treats
    )
