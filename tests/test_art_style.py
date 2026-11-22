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


# --- Round 6 hazards (R45) ---

HAZARD_SPRITES = [
    "hz_vent_idle", "hz_vent_warn_0", "hz_vent_warn_1", "hz_jet_0", "hz_jet_1",
    "hz_burner_idle", "hz_burner_warn", "hz_burner_hot_0", "hz_burner_hot_1",
    "hz_tap", "hz_tap_warn", "hz_drop_form_0", "hz_drop_form_1", "hz_drop_form_2", "hz_drop",
]
WARNING_SPRITES = ["hz_vent_warn_0", "hz_vent_warn_1", "hz_burner_warn", "hz_tap_warn"]


@pytest.mark.parametrize("name", HAZARD_SPRITES)
def test_r45_hazard_sprite_follows_the_pixel_art_rules(sprites, name):
    assert name in sprites
    surface = sprites[name]
    used = set(opaque_colours(surface))
    palette = {tuple(c) for c in config.PALETTE}
    assert used and used <= palette, name
    assert len(used) <= 16
    w, h = surface.get_size()
    assert {surface.get_at((x, y)).a for x in range(w) for y in range(h)} <= {0, 255}


def test_r45_hazard_sprite_sizes(sprites):
    assert sprites["hz_vent_idle"].get_size() == config.VENT_SIZE
    assert sprites["hz_jet_0"].get_size() == config.JET_SIZE
    assert sprites["hz_drop"].get_size() == config.DROP_SIZE
    assert sprites["hz_burner_hot_0"].get_width() == config.BURNER_WIDTH


@pytest.mark.parametrize("name", WARNING_SPRITES)
def test_r45_warning_sprites_use_a_warning_colour(sprites, name):
    warn = {config.COLORS["warn_orange"], config.COLORS["warn_red"]}
    assert set(opaque_colours(sprites[name])) & warn, name


def test_r45_no_decoration_or_scenery_uses_warning_colours(sprites):
    warn = {config.COLORS["warn_orange"], config.COLORS["warn_red"]}
    for name, surface in sprites.items():
        if name.startswith(("mug_", "pot_", "clock_", "scn_")):
            assert not set(opaque_colours(surface)) & warn, name


def test_r45_hazard_jets_are_much_wider_than_decorative_steam(sprites):
    for name in ("hz_jet_0", "hz_jet_1"):
        jet = sprites[name]
        w, h = jet.get_size()
        columns = {x for x in range(w) for y in range(h) if jet.get_at((x, y)).a}
        assert len(columns) >= 10, name
    white = config.COLORS["text_white"]
    for name, steam_rows in [(f"mug_{i}", 8) for i in range(4)] + [(f"pot_{i}", 10) for i in range(4)]:
        s = sprites[name]
        for y in range(steam_rows):
            count = sum(1 for x in range(s.get_width()) if s.get_at((x, y)).a and tuple(s.get_at((x, y)))[:3] == white)
            assert count <= 2, (name, y)


def _hazard_game(hazard):
    from albert.game import Game
    from albert.level import Hazard, Level, Platform

    level = Level(
        platforms=[Platform(0, 160, 320, 16), Platform(100, 120, 48, 16), Platform(0, 0, 8, 4)],
        world_width=config.INTERNAL_WIDTH,
        world_height=config.INTERNAL_HEIGHT,
        start=(8, 160 - config.PLAYER_HEIGHT),
        hazards=[Hazard(**hazard)],
    )
    return Game(level=level)


HAZARD_SCENES = {
    # hazard on the (100, 120, 48) cabinet; region (x, y, w, h) covering everything it draws
    "vent": (dict(kind="vent", x=110, top=120, section=1, idle=10, warning=10, active=10), (106, 60, 24, 62)),
    "burner": (dict(kind="burner", x=116, top=120, section=1, idle=10, warning=10, active=10), (112, 112, 24, 12)),
    "drip": (dict(kind="drip", x=124, top=60, section=1, idle=10, warning=10, active=28, floor=120), (118, 48, 16, 74)),
}


@pytest.mark.parametrize("kind", list(HAZARD_SCENES))
def test_r45_idle_warning_and_active_look_different(sprites, kind):
    from albert.render import draw

    hazard, region = HAZARD_SCENES[kind]
    game = _hazard_game(hazard)
    looks = []
    for t in (0, 10, 20):  # idle, warning, first active update
        game.hazard_ticks = t
        canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
        draw(canvas, game, sprites)
        looks.append(pygame.image.tobytes(canvas.subsurface(pygame.Rect(region)), "RGB"))
    assert len(set(looks)) == 3, kind


def test_r45_albert_flashes_while_invulnerable(sprites):
    from albert.render import draw

    game = _hazard_game(HAZARD_SCENES["vent"][0])
    p = game.player
    albert = pygame.Rect(round(p.x), round(p.y), p.width, p.height)

    def look(invulnerable):
        game.invulnerable_ticks = invulnerable
        canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
        draw(canvas, game, sprites)
        return pygame.image.tobytes(canvas.subsurface(albert), "RGB")

    normal = look(0)
    assert look(4) != normal, "(4 // 4) % 2 == 1: hidden"
    assert look(8) == normal, "(8 // 4) % 2 == 0: drawn"
    assert look(60) != normal and look(56) == normal


