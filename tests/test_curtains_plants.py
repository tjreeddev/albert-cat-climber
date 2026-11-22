"""R37 — Curtains and hanging plants sway.

The sprite-difference checks for R37 live in test_art_style.py.
"""

import pytest

from albert import config


def runs(values):
    """Collapse consecutive repeats: [0, 0, 1, 1, 2] -> [0, 1, 2]."""
    out = []
    for v in values:
        if not out or out[-1] != v:
            out.append(v)
    return out


@pytest.mark.parametrize("phase", [0, 45])
def test_r37_curtains_sway_0_1_2_1_every_120_ticks(phase):
    from albert.effects import scenery_anim
    from albert.level import Scenery

    w = Scenery("window", 0, 0, *config.WINDOW_SIZE, 1, phase=phase, view="garden")
    curtain = [scenery_anim(w, t)[3] for t in range(240)]
    assert curtain[:120] == curtain[120:], "curtains must loop every 120 ticks"
    sequence = runs(curtain[:120])
    # Starting from any point in the loop, the order of frames is 0, 1, 2, 1 repeating.
    doubled = [0, 1, 2, 1] * 3
    assert any(doubled[i : i + len(sequence)] == sequence for i in range(4)), sequence
    assert set(curtain) == {0, 1, 2}


def test_r37_default_windows_all_have_swaying_curtains(default_game):
    from albert.effects import scenery_anim

    for w in (s for s in default_game.level.scenery if s.kind == "window"):
        assert {scenery_anim(w, t)[3] for t in range(120)} == {0, 1, 2}


def test_r37_plants_cycle_through_two_frames():
    from albert.effects import anim_frame, scenery_anim
    from albert.level import Scenery

    plant = Scenery("plant", 0, 0, *config.PLANT_SIZE, 1, phase=7)
    frames = [scenery_anim(plant, t) for t in range(200)]
    assert set(frames) == {(0,), (1,)}
    for t in range(200):
        assert scenery_anim(plant, t) == (anim_frame(t, *config.SCENERY_FRAMES["plant"], 7),)


def test_r37_default_level_has_swaying_plants(default_game):
    from albert.effects import scenery_anim

    plants = [s for s in default_game.level.scenery if s.kind == "plant"]
    assert plants
    for p in plants:
        assert {scenery_anim(p, t) for t in range(100)} == {(0,), (1,)}
