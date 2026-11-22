"""R32 — Effects are visual only and reset on restart."""

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
LEDGE = (160, 470, 48, 16)
START = (40, FLOOR[1] - config.PLAYER_HEIGHT)


def gameplay(game):
    from albert.game import hud_text

    p = game.player
    return (
        (p.x, p.y, p.vx, p.vy, p.on_ground, p.facing),
        [(d.x, d.direction) for d in game.drawers],
        (game.camera_x, game.camera_y),
        game.state,
        game.treats_collected,
        hud_text(game),
    )


def scripted(frame):
    """Walk right, hop now and then, wander back: lands, collects, rides."""
    keys = {}
    if frame % 240 < 160:
        keys["right"] = True
    elif frame % 240 < 220:
        keys["left"] = True
    if frame % 45 in (0, 1):
        keys["jump"] = True
    return keys


def default_level_script(frame):
    """On the default level: walk, hop onto the second cabinet and settle (a sure
    landing), then carry on with the wandering script."""
    if frame < 20:
        return dict(right=True)
    if frame < 50:
        return dict(right=True, jump=frame == 20)
    if frame < 90:
        return {}
    return scripted(frame - 90)


def record(game, run_frames, frames, script=scripted):
    states, saw_particles = [], False
    for f in range(frames):
        run_frames(game, 1, **script(f))
        states.append(gameplay(game))
        saw_particles = saw_particles or bool(game.particles)
    return states, saw_particles


def no_effects(monkeypatch):
    from albert import effects

    monkeypatch.setattr(effects, "dust_particles", lambda *a, **k: [])
    monkeypatch.setattr(effects, "sparkle_particles", lambda *a, **k: [])


def test_r32_custom_level_plays_the_same_with_and_without_effects(make_game, run_frames, monkeypatch):
    level_args = dict(
        platforms=[FLOOR, LEDGE],
        start=START,
        treats=[(120, FLOOR[1] - 8), (180, LEDGE[1] - 8)],
        drawers=[dict(min_x=220, max_x=280, y=480, speed=30)],
    )
    with_fx, saw = record(make_game(**level_args, decorations=[("mug", 60, 484), ("clock", 20, 420)]), run_frames, 600)
    assert saw, "the script should cause at least one effect"

    no_effects(monkeypatch)
    without, saw = record(make_game(**level_args), run_frames, 600)
    assert not saw
    assert with_fx == without


def test_r32_default_level_plays_the_same_with_and_without_effects(run_frames, monkeypatch):
    from albert.game import Game
    from albert.level import build_level

    with_fx, saw = record(Game(), run_frames, 900, default_level_script)
    assert saw

    no_effects(monkeypatch)
    bare = build_level()
    bare.decorations = []
    without, _ = record(Game(level=bare), run_frames, 900, default_level_script)
    assert with_fx == without


def test_r32_albert_falls_straight_through_a_decoration(make_game, run_frames):
    # A mug floating in mid-air, directly under Albert, with nothing else to land on.
    game = make_game([FLOOR], start=(100, 300), decorations=[("mug", 104, 360)])
    run_frames(game, 1)
    while game.player.y + game.player.height < 360 + 16:
        assert not game.player.on_ground
        run_frames(game, 1)
    assert game.player.vy > 0
    assert not game.player.on_ground


def test_r32_default_decorations_are_not_platforms(default_game):
    for d in default_game.level.decorations:
        assert all(d is not p for p in default_game.level.platforms)


def test_r32_physics_constants_are_unchanged():
    assert config.MOVE_SPEED == 100.0
    assert config.GRAVITY == 900.0
    assert config.JUMP_VELOCITY == 320.0
    assert config.MAX_FALL_SPEED == 400.0


def _land_then_lose(make_game, run_frames):
    """Land on FLOOR (spawning dust), then fall out of the world."""
    from albert.game import GameState

    game = make_game([FLOOR], start=(100, 440))
    while not game.particles:
        run_frames(game, 1)
    game.player.y = game.level.world_height + 1
    game.player.on_ground = False
    run_frames(game, 1)
    assert game.state == GameState.LOST
    assert game.particles
    return game


def test_r32_restart_after_losing_clears_ticks_and_particles(make_game, run_frames):
    game = _land_then_lose(make_game, run_frames)
    run_frames(game, 1, restart=True)
    assert game.ticks == 0
    assert game.particles == []


def test_r32_restart_after_winning_clears_ticks_and_particles(make_game, run_frames):
    from albert import effects
    from albert.game import GameState

    game = make_game([FLOOR], start=(100, 440), add_decoy_goal=False)
    run_frames(game, 120)
    assert game.state == GameState.WON
    assert game.ticks > 0
    game.particles.extend(effects.dust_particles(game.player))  # the winning dust has faded by now
    run_frames(game, 1, restart=True)
    assert game.ticks == 0
    assert game.particles == []


def test_r32_restart_during_playing_changes_neither(make_game, run_frames):
    game = make_game([FLOOR], start=(100, 440))
    while not game.particles:
        run_frames(game, 1)
    ticks, count = game.ticks, len(game.particles)
    run_frames(game, 1, restart=True)
    assert game.ticks == ticks + 1
    assert len(game.particles) == count
