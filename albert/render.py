"""Drawing: world with camera offset, Albert, drawers, treats, decorations, particles,
HUD, overlays, and pixel-perfect scaling (R7)."""

import pygame

from albert import config, effects
from albert.game import GameState, hud_text
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


def _draw_hud(canvas, game, sprites):
    """R12: treat icon and "collected/total", fixed to the top-left of the screen."""
    icon = sprites["treat"]
    text = render_text(hud_text(game), C["text_white"])
    panel = pygame.Rect(2, 2, 3 + icon.get_width() + 3 + text.get_width() + 3, 12)
    pygame.draw.rect(canvas, C["panel"], panel)
    canvas.blit(icon, (panel.left + 3, panel.top + 2))
    canvas.blit(text, (panel.left + 3 + icon.get_width() + 3, panel.top + 4))


def _draw_decorations(canvas, game, sprites, kinds, on_screen, screen):
    """R29: decorations of the given kinds, showing their current animation frame."""
    for d in game.level.decorations:
        if d.kind in kinds:
            w, h = config.DECORATION_SIZES[d.kind]
            rect = on_screen(pygame.Rect(d.x, d.y, w, h))
            if rect.colliderect(screen):
                canvas.blit(sprites[f"{d.kind}_{effects.decoration_frame(d, game.ticks)}"], rect)


def _blit_strip(canvas, strip, left, top, offset, right):
    """Draw a horizontally looping strip shifted right by `offset` px, from `left` to `right`."""
    loop = strip.get_width()
    for x in range(left - loop + offset, right, loop):
        canvas.blit(strip, (x, top))


def _draw_window(canvas, item, rect, game, sprites):
    """R35-R37: sky, drifting clouds, the section's animated view, then curtains and frame."""
    clouds, view_frame, birds, curtain = effects.scenery_anim(item, game.ticks)
    f = config.WINDOW_FRAME
    glass = rect.inflate(-2 * f, -2 * f)
    view = item.view

    previous_clip = canvas.get_clip()
    canvas.set_clip(glass.clip(previous_clip))
    canvas.blit(sprites[f"scn_{view}_sky"], glass)
    _blit_strip(canvas, sprites["scn_clouds"], glass.left, glass.top + 4, clouds, glass.right)
    canvas.blit(sprites[f"scn_{view}_land"], glass)
    if view == "sky":
        _blit_strip(canvas, sprites["scn_sky_birds"], glass.left, glass.top + 30, birds, glass.right)
    else:
        canvas.blit(sprites[f"scn_{view}_{view_frame}"], glass)
    canvas.set_clip(previous_clip)

    left = sprites[f"scn_curtain_{curtain}"]
    canvas.blit(left, glass.topleft)
    canvas.blit(pygame.transform.flip(left, True, False), (glass.right - left.get_width(), glass.top))
    canvas.blit(sprites["scn_frame"], rect)


def _draw_scenery(canvas, game, sprites, on_screen, screen):
    """R33-R38: large background scenery, drawn right after the wallpaper."""
    for item in game.level.scenery:
        rect = on_screen(item)
        if not rect.colliderect(screen):
            continue
        if item.kind == "window":
            _draw_window(canvas, item, rect, game, sprites)
        elif item.kind == "tiles":
            _tile(canvas, sprites["scn_tile"], rect)
        elif item.kind == "picture":
            canvas.blit(sprites["scn_picture"], rect)
        else:  # plant
            canvas.blit(sprites[f"scn_plant_{effects.scenery_anim(item, game.ticks)[0]}"], rect)


def _draw_particles(canvas, game, cam_x, cam_y):
    """R30/R31: dust is a 1x1 pixel; a sparkle is a brass plus sign, then a white dot."""
    for p in game.particles:
        x, y = round(p.x) - cam_x, round(p.y) - cam_y
        if p.kind == "sparkle" and p.life > config.SPARKLE_LIFE / 2:
            pygame.draw.rect(canvas, C["brass"], (x - 1, y, 3, 1))
            pygame.draw.rect(canvas, C["brass"], (x, y - 1, 1, 3))
        else:
            colour = C["text_white"] if p.kind == "sparkle" else C["counter_shade"]
            pygame.draw.rect(canvas, colour, (x, y, 1, 1))


def draw(canvas, game, sprites):
    """Draw one frame of `game` onto the 320x180 internal canvas."""
    cam_x, cam_y = round(game.camera_x), round(game.camera_y)  # R22: scrolls on both axes
    screen = canvas.get_rect()

    def on_screen(thing):
        return pygame.Rect(round(thing.x) - cam_x, round(thing.y) - cam_y, round(thing.width), round(thing.height))

    # Wallpaper, scrolled with the camera on both axes.
    bg = sprites["background"]
    ox, oy = -(cam_x % bg.get_width()), -(cam_y % bg.get_height())
    _tile(canvas, bg, pygame.Rect(ox, oy, config.INTERNAL_WIDTH - ox, config.INTERNAL_HEIGHT - oy))

    # Background scenery (R33-R38): windows with outdoor views, tiles, pictures, plants.
    _draw_scenery(canvas, game, sprites, on_screen, screen)

    # Wall clocks (R28), in front of the scenery and behind everything else.
    _draw_decorations(canvas, game, sprites, {"clock"}, on_screen, screen)

    # Cabinets.
    for p in game.level.platforms:
        rect = on_screen(p)
        if rect.colliderect(screen):
            _tile(canvas, sprites["cabinet"], rect)

    # Moving drawers (R15), at their current positions.
    for d in game.drawers:
        rect = on_screen(d)
        if rect.colliderect(screen):
            canvas.blit(sprites["drawer"], rect)

    # Mugs and pots on the cabinets (R28).
    _draw_decorations(canvas, game, sprites, {"mug", "pot"}, on_screen, screen)

    # Treats not yet collected this run (R10).
    for t in game.visible_treats():
        rect = on_screen(t)
        if rect.colliderect(screen):
            canvas.blit(sprites["treat"], rect)

    # Albert.
    player = game.player
    canvas.blit(_cat_frame(player, sprites), on_screen(player))

    # Landing dust and treat sparkles (R30/R31), in front of Albert.
    _draw_particles(canvas, game, cam_x, cam_y)

    _draw_hud(canvas, game, sprites)

    if game.state == GameState.WON:
        _draw_overlay(canvas, "YOU WIN!", C["win_green"])
    elif game.state == GameState.LOST:
        _draw_overlay(canvas, "YOU LOSE", C["lose_red"])
