# this_file: tests/test_fly_consumers.py
"""Qualify authored Fly consumers with stand-ins, never native handlers."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "Scripts/GrabLab"


@pytest.mark.parametrize("path,expected", [
    (SCRIPTS / "grablab_on_f5_mac.py", {"fly.ap", "fly.ap.hotkey", "grablab"}),
    (SCRIPTS / "grablab_on_save.py", {"fly.ap", "grablab"}),
    (ROOT / "examples/native_smoke.py", {
        "fly.ap", "fly.ap.application.preflib", "fly.qt", "grablab",
        "pathlib", "tempfile",
    }),
])
def test_authored_consumer_when_parsed_then_provider_imports_use_fly(path, expected):
    tree = ast.parse(path.read_text())
    assert {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} == expected
    assert not any(alias.name.startswith(("fontlabapp", "PythonQt"))
                   for node in ast.walk(tree) if isinstance(node, ast.Import)
                   for alias in node.names)


def test_embedded_main_when_parsed_then_only_example_application_uses_fly():
    path = ROOT / "src/grablab/grab.py"
    tree = ast.parse(path.read_text())
    main = tree.body[-1]
    assert isinstance(main, ast.If)
    assert ast.unparse(main.test) == "__name__ == '__main__'"
    assert isinstance(main.body[0], ast.ImportFrom)
    assert main.body[0].module == "fly.ap"
    assert [name.name for name in main.body[0].names] == ["Application"]
    assert any(isinstance(node, ast.ImportFrom) and node.module == "fontlabapp"
               for node in tree.body), "Library implementation keeps canonical imports"
    compile(tree, str(path), "exec")  # Compiling must not perform broad capture.


def install_standins(monkeypatch, **exports):
    """Replace only this test's import boundary; no provider is loaded."""
    for name, members in exports.items():
        module = ModuleType(name)
        vars(module).update(members)
        monkeypatch.setitem(sys.modules, name, module)


def test_save_script_when_connected_then_defers_capture_and_accepts_signal_bool(monkeypatch):
    callbacks, captures = [], []
    action = SimpleNamespace(triggered=SimpleNamespace(connect=callbacks.append))
    app = SimpleNamespace(ui=SimpleNamespace(menu=SimpleNamespace(
        file=SimpleNamespace(save_font=SimpleNamespace(qaction=action)))))
    install_standins(monkeypatch, **{
        "fly.ap": {"__all__": ["app"], "app": app},
        "grablab": {"Grab": lambda: SimpleNamespace(grabAll=lambda: captures.append("all"))},
    })
    runpy.run_path(str(SCRIPTS / "grablab_on_save.py"))
    assert len(callbacks) == 1 and not captures
    callbacks[0](True)
    callbacks[0]()
    assert captures == ["all", "all"]


def test_hotkey_script_when_run_then_preserves_registration_throttle_and_modal_route(monkeypatch):
    bindings, captures, starts = [], [], []
    modal = SimpleNamespace(className=lambda: "QDialog")
    active = [None]
    app = SimpleNamespace(qapp=SimpleNamespace(activeModalWidget=lambda: active[0]))
    hotkey = SimpleNamespace(on=lambda *args: bindings.append(args), run=lambda: starts.append(True))
    grab = SimpleNamespace(
        grabAll=lambda: captures.append("all"), newGrab=lambda: captures.append("new"),
        grabCanvas=lambda: captures.append("canvas"),
        grabWidget=lambda *args: captures.append(args),
        grabScreens=lambda screens: captures.append(screens),
    )
    install_standins(monkeypatch, **{
        "fly.ap": {"__all__": ["app"], "app": app},
        "fly.ap.hotkey": {"HotkeyManager": lambda: hotkey},
        "grablab": {"Grab": lambda: grab},
    })
    monkeypatch.setenv("GRABLAB", "0")
    namespace = runpy.run_path(str(SCRIPTS / "grablab_on_f5_mac.py"))
    assert starts == [True] and [binding[0] for binding in bindings] == ["F5", "F6"]
    assert [binding[1] for binding in bindings] == [namespace["grab_start_all"], namespace["grab_start_canvas"]]
    assert all(binding[2] is namespace["grab_stop"] for binding in bindings)
    assert not captures
    assert namespace["grab_start_all"]() is False and not captures
    monkeypatch.setenv("GRABLAB", "0")
    assert namespace["grab_start_all"]() is False
    assert captures == ["all"]
    monkeypatch.setenv("GRABLAB", "0")
    active[0] = modal
    assert namespace["grab_start_all"]() is False
    assert captures[1:] == ["new", (modal, "d", "qdialog"), [0]]
    monkeypatch.setenv("GRABLAB", "0")
    assert namespace["grab_start_canvas"]() is False
    assert captures[-2:] == ["new", "canvas"]
    assert namespace["grab_stop"]() is False
    assert namespace["grab_start_canvas"]() is False
    assert captures[-2:] == ["new", "canvas"]


@pytest.mark.parametrize("fail", [False, True])
def test_native_smoke_with_standins_when_capture_finishes_or_fails_then_cleans_up(monkeypatch, fail):
    applications, widgets, directories = [], [], []

    def application(**kwargs):
        assert kwargs == {"with_ui": True, "with_preflib": False}
        app = SimpleNamespace(paths=SimpleNamespace())
        applications.append(app)
        return app

    def widget():
        item = SimpleNamespace(resize=lambda *size: None, deleteLater=lambda: widgets.append("deleted"))
        widgets.append(item)
        return item

    def capture(application, folder_base):
        directories.append(folder_base)
        assert application is applications[0]
        assert application.paths.appPrefLibPath == folder_base / "prefs.json"

        def grab_widget(*args):
            assert args == (widgets[0], "test", "hidden", "Smoke widget")
            if fail:
                raise RuntimeError("owned capture failure")
            paths = [folder_base / "test.png", folder_base / "test.svg"]
            for path in paths:
                path.write_text("stand-in")
            return paths

        return SimpleNamespace(newGrab=lambda: None, grabWidget=grab_widget)

    install_standins(monkeypatch, **{
        "fly.ap": {"Application": application},
        "fly.ap.application.preflib": {"PrefLib": lambda app: SimpleNamespace(app=app)},
        "fly.qt": {"QtGui": SimpleNamespace(QWidget=widget)},
        "grablab": {"Grab": capture},
    })
    if fail:
        with pytest.raises(RuntimeError, match="owned capture failure"):
            runpy.run_path(str(ROOT / "examples/native_smoke.py"))
    else:
        runpy.run_path(str(ROOT / "examples/native_smoke.py"))
    assert widgets[-1] == "deleted"
    assert len(directories) == 1 and not directories[0].exists()
