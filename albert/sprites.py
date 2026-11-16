"""16-bit-style pixel art for Albert, the cabinets, the wall and overlay text (R7).

Every sprite is a character map; each character is a palette colour from
`config.COLORS` and '.' is transparent.
"""

import pygame

from albert import config

C = config.COLORS

_CAT_KEY = {
    "K": C["cat_black"],
    "G": C["cat_shade"],
    "R": C["cat_rim"],
    "Y": C["cat_eye"],
    "P": C["cat_pink"],
}

# Albert facing right, 16x14. Head and ears on the right, tail curling up on the left.
_CAT_UPPER = [
    "..........K..K..",
    ".K.......KPKKPK.",
    ".K.......KKKKKK.",
    ".R.......KYKKYK.",
    ".K.......KKKPKKK",
    "..K......KKKKKK.",
    "..KKKKKKKKKKKKR.",
    "..KKKKKKKKKKKK..",
    "..KGGKKKKKKGKK..",
    "..KKKKKKKKKKKK..",
]

_CAT_LEGS = {
    "cat_idle": [
        "..KK.KK....KK.K.",
        "..KK.KK....KK.K.",
        "..KK.KK....KK.K.",
        ".RKK.RK....RK.R.",
    ],
    "cat_walk_1": [
        "..KK..KK..KK..K.",
        ".KK....KK.KK...K",
        ".K......K.K....K",
        ".R......R.R....R",
    ],
    "cat_walk_2": [
        "...KK.KK...KKK..",
        "...KK.KK....KK..",
        "....KK.K....K.K.",
        "....R..R....R.R.",
    ],
    "cat_jump": [
        "KKKK.......KKKK.",
        "R..........K..KR",
        "................",
        "................",
    ],
}

_CABINET_KEY = {
    "C": C["counter_top"],
    "c": C["counter_shade"],
    "d": C["wood_dark"],
    "M": C["wood_mid"],
    "L": C["wood_light"],
    "H": C["brass"],
}

# One 16x16 cabinet: countertop edge on top, a panelled door with a brass handle.
_CABINET = [
    "CCCCCCCCCCCCCCCC",
    "cccccccccccccccc",
    "dddddddddddddddd",
    "dMMMMMMMMMMMMMMd",
    "dMLLLLLLLLLLLLMd",
    "dMLMMMMMMMMMMLMd",
    "dMLMMMMMMMMHMLMd",
    "dMLMMMMMMMMHMLMd",
    "dMLMMMMMMMMMMLMd",
    "dMLMMMMMMMMMMLMd",
    "dMLMMMMMMMMMMLMd",
    "dMLMMMMMMMMMMLMd",
    "dMLLLLLLLLLLLLMd",
    "dMMMMMMMMMMMMMMd",
    "dMMMMMMMMMMMMMMd",
    "dddddddddddddddd",
]

# 5x5 pixel font for the win/lose overlay.
_FONT = {
    "A": [".###.", "#...#", "#####", "#...#", "#...#"],
    "E": ["#####", "#....", "####.", "#....", "#####"],
    "I": ["#####", "..#..", "..#..", "..#..", "#####"],
    "L": ["#....", "#....", "#....", "#....", "#####"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "####.", "#....", "#...."],
    "R": ["####.", "#...#", "####.", "#..#.", "#...#"],
    "S": [".####", "#....", ".###.", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", ".###."],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "Y": ["#...#", ".#.#.", "..#..", "..#..", "..#.."],
    "!": ["..#..", "..#..", "..#..", ".....", "..#.."],
    " ": [".....", ".....", ".....", ".....", "....."],
}


def surface_from_map(rows, key):
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("sprite rows must all be the same width")
    surface = pygame.Surface((width, len(rows)), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char != ".":
                surface.set_at((x, y), (*key[char], 255))
    return surface


def _wall_tile():
    """A 32x32 kitchen wallpaper tile: soft stripes with a small diamond motif."""
    rows = []
    for y in range(32):
        row = ""
        for x in range(32):
            if x in (0, 16):
                row += "D"
            elif x in (1, 15, 17, 31):
                row += "M"
            elif (x, y) in {(8, 7), (7, 8), (9, 8), (8, 9), (24, 23), (23, 24), (25, 24), (24, 25)}:
                row += "M"
            else:
                row += "L"
        rows.append(row)
    return surface_from_map(rows, {"L": C["wall_light"], "M": C["wall_mid"], "D": C["wall_dark"]})


def load_sprites():
    sprites = {name: surface_from_map(_CAT_UPPER + legs, _CAT_KEY) for name, legs in _CAT_LEGS.items()}
    sprites["cabinet"] = surface_from_map(_CABINET, _CABINET_KEY)
    sprites["background"] = _wall_tile()
    return sprites


def render_text(text, colour, scale=1):
    """Draw `text` in the 5x5 pixel font. Unknown characters render as spaces."""
    glyph_w, gap = 5, 1
    surface = pygame.Surface((max(1, len(text) * (glyph_w + gap) - gap), 5), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for i, char in enumerate(text.upper()):
        for y, row in enumerate(_FONT.get(char, _FONT[" "])):
            for x, cell in enumerate(row):
                if cell == "#":
                    surface.set_at((i * (glyph_w + gap) + x, y), (*colour, 255))
    if scale != 1:
        surface = pygame.transform.scale(surface, (surface.get_width() * scale, surface.get_height() * scale))
    return surface
