"""R17 — Drawers are one-way platforms (the same landing rules as cabinets, R3)."""

import pytest

from albert import config
from albert.physics import is_standing_on

FLOOR = (0, 500, 320, 16)


def drawer(start_x, y, min_x=None, max_x=None, speed=40.0, start_direction=1):
    return dict(
        min_x=start_x if min_x is None else min_x,
        max_x=start_x if max_x is None else max_x,
        y=y,
        speed=speed,
        start_x=start_x,
        start_direction=start_direction,
    )


def run_until_grounded(game, run_frames, max_frames=600, **keys):
    for _ in range(max_frames):
        run_frames(game, 1, **keys)
        if game.player.on_ground:
            return
    pytest.fail("Albert never landed")


def test_r17_falling_onto_a_moving_drawer_lands_on_its_top(make_game, run_frames):
    game = make_game([], start=(140, 200), drawers=[drawer(130, 300, min_x=110, max_x=150)])
    run_until_grounded(game, run_frames)
    d = game.drawers[0]
    assert game.player.y + game.player.height == pytest.approx(d.y)
    assert game.player.vy == 0
    assert is_standing_on(game.player, d)


def test_r17_fast_fall_does_not_pass_through_a_drawer(make_game, run_frames):
    game = make_game([], start=(110, 100), drawers=[drawer(100, 4000)], world_height=5000)
    run_until_grounded(game, run_frames, max_frames=3000)
    assert game.player.y + game.player.height == pytest.approx(4000)


def test_r17_albert_jumps_up_through_a_drawer_and_lands_on_it(make_game, run_frames):
    top = FLOOR[1] - config.PLAYER_HEIGHT - 10
    game = make_game([FLOOR], start=(130, FLOOR[1] - config.PLAYER_HEIGHT), drawers=[drawer(122, top)])

    run_frames(game, 1, jump=True)
    highest_feet = game.player.y + game.player.height
    for _ in range(180):
        run_frames(game, 1)
        highest_feet = min(highest_feet, game.player.y + game.player.height)

    assert highest_feet < top, "Albert was blocked from below"
    assert game.player.on_ground
    assert game.player.y + game.player.height == pytest.approx(top)


def test_r17_a_drawer_never_pushes_albert_sideways(make_game, run_frames):
    # The drawer slides left straight through Albert's body; he stays put on the floor.
    start = (150, FLOOR[1] - config.PLAYER_HEIGHT)
    game = make_game(
        [FLOOR], start=start, drawers=[drawer(200, 490, min_x=60, max_x=200, start_direction=-1)]
    )
    run_frames(game, 150)
    assert (game.player.x, game.player.y) == start
    assert game.player.on_ground


def test_r17_walking_off_a_drawer_starts_a_fall(make_game, run_frames):
    game = make_game([], start=(110, 300 - config.PLAYER_HEIGHT), drawers=[drawer(100, 300)])
    run_frames(game, 1)
    assert game.player.on_ground
    run_frames(game, 60, right=True)
    assert not game.player.on_ground
    assert game.player.y > 300


def test_r17_falls_when_the_drawer_slides_out_from_under_him(make_game, run_frames):
    # Albert is pinned at the left wall while the drawer keeps sliding left past it.
    game = make_game(
        [], start=(0, 300 - config.PLAYER_HEIGHT), drawers=[drawer(0, 300, min_x=-40, max_x=40, start_direction=-1)]
    )
    run_frames(game, 1)
    assert game.player.on_ground
    run_frames(game, 60)
    assert not game.player.on_ground
    assert game.player.y > 300 - config.PLAYER_HEIGHT
