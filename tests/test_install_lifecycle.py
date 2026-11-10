# this_file: tests/test_install_lifecycle.py
"""Original install.vfpy contracts, confined to temporary checkout/user folders."""

import json
import platform
import runpy
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

INSTALLER = Path(__file__).resolve().parents[1] / "install.vfpy"
EXT_ID = "org.example.fixture"


def denied(*args, **kwargs):
    raise AssertionError("Real process/network access is forbidden in installer tests")


@pytest.fixture
def installer(tmp_path, monkeypatch):
    isolated_home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(isolated_home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(isolated_home / ".config"))
    monkeypatch.setattr(subprocess, "run", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    data = tmp_path / "FontLab 9"
    source = tmp_path / "checkout"
    source.mkdir()
    (source / "pkg").mkdir()
    (source / "pkg/__init__.py").write_text("VALUE = 42\n")
    (source / "PKG-INFO").write_text("Name: fixture\nVersion: 1.2.3\n")
    (source / "pyproject.toml").write_text(
        '[project]\nname = "fixture-dist"\n'
        '[tool.hatch.build.targets.wheel]\npackages = ["pkg"]\n'
        '[tool.fontlab-install]\nid = "org.example.fixture"\nscripts = ["Menu"]\n'
    )
    (source / "Scripts/Group").mkdir(parents=True)
    (source / "Scripts/Group/One.py").write_bytes(b"#FLM: One\nprint('one')\n")
    (source / "Menu").mkdir()
    (source / "Menu/Two.vfpy").write_bytes(b"#FLM: Two\nprint('two')\n")
    preferences = SimpleNamespace(dataPathDefault=str(data))
    monkeypatch.setitem(sys.modules, "fontlab", SimpleNamespace(flPreferences=lambda: preferences))
    namespace = runpy.run_path(str(INSTALLER), run_name="fontlab_install")
    globals_ = namespace["main"].__globals__
    globals_["SOURCE"] = source
    globals_["UV_CANDIDATES"] = ()
    monkeypatch.setattr(globals_["shutil"], "which", lambda name: None)
    assert not data.exists(), "Safe import must not initialize FontLab or install anything"
    return SimpleNamespace(**globals_)


@pytest.mark.parametrize("mode", ["copied", "linked", "scripts-only"])
def test_main_when_owned_then_exact_payload_metadata_and_uninstall(installer, mode, capsys):
    i = installer
    if mode == "linked":
        (i.SOURCE / ".git").mkdir()
    if mode == "scripts-only":
        with (i.SOURCE / "pyproject.toml").open("a") as f:
            f.write("packages = []\n")
    i.main()
    data, site = i.data_dir(), i.site_dir(i.data_dir())
    state = i.installed()[EXT_ID]
    assert state["version"] == "1.2.3"
    assert state["mode"] == ("linked" if mode == "linked" else "copied")
    for source, relative in i.script_sources(["Menu"]):
        assert (data / "Scripts" / relative).read_bytes() == source.read_bytes()
    assert (site / "fontlab_install.py").read_bytes() == INSTALLER.read_bytes()
    if mode == "scripts-only":
        assert not list(site.glob("*.dist-info")) and not (site / "pkg").exists()
    else:
        target = i.SOURCE / "pkg" if mode == "linked" else data / "Extensions" / EXT_ID / "lib/pkg"
        assert (site / "pkg").resolve() == target
        assert (site / "pkg/__init__.py").read_bytes() == b"VALUE = 42\n"
        info = site / "fixture_dist-1.2.3.dist-info"
        assert (info / "METADATA").read_text() == "Metadata-Version: 2.1\nName: fixture-dist\nVersion: 1.2.3\n"
        assert (info / "INSTALLER").read_text() == "install.vfpy\n"
        assert "Tag: py3-none-any\n" in (info / "WHEEL").read_text()
        assert (info / "RECORD").read_text().splitlines() == [
            "pkg,,", *[f"{info.name}/{name},," for name in ("METADATA", "INSTALLER", "WHEEL", "RECORD")]
        ]
    foreign = data / "Scripts/Group/foreign.txt"
    foreign.write_bytes(b"keep")
    compiled = data / "Scripts/Group/One.pyc"
    compiled.write_bytes(b"compiled")
    assert i.list_extensions() == {EXT_ID: state}
    assert EXT_ID in capsys.readouterr().out
    i.uninstall(EXT_ID)
    assert i.installed() == {}
    assert foreign.read_bytes() == b"keep" and not compiled.exists()
    assert (i.SOURCE / "pkg/__init__.py").read_bytes() == b"VALUE = 42\n"
    assert [r["action"] for r in i.read_log(data / "Extensions" / EXT_ID)] == ["install", "uninstall"]
    assert i.list_extensions() == {}
    assert "No extensions installed" in capsys.readouterr().out
    with pytest.raises(RuntimeError, match="not installed"):
        i.uninstall(EXT_ID)


def test_update_when_owned_then_stale_files_removed_and_foreign_files_kept(installer):
    i = installer
    i.main()
    data = i.data_dir()
    old = data / "Scripts/Group/One.py"
    old.with_suffix(".vfpyc").write_bytes(b"cache")
    (i.SOURCE / "Scripts/Group/One.py").unlink()
    (i.SOURCE / "Menu/Two.vfpy").write_bytes(b"print('updated')\n")
    (i.SOURCE / ".git").mkdir()
    foreign = data / "Scripts/foreign.txt"
    foreign.write_text("keep")
    i.main()
    assert not old.exists() and not old.with_suffix(".vfpyc").exists()
    assert not (data / "Scripts/Group").exists()
    assert not (data / "Extensions" / EXT_ID / "lib").exists()
    assert (data / "Scripts/Menu/Two.vfpy").read_bytes() == b"print('updated')\n"
    assert foreign.read_text() == "keep"
    assert i.installed()[EXT_ID]["mode"] == "linked"


@pytest.mark.parametrize("conflict", ["script", "category-link"])
def test_main_when_script_path_taken_then_reinstalled_and_link_target_preserved(installer, tmp_path, conflict):
    """Scripts are always reinstalled: a file at a script path is replaced, a folder link becomes a real folder."""
    i = installer
    data = i.data_dir()
    outside = tmp_path / "foreign"
    outside.mkdir()
    (outside / "keep").write_bytes(b"foreign")
    script = data / "Scripts/Group/One.py"
    if conflict == "script":
        script.parent.mkdir(parents=True)
        script.write_bytes(b"stale")
    else:
        script.parent.parent.mkdir(parents=True)
        script.parent.symlink_to(outside, target_is_directory=True)
    i.main()
    assert script.read_bytes() == (i.SOURCE / "Scripts/Group/One.py").read_bytes()
    assert not script.parent.is_symlink()
    assert sorted(p.name for p in outside.iterdir()) == ["keep"], "A linked folder's target is never written"


def test_main_when_directory_at_script_path_then_refuses(installer):
    i = installer
    script = i.data_dir() / "Scripts/Group/One.py"
    script.mkdir(parents=True)
    with pytest.raises(RuntimeError, match="Refusing"):
        i.main()
    assert script.is_dir()


@pytest.mark.parametrize("conflict", ["extension", "extension-link", "package", "menu"])
def test_main_when_foreign_target_then_refuses_and_preserves(installer, tmp_path, conflict):
    i = installer
    data = i.data_dir()
    outside = tmp_path / "foreign"
    outside.mkdir()
    sentinel = outside / "keep"
    sentinel.write_bytes(b"foreign")
    targets = {
        "script": data / "Scripts/Group/One.py",
        "category-link": data / "Scripts/Group",
        "extension": data / "Extensions" / EXT_ID,
        "extension-link": data / "Extensions" / EXT_ID,
        "package": i.site_dir(data) / "pkg",
        "menu": data / "Scripts/Extensions",
    }
    target = targets[conflict]
    target.parent.mkdir(parents=True, exist_ok=True)
    if conflict.endswith("link"):
        target.symlink_to(outside, target_is_directory=True)
    elif conflict == "script":
        target.write_bytes(b"foreign")
    else:
        target.mkdir()
        (target / "keep").write_bytes(b"foreign")
    with pytest.raises(RuntimeError, match="Refusing"):
        i.main()
    assert sentinel.read_bytes() == b"foreign"
    if conflict.endswith("link"):
        assert target.is_symlink() and target.resolve() == outside
    else:
        assert (target if conflict == "script" else target / "keep").read_bytes() == b"foreign"
    if not conflict.startswith("extension"):
        assert i.read_log(data / "Extensions" / EXT_ID)[-1]["action"] == "failed"


def test_remove_when_outside_or_symlink_then_never_deletes_outside_target(installer, tmp_path):
    i = installer
    data = i.data_dir()
    data.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_bytes(b"keep")
    with pytest.raises(RuntimeError, match="outside"):
        i.remove_path(outside, data)
    link = data / "link.py"
    link.symlink_to(outside)
    i.remove_path(link, data)
    assert not link.is_symlink() and outside.read_bytes() == b"keep"


def test_copy_when_compilation_fails_then_previous_tree_survives(installer):
    i = installer
    target = i.data_dir() / "lib"
    i.copy_tree([i.SOURCE / "pkg"], target, EXT_ID)
    (i.SOURCE / "pkg/__init__.py").write_text("broken (\n")
    with pytest.raises(SyntaxError):
        i.copy_tree([i.SOURCE / "pkg"], target, EXT_ID)
    assert (target / "pkg/__init__.py").read_bytes() == b"VALUE = 42\n"
    assert not list(target.parent.glob(".lib.new-*"))
    (i.SOURCE / "pkg/__init__.py").write_text("VALUE = 43\n")
    i.copy_tree([i.SOURCE / "pkg"], target, EXT_ID)
    assert (target / "pkg/__init__.py").read_bytes() == b"VALUE = 43\n"
    assert not list(target.parent.glob(".lib.old-*"))


def test_scripts_when_junk_present_then_only_exact_sources_selected(installer):
    i = installer
    for name in ["Scripts/.DS_Store", "Scripts/Group/One.pyc", "Scripts/Group/One.vfpyc", "Scripts/__pycache__/cached.py"]:
        path = i.SOURCE / name
        path.parent.mkdir(exist_ok=True)
        path.write_text("ignored")
    assert {str(rel) for _, rel in i.script_sources(["Menu"])} == {"Group/One.py", "Menu/Two.vfpy"}
    (i.SOURCE / "Scripts").rename(i.SOURCE / "temporary-scripts")
    (i.SOURCE / "temporary-scripts").rename(i.SOURCE / "scripts")
    assert {str(rel) for _, rel in i.script_sources(["Menu"])} == {"Menu/Two.vfpy"}
    assert i.norm("FiXture.-Dist") == "fixture_dist"


@pytest.mark.parametrize("value", ["bad", "", "../outside"])
def test_main_when_invalid_id_then_refuses_before_user_folder_creation(installer, value):
    i = installer
    config = i.SOURCE / "pyproject.toml"
    config.write_text(config.read_text().replace(EXT_ID, value))
    with pytest.raises(RuntimeError, match="needs.*id"):
        i.main()
    assert not i.data_dir().exists()


def test_packages_when_absent_or_invalid_then_refuses(installer):
    i = installer
    for config in [{}, {"packages": ["missing"]}]:
        with pytest.raises(RuntimeError, match="wheel packages"):
            i.package_dirs({}, config)
    assert i.package_dirs({}, {"packages": []}) == []


@pytest.mark.parametrize("callable_value", [False, True])
def test_data_dir_when_preference_value_or_callable_then_resolves_owned_path(installer, monkeypatch, callable_value):
    data = installer.data_dir()
    value = (lambda: str(data)) if callable_value else str(data)
    monkeypatch.setitem(sys.modules, "fontlab", SimpleNamespace(flPreferences=lambda: SimpleNamespace(dataPathDefault=value)))
    assert installer.data_dir() == data
    monkeypatch.setitem(sys.modules, "fontlab", SimpleNamespace(flPreferences=lambda: SimpleNamespace(dataPathDefault="")))
    with pytest.raises(RuntimeError, match="did not report"):
        installer.data_dir()


@pytest.mark.parametrize("output,expected", [("v1.0.0-0-g123", "1.0.0"), ("v1.0.0-2-g123", "1.0.0+2.g123"), ("invalid", "9.0")])
def test_version_when_git_describe_then_tag_distance_or_fallback(installer, monkeypatch, output, expected):
    i = installer
    (i.SOURCE / "PKG-INFO").write_text("Name: no-version\n")
    calls = []
    def fake(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(stdout=output)
    monkeypatch.setattr(subprocess, "run", fake)
    assert i.version({"tool": {"hatch": {"version": {"raw-options": {"fallback_version": "9.0"}}}}}) == expected
    assert calls[0][0][:3] == ["git", "-C", str(i.SOURCE)]
    assert calls[0][1]["timeout"] == 20 and calls[0][1]["check"] is True
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(OSError("no git")))
    assert i.version({}) == "0.0.0"


def test_site_when_legacy_link_then_preserves_inside_and_outside_contents(installer, tmp_path):
    i = installer
    data = i.data_dir()
    site = i.site_dir(data)
    site.parent.mkdir(parents=True)
    for original in [data / "old-site", tmp_path / "outside-site"]:
        original.mkdir()
        (original / "keep.txt").write_text("keep")
        site.symlink_to(original, target_is_directory=True)
        assert i.prepare_site(data) == site
        assert not site.is_symlink() and (site / "keep.txt").read_text() == "keep"
        assert original.exists() == (original.parent == tmp_path)
        (site / "keep.txt").unlink()
        site.rmdir()


def test_venv_links_when_repaired_then_keeps_packages_and_refuses_foreign_dirs(installer, tmp_path):
    i = installer
    data = i.data_dir()
    site = i.prepare_site(data)
    venv = data / ".venv"
    _, vsite = i.venv_paths(venv)
    vsite.mkdir(parents=True)
    (vsite / "keep.py").write_text("owned")
    (vsite / "_virtualenv.py").write_text("do not import")
    (vsite / "existing.py").write_text("old")
    (site / "existing.py").write_text("current")
    i.link_venv_site(vsite, site)
    i.link_venv_site(vsite, site)
    assert vsite.resolve() == site and (site / "keep.py").read_text() == "owned"
    assert (site / "existing.py").read_text() == "current" and not (site / "_virtualenv.py").exists()
    i.link_venv_dirs(data, venv)
    i.link_venv_dirs(data, venv)
    for name in i.VENV_DIRS:
        assert (data / name).resolve() == venv / name
    (data / "bin").unlink()
    (data / "bin").mkdir()
    with pytest.raises(RuntimeError, match="Refusing"):
        i.link_venv_dirs(data, venv)


@pytest.mark.parametrize("outcome", ["existing", "create", "fail", "mismatch", "no-links"])
def test_venv_when_process_outcome_then_matching_or_preserved_failure(installer, monkeypatch, outcome):
    i = installer
    data = i.data_dir()
    site = i.prepare_site(data)
    python, vsite = i.venv_paths(data / ".venv")
    python.parent.mkdir(parents=True)
    python.write_text("previous interpreter")
    good = [list(sys.version_info[:2]), platform.machine(), str(site)]
    calls = []
    def fake_run(command, **kwargs):
        calls.append(command)
        if command[0] == "fake-uv":
            if outcome == "fail" or len([c for c in calls if c[0] == "fake-uv"]) == 1:
                return SimpleNamespace(returncode=1, stdout="unavailable")
            python.parent.mkdir(parents=True, exist_ok=True)
            python.write_text("new interpreter")
            return SimpleNamespace(returncode=0, stdout="created")
        found = good if outcome in ("existing", "no-links") or python.read_text() == "new interpreter" else [[0, 0], "wrong", "wrong"]
        if outcome == "mismatch":
            found = [[0, 0], "wrong", "wrong"]
        return SimpleNamespace(returncode=0, stdout=json.dumps(found))
    monkeypatch.setattr(subprocess, "run", fake_run)
    if outcome == "no-links":
        monkeypatch.setattr(i.os, "symlink", lambda *a, **k: (_ for _ in ()).throw(OSError("denied")))
        assert i.ensure_venv(data, site, "fake-uv") is None
    elif outcome in ("fail", "mismatch"):
        with pytest.raises(RuntimeError, match="could not create|does not match"):
            i.ensure_venv(data, site, "fake-uv")
    else:
        assert i.ensure_venv(data, site, "fake-uv") == python
        assert vsite.resolve() == site
    if outcome not in ("existing", "no-links"):
        backups = list(data.glob(".venv.backup-*"))
        assert len(backups) == 1 and (backups[0] / "bin/python").read_text() == "previous interpreter"
    assert all(c[0] in ("fake-uv", str(python)) for c in calls)


def test_uv_and_probe_when_missing_or_available_then_deterministic_result(installer, tmp_path, monkeypatch):
    i = installer
    assert i.find_uv() is None
    uv = tmp_path / "uv"
    uv.write_text("fake")
    monkeypatch.setitem(i.main.__globals__, "UV_CANDIDATES", (str(tmp_path / "absent"), str(uv)))
    assert i.find_uv() == str(uv)
    assert i.probe(tmp_path / "missing-python") is None
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="bad"))
    assert i.probe(uv) is None
    assert not i.matches(None)
    assert not i.matches([list(sys.version_info[:2]), "wrong", str(tmp_path)])
    assert not i.matches([list(sys.version_info[:2]), platform.machine(), "wrong"], tmp_path)


def test_record_when_symlinks_denied_then_copy_and_metadata_requirements(installer, monkeypatch):
    i = installer
    site = i.prepare_site(i.data_dir())
    monkeypatch.setattr(i.os, "symlink", lambda *a, **k: (_ for _ in ()).throw(OSError("denied")))
    placed = i.write_record(site, "fixture-dist", "1.0", [i.SOURCE / "pkg"], ["dep>=1"])
    assert not placed[0].is_symlink() and (placed[0] / "__init__.py").read_bytes() == b"VALUE = 42\n"
    assert "Requires-Dist: dep>=1\n" in (placed[1] / "METADATA").read_text()
    i.remove_old_dist(site, "fixture-dist")
    assert not any(site.iterdir())
