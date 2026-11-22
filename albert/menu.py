"""The title menu, controls screen and the app that switches between them and a game (Round 7, R47-R52).

Pure Python: must not import pygame. Screens react to key *presses* (held now,
not held on the previous update), so a held key acts only once. The game itself
knows nothing about menus.
"""

from dataclasses import dataclass, fields
from enum import Enum

from albert.game import Game, GameState, Inputs

OPTIONS = ("START", "CONTROLS", "QUIT")
TITLE = "ALBERT CAT CLIMBER"
MENU_HINT = "UP DOWN  ENTER"
CONTROLS_TITLE = "CONTROLS"
CONTROLS_LINES = (
    "MOVE    LEFT RIGHT / A D",
    "JUMP    SPACE UP / W",
    "RESTART R / ENTER",
    "MENU    M / ESC",
    "BACK    ESC",
)
CONTROLS_HINT = "ESC BACK"
OVERLAY_HINT = "R RESTART   M MENU"


@dataclass(frozen=True)
class Keys:
    """Which keys are held this update (see __main__.read_inputs for the mapping)."""

    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    jump: bool = False
    confirm: bool = False
    back: bool = False
    restart: bool = False
    menu: bool = False

    def any_held(self):
        return any(getattr(self, f.name) for f in fields(self))


class Screen(Enum):
    MENU = "menu"
    CONTROLS = "controls"
    GAME = "game"


class App:
    def __init__(self):
        self.screen = Screen.MENU
        self.selected = 0
        self.game = None
        self.quit_requested = False
        self.backdrop = Game()  # R52: the kitchen behind the menu; never played
        self._previous = Keys()
        self._gate = False  # R51: ignore game input until every key is released

    def update(self, keys, dt):
        """Handle one update on the screen showing when it starts (R48)."""
        pressed = Keys(**{f.name: getattr(keys, f.name) and not getattr(self._previous, f.name) for f in fields(keys)})
        self._previous = keys
        if self.screen == Screen.MENU:
            self.backdrop.ticks += 1
            self._update_menu(pressed)
        elif self.screen == Screen.CONTROLS:
            self.backdrop.ticks += 1
            if pressed.back or pressed.confirm:  # R50
                self.screen = Screen.MENU
        else:
            self._update_game(keys, pressed, dt)

    def _update_menu(self, pressed):
        if pressed.up != pressed.down:  # R48: both at once cancel out
            self.selected = (self.selected + (1 if pressed.down else -1)) % len(OPTIONS)
        if pressed.back:  # R49
            self.quit_requested = True
        elif pressed.confirm:
            choice = OPTIONS[self.selected]
            if choice == "START":
                self.game, self.screen, self._gate = Game(), Screen.GAME, True
            elif choice == "CONTROLS":
                self.screen = Screen.CONTROLS
            else:
                self.quit_requested = True

    def _update_game(self, keys, pressed, dt):
        finished = self.game.state in (GameState.WON, GameState.LOST)
        if pressed.back or (pressed.menu and finished):  # R51
            self.game, self.screen, self.selected = None, Screen.MENU, 0
            return
        if self._gate and not keys.any_held():
            self._gate = False
        inputs = Inputs() if self._gate else Inputs(keys.left, keys.right, keys.jump, keys.restart)
        self.game.update(inputs, dt)
