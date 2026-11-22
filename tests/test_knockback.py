"""R44 — Knockback, control override and invulnerability."""

import math

import pytest

from albert import config

FLOOR = (0, 500, 320, 16)
STAND_Y = FLOOR[1] - config.PLAYER_HEIGHT
DT = 1 / config.FPS
ALWAYS = dict(idle=0, warning=0, active=60)


def vent(x=150, top=500, **timing):
    args = dict(kind="vent", x=x, top=top, section=1)
    args.update(timing or ALWAYS)
    return args


def test_r44_knockback_constants_match_the_spec():
    assert config.KNOCKBACK_SPEED == 180
    assert config.KNOCKBACK_TICKS == 18
    assert config.INVULNERABLE_TICKS == 60
    assert config.HIT_PUFF_COUNT == 6


@pytest.mark.parametrize("albert_x, expected_dir", [(150, 1), (146, -1), (158, 1)])
def test_r44_a_hit_sets_the_knockback_state(make_game, run_frames, albert_x, expected_dir):
    # The jet is x 152-164 (centre 158); Albert's centre is albert_x + 8.
    game = make_game([FLOOR], start=(albert_x, STAND_Y), hazards=[vent()])
    run_frames(game, 1)
    p = game.player
    assert p.vy == -config.KNOCKBACK_SPEED
    assert p.on_ground is False
    assert game.knockback_dir == expected_dir
    assert game.knockback_ticks == config.KNOCKBACK_TICKS
    assert game.invulnerable_ticks == config.INVULNERABLE_TICKS


def test_r44_input_is_overridden_for_18_updates_then_works_again(make_game, run_frames):
    game = make_game([FLOOR], start=(160, STAND_Y))
    game.knockback_ticks, game.knockback_dir = config.KNOCKBACK_TICKS, 1
    p = game.player
    for n in range(config.KNOCKBACK_TICKS):
        x = p.x
        run_frames(game, 1, left=True, jump=True)
        assert p.x == pytest.approx(x + config.MOVE_SPEED * DT), f"update {n + 1} should push right"
        assert p.on_ground, "jump is ignored while knocked back"
    assert game.knockback_ticks == 0
    x = p.x
    run_frames(game, 1, left=True)
    assert p.x == pytest.approx(x - config.MOVE_SPEED * DT), "update 19 follows the input again"


def test_r44_jump_works_again_after_the_override(make_game, run_frames):
    game = make_game([FLOOR], start=(160, STAND_Y))
    game.knockback_ticks, game.knockback_dir = 2, -1
    run_frames(game, 2, jump=True)
    assert game.player.on_ground
    run_frames(game, 1, jump=True)
    assert game.player.vy < 0


def test_r44_no_hit_for_59_updates_then_hit_again(make_game, run_frames):
    # Albert stays inside a tall, always-active jet on a ledge-free floor while invulnerable.
    game = make_game([FLOOR], start=(150, STAND_Y), hazards=[vent()])
    game.invulnerable_ticks = config.INVULNERABLE_TICKS
    for n in range(config.INVULNERABLE_TICKS - 1):
        run_frames(game, 1)
        assert game.invulnerable_ticks == config.INVULNERABLE_TICKS - 1 - n
        assert game.knockback_ticks == 0, f"update {n + 1} must not hit"
    run_frames(game, 1)
    assert game.knockback_ticks == config.KNOCKBACK_TICKS, "the 60th update can hit again"
    assert game.invulnerable_ticks == config.INVULNERABLE_TICKS


def test_r44_a_hit_spawns_six_puffs_at_alberts_centre(make_game, run_frames):
    game = make_game([FLOOR], start=(150, STAND_Y), hazards=[vent()])
    run_frames(game, 1)
    puffs = [q for q in game.particles if q.kind == "puff"]
    assert len(puffs) == config.HIT_PUFF_COUNT
    p = game.player
    for q in puffs:
        assert (q.x, q.y) == pytest.approx((p.x + p.width / 2, p.y + p.height / 2))
        assert math.hypot(q.vx, q.vy) == pytest.approx(30)
        assert q.life == 15
    assert puffs[0].vx == pytest.approx(0, abs=1e-9) and puffs[0].vy == pytest.approx(-30)


def test_r44_hits_do_not_touch_treats_or_the_hud(make_game, run_frames):
    from albert.game import hud_text

    game = make_game([FLOOR], start=(150, STAND_Y), treats=[(260, FLOOR[1] - 8)], hazards=[vent()])
    before = (game.treats_collected, list(game.visible_treats()), hud_text(game))
    run_frames(game, 1)
    assert game.invulnerable_ticks > 0
    assert (game.treats_collected, list(game.visible_treats()), hud_text(game)) == before


def test_r44_a_knockback_out_of_the_world_loses_only_through_r4(make_game, run_frames):
    from albert.game import GameState

    # A short ledge with nothing below: the 30 px push takes Albert from x 152 to 182, off its edge at 180.
    ledge = (140, 300, 40, 16)
    game = make_game([ledge], start=(152, 300 - config.PLAYER_HEIGHT), world_height=600,
                     hazards=[vent(top=300)])
    for _ in range(300):
        run_frames(game, 1)
        if game.state == GameState.LOST:
            break
        assert game.player.y <= game.level.world_height
    assert game.state == GameState.LOST
    assert game.player.y > game.level.world_height


def test_r44_restart_clears_knockback_and_invulnerability(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=(150, STAND_Y), hazards=[vent()])
    run_frames(game, 1)
    assert game.knockback_ticks and game.invulnerable_ticks
    game.player.y, game.player.vy = game.level.world_height + 1, 0  # cancel the knockback bounce
    run_frames(game, 1)
    assert game.state == GameState.LOST
    run_frames(game, 1, restart=True)
    assert (game.hazard_ticks, game.knockback_ticks, game.invulnerable_ticks) == (0, 0, 0)


def test_r44_knockback_freezes_when_lost(make_game, run_frames):
    from albert.game import GameState

    game = make_game([FLOOR], start=(150, STAND_Y), hazards=[vent()])
    run_frames(game, 1)
    game.player.y, game.player.vy = game.level.world_height + 1, 0  # cancel the knockback bounce
    run_frames(game, 1)
    assert game.state == GameState.LOST
    frozen = (game.knockback_ticks, game.invulnerable_ticks)
    run_frames(game, 10)
    assert (game.knockback_ticks, game.invulnerable_ticks) == frozen


def test_r44_win_takes_priority_over_a_hit_on_the_same_update(make_game, run_frames):
    from albert.game import GameState

    start = (150, 420)

    def landing_update():
        game = make_game([FLOOR], start=start, add_decoy_goal=False)
        for n in range(1, 200):
            run_frames(game, 1)
            if game.state == GameState.WON:
                return n
        return None

    n = landing_update()
    assert n
    # The vent on the goal turns active exactly on the landing update n.
    game = make_game([FLOOR], start=start, add_decoy_goal=False, hazards=[vent(idle=n, warning=0, active=30)])
    run_frames(game, n)
    assert game.state == GameState.WON
    assert game.invulnerable_ticks == 0 and game.knockback_ticks == 0
    assert not [q for q in game.particles if q.kind == "puff"]
