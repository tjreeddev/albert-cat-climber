"""R51 — Leaving a game returns to the menu."""

import pytest

from albert import config

DT = 1 / config.FPS


def tap(app, **keys):
    from albert.menu import Keys

    app.update(Keys(**keys), DT)
    app.update(Keys(), DT)


def started():
    """An app in a game, past the start gate."""
    from albert.menu import App, Screen

    app = App()
    tap(app, confirm=True)
    assert app.screen == Screen.GAME
    return app


@pytest.mark.parametrize("state", ["PLAYING", "WON", "LOST"])
def test_r51_back_returns_to_the_menu_from_any_game_state(state):
    from albert.game import GameState
    from albert.menu import Screen

    app = started()
    app.game.state = GameState[state]
    tap(app, back=True)
    assert app.screen == Screen.MENU
    assert app.game is None
    assert app.selected == 0


@pytest.mark.parametrize("state", ["WON", "LOST"])
def test_r51_m_returns_to_the_menu_from_win_or_lose(state):
    from albert.game import GameState
    from albert.menu import Screen

    app = started()
    app.game.state = GameState[state]
    tap(app, menu=True)
    assert app.screen == Screen.MENU
    assert app.game is None


def test_r51_m_does_nothing_while_playing():
    from albert.menu import Screen

    app = started()
    game, ticks = app.game, app.game.ticks
    tap(app, menu=True)
    assert app.screen == Screen.GAME
    assert app.game is game
    assert game.ticks == ticks + 2, "the game keeps being updated"


def test_r51_restart_still_works_on_the_lose_screen():
    from albert.game import GameState
    from albert.menu import Screen

    app = started()
    game = app.game
    game.player.y = game.level.world_height + 1
    game.player.on_ground = False
    tap(app)
    assert game.state == GameState.LOST
    tap(app, restart=True)
    assert app.screen == Screen.GAME
    assert app.game is game
    assert game.state == GameState.PLAYING


def test_r51_starting_again_gives_a_fresh_game():
    from albert.game import Game
    from albert.menu import Keys

    app = started()
    for _ in range(90):
        app.update(Keys(right=True), DT)
    first = app.game
    tap(app, back=True)
    tap(app, confirm=True)
    assert app.game is not first
    assert (app.game.player.x, app.game.player.y) == (Game().player.x, Game().player.y)
    assert app.game.ticks == 1, "one update since the fresh start"


def test_r51_start_gate_ignores_held_keys_until_all_are_released():
    from albert.menu import App, Keys

    app = App()
    space = Keys(confirm=True, jump=True)  # Space is both confirm and jump
    app.update(space, DT)  # chooses START
    game = app.game
    start_x = game.player.x
    for _ in range(10):
        app.update(Keys(confirm=True, jump=True, right=True), DT)
    assert game.hazard_ticks == 10, "time passes during the gate"
    assert game.player.on_ground and game.player.vy == 0, "the held Space didn't jump"
    assert game.player.x == start_x, "held keys are ignored"
    app.update(Keys(), DT)  # everything released: the gate opens
    app.update(Keys(jump=True), DT)
    assert game.player.vy < 0, "jump works once the gate is open"
