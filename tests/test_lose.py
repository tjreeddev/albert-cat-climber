"""R4 — If Albert falls below the playable area, the player loses."""

from albert import config


def test_r4_falling_below_the_world_bottom_loses(make_game, run_frames):
    from albert.game import GameState

    world_height = 300
    game = make_game([(0, 100, 40, 8)], start=(200, 150), world_height=world_height)

    for _ in range(600):
        run_frames(game, 1)
        if game.state == GameState.LOST:
            break
        # Not lost while any part of Albert is still inside the world.
        assert game.player.y <= world_height
    assert game.state == GameState.LOST
    assert game.player.y > world_height


def test_r4_default_level_dropping_below_world_bottom_loses(default_game, run_frames):
    from albert.game import GameState

    default_game.player.y = default_game.level.world_height + 1
    default_game.player.on_ground = False
    run_frames(default_game, 1)
    assert default_game.state == GameState.LOST


def test_r4_falling_onto_a_lower_cabinet_is_not_a_loss(make_game, run_frames):
    from albert.game import GameState

    upper = (100, 200, 60, 8)
    lower = (100, 400, 200, 8)
    game = make_game([upper, lower], start=(140, 200 - config.PLAYER_HEIGHT))

    run_frames(game, 30, right=True)
    run_frames(game, 120)
    assert game.state == GameState.PLAYING
    assert game.player.on_ground
    assert game.player.y + game.player.height == lower[1]


def test_r4_starting_the_game_is_not_a_loss(default_game):
    from albert.game import GameState

    assert default_game.state == GameState.PLAYING


def test_r4_input_is_ignored_after_losing(make_game, run_frames):
    from albert.game import GameState

    game = make_game([(0, 100, 40, 8)], start=(200, 150), world_height=300)
    run_frames(game, 600)
    assert game.state == GameState.LOST

    x_lost = game.player.x
    run_frames(game, 30, right=True, jump=True)
    assert game.state == GameState.LOST
    assert game.player.x == x_lost
