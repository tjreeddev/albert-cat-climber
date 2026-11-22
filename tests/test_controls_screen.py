"""R50 — The controls screen lists the keys and goes back."""

import pytest

from albert import config

DT = 1 / config.FPS


def tap(app, **keys):
    from albert.menu import Keys

    app.update(Keys(**keys), DT)
    app.update(Keys(), DT)


def on_controls():
    from albert.menu import App, Screen

    app = App()
    tap(app, down=True)
    tap(app, confirm=True)
    assert app.screen == Screen.CONTROLS
    return app


@pytest.mark.parametrize("key", ["back", "confirm"])
def test_r50_back_or_confirm_returns_with_controls_selected(key):
    from albert.menu import Screen

    app = on_controls()
    tap(app, **{key: True})
    assert app.screen == Screen.MENU
    assert app.selected == 1
    assert app.quit_requested is False


@pytest.mark.parametrize("key", ["left", "right", "up", "down", "jump", "restart", "menu"])
def test_r50_other_keys_do_nothing(key):
    from albert.menu import Screen

    app = on_controls()
    tap(app, **{key: True})
    assert app.screen == Screen.CONTROLS
    assert app.selected == 1
    assert app.quit_requested is False


def test_r50_controls_text_matches_the_spec():
    from albert import menu

    assert menu.CONTROLS_TITLE == "CONTROLS"
    assert menu.CONTROLS_LINES == (
        "MOVE    LEFT RIGHT / A D",
        "JUMP    SPACE UP / W",
        "RESTART R / ENTER",
        "MENU    M / ESC",
        "BACK    ESC",
    )
    assert menu.CONTROLS_HINT == "ESC BACK"
