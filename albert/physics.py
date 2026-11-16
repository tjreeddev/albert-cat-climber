"""Albert's movement, gravity, jumping and one-way platform collision.

Pure Python: must not import pygame. Coordinates are world pixels with y
growing downward; positions are top-left corners.
"""

from dataclasses import dataclass

from albert import config

_EPSILON = 1e-6


@dataclass
class Player:
    x: float
    y: float
    width: int = config.PLAYER_WIDTH
    height: int = config.PLAYER_HEIGHT
    vx: float = 0.0
    vy: float = 0.0
    on_ground: bool = False
    facing: int = 1  # 1 = right, -1 = left (used only for drawing)
    walk_time: float = 0.0  # seconds spent walking (used only for animation)

    @property
    def bottom(self):
        return self.y + self.height


def overlaps_horizontally(player, platform):
    return player.x < platform.x + platform.width and player.x + player.width > platform.x


def is_standing_on(player, platform):
    return overlaps_horizontally(player, platform) and abs(player.bottom - platform.y) < _EPSILON


def step(player, direction, jump, platforms, world_width, dt):
    """Advance Albert by one fixed timestep.

    direction: -1 (left), 0 (none) or 1 (right)
    jump:      True while a jump key is held
    Returns the platform Albert landed on this step, or None.
    """
    # R1: horizontal movement, kept inside the tower walls.
    player.vx = direction * config.MOVE_SPEED
    if direction:
        player.facing = direction
    player.x = min(max(player.x + player.vx * dt, 0.0), world_width - player.width)

    # R2: jump only from the ground; gravity always applies, up to a cap.
    if jump and player.on_ground:
        player.vy = -config.JUMP_VELOCITY
    player.on_ground = False
    player.vy = min(player.vy + config.GRAVITY * dt, config.MAX_FALL_SPEED)

    previous_bottom = player.bottom
    player.y += player.vy * dt

    # R3: one-way cabinets. Only land when moving down and the feet crossed
    # the top surface this step (swept, so fast falls cannot tunnel through).
    landed = None
    if player.vy >= 0:
        for platform in platforms:
            if (
                overlaps_horizontally(player, platform)
                and previous_bottom <= platform.y + _EPSILON
                and player.bottom >= platform.y
                and (landed is None or platform.y < landed.y)
            ):
                landed = platform
        if landed is not None:
            player.y = landed.y - player.height
            player.vy = 0.0
            player.on_ground = True

    player.walk_time = player.walk_time + dt if (direction and player.on_ground) else 0.0
    return landed
