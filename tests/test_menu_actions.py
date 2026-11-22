"""R49 — Menu options start, show controls or quit."""

import pytest

from albert import config

DT = 1 / config.FPS


def tap(app, **keys):
    from albert.menu import Keys

    app.update(Keys(**keys), DT)
    app.update(Keys(), DT)


def snapshot(game):
    p = game.player
    return (
        (p.x, p.y, p.vx, p.vy, p.on_ground, p.facing),
        [(d.x, d.direction) for d in game.drawers],
        (game.camera_x, game.camera_y),
        game.state,
        game.ticks,
        game.hazard_ticks,
        game.knockback_ticks,
        game.invulnerable_ticks,
        set(game.collected),
        list(game.particles),
    )


def test_r49_start_begins_a_fresh_game():
    from albert.game import Game
    from albert.menu import App, Keys, Screen

    app = App()
    app.update(Keys(confirm=True), DT)
    assert app.screen == Screen.GAME
    assert isinstance(app.game, Game)
    assert app.game is not app.backdrop
    assert snapshot(app.game) == snapshot(Game())


def test_r49_controls_opens_the_controls_screen():
    from albert.menu import App, Screen

    app = App()
    tap(app, down=True)
    tap(app, confirm=True)
    assert app.screen == Screen.CONTROLS
    assert app.game is None


def test_r49_quit_requests_quit():
    from albert.menu import App

    app = App()
    tap(app, up=True)  # wraps to QUIT
    assert app.selected == 2
    tap(app, confirm=True)
    assert app.quit_requested is True


def test_r49_back_on_the_menu_requests_quit():
    from albert.menu import App

    app = App()
    tap(app, back=True)
    assert app.quit_requested is True


@pytest.mark.parametrize("key", ["left", "right", "up", "down", "jump", "restart", "menu"])
def test_r49_nothing_else_quits(key):
    from albert.menu import App

    app = App()
    for _ in range(3):
        tap(app, **{key: True})
    assert app.quit_requested is False
