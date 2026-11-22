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
    """R8, revised in Round 7 (R53): the run starts on the menu, confirms START, then plays."""
    from albert.__main__ import run
    from albert.game import Game, GameState
    from albert.menu import App, Keys, Screen

    def script(frame):
        if frame == 0:
            return Keys(confirm=True)  # START
        if frame == 1:
            return Keys()  # release everything: the start gate opens
        return Keys(right=(frame // 60) % 2 == 0, left=(frame // 60) % 2 == 1, jump=frame % 45 == 0)

    app = run(max_frames=300, input_script=script)
    assert isinstance(app, App)
    assert app.screen == Screen.GAME
    assert isinstance(app.game, Game)
    assert app.game.state in set(GameState)
    assert app.game.ticks == 299, "every frame after START updated the game"
    assert app.game.player.x != Game().player.x, "the scripted input reached the game"


def test_r53_a_scripted_quit_ends_the_run_early():
    from albert.__main__ import run
    from albert.menu import Keys

    presses = {0: Keys(up=True), 2: Keys(confirm=True)}  # up wraps to QUIT, then confirm

    app = run(max_frames=300, input_script=lambda frame: presses.get(frame, Keys()))
    assert app.quit_requested is True
    assert app.backdrop.ticks == 3, "the run stopped right after the quitting update"


def test_r53_read_inputs_maps_keys_as_in_the_spec():
    import pygame

    from albert.__main__ import read_inputs
    from albert.menu import Keys

    expected = {
        pygame.K_LEFT: {"left"}, pygame.K_a: {"left"},
        pygame.K_RIGHT: {"right"}, pygame.K_d: {"right"},
        pygame.K_UP: {"up", "jump"}, pygame.K_w: {"up", "jump"},
        pygame.K_DOWN: {"down"}, pygame.K_s: {"down"},
        pygame.K_SPACE: {"jump", "confirm"},
        pygame.K_RETURN: {"confirm", "restart"},
        pygame.K_ESCAPE: {"back"}, pygame.K_BACKSPACE: {"back"},
        pygame.K_r: {"restart"},
        pygame.K_m: {"menu"},
    }
    fields = set(Keys.__dataclass_fields__)
    for key, on in expected.items():
        keys = read_inputs({key})
        assert isinstance(keys, Keys)
        assert {f for f in fields if getattr(keys, f)} == on, pygame.key.name(key)
    assert not any(getattr(read_inputs(set()), f) for f in fields)


def test_r53_menu_module_is_pure_and_offline():
    path = PACKAGE / "menu.py"
    assert path.exists()
    imported = imported_top_modules(path)
    assert "pygame" not in imported
    assert not imported & NETWORK_MODULES


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
