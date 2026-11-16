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
}
PALETTE = list(COLORS.values())
