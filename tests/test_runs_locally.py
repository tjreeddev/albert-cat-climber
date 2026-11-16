"""R8 — The game runs on the user's own computer."""

import ast
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "albert"

NETWORK_MODULES = {"socket", "urllib", "http", "requests", "ftplib", "smtplib", "ssl", "websockets"}
PURE_LOGIC_MODULES = ["config", "physics", "level", "game"]


def imported_top_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def test_r8_requirements_are_only_pygame_ce_and_pytest():
    lines = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    names = {
        re.split(r"[<>=!~\[ ;]", line.strip(), maxsplit=1)[0].lower()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    }
    assert names == {"pygame-ce", "pytest"}


def test_r8_pygame_ce_is_what_import_pygame_provides():
    """pygame-ce is installed and is imported with the standard `import pygame`."""
    from importlib.metadata import PackageNotFoundError, version

    import pygame

    assert getattr(pygame, "IS_CE", False), "import pygame did not load pygame-ce"
    try:
        version("pygame")
    except PackageNotFoundError:
        pass
    else:
        raise AssertionError("classic pygame is also installed; it conflicts with pygame-ce")


def test_r8_game_has_a_python_m_albert_entry_point():
    assert importlib.util.find_spec("albert.__main__") is not None


def test_r8_game_runs_300_frames_headlessly_with_scripted_input():
    from albert.__main__ import run
    from albert.game import Game, GameState, Inputs

    def script(frame):
        return Inputs(right=(frame // 60) % 2 == 0, left=(frame // 60) % 2 == 1, jump=frame % 45 == 0)

    game = run(max_frames=300, input_script=script)
    assert isinstance(game, Game)
    assert game.state in set(GameState)


def test_r8_game_does_not_use_the_network():
    files = list(PACKAGE.glob("*.py"))
    assert files, "albert package has no source files"
    for path in files:
        used = imported_top_modules(path) & NETWORK_MODULES
        assert not used, f"{path.name} imports network modules: {used}"


def test_r8_game_logic_does_not_import_pygame():
    """Supports headless testing: logic modules stay pure Python (CLAUDE.md)."""
    for name in PURE_LOGIC_MODULES:
        path = PACKAGE / f"{name}.py"
        assert path.exists(), f"missing albert/{name}.py"
        assert "pygame" not in imported_top_modules(path), f"albert/{name}.py imports pygame"
