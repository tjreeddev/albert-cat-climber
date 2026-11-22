"""R35 — The view outside changes as Albert climbs.

The headless render check that the four views look different lives in
test_art_style.py (only the R7, R8 and R12 tests touch Pygame).
"""

from albert import config
from albert.level import build_level


def test_r35_view_by_section_matches_the_spec():
    assert config.VIEW_BY_SECTION == {1: "garden", 2: "town", 3: "city", 4: "sky"}


def test_r35_each_window_shows_its_sections_view():
    for w in build_level().scenery:
        if w.kind == "window":
            assert w.view == config.VIEW_BY_SECTION[w.section], w


def test_r35_all_four_views_appear_in_the_level():
    views = {w.view for w in build_level().scenery if w.kind == "window"}
    assert views == {"garden", "town", "city", "sky"}
