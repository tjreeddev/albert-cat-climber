"""R42 — Hot burners."""

from albert import config

FLOOR = (0, 500, 320, 16)
STOVE = (140, 450, 48, 16)  # burner strip from x 156 to 172
ON_STOVE_Y = STOVE[1] - config.PLAYER_HEIGHT
ALWAYS = dict(idle=0, warning=0, active=60)


def burner(**timing):
    args = dict(kind="burner", x=156, top=STOVE[1], section=1)
    args.update(timing or ALWAYS)
    return args


def was_hit(game):
    return game.invulnerable_ticks > 0


def test_r42_burner_hit_area_is_the_strip_while_active():
    from albert.hazards import hit_area, phase_of
    from albert.level import Hazard

    h = Hazard("burner", 156, 450, 1, idle=10, warning=5, active=5)
    for t in range(40):
        expected = (156, 449, config.BURNER_WIDTH, 1) if phase_of(h, t) == "active" else None
        assert hit_area(h, t) == expected


def test_r42_standing_on_a_hot_burner_is_a_hit(make_game, run_frames):
    game = make_game([FLOOR, STOVE], start=(150, ON_STOVE_Y), hazards=[burner()])
    assert game.player.on_ground
    run_frames(game, 1)
    assert was_hit(game)


def test_r42_standing_clear_of_the_strip_is_safe(make_game, run_frames):
    for x in (140, 172):  # touching the strip's edges only
        game = make_game([FLOOR, STOVE], start=(x, ON_STOVE_Y), hazards=[burner()])
        for _ in range(60):
            run_frames(game, 1)
            assert not was_hit(game), x


def test_r42_being_in_mid_air_above_it_is_safe_until_landing(make_game, run_frames):
    game = make_game([FLOOR, STOVE], start=(156, 380), hazards=[burner()])
    for _ in range(120):
        run_frames(game, 1)
        if was_hit(game):
            break
    assert was_hit(game), "landing on the hot strip is standing on it"
    # The hit came on the landing update: Albert's feet are on the stove top, not above it.
    assert game.player.y + game.player.height == STOVE[1]


def test_r42_jumping_up_through_the_stove_cabinet_is_safe(make_game, run_frames):
    game = make_game([FLOOR, STOVE], start=(156, FLOOR[1] - config.PLAYER_HEIGHT), hazards=[burner()])
    run_frames(game, 1, jump=True)
    while game.player.vy < 0:
        assert not was_hit(game)
        run_frames(game, 1)
    assert not was_hit(game)


def test_r42_no_hit_while_idle_or_warning(make_game, run_frames):
    game = make_game([FLOOR, STOVE], start=(150, ON_STOVE_Y), hazards=[burner(idle=100, warning=100, active=10)])
    for _ in range(199):
        run_frames(game, 1)
        assert not was_hit(game)
    run_frames(game, 1)
    assert was_hit(game), "update 200 is the first active one"


def test_r42_burner_cabinet_collides_like_any_cabinet(make_game, run_frames):
    def landing(hazards):
        game = make_game([FLOOR, STOVE], start=(144, 380), hazards=hazards)
        for n in range(200):
            run_frames(game, 1)
            if game.player.on_ground:
                return n, game.player.y
        return None

    cold = burner(idle=1000, warning=10, active=10)
    assert landing([cold]) == landing([])
