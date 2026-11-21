"""The kitchen level. Pure Python: must not import pygame."""

from dataclasses import dataclass, field

from albert import config


@dataclass(eq=False)
class Platform:
    """A cabinet. Its top surface is at `y`; Albert lands on it from above."""

    x: float
    y: float
    width: float
    height: float
    section: int = 1  # R23 (Round 4): which route section it belongs to


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
    section: int = 1  # R23 (Round 4)

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
    route: list = field(default_factory=list)  # R23 (Round 4): intended stops in order

    @property
    def goal_platform(self):
        """R5: the highest cabinet (smallest y) is the goal."""
        return min(self.platforms, key=lambda p: p.y)


WORLD_WIDTH = 960  # R21: 3 screens wide
WORLD_HEIGHT = 1080  # R21: 6 screens tall

# R23: the route, in order, from the counter to the goal (spec.md 10.2). It snakes
# up the kitchen: S1 right along the bottom, S2 left, S3 right, S4 left to the goal.
# Cabinets are ("cab", section, x, y, width), all 16 px tall.
# Drawers are ("drawer", section, min_x, max_x, y, speed, start_x, start_direction).
# Physics limits: max jump ~57 px high; reach ~60 px on the level, less when rising.
_ROUTE = [
    # S1 - counter run: wide cabinets, short gaps, small rises, no drawers.
    ("cab", 1, 16, 1060, 80),  # starting counter
    ("cab", 1, 116, 1036, 56),
    ("cab", 1, 192, 1012, 56),
    ("cab", 1, 268, 1020, 48),
    ("cab", 1, 336, 994, 64),
    ("cab", 1, 420, 970, 48),
    ("cab", 1, 490, 976, 56),
    ("cab", 1, 568, 950, 48),
    ("cab", 1, 638, 926, 56),
    ("cab", 1, 716, 902, 48),
    ("cab", 1, 786, 880, 56),
    ("cab", 1, 864, 858, 64),  # right wall
    # S2 - lower cabinets, heading left: narrower, wider gaps, one slow drawer.
    ("cab", 2, 904, 822, 40),
    ("cab", 2, 838, 792, 36),
    ("cab", 2, 780, 800, 32),
    ("cab", 2, 712, 768, 36),
    ("cab", 2, 650, 770, 36),
    ("drawer", 2, 534, 596, 740, 35, 534, 1),  # board at the right end, ride left
    ("cab", 2, 480, 712, 36),
    ("cab", 2, 418, 720, 32),
    ("cab", 2, 352, 688, 36),
    ("cab", 2, 292, 656, 32),
    ("cab", 2, 226, 662, 36),
    ("cab", 2, 162, 630, 32),
    ("cab", 2, 100, 600, 36),
    ("cab", 2, 40, 596, 40),  # left wall
    # S3 - upper cabinets, heading right: narrow, long gaps, two drawers.
    ("cab", 3, 4, 556, 28),
    ("cab", 3, 64, 520, 28),
    ("cab", 3, 124, 486, 28),
    ("cab", 3, 190, 490, 24),
    ("drawer", 3, 234, 318, 456, 45, 234, 1),  # board at the left end, ride right
    ("cab", 3, 370, 446, 28),
    ("cab", 3, 436, 412, 24),
    ("cab", 3, 498, 420, 28),
    ("drawer", 3, 546, 638, 384, 45, 638, -1),
    ("cab", 3, 690, 370, 28),
    ("cab", 3, 756, 340, 24),
    ("cab", 3, 820, 334, 28),
    ("cab", 3, 884, 310, 32),  # right wall
    # S4 - top shelves, heading left: narrowest, longest gaps, three faster drawers.
    ("cab", 4, 928, 268, 24),
    ("cab", 4, 872, 226, 24),
    ("drawer", 4, 740, 820, 196, 50, 740, 1),  # then hop straight onto the next drawer
    ("drawer", 4, 600, 688, 170, 55, 688, -1),
    ("cab", 4, 556, 140, 24),
    ("cab", 4, 492, 150, 24),
    ("cab", 4, 424, 116, 24),
    ("drawer", 4, 290, 372, 84, 55, 290, 1),
    ("cab", 4, 246, 56, 24),
    ("cab", 4, 180, 40, 24),
    ("cab", 4, 100, 24, 40),  # goal: the highest cabinet
]

# R24: off-route side cabinets, each holding a treat that needs a detour.
_SIDE = [
    (3, 330, 400, 24),  # up and back from (370, 446)
    (4, 620, 104, 24),  # up and back from (556, 140)
]

# R9/R24: treats as (x, top of the cabinet they rest on). 2/3/3/4 per section.
_TREATS = [
    (288, 1020),  # S1, centred
    (588, 950),  # S1, centred
    (780, 800),  # S2, left edge
    (430, 720),  # S2, centred
    (186, 630),  # S2, right edge
    (134, 486),  # S3, centred
    (452, 412),  # S3, right edge
    (330, 400),  # S3, side cabinet
    (872, 226),  # S4, left edge
    (500, 150),  # S4, centred
    (636, 104),  # S4, side cabinet, right edge
    (246, 56),  # S4, left edge
]

_CABINET_HEIGHT = 16


def _stop(entry):
    kind, section, *spec = entry
    if kind == "cab":
        x, y, width = spec
        return Platform(x, y, width, _CABINET_HEIGHT, section)
    min_x, max_x, y, speed, start_x, direction = spec
    return Drawer(min_x, max_x, y, speed=speed, start_x=start_x, start_direction=direction, section=section)


def build_level():
    route = [_stop(entry) for entry in _ROUTE]
    sides = [Platform(x, y, w, _CABINET_HEIGHT, s) for s, x, y, w in _SIDE]
    platforms = [s for s in route if isinstance(s, Platform)] + sides
    drawers = [s for s in route if isinstance(s, Drawer)]
    counter = route[0]
    start = (32, counter.y - config.PLAYER_HEIGHT)
    treats = [Treat(x, top - config.TREAT_SIZE) for x, top in _TREATS]
    return Level(
        platforms=platforms,
        world_width=WORLD_WIDTH,
        world_height=WORLD_HEIGHT,
        start=start,
        treats=treats,
        drawers=drawers,
        route=route,
    )
