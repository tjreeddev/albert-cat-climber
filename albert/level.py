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


@dataclass(frozen=True, eq=False)
class Drawer:
    """A moving drawer's fixed definition (R15). Its left edge slides between
    min_x and max_x at a fixed height; the game tracks where it is now."""

    min_x: float
    max_x: float
    y: float
    width: float = config.DRAWER_WIDTH
    height: float = config.DRAWER_HEIGHT
    speed: float = config.DRAWER_SPEED
    start_x: float = None  # defaults to min_x
    start_direction: int = 1  # 1 = right, -1 = left

    def __post_init__(self):
        if self.start_x is None:
            object.__setattr__(self, "start_x", self.min_x)


@dataclass
class Level:
    platforms: list
    world_width: int
    world_height: int
    start: tuple  # (x, y) top-left of Albert at the start
    treats: list = field(default_factory=list)  # R9 (Round 2)
    drawers: list = field(default_factory=list)  # R15 (Round 3)

    @property
    def goal_platform(self):
        """R5: the highest cabinet (smallest y) is the goal."""
        return min(self.platforms, key=lambda p: p.y)


# (x, y, width, height), bottom to top. Each stop is one jump from the one
# below it. Difficulty comes from the layout, not the physics: narrow 32 px
# cabinets, rises of 44-48 px (max jump ~57 px), side gaps of 28-34 px, and the
# route switches direction twice, so jumps must be aimed and timed.
# Round 3: the two turn-back cabinets at (186, 342) and (64, 160) are now the
# moving drawers in _DRAWERS, so those two climbs need timed jumps.
_TOWER = [
    (16, 524, 80, 16),  # starting counter
    (124, 480, 32, 16),  # climb right...
    (188, 434, 32, 16),
    (252, 390, 48, 16),  # ...to the right wall, then drawer A turns back left
    (124, 298, 32, 16),
    (60, 252, 32, 16),
    (0, 208, 32, 16),  # left wall, then drawer B turns back right
    (128, 116, 32, 16),
    (194, 70, 32, 16),
    (258, 26, 40, 16),  # goal: the highest cabinet
]

# R15: (min_x, max_x, y, start_x, start_direction). Each drawer is in reach of
# the cabinet below at one end of its path and out of reach at the other.
_DRAWERS = [
    (150, 222, 342, 186, 1),  # A: board at the right end, ride left to (124, 298)
    (30, 100, 160, 64, -1),  # B: board at the left end, ride right to (128, 116)
]

# R9: treats as (cabinet index in _TOWER, x). Each rests on its cabinet's top.
# Never on the counter (0) or the goal (9); two sit near a cabinet edge.
_TREATS = [
    (2, 200),  # centred
    (3, 290),  # far right edge of the right-wall cabinet
    (4, 136),  # centred
    (6, 2),  # far left edge of the left-wall cabinet
    (7, 140),  # centred
]

WORLD_WIDTH = config.INTERNAL_WIDTH
WORLD_HEIGHT = 540


def build_level():
    platforms = [Platform(*spec) for spec in _TOWER]
    counter = platforms[0]
    start = (32, counter.y - config.PLAYER_HEIGHT)
    treats = [Treat(x, platforms[i].y - config.TREAT_SIZE) for i, x in _TREATS]
    drawers = [
        Drawer(min_x, max_x, y, start_x=start_x, start_direction=d) for min_x, max_x, y, start_x, d in _DRAWERS
    ]
    return Level(
        platforms=platforms,
        world_width=WORLD_WIDTH,
        world_height=WORLD_HEIGHT,
        start=start,
        treats=treats,
        drawers=drawers,
    )
