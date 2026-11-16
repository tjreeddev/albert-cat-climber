"""Entry point: `python -m albert` opens the game window (R8)."""

import pygame

from albert import config, render
from albert.game import Game, Inputs
from albert.sprites import load_sprites

LEFT_KEYS = {pygame.K_LEFT, pygame.K_a}
RIGHT_KEYS = {pygame.K_RIGHT, pygame.K_d}
JUMP_KEYS = {pygame.K_SPACE, pygame.K_UP, pygame.K_w}
RESTART_KEYS = {pygame.K_r, pygame.K_RETURN}
ALL_KEYS = LEFT_KEYS | RIGHT_KEYS | JUMP_KEYS | RESTART_KEYS


def read_inputs(pressed):
    """Map a set of currently held pygame key codes to game Inputs."""
    return Inputs(
        left=bool(pressed & LEFT_KEYS),
        right=bool(pressed & RIGHT_KEYS),
        jump=bool(pressed & JUMP_KEYS),
        restart=bool(pressed & RESTART_KEYS),
    )


def run(max_frames=None, input_script=None):
    """Run the game loop and return the final Game.

    max_frames:   stop after this many updates (None = until the window closes)
    input_script: optional function frame_number -> Inputs, used instead of
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
    game = Game()
    dt = 1 / config.FPS

    frame = 0
    running = True
    while running and (max_frames is None or frame < max_frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        if input_script is not None:
            inputs = input_script(frame)
        else:
            held = pygame.key.get_pressed()
            inputs = read_inputs({key for key in ALL_KEYS if held[key]})

        game.update(inputs, dt)
        render.draw(canvas, game, sprites)
        window.blit(render.scale_to_window(canvas), (0, 0))
        pygame.display.flip()

        if input_script is None:
            clock.tick(config.FPS)
        frame += 1

    pygame.quit()
    return game


def main():
    run()


if __name__ == "__main__":
    main()
