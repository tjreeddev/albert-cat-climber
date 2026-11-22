"""R47 — The game starts on the title menu."""


def test_r47_app_starts_on_the_menu_with_start_selected():
    from albert.menu import OPTIONS, App, Screen

    app = App()
    assert app.screen == Screen.MENU
    assert OPTIONS == ("START", "CONTROLS", "QUIT")
    assert app.selected == 0
    assert app.game is None
    assert app.quit_requested is False


def test_r47_the_backdrop_is_a_game_at_its_starting_state():
    from albert.game import Game, GameState
    from albert.menu import App

    backdrop, fresh = App().backdrop, Game()
    assert isinstance(backdrop, Game)
    assert backdrop.state == GameState.PLAYING
    assert (backdrop.player.x, backdrop.player.y) == (fresh.player.x, fresh.player.y)
    assert (backdrop.camera_x, backdrop.camera_y) == (fresh.camera_x, fresh.camera_y)
    assert backdrop.ticks == 0 and backdrop.hazard_ticks == 0


def test_r47_game_itself_still_starts_playing():
    from albert.game import Game, GameState

    assert Game().state == GameState.PLAYING
