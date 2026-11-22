"""16-bit-style pixel art for Albert, the cabinets, drawers, the wall, cat treats,
kitchen decorations and text (R7).

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

# A 32x16 pulled-out drawer (R15): light wooden top lip to land on, a panelled
# front and a centred brass pull, with a dark edge so it reads against the wall.
_DRAWER = [
    "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
    "dddddddddddddddddddddddddddddddd",
    "dMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMd",
    "dMLLLLLLLLLLLLLLLLLLLLLLLLLLLLMd",
    "dMLMMMMMMMMMMMMMMMMMMMMMMMMMMLMd",
    "dMLMMMMMMMMMMMMMMMMMMMMMMMMMMLMd",
    "dMLMMMMMMMMMHHHHHHHHMMMMMMMMMLMd",
    "dMLMMMMMMMMMHddddddHMMMMMMMMMLMd",
    "dMLMMMMMMMMMMMMMMMMMMMMMMMMMMLMd",
    "dMLMMMMMMMMMMMMMMMMMMMMMMMMMMLMd",
    "dMLMMMMMMMMMMMMMMMMMMMMMMMMMMLMd",
    "dMLLLLLLLLLLLLLLLLLLLLLLLLLLLLMd",
    "dMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMd",
    "dddddddddddddddddddddddddddddddd",
    ".dddddddddddddddddddddddddddddd.",
]

_TREAT_KEY = {
    "K": C["cat_black"],
    "S": C["treat_mid"],
    "H": C["treat_light"],
}

# A fish-shaped cat treat, 8x8 (R9). Dark outline so it stands out on wood and wall.
_TREAT = [
    "........",
    "........",
    "..KKKK.K",
    ".KSHHSKK",
    "KSKSSSSK",
    "KSSSSSSK",
    ".KSSSSKK",
    "..KKKK.K",
]

# --- Round 5 kitchen decorations (R28/R29) ---
_DECOR_KEY = {
    "d": C["wood_dark"],
    "M": C["wood_mid"],
    "R": C["lose_red"],
    "C": C["counter_top"],
    "c": C["counter_shade"],
    "k": C["panel"],
    "S": C["text_white"],
    "o": C["wall_dark"],
    "g": C["win_green"],
    "G": C["cat_shade"],
}

# A red coffee mug, 8x8, with its handle on the right.
_MUG = [
    "dddddd..",
    "dMMMMdd.",
    "dRRRRd.d",
    "dRRRRd.d",
    "dRRRRdd.",
    "dRRRRd..",
    "dRRRRd..",
    ".dddd...",
]

# A steel cooking pot with a lid and side handles, 16x10.
_POT = [
    "......kkkk......",
    "...kkkkkkkkkk...",
    "..kCCCCCCCCCCk..",
    "kkkkkkkkkkkkkkkk",
    "k.kCCCCCCCCCCk.k",
    "..kCccccccccCk..",
    "..kCccccccccCk..",
    "..kCccccccccCk..",
    "..kcccccccccck..",
    "...kkkkkkkkkk...",
]

_STEAM_WAVE = [0, 1, 1, 0, -1, -1, 0, 1]  # x offset of a steam wisp, row by row


def _steam(width, height, wisps, frame):
    """Rising wisps of steam: white pixels with a darker edge so they read on the wall.
    Each frame shifts the wave and the gaps up by two rows."""
    grid = [["."] * width for _ in range(height)]
    for base, offset in wisps:
        for y in range(height):
            k = (y + 2 * frame + offset) % 8
            if k == 7 or (y == 0 and frame % 2):  # gaps that drift upward
                continue
            x = base + _STEAM_WAVE[k]
            grid[y][x] = "S"
            if grid[y][x + 1] == ".":
                grid[y][x + 1] = "o"
    return ["".join(row) for row in grid]


def _clock(lit):
    """A 16x8 appliance clock showing 9:30; the digits blink on and off."""
    on = "g" if lit else "G"
    digits = [  # 9 : 3 0, each 3x5 except the colon
        ["###", "#.#", "###", "..#", "###"],
        [".", "#", ".", "#", "."],
        ["###", "..#", "###", "..#", "###"],
        ["###", "#.#", "#.#", "#.#", "###"],
    ]
    rows = ["c" * 16]
    for y in range(5):
        row = "ck"
        for i, d in enumerate(digits):
            row += d[y].replace("#", on).replace(".", "k") + ("k" if i < 3 else "")
        rows.append(row + "k" * (15 - len(row)) + "c")
    rows += ["c" + "k" * 14 + "c", "c" * 16]
    return rows


# --- Round 5 background scenery (R33-R38) ---
# Drawn procedurally on character grids. Scenery never uses the cabinet and
# drawer colours, and stays light so black Albert reads clearly in front of it.
_SCN_KEY = {
    "s": C["sky_light"],
    "S": C["sky_blue"],
    "W": C["text_white"],
    "g": C["leaf_light"],
    "G": C["leaf_dark"],
    "r": C["roof_red"],
    "t": C["stone_grey"],
    "b": C["building_blue"],
    "h": C["hill_green"],
    "y": C["cat_eye"],
    "p": C["cat_rim"],
    "R": C["lose_red"],
    "o": C["treat_light"],
    "B": C["brass"],
}
GLASS_W = config.WINDOW_SIZE[0] - 2 * config.WINDOW_FRAME  # 184
GLASS_H = config.WINDOW_SIZE[1] - 2 * config.WINDOW_FRAME  # 120


class _Grid:
    """A small drawing helper: a character grid that becomes a sprite."""

    def __init__(self, w, h, fill="."):
        self.w, self.h = w, h
        self.rows = [[fill] * w for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.rows[y][x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r + r:
                    self.put(xx, yy, c)

    def surface(self):
        return surface_from_map(["".join(row) for row in self.rows], _SCN_KEY)


def _sky(split, top="S", bottom="s"):
    """Two sky tones with a dithered seam at row `split`."""
    g = _Grid(GLASS_W, GLASS_H, bottom)
    g.rect(0, 0, GLASS_W, split, top)
    for x in range(0, GLASS_W, 2):
        g.put(x, split, top)
        g.put(x + 1, split + 2, top)
    return g.surface()


def _clouds():
    """A strip of puffy clouds that wraps every CLOUD_LOOP px, with a light shaded underside."""
    loop = config.CLOUD_LOOP
    g = _Grid(loop, 36)
    for cx, cy, size in [(24, 16, 7), (70, 10, 5), (118, 18, 8)]:
        for dx, r in [(-size, size - 2), (0, size), (size, size - 1), (size // 2, size - 1)]:
            for yy in range(cy - r, cy + r + 1):
                for xx in range(cx + dx - r, cx + dx + r + 1):
                    if (xx - cx - dx) ** 2 + (yy - cy) ** 2 <= r * r + r:
                        g.put(xx % loop, yy, "W")
        for x in range(cx - 2 * size, cx + 2 * size):
            if g.rows[cy + size - 1][x % loop] == "W":
                g.put(x % loop, cy + size - 1, "s")
    return g.surface()


def _garden_land():
    g = _Grid(GLASS_W, GLASS_H)
    for x0 in (8, 70, 132):  # distant cottages
        g.rect(x0, 70, 40, 22, "W")
        for i in range(12):
            g.rect(x0 - 2 + i, 70 - i, 44 - 2 * i, 1, "r")
        g.rect(x0 + 8, 78, 6, 6, "S")
        g.rect(x0 + 26, 78, 6, 6, "S")
    g.rect(0, 92, GLASS_W, 28, "g")  # lawn
    for x in range(0, GLASS_W, 7):
        g.put(x, 110 + x % 3, "G")
    for x in range(2, GLASS_W, 8):  # picket fence
        g.rect(x, 90, 4, 18, "W")
        g.rect(x + 1, 89, 2, 1, "W")
        g.rect(x + 3, 92, 1, 16, "t")
    g.rect(0, 95, GLASS_W, 2, "t")
    g.rect(0, 103, GLASS_W, 2, "t")
    return g.surface()


def _garden_trees(frame):
    """Three trees whose crowns lean one way, then the other."""
    g = _Grid(GLASS_W, GLASS_H)
    sway = 1 if frame else -1
    for cx, top in [(36, 40), (100, 30), (160, 44)]:
        g.rect(cx - 2, top + 22, 5, 100 - top - 22, "t")
        g.disc(cx + sway, top + 10, 12, "G")
        g.disc(cx + 2 * sway - 4, top + 4, 8, "G")
        g.disc(cx + 2 * sway + 3, top + 6, 6, "g")
        g.disc(cx + sway - 6, top + 14, 4, "g")
    return g.surface()


_CHIMNEYS = [(20, 54), (66, 46), (120, 58), (164, 50)]


def _house(g, x0, base, w, wall, roof_rows):
    """A house front with a pitched roof whose eaves start at y=`base`."""
    g.rect(x0, base, w, GLASS_H - base, wall)
    half = w // 2 + 2
    for i in range(roof_rows):
        inset = i * half // roof_rows
        g.rect(x0 - 2 + inset, base - i, w + 4 - 2 * inset, 1, "r")
    g.rect(x0 - 2, base, w + 4, 1, "t")  # eaves line


def _town_land():
    g = _Grid(GLASS_W, GLASS_H)
    for cx, top in _CHIMNEYS:  # chimneys rise from the back-row roofs
        g.rect(cx, top, 6, 20, "b")
        g.rect(cx - 1, top, 8, 2, "t")
    for x0, base, w in [(4, 74, 40), (50, 68, 40), (100, 76, 40), (146, 70, 40)]:  # back row
        _house(g, x0, base, w, "t", 14)
        g.rect(x0 + 8, base + 6, 5, 6, "s")
        g.rect(x0 + w - 13, base + 6, 5, 6, "s")
    for x0, base, w in [(-10, 96, 56), (56, 92, 60), (126, 98, 64)]:  # front row
        _house(g, x0, base, w, "W", 18)
        for wx in range(x0 + 8, x0 + w - 8, 16):
            g.rect(wx, base + 6, 6, 8, "S")
    return g.surface()


def _town_smoke(frame):
    """Puffs rising from each chimney; each frame moves every puff up one step."""
    g = _Grid(GLASS_W, GLASS_H)
    for i, (cx, top) in enumerate(_CHIMNEYS):
        for step in range(3):
            k = (step + frame + i) % 3
            drift = k * 2 if i % 2 else -k * 2
            g.disc(cx + 3 + drift, top - 6 - 9 * k, 2 + k, "W" if k < 2 else "s")
    return g.surface()


_TOWERS = [(0, 40, 30), (34, 20, 26), (64, 50, 24), (92, 14, 30), (126, 36, 22), (152, 26, 32)]


def _tower_windows(x0, top, w):
    for j, wy in enumerate(range(top + 6, GLASS_H - 4, 8)):
        for i, wx in enumerate(range(x0 + 3, x0 + w - 6, 6)):
            yield i, j, wx, wy


def _city_land():
    g = _Grid(GLASS_W, GLASS_H)
    for x0, top, w in _TOWERS:
        g.rect(x0, top, w, GLASS_H - top, "b")
        g.rect(x0, top, w, 2, "t")
        g.rect(x0 + w - 3, top + 2, 3, GLASS_H - top - 2, "t")
        for _, _, wx, wy in _tower_windows(x0, top, w):
            g.rect(wx, wy, 3, 4, "s")
    return g.surface()


def _city_lights(frame):
    """Lit windows; a different set glows in each frame."""
    g = _Grid(GLASS_W, GLASS_H)
    for n, tower in enumerate(_TOWERS):
        for i, j, wx, wy in _tower_windows(*tower):
            if (i + 2 * j + n + frame) % 3 == 0:
                g.rect(wx, wy, 3, 4, "y")
    return g.surface()


def _sky_hills():
    g = _Grid(GLASS_W, GLASS_H)
    for x in range(GLASS_W):
        far = 92 + 6 * ((x * 7) % 60 - 30) ** 2 // 900
        near = 104 + 5 * ((x * 3 + 20) % 80 - 40) ** 2 // 1600
        g.rect(x, far, 1, GLASS_H - far, "h")
        g.rect(x, near, 1, GLASS_H - near, "g")
    return g.surface()


def _birds():
    g = _Grid(config.BIRD_LOOP, 30)
    wings = [(0, 0), (1, 0), (1, 1), (2, 1), (3, 2), (4, 1), (5, 2), (6, 1), (7, 1), (7, 0), (8, 0)]
    for bx, by in [(20, 8), (36, 15), (100, 20)]:
        for dx, dy in wings:
            g.put(bx + dx, by + dy, "b")
    return g.surface()


def _frame():
    """The window frame and centre mullion; the glass inside is transparent. No sill."""
    w, h = config.WINDOW_SIZE
    f = config.WINDOW_FRAME
    g = _Grid(w, h, "p")
    g.rect(1, 1, w - 2, h - 2, "t")
    g.rect(f, f, w - 2 * f, h - 2 * f, ".")
    g.rect(w // 2 - 1, f, 2, h - 2 * f, "t")
    return g.surface()


def _curtain(frame):
    """The left curtain: red gingham gathered at a tie-back. Frames sway its inner edge."""
    w = config.CURTAIN_WIDTH
    g = _Grid(w, GLASS_H)
    sway = [-2, 0, 2][frame]
    for y in range(GLASS_H):
        if y < 6:
            width = w
        elif y < 70:
            width = 20 - (y - 6) * 9 // 64 + sway * (y - 6) // 64
        elif y < 76:
            width = 10 + sway // 2
        else:
            width = 10 + (y - 76) * 10 // 44 + sway
        width = max(2, min(w, width))
        for x in range(width):
            g.put(x, y, "R" if (x // 4 + y // 4) % 2 else "W")
        g.put(width - 1, y, "R")
    g.rect(0, 70, 12 + sway // 2, 3, "B")  # tie-back
    g.rect(0, 0, w, 3, "R")  # pelmet
    return g.surface()


def _picture():
    """A framed painting of green hills under a yellow sun."""
    w, h = config.PICTURE_SIZE
    g = _Grid(w, h, "B")
    g.rect(1, 1, w - 2, h - 2, "r")
    g.rect(3, 3, w - 6, h - 6, "s")
    g.disc(34, 10, 3, "y")
    for x in range(3, w - 3):
        top = 20 + abs(x - 18) // 4
        g.rect(x, top, 1, h - 3 - top, "h")
    g.rect(14, 14, 3, 8, "G")
    g.disc(15, 13, 3, "g")
    return g.surface()


def _plant(frame):
    """A hanging plant in a terracotta pot; its trailing vines sway."""
    w, h = config.PLANT_SIZE
    g = _Grid(w, h)
    g.rect(11, 0, 2, 8, "t")  # cord
    for i in range(8):
        g.rect(5 + i // 3, 8 + i, 14 - 2 * (i // 3), 1, "r")
    g.rect(4, 8, 16, 2, "o")
    sway = 1 if frame else -1
    for vx, length in [(5, 26), (10, 30), (15, 22), (19, 28)]:
        for y in range(10, 10 + length):
            x = vx + sway * (y - 10) // 12
            g.put(x, y, "G")
            if y % 4 == 0:
                g.put(x + 1, y, "g")
                g.put(x - 1, y + 1, "g")
    g.disc(12, 8, 4, "g")
    g.disc(7, 9, 2, "G")
    g.disc(17, 9, 2, "G")
    return g.surface()


def _tile():
    """One pale-blue backsplash tile with a bevel and grout lines. No white, so the
    tiles never read as HUD text or as a cabinet's countertop."""
    g = _Grid(config.TILE_SIZE, config.TILE_SIZE, "s")
    g.rect(2, 13, 12, 1, "S")
    g.rect(13, 2, 1, 12, "S")
    g.rect(0, 15, 16, 1, "t")
    g.rect(15, 0, 1, 16, "t")
    return g.surface()


