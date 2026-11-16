"""R7 — The game uses a 16-bit-style pixel art appearance.

These tests check the measurable parts of the style. Whether the overall
look fits the 16-bit era is a manual review (see spec.md R7).
"""

import pygame
import pytest

from albert import config

CAT_FRAMES = ["cat_idle", "cat_walk_1", "cat_walk_2", "cat_jump"]
REQUIRED_SPRITES = CAT_FRAMES + ["cabinet", "background"]


@pytest.fixture(scope="module")
def sprites():
    from albert.sprites import load_sprites

    pygame.init()
    pygame.display.set_mode((1, 1))
    return load_sprites()


def opaque_colours(surface):
    colours = []
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            c = surface.get_at((x, y))
            if c.a:
                colours.append((c.r, c.g, c.b))
    return colours


def luminance(rgb):
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def test_r7_internal_resolution_is_320_by_180():
    assert (config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT) == (320, 180)


def test_r7_window_scale_is_whole_number_4():
    assert isinstance(config.SCALE, int)
    assert config.SCALE == 4


def test_r7_palette_is_declared_as_rgb_tuples():
    assert len(config.PALETTE) >= 2
    for colour in config.PALETTE:
        assert len(colour) == 3
        assert all(isinstance(v, int) and 0 <= v <= 255 for v in colour)


@pytest.mark.parametrize("name", REQUIRED_SPRITES)
def test_r7_required_sprite_exists(sprites, name):
    assert name in sprites
    assert isinstance(sprites[name], pygame.Surface)


@pytest.mark.parametrize("name", REQUIRED_SPRITES)
def test_r7_sprite_uses_at_most_16_palette_colours(sprites, name):
    used = set(opaque_colours(sprites[name]))
    palette = {tuple(c) for c in config.PALETTE}
    assert used, f"{name} has no visible pixels"
    assert used <= palette, f"{name} uses colours outside the palette: {used - palette}"
    assert len(used) <= 16


@pytest.mark.parametrize("name", REQUIRED_SPRITES)
def test_r7_sprite_has_no_semi_transparent_pixels(sprites, name):
    surface = sprites[name]
    w, h = surface.get_size()
    alphas = {surface.get_at((x, y)).a for x in range(w) for y in range(h)}
    assert alphas <= {0, 255}


@pytest.mark.parametrize("name", CAT_FRAMES)
def test_r7_cat_frames_match_albert_size(sprites, name):
    assert sprites[name].get_size() == (config.PLAYER_WIDTH, config.PLAYER_HEIGHT)


def test_r7_albert_is_a_black_cat_with_a_visible_highlight(sprites):
    colours = opaque_colours(sprites["cat_idle"])
    dark = sum(1 for c in colours if luminance(c) < 64)
    assert dark / len(colours) >= 0.5, "Albert should be mostly black"
    assert any(luminance(c) > 100 for c in colours), "Albert needs a highlight (eyes/outline)"


def test_r7_scaling_is_nearest_neighbour():
    from albert.render import scale_to_window

    a, b = (10, 10, 10), (240, 200, 40)
    src = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    for x in range(config.INTERNAL_WIDTH):
        for y in range(config.INTERNAL_HEIGHT):
            src.set_at((x, y), a if (x + y) % 2 else b)

    out = scale_to_window(src)
    assert out.get_size() == (config.INTERNAL_WIDTH * config.SCALE, config.INTERNAL_HEIGHT * config.SCALE)

    data = pygame.image.tobytes(out, "RGB")
    colours = {data[i : i + 3] for i in range(0, len(data), 3)}
    assert colours == {bytes(a), bytes(b)}, "scaling blended colours"

    for x, y in [(0, 0), (1, 0), (37, 91), (319, 179)]:
        expected = src.get_at((x, y))
        for dx in range(config.SCALE):
            for dy in range(config.SCALE):
                assert out.get_at((x * config.SCALE + dx, y * config.SCALE + dy)) == expected
