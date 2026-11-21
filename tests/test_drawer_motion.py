"""R16 — Drawers move horizontally back and forth."""

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
START = (150, FLOOR[1] - config.PLAYER_HEIGHT)  # Albert waits on the floor, away from the drawer
SPEED = 40.0


def drawer(start_x=150, start_direction=1, min_x=100, max_x=200, y=300, speed=SPEED):
    return dict(min_x=min_x, max_x=max_x, y=y, speed=speed, start_x=start_x, start_direction=start_direction)


def test_r16_drawer_moves_right_by_speed_times_dt(make_game, run_frames):
    game = make_game([FLOOR], start=START, drawers=[drawer(start_direction=1)])
    run_frames(game, 1)
    assert game.drawers[0].x == pytest.approx(150 + SPEED / config.FPS)


def test_r16_drawer_moves_left_by_speed_times_dt(make_game, run_frames):
    game = make_game([FLOOR], start=START, drawers=[drawer(start_direction=-1)])
    run_frames(game, 30)
    assert game.drawers[0].x == pytest.approx(150 - SPEED * 30 / config.FPS)


def test_r16_drawer_reverses_at_max_x(make_game, run_frames):
    game = make_game([FLOOR], start=START, drawers=[drawer(start_x=199.9, start_direction=1)])
    run_frames(game, 1)
    d = game.drawers[0]
    assert d.x == pytest.approx(200)
    assert d.direction == -1
    run_frames(game, 1)
    assert d.x < 200


def test_r16_drawer_reverses_at_min_x(make_game, run_frames):
    game = make_game([FLOOR], start=START, drawers=[drawer(start_x=100.1, start_direction=-1)])
    run_frames(game, 1)
    d = game.drawers[0]
    assert d.x == pytest.approx(100)
    assert d.direction == 1
    run_frames(game, 1)
    assert d.x > 100


def test_r16_drawer_stays_in_range_and_keeps_its_height(make_game, run_frames):
    game = make_game([FLOOR], start=START, drawers=[drawer()])
    d = game.drawers[0]
    seen_directions = set()
    for _ in range(1000):
        run_frames(game, 1)
        assert 100 <= d.x <= 200
        assert d.y == 300
        seen_directions.add(d.direction)
    assert seen_directions == {-1, 1}


def test_r16_default_drawers_move_back_and_forth(default_game, run_frames):
    lo = [d.x for d in default_game.drawers]
    hi = list(lo)
    for _ in range(600):
        run_frames(default_game, 1)
        for i, d in enumerate(default_game.drawers):
            lo[i], hi[i] = min(lo[i], d.x), max(hi[i], d.x)
    for i, spec in enumerate(default_game.level.drawers):
        assert lo[i] == pytest.approx(spec.min_x)
        assert hi[i] == pytest.approx(spec.max_x)


def test_r16_drawer_motion_is_deterministic():
    from albert.game import Game, Inputs

    a, b = Game(), Game()
    for _ in range(500):
        a.update(Inputs(), 1 / config.FPS)
        b.update(Inputs(), 1 / config.FPS)
    assert [(d.x, d.direction) for d in a.drawers] == [(d.x, d.direction) for d in b.drawers]


@pytest.mark.parametrize("state_name", ["WON", "LOST"])
def test_r16_drawers_do_not_move_after_the_game_ends(make_game, run_frames, state_name):
    from albert.game import GameState

    game = make_game([FLOOR], start=START, drawers=[drawer()])
    run_frames(game, 10)
    game.state = GameState[state_name]
    before = [(d.x, d.direction) for d in game.drawers]
    run_frames(game, 60, left=True, jump=True)
    assert [(d.x, d.direction) for d in game.drawers] == before
