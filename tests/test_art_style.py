"""R7 — The game uses a 16-bit-style pixel art appearance.

These tests check the measurable parts of the style. Whether the overall
look fits the 16-bit era is a manual review (see spec.md R7).
"""

import pygame
import pytest

from albert import config

CAT_FRAMES = ["cat_idle", "cat_walk_1", "cat_walk_2", "cat_jump"]
DECORATION_FRAMES = {"mug": 4, "pot": 4, "clock": 2}  # Round 5 (R29): frames per kind
DECORATION_SPRITES = [f"{kind}_{i}" for kind, n in DECORATION_FRAMES.items() for i in range(n)]
REQUIRED_SPRITES = CAT_FRAMES + ["cabinet", "background", "treat", "drawer"] + DECORATION_SPRITES


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


def test_r7_treat_sprite_matches_treat_hitbox(sprites):
    """Round 2: the treat sprite follows R7 and matches its 8x8 hitbox."""
    assert sprites["treat"].get_size() == (config.TREAT_SIZE, config.TREAT_SIZE)


def test_r7_drawer_sprite_matches_drawer_size(sprites):
    """Round 3: the drawer sprite follows R7 and matches the drawer's 32x16 size."""
    assert sprites["drawer"].get_size() == (config.DRAWER_WIDTH, config.DRAWER_HEIGHT)


@pytest.mark.parametrize("name", DECORATION_SPRITES)
def test_r7_decoration_sprites_match_their_kind_size(sprites, name):
    """Round 5: decoration frames follow R7 and match config.DECORATION_SIZES."""
    kind = name.rsplit("_", 1)[0]
    assert sprites[name].get_size() == config.DECORATION_SIZES[kind]


@pytest.mark.parametrize("kind", list(DECORATION_FRAMES))
def test_r7_decoration_frames_all_differ(sprites, kind):
    frames = [pygame.image.tobytes(sprites[f"{kind}_{i}"], "RGBA") for i in range(DECORATION_FRAMES[kind])]
    assert len(set(frames)) == len(frames)


def _render_decoration(kind, ticks):
    """Headless render of one decoration (phase 0) on a one-screen level; returns its on-screen pixels."""
    from albert.game import Game
    from albert.level import Decoration, Level, Platform
    from albert.render import draw
    from albert.sprites import load_sprites

    w, h = config.DECORATION_SIZES[kind]
    floor = Platform(0, 160, 320, 16)
    x, y = 200, (floor.y - h if kind != "clock" else 40)
    level = Level(
        platforms=[floor, Platform(0, 0, 8, 4)],
        world_width=config.INTERNAL_WIDTH,
        world_height=config.INTERNAL_HEIGHT,
        start=(40, floor.y - config.PLAYER_HEIGHT),
        decorations=[Decoration(kind, x, y, 1, 0)],
    )
    game = Game(level=level)
    game.ticks = ticks
    canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    draw(canvas, game, load_sprites())
    return pygame.image.tobytes(canvas.subsurface(pygame.Rect(x, y, w, h)), "RGB")


@pytest.mark.parametrize("kind", list(DECORATION_FRAMES))
def test_r29_render_changes_between_frames_and_not_within_one(sprites, kind):
    frame_ticks, _ = config.DECORATION_FRAMES[kind]
    assert _render_decoration(kind, 0) != _render_decoration(kind, frame_ticks)
    assert _render_decoration(kind, 0) == _render_decoration(kind, frame_ticks - 1)


