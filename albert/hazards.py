"""Kitchen hazard timing and hit areas (Round 6, R40-R43).

Pure Python: must not import pygame. Everything is driven by the gameplay
hazard clock (`Game.hazard_ticks`), never by the visual-only `Game.ticks`.
"""

from albert import config, physics


def cycle(hazard):
    return hazard.idle + hazard.warning + hazard.active


def cycle_time(hazard, hazard_ticks):
    """Where the hazard is in its cycle: 0 .. cycle - 1."""
    return (hazard_ticks + hazard.phase) % cycle(hazard)


def phase_of(hazard, hazard_ticks):
    """R40: "idle", "warning" or "active"."""
    t = cycle_time(hazard, hazard_ticks)
    if t < hazard.idle:
        return "idle"
    if t < hazard.idle + hazard.warning:
        return "warning"
    return "active"


def hit_area(hazard, hazard_ticks):
    """R41-R43: the (x, y, w, h) rectangle that can hit Albert, or None unless active."""
    if phase_of(hazard, hazard_ticks) != "active":
        return None
    if hazard.kind == "vent":
        w, h = config.JET_SIZE
        return (hazard.x + 2, hazard.top - h, w, h)
    if hazard.kind == "burner":
        return (hazard.x, hazard.top - 1, config.BURNER_WIDTH, 1)
    k = cycle_time(hazard, hazard_ticks) - hazard.idle - hazard.warning  # active update 0, 1, ...
    return (hazard.x, hazard.top + config.DRIP_SPEED * k, *config.DROP_SIZE)


def touches(hazard, hazard_ticks, player, platforms):
    """Whether an active hazard hits Albert this update."""
    area = hit_area(hazard, hazard_ticks)
    if area is None:
        return False
    x, y, w, h = area
    overlaps_x = player.x < x + w and player.x + player.width > x
    if hazard.kind == "burner":  # R42: only while standing on that cabinet
        return (
            player.on_ground
            and overlaps_x
            and any(
                p.y == hazard.top and p.x <= x < p.x + p.width and physics.is_standing_on(player, p)
                for p in platforms
            )
        )
    return overlaps_x and player.y < y + h and player.y + player.height > y
