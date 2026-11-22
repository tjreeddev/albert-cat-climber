"""R41 — Steam vents."""

from albert import config

FLOOR = (0, 500, 320, 16)
STAND_Y = FLOOR[1] - config.PLAYER_HEIGHT
ALWAYS = dict(idle=0, warning=0, active=60)  # active on every update
NEVER_ACTIVE_SOON = dict(idle=500, warning=100, active=10)


def vent(x=150, top=500, **timing):
    args = dict(kind="vent", x=x, top=top, section=1)
    args.update(timing or ALWAYS)
    return args


def was_hit(game):
    return game.invulnerable_ticks > 0


def test_r41_jet_area_is_exact_while_active():
    from albert.hazards import hit_area, phase_of
    from albert.level import Hazard

    h = Hazard("vent", 150, 500, 1, idle=10, warning=5, active=5)
    for t in range(40):
        if phase_of(h, t) == "active":
            assert hit_area(h, t) == (152, 444, 12, 56)
        else:
            assert hit_area(h, t) is None


def test_r41_standing_in_an_active_jet_is_a_hit(make_game, run_frames):
    game = make_game([FLOOR], start=(148, STAND_Y), hazards=[vent()])
    run_frames(game, 1)
    assert was_hit(game)


def test_r41_standing_beside_the_jet_is_safe(make_game, run_frames):
    game = make_game([FLOOR], start=(120, STAND_Y), hazards=[vent()])  # 120-136, jet starts at 152
    for _ in range(60):
        run_frames(game, 1)
        assert not was_hit(game)


def test_r41_touching_only_the_jets_edge_is_safe(make_game, run_frames):
    game = make_game([FLOOR], start=(152 - config.PLAYER_WIDTH, STAND_Y), hazards=[vent()])
    for _ in range(60):
        run_frames(game, 1)
        assert not was_hit(game)


def test_r41_falling_into_an_active_jet_is_a_hit(make_game, run_frames):
    game = make_game([FLOOR], start=(150, 380), hazards=[vent()])
    assert not game.player.on_ground
    for _ in range(60):
        run_frames(game, 1)
        if was_hit(game):
            break
    assert was_hit(game)


def test_r41_rising_into_an_active_jet_is_a_hit(make_game, run_frames):
    # The vent sits on a ledge above Albert; he jumps up through the ledge into its jet.
    ledge = (130, 450, 60, 16)
    game = make_game([FLOOR, ledge], start=(150, STAND_Y), hazards=[vent(top=450)])
    run_frames(game, 1, jump=True)
    rising_hit = False
    for _ in range(40):
        vy_before = game.player.vy
        run_frames(game, 1)
        if was_hit(game):
            rising_hit = vy_before < 0
            break
    assert rising_hit, "Albert should be hit while still rising"


def test_r41_no_hit_while_idle_or_warning(make_game, run_frames):
    game = make_game([FLOOR], start=(148, STAND_Y), hazards=[vent(**NEVER_ACTIVE_SOON)])
    for _ in range(300):
        run_frames(game, 1)
        assert not was_hit(game)


def test_r41_the_vent_is_not_a_platform(make_game, run_frames):
    game = make_game([FLOOR], start=(150, 400), hazards=[vent(top=500, **NEVER_ACTIVE_SOON)])
    for _ in range(120):
        run_frames(game, 1)
    assert game.player.on_ground
    assert game.player.y + game.player.height == FLOOR[1]  # landed on the floor, not the vent box
