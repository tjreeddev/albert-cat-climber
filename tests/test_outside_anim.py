"""R36 — The outside view is always gently moving.

The headless pixel checks for R36 live in test_art_style.py.
"""

import pytest

from albert import config

VIEWS = ["garden", "town", "city", "sky"]


def window(view, phase=0):
    from albert.level import Scenery

    w, h = config.WINDOW_SIZE
    return Scenery("window", 0, 0, w, h, 1, phase=phase, view=view)


def expected_window_state(view, ticks, phase):
    from albert.effects import anim_frame, scroll_offset

    cloud = scroll_offset(ticks, config.CLOUD_TICKS_PER_PX, config.CLOUD_LOOP, phase)
    if view == "sky":
        view_frame = 0
        birds = scroll_offset(ticks, config.BIRD_TICKS_PER_PX, config.BIRD_LOOP, phase)
    else:
        view_frame = anim_frame(ticks, *config.SCENERY_FRAMES[view], phase)
        birds = 0
    curtain = config.CURTAIN_SEQUENCE[anim_frame(ticks, *config.SCENERY_FRAMES["curtain"], phase)]
    return (cloud, view_frame, birds, curtain)


def test_r36_animation_constants_match_the_spec():
    assert config.CLOUD_TICKS_PER_PX == 6
    assert config.CLOUD_LOOP == 160
    assert config.BIRD_TICKS_PER_PX == 3
    assert config.BIRD_LOOP == 160
    assert config.SCENERY_FRAMES == {
        "garden": (45, 2),
        "town": (20, 3),
        "city": (50, 2),
        "curtain": (30, 4),
        "plant": (50, 2),
    }
    assert tuple(config.CURTAIN_SEQUENCE) == (0, 1, 2, 1)


@pytest.mark.parametrize(
    "ticks, per_px, loop, phase, expected",
    [(0, 6, 160, 0, 0), (5, 6, 160, 0, 0), (6, 6, 160, 0, 1), (959, 6, 160, 0, 159), (960, 6, 160, 0, 0),
     (0, 6, 160, 12, 2), (9, 3, 160, 0, 3), (480, 3, 160, 0, 0)],
)
def test_r36_scroll_offset_formula(ticks, per_px, loop, phase, expected):
    from albert.effects import scroll_offset

    assert scroll_offset(ticks, per_px, loop, phase) == expected
    assert scroll_offset(ticks, per_px, loop, phase) == ((ticks + phase) // per_px) % loop


def test_r36_scroll_offset_phase_defaults_to_zero():
    from albert.effects import scroll_offset

    assert scroll_offset(12, 6, 160) == 2


@pytest.mark.parametrize("view", VIEWS)
@pytest.mark.parametrize("phase", [0, 37])
def test_r36_window_state_follows_the_definitions(view, phase):
    from albert.effects import scenery_anim

    w = window(view, phase)
    for t in range(0, 2000, 11):
        assert scenery_anim(w, t) == expected_window_state(view, t, phase)


def test_r36_static_scenery_has_no_animation_state():
    from albert.effects import scenery_anim
    from albert.level import Scenery

    assert scenery_anim(Scenery("tiles", 0, 0, 64, 32, 1), 123) == ()
    assert scenery_anim(Scenery("picture", 0, 0, *config.PICTURE_SIZE, 1), 123) == ()


def test_r36_every_default_window_changes_within_any_60_updates(default_game):
    from albert.effects import scenery_anim

    windows = [s for s in default_game.level.scenery if s.kind == "window"]
    assert windows
    for w in windows:
        for start in range(0, 3000, 13):
            states = {scenery_anim(w, t) for t in range(start, start + 61)}
            assert len(states) > 1, f"{w.view} window is still from tick {start}"


@pytest.mark.parametrize("view", VIEWS)
def test_r36_clouds_move_in_every_view(view):
    from albert.effects import scenery_anim

    clouds = {scenery_anim(window(view), t)[0] for t in range(0, 61)}
    assert len(clouds) > 1


def _scenery_state(game):
    from albert.effects import scenery_anim

    return [scenery_anim(s, game.ticks) for s in game.level.scenery]


def test_r36_same_inputs_give_the_same_scenery_state(run_frames):
    from albert.game import Game

    a, b = Game(), Game()
    script = [dict(right=True)] * 30 + [dict(right=True, jump=True)] * 10 + [dict()] * 40
    for keys in script * 3:
        run_frames(a, 1, **keys)
        run_frames(b, 1, **keys)
        assert _scenery_state(a) == _scenery_state(b)


def test_r36_scenery_animates_while_lost_and_resets_on_restart(default_game, run_frames):
    from albert.game import GameState

    start_state = _scenery_state(default_game)
    default_game.player.y = default_game.level.world_height + 1
    default_game.player.on_ground = False
    run_frames(default_game, 1)
    assert default_game.state == GameState.LOST
    seen = set()
    for _ in range(60):
        run_frames(default_game, 1)
        seen.add(tuple(_scenery_state(default_game)))
    assert len(seen) > 1
    run_frames(default_game, 1, restart=True)
    assert _scenery_state(default_game) == start_state


def test_r36_scenery_animates_while_won(default_game, run_frames):
    from albert.game import GameState

    goal = default_game.level.goal_platform
    p = default_game.player
    p.x, p.y = goal.x + goal.width / 2 - p.width / 2, goal.y - p.height - 5
    p.on_ground = False
    run_frames(default_game, 60)
    assert default_game.state == GameState.WON
    seen = set()
    for _ in range(60):
        run_frames(default_game, 1)
        seen.add(tuple(_scenery_state(default_game)))
    assert len(seen) > 1
