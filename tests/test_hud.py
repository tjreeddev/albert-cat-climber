"""R12 — The HUD displays the number of collected treats and the total available."""

import pygame
import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
START = (100, FLOOR[1] - config.PLAYER_HEIGHT)
HUD_REGION = pygame.Rect(0, 0, 80, 20)  # top-left corner of the 320x180 screen
WHITE = config.COLORS["text_white"]


@pytest.fixture(scope="module")
def sprites():
    from albert.sprites import load_sprites

    pygame.init()
    pygame.display.set_mode((1, 1))
    return load_sprites()


def hud_pixels(game, sprites):
    """Positions of HUD text pixels in the top-left region after a full draw."""
    from albert import render

    canvas = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))
    render.draw(canvas, game, sprites)
    return {
        (x, y)
        for x in range(HUD_REGION.left, HUD_REGION.right)
        for y in range(HUD_REGION.top, HUD_REGION.bottom)
        if tuple(canvas.get_at((x, y)))[:3] == WHITE
    }


def test_r12_hud_text_shows_collected_over_total(default_game):
    from albert.game import hud_text

    assert hud_text(default_game) == "0/12"  # Round 4: 12 treats (was 0/5)


def test_r12_hud_text_updates_when_a_treat_is_collected(make_game, run_frames):
    from albert.game import hud_text

    game = make_game([FLOOR], start=START, treats=[(150, FLOOR[1] - 8), (260, FLOOR[1] - 8)])
    assert hud_text(game) == "0/2"
    run_frames(game, 60, right=True)
    assert hud_text(game) == "1/2"


def test_r12_font_has_every_hud_character(sprites):
    from albert.sprites import render_text

    for char in "0123456789/":
        glyph = render_text(char, WHITE)
        w, h = glyph.get_size()
        assert any(glyph.get_at((x, y)).a for x in range(w) for y in range(h)), f"no glyph for {char!r}"


def test_r12_digits_have_distinct_glyphs(sprites):
    from albert.sprites import render_text

    images = {pygame.image.tobytes(render_text(d, WHITE), "RGBA") for d in "0123456789"}
    assert len(images) == 10


def test_r12_hud_is_drawn_in_the_top_left(default_game, sprites):
    assert hud_pixels(default_game, sprites)


def test_r12_hud_pixels_change_with_the_count(make_game, run_frames, sprites):
    game = make_game([FLOOR], start=START, treats=[(150, FLOOR[1] - 8), (260, FLOOR[1] - 8)])
    before = hud_pixels(game, sprites)
    run_frames(game, 60, right=True)
    assert game.treats_collected == 1
    assert hud_pixels(game, sprites) != before


def test_r12_hud_is_fixed_to_the_screen_not_the_camera(default_game, sprites):
    at_bottom = hud_pixels(default_game, sprites)
    goal = default_game.level.goal_platform
    default_game.player.x, default_game.player.y = goal.x, goal.y - config.PLAYER_HEIGHT
    default_game.camera_y = 0
    default_game.camera_x = default_game.level.world_width - config.INTERNAL_WIDTH  # Round 4: x scrolls too
    assert hud_pixels(default_game, sprites) == at_bottom


@pytest.mark.parametrize("state", ["WON", "LOST"])
def test_r12_hud_is_shown_on_the_win_and_lose_screens(default_game, sprites, state):
    from albert.game import GameState

    playing = hud_pixels(default_game, sprites)
    default_game.state = GameState[state]
    assert hud_pixels(default_game, sprites) == playing
