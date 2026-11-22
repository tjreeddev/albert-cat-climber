"""R48 — The menu is navigated with single key presses."""

import pytest

from albert import config

DT = 1 / config.FPS


def tap(app, **keys):
    """Press keys for one update, then release them for one update."""
    from albert.menu import Keys

    app.update(Keys(**keys), DT)
    app.update(Keys(), DT)


def test_r48_down_moves_the_selection_and_wraps():
    from albert.menu import App

    app = App()
    seen = []
    for _ in range(4):
        tap(app, down=True)
        seen.append(app.selected)
    assert seen == [1, 2, 0, 1]


def test_r48_up_moves_the_selection_and_wraps():
    from albert.menu import App

    app = App()
    seen = []
    for _ in range(4):
        tap(app, up=True)
        seen.append(app.selected)
    assert seen == [2, 1, 0, 2]


def test_r48_up_and_down_together_do_nothing():
    from albert.menu import App

    app = App()
    tap(app, up=True, down=True)
    assert app.selected == 0


def test_r48_a_held_key_moves_only_once():
    from albert.menu import App, Keys

    app = App()
    for _ in range(30):
        app.update(Keys(down=True), DT)
    assert app.selected == 1


@pytest.mark.parametrize("key", ["left", "right", "jump", "restart", "menu"])
def test_r48_other_keys_do_not_change_the_selection(key):
    from albert.menu import App, Screen

    app = App()
    tap(app, **{key: True})
    assert app.selected == 0
    assert app.screen == Screen.MENU
    assert app.quit_requested is False


def test_r48_esc_held_from_the_game_does_not_quit_from_the_menu():
    from albert.menu import App, Keys, Screen

    app = App()
    tap(app, confirm=True)  # START
    assert app.screen == Screen.GAME
    for _ in range(20):  # hold Esc: leaves the game once, then keeps being held
        app.update(Keys(back=True), DT)
    assert app.screen == Screen.MENU
    assert app.quit_requested is False


def test_r48_confirm_held_from_the_controls_screen_does_not_act_on_the_menu():
    from albert.menu import App, Keys, Screen

    app = App()
    tap(app, down=True)
    tap(app, confirm=True)  # CONTROLS
    assert app.screen == Screen.CONTROLS
    for _ in range(20):  # hold confirm: back to the menu once, not into CONTROLS again
        app.update(Keys(confirm=True), DT)
    assert app.screen == Screen.MENU