def _scenery_sprites():
    sprites = {
        "scn_clouds": _clouds(),
        "scn_frame": _frame(),
        "scn_picture": _picture(),
        "scn_tile": _tile(),
        "scn_garden_sky": _sky(56),
        "scn_garden_land": _garden_land(),
        "scn_town_sky": _sky(66, top="S", bottom="W"),
        "scn_town_land": _town_land(),
        "scn_city_sky": _sky(70),
        "scn_city_land": _city_land(),
        "scn_sky_sky": _sky(84),
        "scn_sky_land": _sky_hills(),
        "scn_sky_birds": _birds(),
    }
    for i in range(2):
        sprites[f"scn_garden_{i}"] = _garden_trees(i)
        sprites[f"scn_city_{i}"] = _city_lights(i)
        sprites[f"scn_plant_{i}"] = _plant(i)
    for i in range(3):
        sprites[f"scn_town_{i}"] = _town_smoke(i)
        sprites[f"scn_curtain_{i}"] = _curtain(i)
    return sprites


# --- Round 6 hazards (R45) ---
# Warning orange and red appear only here, so a glow always means danger.
_HZ_KEY = {
    "k": C["panel"],
    "p": C["cat_rim"],
    "t": C["stone_grey"],
    "W": C["text_white"],
    "s": C["sky_light"],
    "S": C["sky_blue"],
    "G": C["cat_shade"],
    "o": C["warn_orange"],
    "r": C["warn_red"],
}


