# this_file: tests/test_install_contract.py
"""Source installer declarations and owned execution; no host/process/network effects."""

import runpy
import socket
import subprocess
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = "fontlab-fontlabapp>=1.2.0"
QUARTZ = "pyobjc-framework-Quartz>=10; sys_platform == 'darwin'"
FLY = "fontlab-fly>=1.3.0"
REQUIRES = [APP, FLY, QUARTZ]


def denied(*args, **kwargs):
    raise AssertionError("Real process/network access is forbidden in installer tests")


@pytest.fixture
def installer(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "home/.config"))
    monkeypatch.setattr(subprocess, "run", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    data, source = tmp_path / "data", tmp_path / "source"
    (source / "src/grablab").mkdir(parents=True)
    (source / "src/grablab/__init__.py").write_text("VALUE = 42\n")
    (source / "PKG-INFO").write_text("Name: fontlab-grablab\nVersion: 1.2.3\n")
    (source / "pyproject.toml").write_bytes((ROOT / "pyproject.toml").read_bytes())
    monkeypatch.setitem(sys.modules, "fontlab", SimpleNamespace(
        flPreferences=lambda: SimpleNamespace(dataPathDefault=str(data))))
    namespace = runpy.run_path(str(ROOT / "install.vfpy"), run_name="fontlab_install")
    globals_ = namespace["main"].__globals__
    globals_["SOURCE"] = source
    globals_["UV_CANDIDATES"] = ()
    monkeypatch.setattr(globals_["shutil"], "which", lambda name: None)
    assert not data.exists(), "Import must not initialize an installation"
    return SimpleNamespace(**globals_)


def test_source_install_declarations_and_sdist_inputs_are_explicit():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert project["project"]["dependencies"] == [APP]
    assert project["tool"]["fontlab-install"] == {
        "id": "com.fontlab.grablab", "dependencies": REQUIRES}
    assert {"Scripts", "install.vfpy"} <= set(
        project["tool"]["hatch"]["build"]["targets"]["sdist"]["only-include"])


@pytest.mark.parametrize("uv,status", [(None, 0), ("fake-uv", 0), ("fake-uv", 1)])
def test_source_install_when_consumer_dependencies_missing_then_exact_metadata_command_or_failure(
    installer, monkeypatch, capsys, uv, status
):
    i = installer
    calls = []

    def distribution(name):
        if i.norm(name) != i.norm("fontlab-fontlabapp"):
            raise i.metadata.PackageNotFoundError(name)
        # Installed earlier from its sibling checkout, so uv must not look it up.
        return SimpleNamespace(version="1.2.0", read_text=lambda f: "install.vfpy\n" if f == "INSTALLER" else None)

    def fake_run(command, **kwargs):
        assert command[0] == "fake-uv" and command[1:3] == ["pip", "install"]
        calls.append(command)
        return SimpleNamespace(returncode=status, stdout="owned uv result")

    monkeypatch.setattr(i.metadata, "distribution", distribution)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setitem(i.main.__globals__, "find_uv", lambda: uv)
    python = i.data_dir() / ".venv/bin/python"
    monkeypatch.setitem(i.main.__globals__, "ensure_venv", lambda *args: python)
    if status:
        with pytest.raises(RuntimeError, match="exit 1"):
            i.main()
    else:
        i.main()
    site = i.site_dir(i.data_dir())
    metadata = (site / "fontlab_grablab-1.2.3.dist-info/METADATA").read_text()
    assert [line for line in metadata.splitlines() if line.startswith("Requires-Dist:")] == [
        "Requires-Dist: " + req for req in REQUIRES]
    assert "Provides-Extra:" not in metadata
    records = i.read_log(i.data_dir() / "Extensions/com.fontlab.grablab")
    assert records[0]["requires"] == REQUIRES
    if uv:
        assert calls == [[uv, "pip", "install", "--link-mode=copy", "--python", str(python)] + REQUIRES]
    else:
        assert not calls and "Missing dependencies (install uv" in capsys.readouterr().out
    if status:
        assert records[-1]["action"] == "failed" and "owned uv result" in records[-1]["error"]
    else:
        assert records[-1]["action"] == "install"
    assert (i.SOURCE / "src/grablab/__init__.py").read_text() == "VALUE = 42\n"


def test_existing_presence_only_fast_path_is_retained_without_uv(installer, monkeypatch, capsys):
    i = installer
    monkeypatch.setattr(i.metadata, "distribution", lambda name: SimpleNamespace(version="0.0.0"))
    assert i.missing(REQUIRES) == [], "Known limit: presence does not validate installed versions"
    i.main()
    assert "Missing dependencies" not in capsys.readouterr().out


@pytest.mark.parametrize("version", ["0.0.0", "99.0.0"])
@pytest.mark.parametrize("python_route", [True, False])
def test_uv_when_distributions_present_then_resolves_complete_requirements(
    installer, monkeypatch, tmp_path, version, python_route
):
    i = installer
    monkeypatch.setattr(i.metadata, "distribution", lambda name: SimpleNamespace(version=version))
    calls = []
    monkeypatch.setitem(i.main.__globals__, "run", lambda cmd: (
        calls.append(cmd) or SimpleNamespace(returncode=0, stdout="resolved")))
    python = tmp_path / "venv/bin/python" if python_route else None
    i.install_dependencies(tmp_path, REQUIRES, "owned-uv", python)
    target = ["--python", str(python)] if python else [
        "--python", i.python_requests()[1], "--target", str(tmp_path)]
    assert calls == [["owned-uv", "pip", "install", "--link-mode=copy"] + target + REQUIRES]
    assert "--upgrade" not in calls[0] and "--reinstall" not in calls[0]


@pytest.mark.parametrize("requirements", [
    ["absent>=1; python_version < '0'"], ["owned[feature]>=2"],
])
def test_uv_when_marker_or_extra_then_preserves_original_declaration(
    installer, monkeypatch, tmp_path, requirements
):
    i = installer
    monkeypatch.setattr(i.metadata, "distribution", denied)
    calls = []
    monkeypatch.setitem(i.main.__globals__, "run", lambda cmd: (
        calls.append(cmd) or SimpleNamespace(returncode=0, stdout="resolved")))
    i.install_dependencies(tmp_path, requirements, "owned-uv", tmp_path / "python")
    assert calls[0][-len(requirements):] == requirements


@pytest.mark.parametrize("uv", [None, "owned-uv"])
def test_dependencies_when_empty_then_no_probe_or_process(installer, monkeypatch, tmp_path, uv):
    monkeypatch.setattr(installer.metadata, "distribution", denied)
    installer.install_dependencies(tmp_path, [], uv, None)


def test_main_when_uv_process_cannot_start_then_records_failure(installer, monkeypatch):
    i = installer
    monkeypatch.setitem(i.main.__globals__, "find_uv", lambda: "owned-uv")
    monkeypatch.setitem(i.main.__globals__, "ensure_venv", lambda *args: i.SOURCE / "python")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("owned failure")))
    with pytest.raises(OSError, match="owned failure"):
        i.main()
    assert "owned failure" in i.read_log(i.data_dir() / "Extensions/com.fontlab.grablab")[-1]["error"]
