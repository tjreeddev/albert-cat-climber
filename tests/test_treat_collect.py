"""R10 — When Albert touches a treat, it is collected and disappears for the rest of the run."""

from albert import config

FLOOR = (0, 500, 320, 16)
START = (100, FLOOR[1] - config.PLAYER_HEIGHT)  # standing on FLOOR, x from 100 to 116
ON_FLOOR = FLOOR[1] - 8  # y of an 8x8 treat (spec 8.2) resting on FLOOR


def test_r10_walking_into_a_treat_collects_it(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(150, ON_FLOOR)])
    assert game.treats_collected == 0
    run_frames(game, 60, right=True)
    assert game.treats_collected == 1


def test_r10_jumping_into_a_treat_in_mid_air_collects_it(make_game, run_frames):
    # Floating above Albert's head, below the top of his jump.
    game = make_game([FLOOR], start=START, treats=[(104, START[1] - 40)])
    run_frames(game, 1, jump=True)
    run_frames(game, 60)
    assert game.treats_collected == 1


def test_r10_touching_only_edges_does_not_collect(make_game, run_frames):
    # Treat's left edge is exactly at Albert's right edge: no overlap area.
    game = make_game([FLOOR], start=START, treats=[(START[0] + config.PLAYER_WIDTH, ON_FLOOR)])
    run_frames(game, 10)
    assert game.treats_collected == 0


def test_r10_nearby_treat_is_not_collected(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(200, ON_FLOOR)])
    run_frames(game, 30)
    assert game.treats_collected == 0
    assert len(game.visible_treats()) == 1


def test_r10_collected_treat_disappears(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(150, ON_FLOOR), (260, ON_FLOOR)])
    near, far = game.level.treats
    assert game.visible_treats() == [near, far]
    run_frames(game, 60, right=True)
    assert game.visible_treats() == [far]


def test_r10_treat_stays_gone_and_is_not_collected_twice(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(150, ON_FLOOR)])
    run_frames(game, 60, right=True)
    run_frames(game, 60, left=True)
    run_frames(game, 60, right=True)
    assert game.treats_collected == 1
    assert game.visible_treats() == []


def test_r10_two_treats_touched_on_one_frame_are_both_collected(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(102, ON_FLOOR), (108, ON_FLOOR)])
    run_frames(game, 1)
    assert game.treats_collected == 2
    assert game.visible_treats() == []


def test_r10_no_collecting_after_losing(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=START, treats=[(104, ON_FLOOR)])
    game.state = GameState.LOST
    run_frames(game, 10)
    assert game.treats_collected == 0


def test_r10_no_collecting_after_winning(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=START, treats=[(104, ON_FLOOR)])
    game.state = GameState.WON
    run_frames(game, 10)
    assert game.treats_collected == 0
