"""R13 — Restarting after winning or losing restores all treats and resets the count to zero."""


def collect(game, run_frames, treats):
    """Put Albert on each treat (standing on its cabinet) for one update."""
    for t in treats:
        p = game.player
        p.x = t.x
        p.y = t.y + t.height - p.height
        p.vx = p.vy = 0
        run_frames(game, 1)


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


def treat_data(level):
    return [(t.x, t.y, t.width, t.height) for t in level.treats]


def test_r13_restart_after_losing_restores_treats(default_game, run_frames):
    from albert.game import GameState

    collect(default_game, run_frames, default_game.level.treats[:3])
    assert default_game.treats_collected == 3
    lose(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert default_game.treats_collected == 0
    assert default_game.visible_treats() == default_game.level.treats


def test_r13_restart_after_winning_restores_treats(default_game, run_frames):
    from albert.game import GameState

    collect(default_game, run_frames, default_game.level.treats)
    assert default_game.treats_collected == default_game.treats_total
    win(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert default_game.state == GameState.PLAYING
    assert default_game.treats_collected == 0
    assert default_game.visible_treats() == default_game.level.treats


def test_r13_restart_key_during_play_keeps_treats(default_game, run_frames):
    collect(default_game, run_frames, default_game.level.treats[:1])
    run_frames(default_game, 1, restart=True)
    assert default_game.treats_collected == 1
    assert len(default_game.visible_treats()) == default_game.treats_total - 1


def test_r13_treats_can_be_collected_again_after_restart(default_game, run_frames):
    collect(default_game, run_frames, default_game.level.treats[:2])
    lose(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    collect(default_game, run_frames, default_game.level.treats[:1])
    assert default_game.treats_collected == 1


def test_r13_playing_does_not_change_level_treat_data(default_game, run_frames):
    before = treat_data(default_game.level)
    collect(default_game, run_frames, default_game.level.treats)
    win(default_game, run_frames)
    run_frames(default_game, 1, restart=True)
    assert treat_data(default_game.level) == before
