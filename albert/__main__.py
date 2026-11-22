"""Entry point: `python -m albert` opens the game window on the title menu (R8, R53)."""

import pygame

from albert import config, render
from albert.menu import App, Keys
from albert.sprites import load_sprites

# R53: which pygame keys set which Keys field (spec.md 13.2).
KEY_MAP = {
    "left": {pygame.K_LEFT, pygame.K_a},
    "right": {pygame.K_RIGHT, pygame.K_d},
    "up": {pygame.K_UP, pygame.K_w},
    "down": {pygame.K_DOWN, pygame.K_s},
    "jump": {pygame.K_SPACE, pygame.K_UP, pygame.K_w},
    "confirm": {pygame.K_RETURN, pygame.K_SPACE},
    "back": {pygame.K_ESCAPE, pygame.K_BACKSPACE},
    "restart": {pygame.K_r, pygame.K_RETURN},
    "menu": {pygame.K_m},
}
ALL_KEYS = set().union(*KEY_MAP.values())


def read_inputs(pressed):
    """Map a set of currently held pygame key codes to Keys."""
    return Keys(**{name: bool(pressed & codes) for name, codes in KEY_MAP.items()})


def run(max_frames=None, input_script=None):
    """Run the app loop and return the final App.

    max_frames:   stop after this many updates (None = until the window closes or QUIT)
    input_script: optional function frame_number -> Keys, used instead of
                  the keyboard (for headless tests); also disables frame pacing
    """
    pygame.init()
    window = pygame.display.set_mode(
        (config.INTERNAL_WIDTH * config.SCALE, config.INTERNAL_HEIGHT * config.SCALE)
    )
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()
    canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    sprites = load_sprites()
    app = App()
    dt = 1 / config.FPS

    frame = 0
    running = True
    while running and not app.quit_requested and (max_frames is None or frame < max_frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # closing the window always quits; Esc is up to the app
                running = False

        if input_script is not None:
            keys = input_script(frame)
        else:
            held = pygame.key.get_pressed()
            keys = read_inputs({key for key in ALL_KEYS if held[key]})

        app.update(keys, dt)
        if not app.quit_requested:
            render.draw_app(canvas, app, sprites)
            window.blit(render.scale_to_window(canvas), (0, 0))
            pygame.display.flip()

        if input_script is None:
            clock.tick(config.FPS)
        frame += 1

    pygame.quit()
    return app


def main():
    run()


if __name__ == "__main__":
    main()
