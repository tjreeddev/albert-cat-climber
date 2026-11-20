"""R14 — Treats are optional: Albert can win without collecting every treat."""


def land_on_goal(game, run_frames):
    goal = game.level.goal_platform
    p = game.player
    p.x = goal.x + goal.width / 2 - p.width / 2
    p.y = goal.y - p.height - 5
    p.vx = p.vy = 0
    p.on_ground = False
    run_frames(game, 60)


def collect(game, run_frames, treats):
    for t in treats:
        p = game.player
        p.x = t.x
        p.y = t.y + t.height - p.height
        p.vx = p.vy = 0
        run_frames(game, 1)


def test_r14_winning_with_no_treats(default_game, run_frames):
    from albert.game import GameState

    land_on_goal(default_game, run_frames)
    assert default_game.state == GameState.WON
    assert default_game.treats_collected == 0


def test_r14_winning_with_some_treats(default_game, run_frames):
    from albert.game import GameState

    collect(default_game, run_frames, default_game.level.treats[:2])
    land_on_goal(default_game, run_frames)
    assert default_game.state == GameState.WON
    assert default_game.treats_collected == 2


def test_r14_collecting_every_treat_does_not_win(default_game, run_frames):
    from albert.game import GameState

    collect(default_game, run_frames, default_game.level.treats)
    run_frames(default_game, 30)
    assert default_game.treats_collected == default_game.treats_total
    assert default_game.state == GameState.PLAYING
