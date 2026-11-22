"""R45 — Hazards are clearly telegraphed and look different from decorations (pure parts).

The sprite and headless render checks for R45 live in test_art_style.py.
"""

from albert import config


def test_r45_warning_colours_are_declared_in_the_palette():
    for name in ("warn_orange", "warn_red"):
        assert name in config.COLORS
        assert config.COLORS[name] in config.PALETTE


def test_r45_warning_colours_are_unique_in_the_palette():
    warn = {config.COLORS["warn_orange"], config.COLORS["warn_red"]}
    others = [c for name, c in config.COLORS.items() if name not in ("warn_orange", "warn_red")]
    assert len(warn) == 2
    assert not warn & set(others)


def test_r45_an_active_jet_is_at_least_10_px_wide():
    assert config.JET_SIZE[0] >= 10


def test_r45_every_hazard_has_a_warning_before_it_turns_active():
    from albert.hazards import phase_of
    from albert.level import build_level

    for h in build_level().hazards:
        cycle = h.idle + h.warning + h.active
        phases = [phase_of(h, t) for t in range(cycle)]
        for t in range(cycle):
            if phases[t] == "active" and phases[t - 1] != "active":
                assert phases[t - 1] == "warning", f"{h.kind} turns active without a warning"
        assert h.warning >= 45, "warnings last at least 0.75 s"
