"""R28 — The kitchen has fixed decorations in every section."""

import pytest

from albert import config
from albert.level import build_level

KINDS = {"mug", "pot", "clock"}
STEAMING = {"mug", "pot"}


@pytest.fixture(scope="module")
def level():
    return build_level()


def size(d):
    return config.DECORATION_SIZES[d.kind]


def rect(d):
    w, h = size(d)
    return (d.x, d.y, w, h)


def overlaps(a, b):
    """Positive-area overlap of two (x, y, w, h) rectangles."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def drawer_path(d):
    return (d.min_x, d.y, d.max_x + d.width - d.min_x, d.height)


def resting_cabinet(level, d):
    """The static cabinet a mug or pot rests on, or None."""
    w, h = size(d)
    for p in level.platforms:
        if d.y + h == p.y and p.x <= d.x and d.x + w <= p.x + p.width:
            return p
    return None


def test_r28_decoration_sizes_match_the_spec():
    assert config.MUG_SIZE == (8, 16)
    assert config.POT_SIZE == (16, 20)
    assert config.CLOCK_SIZE == (16, 8)
    assert config.DECORATION_SIZES == {"mug": config.MUG_SIZE, "pot": config.POT_SIZE, "clock": config.CLOCK_SIZE}


def test_r28_default_level_has_eight_decorations(level):
    assert len(level.decorations) == 8


def test_r28_two_decorations_in_each_section(level):
    counts = {s: sum(1 for d in level.decorations if d.section == s) for s in (1, 2, 3, 4)}
    assert counts == {1: 2, 2: 2, 3: 2, 4: 2}


def test_r28_all_three_kinds_are_used(level):
    assert {d.kind for d in level.decorations} == KINDS


def test_r28_each_section_has_a_steaming_item(level):
    for s in (1, 2, 3, 4):
        assert any(d.kind in STEAMING for d in level.decorations if d.section == s), f"section {s}"


def test_r28_mugs_and_pots_rest_on_a_static_cabinet_in_their_section(level):
    for d in level.decorations:
        if d.kind in STEAMING:
            cabinet = resting_cabinet(level, d)
            assert cabinet is not None, f"{d} doesn't rest on a cabinet"
            assert cabinet is not level.goal_platform, f"{d} is on the goal"
            assert cabinet.section == d.section, f"{d} is tagged with the wrong section"


def test_r28_mugs_and_pots_are_not_on_drawers(level):
    for d in level.decorations:
        if d.kind in STEAMING:
            w, h = size(d)
            for dr in level.drawers:
                on_top = d.y + h == dr.y and d.x < dr.max_x + dr.width and d.x + w > dr.min_x
                assert not on_top, f"{d} sits on a drawer's path"


def test_r28_clocks_hang_clear_of_cabinets_and_drawer_paths(level):
    for d in level.decorations:
        if d.kind == "clock":
            for p in level.platforms:
                assert not overlaps(rect(d), (p.x, p.y, p.width, p.height)), f"{d} overlaps a cabinet"
            for dr in level.drawers:
                assert not overlaps(rect(d), drawer_path(dr)), f"{d} overlaps a drawer path"


def test_r28_no_decoration_covers_a_treat(level):
    for d in level.decorations:
        for t in level.treats:
            assert not overlaps(rect(d), (t.x, t.y, t.width, t.height)), f"{d} covers a treat"


def test_r28_no_decoration_covers_alberts_start(level):
    start = (*level.start, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
    for d in level.decorations:
        assert not overlaps(rect(d), start), f"{d} covers the start"


def test_r28_decorations_are_inside_the_world(level):
    for d in level.decorations:
        w, h = size(d)
        assert 0 <= d.x and d.x + w <= level.world_width
        assert 0 <= d.y and d.y + h <= level.world_height


def test_r28_decorations_of_a_kind_do_not_all_share_a_phase(level):
    for kind in KINDS:
        frame_ticks, frame_count = config.DECORATION_FRAMES[kind]
        phases = {d.phase % (frame_ticks * frame_count) for d in level.decorations if d.kind == kind}
        if sum(1 for d in level.decorations if d.kind == kind) > 1:
            assert len(phases) > 1, f"every {kind} animates in lockstep"


def test_r28_decorations_are_not_platforms(level):
    for d in level.decorations:
        assert not any(d is p for p in level.platforms)


def test_r28_playing_never_changes_the_decorations(default_game, run_frames):
    before = [(d.kind, d.x, d.y, d.section, d.phase) for d in default_game.level.decorations]
    run_frames(default_game, 120, right=True, jump=True)
    default_game.restart()
    after = [(d.kind, d.x, d.y, d.section, d.phase) for d in default_game.level.decorations]
    assert after == before
