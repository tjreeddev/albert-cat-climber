"""R5 — The player wins by reaching (landing on) the highest cabinet platform."""

from albert import config

FLOOR = (0, 500, 320, 16)


def test_r5_goal_is_the_highest_cabinet():
    from albert.level import build_level

    level = build_level()
    highest_y = min(p.y for p in level.platforms)
    assert level.goal_platform.y == highest_y
    assert sum(1 for p in level.platforms if p.y == highest_y) == 1, "goal must be unique"


def test_r5_landing_on_the_goal_wins(make_game, run_frames):
    from albert.game import GameState

    goal = (100, 300, 60, 8)
    game = make_game([FLOOR, goal], start=(110, 250), add_decoy_goal=False)
    run_frames(game, 120)
    assert game.player.y + game.player.height == goal[1]
    assert game.state == GameState.WON


def test_r5_landing_on_another_cabinet_does_not_win(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=(150, 400))
    run_frames(game, 120)
    assert game.player.on_ground
    assert game.state == GameState.PLAYING


def test_r5_jumping_up_through_the_goal_does_not_win_on_the_way_up(make_game, run_frames):
    from albert.game import GameState

    goal_top = FLOOR[1] - config.PLAYER_HEIGHT - 10
    goal = (100, goal_top, 100, 8)
    game = make_game([FLOOR, goal], start=(130, FLOOR[1] - config.PLAYER_HEIGHT), add_decoy_goal=False)

    run_frames(game, 1, jump=True)
    while game.player.vy < 0:
        assert game.state == GameState.PLAYING
        run_frames(game, 1)


def test_r5_touching_the_goal_from_the_side_does_not_win(make_game, run_frames):
    from albert.game import GameState

    # Goal block sits on the floor at Albert's height; walking into its side
    # is not landing on it.
    goal = (200, FLOOR[1] - config.PLAYER_HEIGHT, 40, config.PLAYER_HEIGHT)
    game = make_game([FLOOR, goal], start=(100, FLOOR[1] - config.PLAYER_HEIGHT), add_decoy_goal=False)
    run_frames(game, 120, right=True)
    assert game.state == GameState.PLAYING


def test_r5_default_level_landing_on_goal_wins(default_game, run_frames):
    from albert.game import GameState

    goal = default_game.level.goal_platform
    p = default_game.player
    p.x = goal.x + goal.width / 2 - p.width / 2
    p.y = goal.y - p.height - 5
    p.vx = p.vy = 0
    p.on_ground = False
    run_frames(default_game, 60)
    assert default_game.state == GameState.WON


def test_r5_input_is_ignored_after_winning(make_game, run_frames):
    from albert.game import GameState

    goal = (100, 300, 60, 8)
    game = make_game([FLOOR, goal], start=(110, 250), add_decoy_goal=False)
    run_frames(game, 120)
    assert game.state == GameState.WON

    x_won, y_won = game.player.x, game.player.y
    run_frames(game, 30, right=True, jump=True)
    assert game.state == GameState.WON
    assert (game.player.x, game.player.y) == (x_won, y_won)
