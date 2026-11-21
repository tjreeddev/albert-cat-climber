"""R20 — Drawers don't change the win, lose, treat or restart rules."""

from albert import config

Y = 300


def drawer_state(game):
    return [(d.x, d.y, d.direction) for d in game.drawers]


def start_state(game):
    return [(d.start_x, d.y, d.start_direction) for d in game.level.drawers]


def drawer_data(level):
    return [
        (d.min_x, d.max_x, d.y, d.width, d.height, d.speed, d.start_x, d.start_direction) for d in level.drawers
    ]


def lose(game, run_frames):
    from albert.game import GameState

    game.player.y = game.level.world_height + 1
    game.player.on_ground = False
    run_frames(game, 1)
    assert game.state == GameState.LOST


def win(game, run_frames):
    from albert.game import GameState

    goal = game.level.goal_platform
    p = game.player
    p.x = goal.x + goal.width / 2 - p.width / 2
    p.y = goal.y - p.height - 5
    p.vx = p.vy = 0
    p.on_ground = False
    run_frames(game, 60)
    assert game.state == GameState.WON


def test_r20_landing_on_a_drawer_above_every_cabinet_does_not_win(make_game, run_frames):
    from albert.game import GameState

    d = dict(min_x=100, max_x=180, y=Y, speed=40.0, start_x=140, start_direction=1)
    game = make_game([(0, 600, 320, 16)], start=(150, 200), add_decoy_goal=False, drawers=[d])
    for _ in range(120):
        run_frames(game, 1)
    assert game.player.on_ground and game.player.y + game.player.height == Y
    assert game.state == GameState.PLAYING


def test_r20_landing_on_a_default_drawer_does_not_win(default_game, run_frames):
    from albert.game import GameState

    for moving in default_game.drawers:
        p = default_game.player
        p.x, p.y = moving.x + 8, moving.y - p.height - 4
        p.vx = p.vy = 0
        p.on_ground = False
        run_frames(default_game, 10)
        assert p.on_ground
        assert default_game.state == GameState.PLAYING


def test_r20_falling_off_a_drawer_out_of_the_world_loses(make_game, run_frames):
    from albert.game import GameState

    d = dict(min_x=-40, max_x=40, y=Y, speed=40.0, start_x=0, start_direction=-1)
    game = make_game([], start=(0, Y - config.PLAYER_HEIGHT), world_height=400, drawers=[d])
    run_frames(game, 240)
    assert game.state == GameState.LOST


def test_r20_restart_after_losing_resets_drawers(default_game, run_frames):
    from albert.game import GameState

    run_frames(default_game, 50)
    assert drawer_state(default_game) != start_state(default_game)
    lose(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert drawer_state(default_game) == start_state(default_game)


def test_r20_restart_after_winning_resets_drawers(default_game, run_frames):
    from albert.game import GameState

    run_frames(default_game, 50)
    win(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert drawer_state(default_game) == start_state(default_game)


def test_r20_restart_key_during_play_does_not_reset_drawers(default_game, run_frames):
    run_frames(default_game, 50)
    before = drawer_state(default_game)
    run_frames(default_game, 1, restart=True)
    after = drawer_state(default_game)
    assert after != start_state(default_game)
    assert after != before, "drawers should keep moving normally"


def test_r20_playing_does_not_change_level_drawer_data(default_game, run_frames):
    before = drawer_data(default_game.level)
    run_frames(default_game, 300, right=True, jump=True)
    lose(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert drawer_data(default_game.level) == before


def test_r20_drawers_do_not_affect_treats_or_hud(default_game, run_frames):
    from albert.game import hud_text

    run_frames(default_game, 300)
    assert default_game.treats_total == 5
    assert default_game.treats_collected == 0
    assert default_game.visible_treats() == default_game.level.treats
    assert hud_text(default_game) == "0/5"
