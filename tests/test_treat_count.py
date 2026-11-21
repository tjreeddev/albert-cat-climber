"""R11 — The game tracks how many treats Albert has collected during the current run."""

from albert import config

FLOOR = (0, 500, 320, 16)
START = (100, FLOOR[1] - config.PLAYER_HEIGHT)
ON_FLOOR = FLOOR[1] - 8  # y of an 8x8 treat (spec 8.2) resting on FLOOR


def test_r11_count_starts_at_zero(default_game):
    assert default_game.treats_collected == 0


def test_r11_total_is_the_number_of_treats_in_the_level(default_game):
    assert default_game.treats_total == len(default_game.level.treats) == 12  # Round 4: was 5


def test_r11_count_goes_up_by_one_per_treat(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(150, ON_FLOOR), (220, ON_FLOOR)])
    counts = []
    for _ in range(150):
        run_frames(game, 1, right=True)
        counts.append(game.treats_collected)
    steps = [b - a for a, b in zip(counts, counts[1:])]
    assert set(steps) <= {0, 1}
    assert counts[-1] == 2


def test_r11_total_never_changes(make_game, run_frames):
    game = make_game([FLOOR], start=START, treats=[(150, ON_FLOOR), (220, ON_FLOOR)])
    assert game.treats_total == 2
    run_frames(game, 150, right=True)
    assert game.treats_collected == 2
    assert game.treats_total == 2


def test_r11_treat_touched_on_the_winning_frame_counts(make_game, run_frames):
    from albert.game import GameState

    goal = (100, 300, 60, 8)
    # Albert's feet are 0.1 px above the goal, so the first update lands him
    # (and wins). The treat on the goal overlaps him, but nothing is collected
    # before that first update.
    game = make_game(
        [FLOOR, goal],
        start=(110, goal[1] - config.PLAYER_HEIGHT - 0.1),
        add_decoy_goal=False,
        treats=[(120, goal[1] - config.TREAT_SIZE)],
    )
    assert game.treats_collected == 0
    run_frames(game, 1)
    assert game.state == GameState.WON
    assert game.treats_collected == 1