def test_r7_particles_are_drawn_in_their_colours(sprites):
    """Round 5: dust is a 1x1 counter_shade pixel; a young sparkle is a brass plus sign."""
    from albert.effects import Particle
    from albert.game import Game
    from albert.level import Level, Platform
    from albert.render import draw

    level = Level(
        platforms=[Platform(0, 160, 320, 16), Platform(0, 0, 8, 4)],
        world_width=config.INTERNAL_WIDTH,
        world_height=config.INTERNAL_HEIGHT,
        start=(40, 160 - config.PLAYER_HEIGHT),
    )
    game = Game(level=level)
    game.particles = [
        Particle("dust", 200, 100, 0, 0, config.DUST_LIFE),
        Particle("sparkle", 260, 60, 0, 0, config.SPARKLE_LIFE),
    ]
    canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    draw(canvas, game, sprites)
    rgb = lambda pos: tuple(canvas.get_at(pos))[:3]  # noqa: E731
    assert rgb((200, 100)) == config.COLORS["counter_shade"]
    for pos in [(260, 60), (259, 60), (261, 60), (260, 59), (260, 61)]:
        assert rgb(pos) == config.COLORS["brass"]


# --- Round 5 background scenery (R33-R38) ---

VIEWS = ["garden", "town", "city", "sky"]
REQUIRED_SCENERY = [f"scn_curtain_{i}" for i in range(3)] + ["scn_plant_0", "scn_plant_1", "scn_picture", "scn_tile"]
CABINET_COLOURS = ["wood_light", "wood_mid", "wood_dark", "counter_top", "counter_shade"]


def scenery_names(sprites):
    return sorted(name for name in sprites if name.startswith("scn_"))


@pytest.mark.parametrize("name", REQUIRED_SCENERY)
def test_r7_required_scenery_sprite_exists(sprites, name):
    assert name in sprites


@pytest.mark.parametrize("view", VIEWS)
def test_r7_each_view_has_scenery_sprites(sprites, view):
    assert any(name.startswith(f"scn_{view}_") for name in sprites), view


def test_r7_scenery_sprite_sizes(sprites):
    assert sprites["scn_picture"].get_size() == config.PICTURE_SIZE
    assert sprites["scn_tile"].get_size() == (config.TILE_SIZE, config.TILE_SIZE)


def test_r7_scenery_sprites_follow_the_pixel_art_rules(sprites):
    names = scenery_names(sprites)
    assert names, "no scenery sprites"
    palette = {tuple(c) for c in config.PALETTE}
    for name in names:
        surface = sprites[name]
        used = set(opaque_colours(surface))
        assert used, f"{name} has no visible pixels"
        assert used <= palette, f"{name} uses colours outside the palette: {used - palette}"
        assert len(used) <= 16, name
        w, h = surface.get_size()
        assert {surface.get_at((x, y)).a for x in range(w) for y in range(h)} <= {0, 255}, name


def test_r38_scenery_never_uses_cabinet_colours(sprites):
    banned = {config.COLORS[c] for c in CABINET_COLOURS}
    for name in scenery_names(sprites):
        clash = set(opaque_colours(sprites[name])) & banned
        assert not clash, f"{name} uses cabinet colours {clash}"


def test_r38_scenery_is_mostly_light_so_albert_stands_out(sprites):
    for name in scenery_names(sprites):
        colours = opaque_colours(sprites[name])
        dark = sum(1 for c in colours if luminance(c) < 64)
        assert dark <= 0.10 * len(colours), f"{name} is {dark / len(colours):.0%} dark"


def test_r37_curtain_and_plant_frames_differ(sprites):
    def raw(name):
        return pygame.image.tobytes(sprites[name], "RGBA")

    curtains = [raw(f"scn_curtain_{i}") for i in range(3)]
    assert len(set(curtains)) == 3
    assert raw("scn_plant_0") != raw("scn_plant_1")


WINDOW_AT = (64, 20)  # a window fully on screen in a one-screen test level


def _scenery_game(scenery, platforms=((0, 160, 320, 16),), start=(8, 160 - config.PLAYER_HEIGHT), treats=(), drawers=()):
    from albert.game import Game
    from albert.level import Drawer, Level, Platform, Scenery, Treat

    level = Level(
        platforms=[Platform(*p) for p in platforms] + [Platform(0, 0, 8, 4)],  # decoy goal
        world_width=config.INTERNAL_WIDTH,
        world_height=config.INTERNAL_HEIGHT,
        start=start,
        treats=[Treat(*t) for t in treats],
        drawers=[Drawer(**d) for d in drawers],
        scenery=[Scenery(**s) for s in scenery],
    )
    return Game(level=level)


