"""Game state: playing, winning, losing, restarting and the camera.

Pure Python: must not import pygame.
"""

from dataclasses import dataclass
from enum import Enum

from albert import config, physics
from albert.level import build_level


class GameState(Enum):
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


@dataclass
class Inputs:
    left: bool = False
    right: bool = False
    jump: bool = False
    restart: bool = False


class Game:
    def __init__(self, level=None):
        self.level = level if level is not None else build_level()
        self.restart()

    def restart(self):
        """R6: put everything back to the starting state."""
        x, y = self.level.start
        self.player = physics.Player(x=x, y=y)
        self.player.on_ground = any(physics.is_standing_on(self.player, p) for p in self.level.platforms)
        self.state = GameState.PLAYING
        self.camera_y = self._camera_target()

    def update(self, inputs, dt):
        if self.state != GameState.PLAYING:
            # R4/R5: gameplay input is ignored; R6: restart only from here.
            if inputs.restart:
                self.restart()
            return

        direction = int(inputs.right) - int(inputs.left)
        landed = physics.step(
            self.player, direction, inputs.jump, self.level.platforms, self.level.world_width, dt
        )

        if self.player.y > self.level.world_height:  # R4: top edge below the world
            self.state = GameState.LOST
        elif landed is self.level.goal_platform:  # R5: landed on the highest cabinet
            self.state = GameState.WON

        self.camera_y = self._camera_target()

    def _camera_target(self):
        """Centre Albert vertically, clamped to the world."""
        target = self.player.y + self.player.height / 2 - config.INTERNAL_HEIGHT / 2
        lowest = max(0, self.level.world_height - config.INTERNAL_HEIGHT)
        return min(max(target, 0), lowest)
