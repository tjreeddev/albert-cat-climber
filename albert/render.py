"""Drawing: world with camera offset, Albert, overlays, and pixel-perfect scaling (R7)."""

import pygame

from albert import config
from albert.game import GameState
from albert.sprites import render_text

C = config.COLORS


def scale_to_window(surface):
    """Whole-number nearest-neighbour upscale (pygame.transform.scale never smooths)."""
    return pygame.transform.scale(
        surface, (surface.get_width() * config.SCALE, surface.get_height() * config.SCALE)
    )


def _tile(canvas, tile, rect):
    """Fill `rect` on the canvas by repeating `tile`, clipped to the rect."""
    previous_clip = canvas.get_clip()
    canvas.set_clip(rect.clip(previous_clip))
    tw, th = tile.get_size()
    for ty in range(rect.top, rect.bottom, th):
        for tx in range(rect.left, rect.right, tw):
            canvas.blit(tile, (tx, ty))
    canvas.set_clip(previous_clip)


def _cat_frame(player, sprites):
    if not player.on_ground:
        name = "cat_jump"
    elif player.vx:
        name = "cat_walk_1" if int(player.walk_time * 8) % 2 == 0 else "cat_walk_2"
    else:
        name = "cat_idle"
    frame = sprites[name]
    return pygame.transform.flip(frame, True, False) if player.facing < 0 else frame


def _draw_overlay(canvas, title, colour):
    panel = pygame.Rect(0, 0, 200, 52)
    panel.center = (config.INTERNAL_WIDTH // 2, config.INTERNAL_HEIGHT // 2)
    pygame.draw.rect(canvas, C["panel"], panel)
    pygame.draw.rect(canvas, colour, panel, 2)

    heading = render_text(title, colour, scale=2)
    canvas.blit(heading, heading.get_rect(midtop=(panel.centerx, panel.top + 10)))
    hint = render_text("PRESS R TO RESTART", C["text_white"])
    canvas.blit(hint, hint.get_rect(midbottom=(panel.centerx, panel.bottom - 10)))


def draw(canvas, game, sprites):
    """Draw one frame of `game` onto the 320x180 internal canvas."""
    cam = round(game.camera_y)

    # Wallpaper, scrolled with the camera.
    bg = sprites["background"]
    offset = -(cam % bg.get_height())
    _tile(canvas, bg, pygame.Rect(0, offset, config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT - offset))

    # Cabinets.
    for p in game.level.platforms:
        rect = pygame.Rect(round(p.x), round(p.y) - cam, round(p.width), round(p.height))
        if rect.colliderect(canvas.get_rect()):
            _tile(canvas, sprites["cabinet"], rect)

    # Albert.
    player = game.player
    canvas.blit(_cat_frame(player, sprites), (round(player.x), round(player.y) - cam))

    if game.state == GameState.WON:
        _draw_overlay(canvas, "YOU WIN!", C["win_green"])
    elif game.state == GameState.LOST:
        _draw_overlay(canvas, "YOU LOSE", C["lose_red"])
