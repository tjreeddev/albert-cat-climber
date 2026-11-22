"""R38 — Scenery is visual only and stays behind gameplay.

The layering, HUD and readability pixel checks for R38 live in test_art_style.py.
"""

from albert import config
from test_visual_only import default_level_script, gameplay

FLOOR = (0, 500, 320, 16)


def record(game, run_frames, frames):
    states = []
    for f in range(frames):
        run_frames(game, 1, **default_level_script(f))
        states.append(gameplay(game))
    return states


def test_r38_default_level_plays_the_same_with_and_without_scenery(run_frames):
    from albert.game import Game
    from albert.level import build_level

    with_scenery = Game()
    assert with_scenery.level.scenery, "the default level should have scenery"
    bare = build_level()
    bare.scenery = []
    assert record(with_scenery, run_frames, 900) == record(Game(level=bare), run_frames, 900)


def test_r38_albert_falls_straight_through_scenery(make_game, run_frames):
    # A large window directly under Albert, with nothing else to land on until FLOOR.
    w, h = config.WINDOW_SIZE
    window = dict(kind="window", x=40, y=320, width=w, height=h, section=1, view="garden")
    tiles = dict(kind="tiles", x=40, y=200, width=192, height=64, section=1)
    game = make_game([FLOOR], start=(100, 100), scenery=[tiles, window])
    run_frames(game, 1)
    while game.player.y + game.player.height < 320 + h:
        assert not game.player.on_ground
        run_frames(game, 1)
    assert game.player.vy > 0


def test_r38_scenery_is_never_a_platform(default_game):
    for s in default_game.level.scenery:
        assert all(s is not p for p in default_game.level.platforms)
