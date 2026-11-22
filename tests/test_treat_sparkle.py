"""R31 — Collecting a treat makes a sparkle."""

import math

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
START = (100, FLOOR[1] - config.PLAYER_HEIGHT)  # standing on FLOOR, x from 100 to 116
ON_FLOOR = FLOOR[1] - 8  # y of an 8x8 treat resting on FLOOR


def flat(rows):
    """Flatten a list of tuples for pytest.approx, which doesn't compare nested sequences."""
    return [v for row in rows for v in row]


def sparkles(game):
    return [p for p in game.particles if p.kind == "sparkle"]


def expected_sparkle(cx, cy):
    out = []
    for k in range(config.SPARKLE_COUNT):
        theta = math.radians(k * 360 / config.SPARKLE_COUNT)
        out.append((cx, cy, config.SPARKLE_SPEED * math.sin(theta), -config.SPARKLE_SPEED * math.cos(theta)))
    return out


def test_r31_sparkle_constants_match_the_spec():
    assert config.SPARKLE_COUNT == 6
    assert config.SPARKLE_LIFE == 18
    assert config.SPARKLE_SPEED == 40
    assert config.MAX_PARTICLES == 48


def test_r31_collecting_a_treat_spawns_a_sparkle_at_its_centre(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(104, ON_FLOOR)])
    run_frames(game, 1)
    assert game.treats_collected == 1
    s = sparkles(game)
    assert len(s) == config.SPARKLE_COUNT
    actual = [(p.x, p.y, p.vx, p.vy) for p in s]
    assert flat(actual) == pytest.approx(flat(expected_sparkle(104 + 4, ON_FLOOR + 4)), abs=1e-9)
    assert all(p.life == config.SPARKLE_LIFE for p in s)


def test_r31_first_sparkle_particle_points_straight_up(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(104, ON_FLOOR)])
    run_frames(game, 1)
    first = sparkles(game)[0]
    assert first.vx == pytest.approx(0, abs=1e-9)
    assert first.vy == pytest.approx(-config.SPARKLE_SPEED)


def test_r31_two_treats_on_one_frame_give_two_sparkles(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(102, ON_FLOOR), (108, ON_FLOOR)])
    run_frames(game, 1)
    s = sparkles(game)
    assert len(s) == 2 * config.SPARKLE_COUNT
    actual = [(p.x, p.y, p.vx, p.vy) for p in s]
    expected = expected_sparkle(106, ON_FLOOR + 4) + expected_sparkle(112, ON_FLOOR + 4)
    assert flat(actual) == pytest.approx(flat(expected), abs=1e-9)


def test_r31_edge_touch_spawns_no_sparkle(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(START[0] + config.PLAYER_WIDTH, ON_FLOOR)])
    run_frames(game, 10)
    assert game.particles == []


def test_r31_a_collected_treat_never_sparkles_again(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(150, ON_FLOOR)])
    run_frames(game, 60, right=True)
    assert game.treats_collected == 1
    run_frames(game, config.SPARKLE_LIFE)
    assert game.particles == []
    for keys in [dict(left=True), dict(right=True), dict(left=True)]:
        for _ in range(60):
            run_frames(game, 1, **keys)
            assert sparkles(game) == []


@pytest.mark.parametrize("state", ["WON", "LOST"])
def test_r31_no_sparkle_when_won_or_lost(make_game, run_frames, state):
    from albert.game import GameState

    game = make_game([FLOOR], start=START, treats=[(104, ON_FLOOR)])
    game.state = GameState[state]
    run_frames(game, 10)
    assert game.particles == []


def test_r31_sparkle_is_gone_after_its_lifetime(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(104, ON_FLOOR)])
    run_frames(game, 1)
    run_frames(game, config.SPARKLE_LIFE - 1)
    assert len(sparkles(game)) == config.SPARKLE_COUNT
    run_frames(game, 1)
    assert sparkles(game) == []


def test_r31_particle_count_is_capped_and_oldest_are_dropped(make_game, run_frames):
    # Nine treats all under Albert: 9 x 6 = 54 sparkle particles on one frame.
    xs = list(range(100, 109))
    game = make_game([FLOOR], start=START, treats=[(x, ON_FLOOR) for x in xs])
    run_frames(game, 1)
    assert game.treats_collected == 9
    assert len(game.particles) == config.MAX_PARTICLES
    # The first treat's sparkle (the oldest particles) was dropped; the second's survives first.
    first = game.particles[0]
    assert (first.x, first.vx) == pytest.approx((xs[1] + 4, 0), abs=1e-9)
    assert game.particles[-1].x == pytest.approx(xs[-1] + 4)
    for _ in range(config.SPARKLE_LIFE + 2):
        run_frames(game, 1)
        assert len(game.particles) <= config.MAX_PARTICLES
