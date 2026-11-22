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


@dataclass(frozen=True, eq=False)
class Decoration:
    """A non-solid, looping kitchen decoration (R28): "mug", "pot" or "clock".
    Its size comes from `config.DECORATION_SIZES`; nothing collides with it."""

    kind: str
    x: float
    y: float
    section: int = 1
    phase: int = 0  # update ticks added before choosing a frame (R29)


@dataclass(frozen=True, eq=False)
class Scenery:
    """A large, non-solid background item (R33): "window", "tiles", "picture" or "plant".
    Only windows have a `view` (R35). Nothing collides with scenery."""

    kind: str
    x: float
    y: float
    width: float
    height: float
    section: int = 1
    phase: int = 0  # update ticks added before choosing frames and offsets (R36/R37)
    view: str = None


@dataclass(frozen=True, eq=False)
class Hazard:
    """A timed kitchen hazard (R39): "vent", "burner" or "drip". `top` is the top of
    its cabinet (for a drip: where the drop starts; `floor` is the cabinet below).
    Its cycle is idle -> warning -> active, in PLAYING updates. Hazards are not solid."""

    kind: str
    x: float
    top: float
    section: int
    idle: int
    warning: int
    active: int
    phase: int = 0
    floor: float = None


@dataclass
class Level:
    platforms: list
    world_width: int
    world_height: int
    start: tuple  # (x, y) top-left of Albert at the start
    treats: list = field(default_factory=list)  # R9 (Round 2)
    drawers: list = field(default_factory=list)  # R15 (Round 3)
    route: list = field(default_factory=list)  # R23 (Round 4): intended stops in order
    decorations: list = field(default_factory=list)  # R28 (Round 5): visual only
    scenery: list = field(default_factory=list)  # R33 (Round 5): visual only, behind everything
    hazards: list = field(default_factory=list)  # R39 (Round 6): timed kitchen hazards

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


# R28 (Round 5): visual-only decorations as (kind, section, x, y, phase), 2 per
# section. Mugs and pots rest on a static cabinet in their section; clocks hang
# on bare wall. None covers a treat, the start or a drawer's path.
_DECORATIONS = [
    ("mug", 1, 230, 1012 - 16, 0),  # on (192, 1012)
    ("clock", 1, 300, 930, 0),
    ("pot", 2, 362, 688 - 20, 0),  # on (352, 688)
    ("clock", 2, 560, 680, 25),
    ("mug", 3, 508, 420 - 16, 17),  # on (498, 420)
    ("pot", 3, 826, 334 - 20, 11),  # on (820, 334)
    ("pot", 4, 428, 116 - 20, 21),  # on (424, 116)
    ("clock", 4, 760, 120, 41),
]


# R33/R34 (Round 5): background scenery as (kind, section, x, y, width, height, phase).
# Large windows are the main feature, 1-2 per section, each centred inside its
# section's height band; tiles fill the views the windows don't reach, and a
# picture and a hanging plant decorate bare wall in every section.
_SCENERY = [
    # S1 - garden view
    ("window", 1, 520, 796, 192, 128, 0),
    ("window", 1, 248, 940, 192, 128, 50),
    ("tiles", 1, 0, 880, 64, 64, 0),
    ("tiles", 1, 608, 928, 64, 32, 0),
    ("picture", 1, 136, 902, 48, 32, 0),
    ("plant", 1, 208, 902, 24, 40, 0),
    # S2 - town view
    ("window", 2, 232, 584, 192, 128, 23),
    ("window", 2, 576, 668, 192, 128, 77),
    ("picture", 2, 720, 804, 48, 32, 0),
    ("plant", 2, 432, 644, 24, 40, 25),
    # S3 - city view
    ("window", 3, 264, 392, 192, 128, 11),
    ("tiles", 3, 0, 480, 64, 64, 0),
    ("tiles", 3, 544, 288, 64, 64, 0),
    ("tiles", 3, 0, 400, 64, 32, 0),
    ("tiles", 3, 416, 288, 64, 32, 0),
    ("picture", 3, 104, 514, 48, 32, 0),
    ("plant", 3, 224, 486, 24, 40, 12),
    # S4 - open sky view
    ("window", 4, 312, 52, 192, 128, 39),
    ("tiles", 4, 640, 240, 128, 96, 0),
    ("tiles", 4, 624, 112, 64, 128, 0),
    ("tiles", 4, 0, 0, 160, 64, 0),
    ("tiles", 4, 480, 192, 64, 32, 0),
    ("tiles", 4, 0, 64, 64, 32, 0),
    ("picture", 4, 192, 84, 48, 32, 0),
    ("plant", 4, 280, 24, 24, 40, 37),
]


# R39 (Round 6): hazards H1-H8 (spec.md 12.3), 1/2/2/3 per section, as
# (kind, section, x, top, idle, warning, active, phase, floor). All sit on static
# route cabinets; the goal and the stop before it stay hazard-free.
_HAZARDS = [
    ("drip", 1, 442, 900, 87, 60, 33, 0, 970),  # H1: teaching drip over (420, 970)
    ("vent", 2, 722, 768, 90, 45, 45, 0, None),  # H2 on (712, 768)
    ("vent", 2, 300, 656, 90, 45, 45, 90, None),  # H3 on (292, 656)
    ("burner", 3, 70, 520, 120, 60, 60, 0, None),  # H4 on (64, 520)
    ("vent", 3, 696, 370, 90, 45, 45, 45, None),  # H5 on (690, 370)
    ("vent", 4, 560, 140, 60, 45, 45, 30, None),  # H6 on (556, 140)
    ("drip", 4, 886, 156, 27, 60, 33, 0, 226),  # H7 over (872, 226)
    ("burner", 4, 254, 56, 80, 60, 60, 0, None),  # H8 on (246, 56)
]


def _scenery(entry):
    kind, section, x, y, width, height, phase = entry
    view = config.VIEW_BY_SECTION[section] if kind == "window" else None
    return Scenery(kind, x, y, width, height, section, phase, view)


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
        decorations=[Decoration(kind, x, y, section, phase) for kind, section, x, y, phase in _DECORATIONS],
        scenery=[_scenery(entry) for entry in _SCENERY],
        hazards=[Hazard(kind, x, top, section, i, w, a, ph, fl) for kind, section, x, top, i, w, a, ph, fl in _HAZARDS],
    )
