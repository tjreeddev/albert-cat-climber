"""R52 — Menu screens are drawn over the animated kitchen (pure parts).

The headless render and font checks for R52 live in test_art_style.py.
"""

from albert import config

DT = 1 / config.FPS


def tap(app, **keys):
    from albert.menu import Keys

    app.update(Keys(**keys), DT)
    app.update(Keys(), DT)


def test_r52_backdrop_animates_on_the_menu_and_controls_screens():
    from albert.menu import App

    app = App()
    tap(app)
    assert app.backdrop.ticks == 2
    tap(app, down=True)
    tap(app, confirm=True)  # into CONTROLS on the first of these two updates
    assert app.backdrop.ticks == 6
    tap(app)
    assert app.backdrop.ticks == 8


def test_r52_backdrop_stops_while_in_a_game():
    from albert.menu import App

    app = App()
    tap(app, confirm=True)  # the confirming update is still on MENU
    ticks = app.backdrop.ticks
    tap(app)
    tap(app, right=True)
    assert app.backdrop.ticks == ticks


def test_r52_backdrop_is_never_played():
    from albert.game import Game
    from albert.menu import App, Keys

    app, fresh = App(), Game()
    for _ in range(200):
        app.update(Keys(right=True, jump=True), DT)
    b = app.backdrop
    assert (b.player.x, b.player.y) == (fresh.player.x, fresh.player.y)
    assert [d.x for d in b.drawers] == [d.x for d in fresh.drawers]
    assert b.hazard_ticks == 0
    assert b.state == fresh.state


def test_r52_menu_texts_match_the_spec():
    from albert import menu

    assert menu.TITLE == "ALBERT CAT CLIMBER"
    assert menu.MENU_HINT == "UP DOWN  ENTER"
    assert menu.OVERLAY_HINT == "R RESTART   M MENU"
