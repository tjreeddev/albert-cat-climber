"""Visual-only animation and particle helpers (Round 5, R27-R31).

Pure Python: must not import pygame. Everything is driven by update ticks,
never wall-clock time or randomness, so effects are deterministic. Gameplay
never reads anything from here.
"""

import math
from dataclasses import dataclass

from albert import config


@dataclass
class Particle:
    """A short-lived visual particle: "dust" (R30) or "sparkle" (R31)."""

    kind: str
    x: float
    y: float
    vx: float
    vy: float
    life: int  # updates left


def anim_frame(ticks, frame_ticks, frame_count, phase=0):
    """R27: which frame of a looping animation to show at `ticks`."""
    return ((ticks + phase) // frame_ticks) % frame_count


def decoration_frame(decoration, ticks):
    """R29: the current frame of a level decoration."""
    frame_ticks, frame_count = config.DECORATION_FRAMES[decoration.kind]
    return anim_frame(ticks, frame_ticks, frame_count, decoration.phase)


def dust_particles(player):
    """R30: a small puff at Albert's feet, spreading out and drifting up."""
    left, right, y = player.x, player.x + player.width, player.y + player.height - 1
    spots = [(left + 2, -30), (left + 4, -15), (right - 4, 15), (right - 2, 30)]
    return [Particle("dust", x, y, vx, -10.0, config.DUST_LIFE) for x, vx in spots]


def sparkle_particles(treat):
    """R31: a ring of particles flying out from the treat's centre, the first straight up."""
    cx, cy = treat.x + treat.width / 2, treat.y + treat.height / 2
    speed, n = config.SPARKLE_SPEED, config.SPARKLE_COUNT
    angles = [2 * math.pi * k / n for k in range(n)]
    return [Particle("sparkle", cx, cy, speed * math.sin(a), -speed * math.cos(a), config.SPARKLE_LIFE) for a in angles]


def puff_particles(player):
    """R44: a ring of steam puffs from Albert's centre when a hazard hits him."""
    cx, cy = player.x + player.width / 2, player.y + player.height / 2
    speed, n = config.HIT_PUFF_SPEED, config.HIT_PUFF_COUNT
    angles = [2 * math.pi * k / n for k in range(n)]
    return [Particle("puff", cx, cy, speed * math.sin(a), -speed * math.cos(a), config.HIT_PUFF_LIFE) for a in angles]


def step_particles(particles, dt):
    """Move each particle by velocity * dt, age it by one update, and drop expired ones."""
    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.life -= 1
    particles[:] = [p for p in particles if p.life > 0]


def scroll_offset(ticks, ticks_per_px, loop_px, phase=0):
    """R36: how far a looping strip (clouds, birds) has drifted, in whole pixels."""
    return ((ticks + phase) // ticks_per_px) % loop_px


def scenery_anim(item, ticks):
    """R36/R37: the animation state of a scenery item at `ticks`, as a tuple of ints.

    window: (cloud_offset, view_frame, bird_offset, curtain_frame)
    plant:  (frame,)
    tiles, picture: ()
    """
    p = item.phase
    if item.kind == "window":
        clouds = scroll_offset(ticks, config.CLOUD_TICKS_PER_PX, config.CLOUD_LOOP, p)
        if item.view == "sky":
            view_frame, birds = 0, scroll_offset(ticks, config.BIRD_TICKS_PER_PX, config.BIRD_LOOP, p)
        else:
            view_frame, birds = anim_frame(ticks, *config.SCENERY_FRAMES[item.view], p), 0
        curtain = config.CURTAIN_SEQUENCE[anim_frame(ticks, *config.SCENERY_FRAMES["curtain"], p)]
        return (clouds, view_frame, birds, curtain)
    if item.kind == "plant":
        return (anim_frame(ticks, *config.SCENERY_FRAMES["plant"], p),)
    return ()
