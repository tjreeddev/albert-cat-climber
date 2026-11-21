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
        self.drawers = [physics.MovingDrawer.from_definition(d) for d in self.level.drawers]  # R16/R20
        x, y = self.level.start
        self.player = physics.Player(x=x, y=y)
        self.player.on_ground = any(
            physics.is_standing_on(self.player, p) for p in self.level.platforms + self.drawers
        )
        self.state = GameState.PLAYING
        self.collected = set()  # R10/R13: treats collected this run
        self.camera_x, self.camera_y = self._camera_target()  # R22

    def update(self, inputs, dt):
        if self.state != GameState.PLAYING:
            # R4/R5: gameplay input is ignored; R6: restart only from here.
            if inputs.restart:
                self.restart()
            return

        self._move_drawers(dt)

        direction = int(inputs.right) - int(inputs.left)
        landed = physics.step(
            self.player, direction, inputs.jump, self.level.platforms + self.drawers, self.level.world_width, dt
        )

        self._collect_treats()  # R10: before the win check, so the winning frame counts

        if self.player.y > self.level.world_height:  # R4: top edge below the world
            self.state = GameState.LOST
        elif landed is self.level.goal_platform:  # R5: landed on the highest cabinet
            self.state = GameState.WON

        self.camera_x, self.camera_y = self._camera_target()

    @property
    def treats_collected(self):
        """R11: treats collected during the current run."""
        return len(self.collected)

    @property
    def treats_total(self):
        return len(self.level.treats)

    def visible_treats(self):
        """R10: treats not yet collected this run, in level order."""
        return [t for t in self.level.treats if t not in self.collected]

    def _move_drawers(self, dt):
        """R16/R18: move every drawer and carry Albert if he stands on one."""
        p = self.player
        ridden = next((d for d in self.drawers if p.on_ground and physics.is_standing_on(p, d)), None)
        for d in self.drawers:
            dx = physics.move_drawer(d, dt)
            if d is ridden:
                p.x = min(max(p.x + dx, 0.0), self.level.world_width - p.width)

    def _collect_treats(self):
        p = self.player
        for t in self.visible_treats():
            if p.x < t.x + t.width and p.x + p.width > t.x and p.y < t.y + t.height and p.y + p.height > t.y:
                self.collected.add(t)

    def _camera_target(self):
        """R22: centre Albert on both axes, each clamped to the world. Returns (x, y)."""
        p = self.player
        x = _clamp(p.x + p.width / 2 - config.INTERNAL_WIDTH / 2, self.level.world_width - config.INTERNAL_WIDTH)
        y = _clamp(p.y + p.height / 2 - config.INTERNAL_HEIGHT / 2, self.level.world_height - config.INTERNAL_HEIGHT)
        return x, y


def _clamp(value, highest):
    return min(max(value, 0), max(0, highest))


def hud_text(game):
    """R12: the HUD's treat counter, e.g. "2/5"."""
    return f"{game.treats_collected}/{game.treats_total}"
