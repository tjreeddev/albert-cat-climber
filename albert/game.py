"""Game state: playing, winning, losing, restarting and the camera.

Pure Python: must not import pygame.
"""

from dataclasses import dataclass
from enum import Enum

from albert import config, effects, hazards, physics
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
        self.ticks = 0  # R27: animation clock, in updates
        self.particles = []  # R30/R31: visual only, oldest first
        self.hazard_ticks = 0  # R40: gameplay hazard clock (PLAYING updates only)
        self.knockback_ticks = 0  # R44: updates of left/right override left
        self.knockback_dir = 0
        self.invulnerable_ticks = 0  # R44: updates until a hazard can hit again

    def update(self, inputs, dt):
        # R27-R29: the animation clock and existing particles run in every state.
        # Particles spawned below start moving on the next update.
        self.ticks += 1
        effects.step_particles(self.particles, dt)

        if self.state != GameState.PLAYING:
            # R4/R5: gameplay input is ignored; R6: restart only from here.
            if inputs.restart:
                self.restart()
            return

        # R40/R44: hazard clock, invulnerability countdown, knockback override.
        self.hazard_ticks += 1
        if self.invulnerable_ticks > 0:
            self.invulnerable_ticks -= 1
        direction, jump = int(inputs.right) - int(inputs.left), inputs.jump
        if self.knockback_ticks > 0:
            direction, jump = self.knockback_dir, False
            self.knockback_ticks -= 1

        self._move_drawers(dt)

        was_standing = self.player.on_ground
        landed = physics.step(
            self.player, direction, jump, self.level.platforms + self.drawers, self.level.world_width, dt
        )
        if landed is not None and not was_standing:  # R30: airborne -> standing
            self._spawn(effects.dust_particles(self.player))

        self._collect_treats()  # R10: before the win check, so the winning frame counts

        if landed is not self.level.goal_platform:  # R44: a win takes priority over a hit
            self._check_hazards()

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
                self._spawn(effects.sparkle_particles(t))  # R31

    def _check_hazards(self):
        """R41-R44: the first active hazard touching Albert knocks him back."""
        if self.invulnerable_ticks > 0:
            return
        p = self.player
        for h in self.level.hazards:
            if hazards.touches(h, self.hazard_ticks, p, self.level.platforms):
                x, _, w, _ = hazards.hit_area(h, self.hazard_ticks)
                self.knockback_dir = 1 if p.x + p.width / 2 >= x + w / 2 else -1
                p.vy, p.on_ground = -config.KNOCKBACK_SPEED, False
                self.knockback_ticks = config.KNOCKBACK_TICKS
                self.invulnerable_ticks = config.INVULNERABLE_TICKS
                self._spawn(effects.puff_particles(p))
                return

    def _spawn(self, new):
        """Add particles, dropping the oldest beyond MAX_PARTICLES (R31)."""
        self.particles.extend(new)
        del self.particles[: max(0, len(self.particles) - config.MAX_PARTICLES)]

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
