"""Game constants. Pure Python: must not import pygame."""

# --- Display (R7) ---
INTERNAL_WIDTH = 320
INTERNAL_HEIGHT = 180
SCALE = 4
FPS = 60
TITLE = "Albert Cat Climber"

# --- Albert's hitbox (world pixels; matches the cat sprite size) ---
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 14

# --- Cat treats (Round 2, R9-R14): 8x8 hitbox matching the treat sprite ---
TREAT_SIZE = 8

# --- Moving drawers (Round 3, R15-R20): 32x16, matching the drawer sprite ---
DRAWER_WIDTH = 32
DRAWER_HEIGHT = 16
DRAWER_SPEED = 40.0  # px/s, slower than Albert's MOVE_SPEED

# --- Kitchen animation and effects (Round 5, R27-R32); timings are in update ticks ---
MUG_SIZE = (8, 16)
POT_SIZE = (16, 20)
CLOCK_SIZE = (16, 8)
DECORATION_SIZES = {"mug": MUG_SIZE, "pot": POT_SIZE, "clock": CLOCK_SIZE}
DECORATION_FRAMES = {"mug": (10, 4), "pot": (8, 4), "clock": (30, 2)}  # kind -> (frame_ticks, frame_count)
MAX_PARTICLES = 48
DUST_COUNT = 4
DUST_LIFE = 12
SPARKLE_COUNT = 6
SPARKLE_LIFE = 18
SPARKLE_SPEED = 40.0  # px/s

# --- Background scenery (Round 5 expansion, R33-R38); timings are in update ticks ---
WINDOW_SIZE = (192, 128)
WINDOW_FRAME = 4  # px of frame around the glass
CURTAIN_WIDTH = 24
PICTURE_SIZE = (48, 32)
PLANT_SIZE = (24, 40)
TILE_SIZE = 16
VIEW_BY_SECTION = {1: "garden", 2: "town", 3: "city", 4: "sky"}
CLOUD_TICKS_PER_PX = 6
CLOUD_LOOP = 160
BIRD_TICKS_PER_PX = 3
BIRD_LOOP = 160
SCENERY_FRAMES = {"garden": (45, 2), "town": (20, 3), "city": (50, 2), "curtain": (30, 4), "plant": (50, 2)}
CURTAIN_SEQUENCE = (0, 1, 2, 1)  # art frame for each curtain animation step

# --- Kitchen hazards (Round 6, R39-R46); times are in PLAYING updates ---
VENT_SIZE = (16, 8)
JET_SIZE = (12, 56)  # the steam jet's hit area and sprite
BURNER_WIDTH = 16
DROP_SIZE = (4, 6)
DRIP_SPEED = 2  # px per update (120 px/s)
KNOCKBACK_SPEED = 180  # upward speed after a hit (px/s)
KNOCKBACK_TICKS = 18  # updates of left/right override after a hit (0.3 s)
INVULNERABLE_TICKS = 60  # updates without hits after a hit (1 s)
HIT_PUFF_COUNT = 6
HIT_PUFF_SPEED = 30.0  # px/s
HIT_PUFF_LIFE = 15

# --- Physics (world pixels and seconds; y grows downward) ---
MOVE_SPEED = 100.0  # horizontal speed while a direction is held (R1)
GRAVITY = 900.0  # downward acceleration (R2)
JUMP_VELOCITY = 320.0  # upward speed at the start of a jump (R2)
MAX_FALL_SPEED = 400.0  # terminal falling speed (R2)

# --- Palette (R7): every sprite colour comes from here ---
COLORS = {
    "cat_black": (14, 12, 22),
    "cat_shade": (38, 34, 58),
    "cat_rim": (96, 94, 128),
    "cat_eye": (240, 208, 64),
    "cat_pink": (232, 128, 148),
    "wall_light": (232, 218, 188),
    "wall_mid": (214, 196, 160),
    "wall_dark": (186, 162, 128),
    "counter_top": (222, 222, 232),
    "counter_shade": (160, 164, 184),
    "wood_light": (200, 132, 76),
    "wood_mid": (160, 98, 54),
    "wood_dark": (106, 62, 34),
    "brass": (248, 220, 120),
    "text_white": (248, 248, 248),
    "panel": (28, 22, 44),
    "win_green": (120, 224, 120),
    "lose_red": (236, 84, 84),
    "treat_mid": (244, 132, 84),
    "treat_light": (252, 200, 150),
    # Round 5 scenery (R33-R38): the outdoor views, plants and tiles
    "sky_light": (184, 222, 248),
    "sky_blue": (124, 180, 236),
    "leaf_light": (124, 192, 96),
    "leaf_dark": (64, 128, 72),
    "roof_red": (184, 88, 72),
    "stone_grey": (156, 158, 176),
    "building_blue": (104, 120, 160),
    "hill_green": (150, 200, 128),
    # Round 6 hazards (R45): warning colours used by nothing else
    "warn_orange": (255, 152, 32),
    "warn_red": (240, 36, 52),
}
PALETTE = list(COLORS.values())
