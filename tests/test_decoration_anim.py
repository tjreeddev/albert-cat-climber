"""R29 — Decorations loop through their animation frames.

The headless render checks for R29 live in test_art_style.py (only the R7, R8
and R12 tests touch Pygame).
"""

from albert import config


def test_r29_frame_timings_match_the_spec():
    assert config.DECORATION_FRAMES == {"mug": (10, 4), "pot": (8, 4), "clock": (30, 2)}


def test_r29_decoration_frame_follows_anim_frame(default_game):
    from albert.effects import anim_frame, decoration_frame

    for d in default_game.level.decorations:
        frame_ticks, frame_count = config.DECORATION_FRAMES[d.kind]
        for t in range(0, 300, 7):
            assert decoration_frame(d, t) == anim_frame(t, frame_ticks, frame_count, d.phase)


def test_r29_every_frame_is_shown_in_one_period(default_game):
    from albert.effects import decoration_frame

    for d in default_game.level.decorations:
        frame_ticks, frame_count = config.DECORATION_FRAMES[d.kind]
        shown = {decoration_frame(d, t) for t in range(frame_ticks * frame_count)}
        assert shown == set(range(frame_count)), d.kind


def _frames_over(game, run_frames, updates):
    from albert.effects import decoration_frame

    seen = []
    for _ in range(updates):
        run_frames(game, 1)
        seen.append(tuple(decoration_frame(d, game.ticks) for d in game.level.decorations))
    return set(seen)


def test_r29_decorations_animate_while_lost(default_game, run_frames):
    from albert.game import GameState

    default_game.player.y = default_game.level.world_height + 1
    default_game.player.on_ground = False
    run_frames(default_game, 1)
    assert default_game.state == GameState.LOST
    assert len(_frames_over(default_game, run_frames, 120)) > 1


def test_r29_decorations_animate_while_won(default_game, run_frames):
    from albert.game import GameState

    goal = default_game.level.goal_platform
    p = default_game.player
    p.x, p.y = goal.x + goal.width / 2 - p.width / 2, goal.y - p.height - 5
    p.on_ground = False
    run_frames(default_game, 60)
    assert default_game.state == GameState.WON
    assert len(_frames_over(default_game, run_frames, 120)) > 1
