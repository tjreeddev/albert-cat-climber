"""R43 — Dripping taps."""

from albert import config

FLOOR = (0, 500, 320, 16)
TOP = 436
ACTIVE = (FLOOR[1] - 6 - TOP) // 2 + 1  # 30 updates of falling
STAND_Y = FLOOR[1] - config.PLAYER_HEIGHT


def drip(idle=10, warning=20, active=ACTIVE, phase=0, x=150):
    return dict(kind="drip", x=x, top=TOP, section=1, idle=idle, warning=warning, active=active, phase=phase,
                floor=FLOOR[1])


def was_hit(game):
    return game.invulnerable_ticks > 0


def test_r43_drop_falls_two_pixels_per_update_and_lands_on_the_floor():
    from albert.hazards import hit_area, phase_of
    from albert.level import Hazard

    h = Hazard(**drip())
    start = h.idle + h.warning
    for k in range(ACTIVE):
        assert phase_of(h, start + k) == "active"
        assert hit_area(h, start + k) == (150, TOP + config.DRIP_SPEED * k, 4, 6)
    last = hit_area(h, start + ACTIVE - 1)
    assert last[1] + last[3] == FLOOR[1], "the last active position rests on the floor"


def test_r43_no_hit_area_while_idle_or_forming():
    from albert.hazards import hit_area
    from albert.level import Hazard

    h = Hazard(**drip())
    for t in range(h.idle + h.warning):
        assert hit_area(h, t) is None


def test_r43_a_falling_drop_hits_albert_standing_under_it(make_game, run_frames):
    from albert.hazards import phase_of

    game = make_game([FLOOR], start=(146, STAND_Y), hazards=[drip()])
    h = game.level.hazards[0]
    for _ in range(120):
        run_frames(game, 1)
        if was_hit(game):
            assert phase_of(h, game.hazard_ticks) == "active"
            break
    assert was_hit(game)


def test_r43_a_falling_drop_hits_albert_in_mid_air(make_game, run_frames):
    # Albert jumps just as the drop starts to fall, so they meet in the air.
    game = make_game([FLOOR], start=(146, STAND_Y), hazards=[drip(idle=0, warning=20)])
    run_frames(game, 19)
    run_frames(game, 1, jump=True)
    airborne_hit = False
    for _ in range(60):
        in_air = not game.player.on_ground
        run_frames(game, 1)
        if was_hit(game):
            airborne_hit = in_air
            break
    assert airborne_hit


def test_r43_albert_beside_the_drop_is_safe(make_game, run_frames):
    game = make_game([FLOOR], start=(154, STAND_Y), hazards=[drip()])  # starts at the drop's right edge
    for _ in range(200):
        run_frames(game, 1)
        assert not was_hit(game)


def test_r43_forming_drop_never_hits(make_game, run_frames):
    # A ledge holds Albert right under the tap; the drop forms there during the warning.
    ledge = (130, TOP + 14, 50, 16)
    game = make_game([FLOOR, ledge], start=(146, TOP), hazards=[drip(idle=0, warning=200)])
    for _ in range(199):
        run_frames(game, 1)
        assert not was_hit(game)