def _hz(rows):
    return surface_from_map(rows, _HZ_KEY)


def _vent(light, lid_up):
    """A 16x8 steam vent: a grille box with a lid and a light. When the lid
    rattles up, steam sputters out of the gap below it."""
    lid = ["..pppppppppppp..", "..pttttttttttp.."]
    body = [
        ".pppppppppppppp.",
        ".pkpkpkpkpkp" + light * 2 + "p.",
        ".pkpkpkpkpkp" + light * 2 + "p.",
        ".pppppppppppppp.",
        "pppppppppppppppp",
    ]
    if lid_up:
        return _hz(lid + ["..W...W....W.W.."] + body)
    return _hz(["." * 16] + lid + body)


def _jet(frame):
    """A 12x56 solid column of steam, billowing out at the top."""
    w, h = config.JET_SIZE
    rows = []
    for y in range(h):
        wobble = (y // 4 + frame) % 2
        if y < 8:  # billowing cloud top
            width = 6 + y // 2 * 2
            pad = (w - width) // 2
            row = "." * pad + "W" * width + "." * (w - pad - width)
        else:
            left, right = wobble, w - (1 - wobble)
            row = "." * left + "".join("s" if x in (left, right - 1) or (x + y + frame) % 7 == 0 else "W"
                                       for x in range(left, right)) + "." * (w - right)
        rows.append(row)
    return _hz(rows)


def _burner(coil, shimmer):
    """A 16x6 stovetop ring: 2 rows of heat shimmer above, then the coil."""
    shimmer_rows = ["..r...r...r...r.", ".r...r...r...r.."] if shimmer == 0 else [".r...r...r...r..", "..r...r...r...r."]
    rows = [*(shimmer_rows if shimmer is not None else ["." * 16] * 2),
            "kkkkkkkkkkkkkkkk",
            "k" + coil * 14 + "k",
            "kk" + coil + "kkkkkkkkkk" + coil + "kk",
            "kkk" + coil * 10 + "kkk"]
    return _hz(rows)


def _tap(collar):
    """An 8x8 wall tap; the collar glows red while a drop forms."""
    return _hz([
        "pppp....",
        "ptttp...",
        "pppppppp",
        "..ptttt" + "p",
        "...p" + collar * 2 + "p.",
        "...pttp.",
        "....pp..",
        "........",
    ])


def _drop(size):
    """A 4x6 water drop; sizes 0-2 grow at the tap, 3 is the falling drop."""
    shapes = [
        ["....", "....", "....", "....", ".SS.", "...."],
        ["....", "....", ".S..", ".SS.", "SsSS", ".SS."],
        ["....", ".S..", ".SS.", "SWSS", "SSSS", ".SS."],
        [".S..", ".SS.", "SWSS", "SWSS", "SSSS", ".SS."],
    ]
    return _hz(shapes[size])


def _hazard_sprites():
    sprites = {
        "hz_vent_idle": _vent("G", lid_up=False),
        "hz_vent_warn_0": _vent("r", lid_up=False),
        "hz_vent_warn_1": _vent("r", lid_up=True),
        "hz_burner_idle": _burner("t", None),
        "hz_burner_warn": _burner("o", None),
        "hz_tap": _tap("t"),
        "hz_tap_warn": _tap("r"),
        "hz_drop": _drop(3),
    }
    for i in range(2):
        sprites[f"hz_jet_{i}"] = _jet(i)
        sprites[f"hz_burner_hot_{i}"] = _burner("r", i)
    for i in range(3):
        sprites[f"hz_drop_form_{i}"] = _drop(i)
    return sprites


# 5x5 pixel font for the win/lose overlay and the treat HUD.
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
    # Round 7 (R52): the rest of A-Z and the menu cursor
    "B": ["####.", "#...#", "####.", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "####."],
    "F": ["#####", "#....", "####.", "#....", "#...."],
    "G": [".####", "#....", "#..##", "#...#", ".####"],
    "H": ["#...#", "#...#", "#####", "#...#", "#...#"],
    "J": ["..###", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#..#.", "#.#..", "##...", "#.#..", "#..#."],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    "Q": [".###.", "#...#", "#.#.#", "#..#.", ".##.#"],
    "V": ["#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "X": ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "Z": ["#####", "...#.", "..#..", ".#...", "#####"],
    ">": [".#...", "..#..", "...#.", "..#..", ".#..."],
    "!": ["..#..", "..#..", "..#..", ".....", "..#.."],
    " ": [".....", ".....", ".....", ".....", "....."],
    "/": ["....#", "...#.", "..#..", ".#...", "#...."],
    "0": [".###.", "#..##", "#.#.#", "##..#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", ".###."],
    "2": ["####.", "....#", ".###.", "#....", "#####"],
    "3": ["####.", "....#", ".###.", "....#", "####."],
    "4": ["#..#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "####."],
    "6": [".###.", "#....", "####.", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#.."],
    "8": [".###.", "#...#", ".###.", "#...#", ".###."],
    "9": [".###.", "#...#", ".####", "....#", ".###."],
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
    sprites["treat"] = surface_from_map(_TREAT, _TREAT_KEY)
    sprites["drawer"] = surface_from_map(_DRAWER, _CABINET_KEY)
    for i in range(4):
        sprites[f"mug_{i}"] = surface_from_map(_steam(8, 8, [(2, 0)], i) + _MUG, _DECOR_KEY)
        sprites[f"pot_{i}"] = surface_from_map(_steam(16, 10, [(4, 0), (10, 3)], i) + _POT, _DECOR_KEY)
    for i in range(2):
        sprites[f"clock_{i}"] = surface_from_map(_clock(lit=i == 0), _DECOR_KEY)
    sprites.update(_scenery_sprites())  # R33-R38
    sprites.update(_hazard_sprites())  # R45
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