def _window(view, phase=0):
    w, h = config.WINDOW_SIZE
    return dict(kind="window", x=WINDOW_AT[0], y=WINDOW_AT[1], width=w, height=h, section=1, phase=phase, view=view)


def _render(game, sprites):
    from albert.render import draw

    canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    draw(canvas, game, sprites)
    return canvas


def _glass(canvas):
    w, h = config.WINDOW_SIZE
    f = config.WINDOW_FRAME
    rect = pygame.Rect(WINDOW_AT[0] + f, WINDOW_AT[1] + f, w - 2 * f, h - 2 * f)
    return pygame.image.tobytes(canvas.subsurface(rect), "RGB")


def test_r35_the_four_views_look_different(sprites):
    glass = {}
    for view in VIEWS:
        game = _scenery_game([_window(view)])
        glass[view] = _glass(_render(game, sprites))
    assert len(set(glass.values())) == 4


@pytest.mark.parametrize("view", VIEWS)
def test_r36_window_glass_changes_as_clouds_drift(sprites, view):
    from albert.effects import scenery_anim

    game = _scenery_game([_window(view)])
    item = game.level.scenery[0]
    assert scenery_anim(item, 0)[0] != scenery_anim(item, 6)[0]
    game.ticks = 0
    before = _glass(_render(game, sprites))
    game.ticks = 6
    assert _glass(_render(game, sprites)) != before


@pytest.mark.parametrize("view", VIEWS)
def test_r36_window_glass_is_identical_for_the_same_animation_state(sprites, view):
    from albert.effects import scenery_anim

    game = _scenery_game([_window(view)])
    item = game.level.scenery[0]
    assert scenery_anim(item, 0) == scenery_anim(item, 2)
    game.ticks = 0
    before = _glass(_render(game, sprites))
    game.ticks = 2
    assert _glass(_render(game, sprites)) == before


def test_r38_gameplay_objects_look_the_same_with_scenery_behind_them(sprites):
    """Cabinet, drawer, treat and Albert all sit in front of a window and a tiles panel."""
    cabinet = (80, 120, 48, 16)
    args = dict(
        platforms=[cabinet],
        start=(90, 120 - config.PLAYER_HEIGHT),
        treats=[(112, 112)],
        drawers=[dict(min_x=150, max_x=200, y=100, start_x=160)],
    )
    tiles = dict(kind="tiles", x=0, y=0, width=64, height=32, section=1)  # under the HUD
    with_scn = _scenery_game([_window("garden"), tiles], **args)
    without = _scenery_game([], **args)
    a, b = _render(with_scn, sprites), _render(without, sprites)

    def assert_same_where_opaque(sprite, top_left):
        w, h = sprite.get_size()
        for x in range(w):
            for y in range(h):
                if sprite.get_at((x, y)).a:
                    pos = (top_left[0] + x, top_left[1] + y)
                    assert a.get_at(pos) == b.get_at(pos), pos

    for x in range(cabinet[0], cabinet[0] + cabinet[2]):
        for y in range(cabinet[1], cabinet[1] + cabinet[3]):
            assert a.get_at((x, y)) == b.get_at((x, y)), (x, y)
    assert_same_where_opaque(sprites["drawer"], (160, 100))
    assert_same_where_opaque(sprites["treat"], (112, 112))
    assert_same_where_opaque(sprites["cat_idle"], (90, 120 - config.PLAYER_HEIGHT))

    hud = pygame.Rect(2, 2, 30, 12)  # inside the opaque HUD panel
    assert pygame.image.tobytes(a.subsurface(hud), "RGB") == pygame.image.tobytes(b.subsurface(hud), "RGB")
    # The scenery really is drawn: somewhere in the window, the two renders differ.
    assert _glass(a) != _glass(b)


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
