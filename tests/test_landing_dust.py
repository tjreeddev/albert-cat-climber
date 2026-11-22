"""R30 — Landing makes a small dust puff."""

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
START = (100, FLOOR[1] - config.PLAYER_HEIGHT)  # standing on FLOOR
ABOVE = (100, 440)  # in the air above FLOOR


def flat(rows):
    """Flatten a list of tuples for pytest.approx, which doesn't compare nested sequences."""
    return [v for row in rows for v in row]


def dust(game):
    return [p for p in game.particles if p.kind == "dust"]


def step_until_standing(game, run_frames, limit=180):
    """Advance one update at a time until Albert stands; fail if he never does."""
    for _ in range(limit):
        assert not dust(game), "dust appeared before landing"
        run_frames(game, 1)
        if game.player.on_ground:
            return
    pytest.fail("Albert never landed")


def expected_dust(player):
    left, right, y = player.x, player.x + player.width, player.y + player.height - 1
    xs = [left + 2, left + 4, right - 4, right - 2]
    vs = [(-30, -10), (-15, -10), (15, -10), (30, -10)]
    return [(x, y, vx, vy) for x, (vx, vy) in zip(xs, vs)]


def test_r30_dust_constants_match_the_spec():
    assert config.DUST_COUNT == 4
    assert config.DUST_LIFE == 12


def test_r30_landing_on_a_cabinet_spawns_dust(make_game, run_frames):
    game = make_game([FLOOR], start=ABOVE)
    step_until_standing(game, run_frames)
    puff = dust(game)
    assert len(puff) == config.DUST_COUNT
    actual = [(p.x, p.y, p.vx, p.vy) for p in puff]
    assert flat(actual) == pytest.approx(flat(expected_dust(game.player)))
    assert all(p.life == config.DUST_LIFE for p in puff)


def test_r30_landing_on_a_drawer_spawns_dust(make_game, run_frames):
    drawer = dict(min_x=80, max_x=120, y=500, speed=20, start_x=92)
    game = make_game([], start=ABOVE, drawers=[drawer])
    step_until_standing(game, run_frames)
    assert len(dust(game)) == config.DUST_COUNT


def test_r30_standing_still_spawns_no_dust(make_game, run_frames):
    game = make_game([FLOOR], start=START)
    for _ in range(60):
        run_frames(game, 1)
        assert game.particles == []


def test_r30_walking_along_a_cabinet_spawns_no_dust(make_game, run_frames):
    game = make_game([FLOOR], start=START)
    for _ in range(60):
        run_frames(game, 1, right=True)
        assert game.particles == []


def test_r30_riding_a_drawer_spawns_no_dust(make_game, run_frames):
    drawer = dict(min_x=60, max_x=140, y=500, speed=40, start_x=92)
    game = make_game([], start=START, drawers=[drawer])
    assert game.player.on_ground
    for _ in range(120):
        run_frames(game, 1)
        assert game.player.on_ground
        assert game.particles == []


def test_r30_rising_through_a_cabinet_and_mid_air_spawn_no_dust(make_game, run_frames):
    # A cabinet 30 px above Albert's head; he jumps up through it.
    above_head = (90, START[1] - 30, 40, 16)
    game = make_game([FLOOR, above_head], start=START)
    run_frames(game, 1, jump=True)
    assert game.player.vy < 0
    while not game.player.on_ground:
        assert game.particles == []
        run_frames(game, 1)


def test_r30_no_dust_at_the_start_or_after_restart(default_game, run_frames):
    assert default_game.particles == []
    run_frames(default_game, 1)
    assert default_game.particles == []
    default_game.player.y = default_game.level.world_height + 1
    default_game.player.on_ground = False
    run_frames(default_game, 1)
    run_frames(default_game, 1, restart=True)
    run_frames(default_game, 1)
    assert default_game.particles == []


def test_r30_dust_moves_by_velocity_times_dt(make_game, run_frames):
    game = make_game([FLOOR], start=ABOVE)
    step_until_standing(game, run_frames)
    before = [(p.x, p.y, p.vx, p.vy, p.life) for p in dust(game)]
    run_frames(game, 1)
    dt = 1 / config.FPS
    after = [(p.x, p.y, p.life) for p in dust(game)]
    expected = [(x + vx * dt, y + vy * dt, life - 1) for x, y, vx, vy, life in before]
    assert flat(after) == pytest.approx(flat(expected))


def test_r30_dust_is_gone_after_its_lifetime(make_game, run_frames):
    game = make_game([FLOOR], start=ABOVE)
    step_until_standing(game, run_frames)
    run_frames(game, config.DUST_LIFE - 1)
    assert len(dust(game)) == config.DUST_COUNT
    run_frames(game, 1)
    assert dust(game) == []


def test_r30_the_winning_landing_spawns_dust(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=ABOVE, add_decoy_goal=False)  # FLOOR is the goal
    step_until_standing(game, run_frames)
    assert game.state == GameState.WON
    assert len(dust(game)) == config.DUST_COUNT
