"""R33 — The kitchen has large background scenery."""

import pytest

from albert import config
from albert.level import build_level

KINDS = {"window", "tiles", "picture", "plant"}


@pytest.fixture(scope="module")
def level():
    return build_level()


def rect(item):
    return (item.x, item.y, item.width, item.height)


def overlap_area(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0, min(ay + ah, by + bh) - max(ay, by))


def windows(level):
    return [s for s in level.scenery if s.kind == "window"]


def test_r33_scenery_constants_match_the_spec():
    assert config.WINDOW_SIZE == (192, 128)
    assert config.WINDOW_FRAME == 4
    assert config.CURTAIN_WIDTH == 24
    assert config.PICTURE_SIZE == (48, 32)
    assert config.PLANT_SIZE == (24, 40)
    assert config.TILE_SIZE == 16


def test_r33_all_four_kinds_are_used(level):
    assert {s.kind for s in level.scenery} == KINDS


def test_r33_four_to_six_windows_one_or_two_per_section(level):
    ws = windows(level)
    assert 4 <= len(ws) <= 6
    for section in (1, 2, 3, 4):
        assert 1 <= sum(1 for w in ws if w.section == section) <= 2, f"section {section}"


def test_r33_window_centres_rise_section_by_section(level):
    ws = windows(level)
    for lower in (1, 2, 3):
        low = [w.y + w.height / 2 for w in ws if w.section == lower]
        high = [w.y + w.height / 2 for w in ws if w.section == lower + 1]
        assert min(low) > max(high), f"S{lower} windows must sit below S{lower + 1} windows"


def section_bands(level):
    """Each section's height band: top of its highest to bottom of its lowest cabinet or drawer."""
    bands = {}
    for section in (1, 2, 3, 4):
        things = [p for p in level.platforms if p.section == section]
        things += [d for d in level.drawers if d.section == section]
        bands[section] = (min(t.y for t in things), max(t.y + t.height for t in things))
    return bands


def band_distance(band, y):
    top, bottom = band
    return max(0, top - y, y - bottom)


def test_r33_section_bands_match_the_spec(level):
    assert section_bands(level) == {1: (858, 1076), 2: (596, 838), 3: (310, 572), 4: (24, 284)}


def test_r33_each_window_sits_inside_its_sections_band(level):
    bands = section_bands(level)
    for w in windows(level):
        top, bottom = bands[w.section]
        assert top <= w.y + w.height / 2 <= bottom, w


def test_r33_other_scenery_is_tagged_with_the_nearest_section(level):
    bands = section_bands(level)
    for s in level.scenery:
        if s.kind != "window":
            centre = s.y + s.height / 2
            nearest = min(band_distance(b, centre) for b in bands.values())
            assert band_distance(bands[s.section], centre) == nearest, s


def test_r33_windows_are_the_main_feature(level):
    window_area = sum(s.width * s.height for s in level.scenery if s.kind == "window")
    tiles_area = sum(s.width * s.height for s in level.scenery if s.kind == "tiles")
    assert window_area > tiles_area


def test_r33_sizes_follow_their_kind(level):
    for s in level.scenery:
        if s.kind == "window":
            assert (s.width, s.height) == config.WINDOW_SIZE
        elif s.kind == "picture":
            assert (s.width, s.height) == config.PICTURE_SIZE
        elif s.kind == "plant":
            assert (s.width, s.height) == config.PLANT_SIZE
        else:  # tiles
            assert s.width % config.TILE_SIZE == 0 and s.height % config.TILE_SIZE == 0
            assert s.width >= 64 and s.height >= 32


def test_r33_only_windows_have_a_view(level):
    for s in level.scenery:
        if s.kind == "window":
            assert s.view is not None
        else:
            assert s.view is None


def test_r33_scenery_is_inside_the_world(level):
    for s in level.scenery:
        assert 0 <= s.x and s.x + s.width <= level.world_width
        assert 0 <= s.y and s.y + s.height <= level.world_height


def test_r33_scenery_items_do_not_overlap_each_other(level):
    items = level.scenery
    for i, a in enumerate(items):
        for b in items[i + 1 :]:
            assert overlap_area(rect(a), rect(b)) == 0, f"{a} overlaps {b}"


def test_r33_scenery_does_not_overlap_any_clock(level):
    w, h = config.CLOCK_SIZE
    for c in (d for d in level.decorations if d.kind == "clock"):
        for s in level.scenery:
            assert overlap_area(rect(s), (c.x, c.y, w, h)) == 0, f"{s} overlaps a clock"


def test_r33_at_most_a_quarter_of_each_window_is_behind_cabinets_or_drawers(level):
    for w in windows(level):
        hidden = sum(overlap_area(rect(w), (p.x, p.y, p.width, p.height)) for p in level.platforms)
        hidden += sum(
            overlap_area(rect(w), (d.min_x, d.y, d.max_x + d.width - d.min_x, d.height)) for d in level.drawers
        )
        assert hidden <= 0.25 * w.width * w.height, f"{w} is {hidden / (w.width * w.height):.0%} hidden"


def test_r33_scenery_is_never_a_platform(level):
    for s in level.scenery:
        assert all(s is not p for p in level.platforms)


def test_r33_playing_never_changes_the_scenery(default_game, run_frames):
    def snapshot():
        return [
            (s.kind, s.x, s.y, s.width, s.height, s.section, s.phase, s.view) for s in default_game.level.scenery
        ]

    before = snapshot()
    run_frames(default_game, 120, right=True, jump=True)
    default_game.restart()
    assert snapshot() == before