# --- Round 7 title menu (R52) ---

MENU_PANEL = pygame.Rect(40, 20, 240, 140)


def _menu_canvas(app, sprites):
    from albert.render import draw_app

    canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    draw_app(canvas, app, sprites)
    return canvas


def _tap(app, **keys):
    from albert.menu import Keys

    app.update(Keys(**keys), 1 / config.FPS)
    app.update(Keys(), 1 / config.FPS)


def test_r52_font_covers_a_to_z_and_every_menu_string():
    import string

    from albert import menu
    from albert.sprites import _FONT

    assert set(string.ascii_uppercase + string.digits + " /!>") <= set(_FONT)
    texts = [menu.TITLE, menu.MENU_HINT, menu.CONTROLS_TITLE, menu.CONTROLS_HINT, menu.OVERLAY_HINT, ">"]
    texts += list(menu.OPTIONS) + list(menu.CONTROLS_LINES)
    for text in texts:
        missing = set(text) - set(_FONT)
        assert not missing, f"{text!r} needs glyphs {missing}"


def test_r52_menu_draws_its_bordered_panel(sprites):
    from albert.menu import App

    canvas = _menu_canvas(App(), sprites)
    assert tuple(canvas.get_at((MENU_PANEL.left + 1, MENU_PANEL.top + 1)))[:3] == config.COLORS["cat_eye"]
    assert tuple(canvas.get_at((MENU_PANEL.left + 4, MENU_PANEL.top + 4)))[:3] == config.COLORS["panel"]


def test_r52_menu_has_no_hud(sprites):
    from albert.menu import App

    canvas = _menu_canvas(App(), sprites)
    hud = {tuple(canvas.get_at((x, y)))[:3] for x in range(2, 32) for y in range(2, 14)}
    assert config.COLORS["panel"] not in hud, "the HUD panel should not be drawn on the menu"


def test_r52_selected_option_is_highlighted_and_moves(sprites):
    from albert.menu import App

    app = App()
    first = _menu_canvas(app, sprites)
    yellow = config.COLORS["cat_eye"]

    def yellow_rows(canvas):
        inner = MENU_PANEL.inflate(-8, -8)
        return {y for y in range(inner.top, inner.bottom) for x in range(inner.left, inner.right)
                if tuple(canvas.get_at((x, y)))[:3] == yellow}

    assert yellow_rows(first) & set(range(70, 80)), "START is drawn in cat_eye"
    _tap(app, down=True)
    second = _menu_canvas(app, sprites)
    assert yellow_rows(second) & set(range(92, 102)), "CONTROLS is drawn in cat_eye"
    assert not yellow_rows(second) & set(range(70, 80))
    options = pygame.Rect(MENU_PANEL.left, 66, MENU_PANEL.width, 62)
    assert pygame.image.tobytes(first.subsurface(options), "RGB") != pygame.image.tobytes(second.subsurface(options), "RGB")


def test_r52_backdrop_animates_behind_the_menu(sprites):
    from albert.menu import App

    app = App()
    before = pygame.image.tobytes(_menu_canvas(app, sprites), "RGB")
    app.backdrop.ticks = 120
    assert pygame.image.tobytes(_menu_canvas(app, sprites), "RGB") != before


def test_r52_controls_screen_differs_from_the_menu(sprites):
    from albert.menu import App

    app = App()
    menu_look = pygame.image.tobytes(_menu_canvas(app, sprites), "RGB")
    _tap(app, down=True)
    menu_controls_selected = pygame.image.tobytes(_menu_canvas(app, sprites), "RGB")
    _tap(app, confirm=True)
    controls = pygame.image.tobytes(_menu_canvas(app, sprites), "RGB")
    assert controls != menu_look and controls != menu_controls_selected


def test_r52_game_screen_uses_the_normal_game_drawing(sprites):
    from albert.menu import App
    from albert.render import draw

    app = App()
    _tap(app, confirm=True)
    expected = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    draw(expected, app.game, sprites)
    assert pygame.image.tobytes(_menu_canvas(app, sprites), "RGB") == pygame.image.tobytes(expected, "RGB")


def test_r52_lose_overlay_shows_the_new_hint(sprites):
    from albert.game import Game, GameState
    from albert.menu import OVERLAY_HINT
    from albert.render import draw
    from albert.sprites import render_text

    game = Game()
    game.state = GameState.LOST
    canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    draw(canvas, game, sprites)
    hint = render_text(OVERLAY_HINT, config.COLORS["text_white"])
    panel = pygame.Rect(0, 0, 200, 52)
    panel.center = (config.INTERNAL_WIDTH // 2, config.INTERNAL_HEIGHT // 2)
    rect = hint.get_rect(midbottom=(panel.centerx, panel.bottom - 10))
    for x in range(hint.get_width()):
        for y in range(hint.get_height()):
            if hint.get_at((x, y)).a:
                assert tuple(canvas.get_at((rect.x + x, rect.y + y)))[:3] == config.COLORS["text_white"]


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
