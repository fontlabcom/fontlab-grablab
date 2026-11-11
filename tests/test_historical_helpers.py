# this_file: tests/test_historical_helpers.py
"""Historical helper dispositions stay explicit and inactive (Issue 250, TODO row 20).

README lists five earlier helpers as preserved historical source outside active
Scripts and distributions. Their preserved source is not on GrabLab ``main``;
these tests guard the README dispositions and the absence of every helper from
Scripts, the wheel/sdist inputs and the installer.
"""

import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPERS = (
    "copy_statusid.py",
    "copy_statusid2.py",
    "print_menu.py",
    "print_uimenu.py",
    "ui_hider.py",
)


def _readme_dispositions() -> dict[str, str]:
    lines = (ROOT / "README.md").read_text().splitlines()
    return {
        line.split("`")[1]: line.split(":", 1)[1].strip()
        for line in lines
        if line.startswith("- `") and line.split("`")[1] in HELPERS
    }


def test_readme_when_read_then_every_helper_has_one_disposition():
    dispositions = _readme_dispositions()
    assert sorted(dispositions) == sorted(HELPERS), dispositions
    assert all(dispositions.values()), dispositions
    assert (
        "outside active Scripts\nand distributions" in (ROOT / "README.md").read_text()
    )


def _distribution_roots() -> list[Path]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    build = project["tool"]["hatch"]["build"]["targets"]
    roots = {ROOT / p for p in build["wheel"]["packages"]} | {
        ROOT / p for p in build["sdist"]["only-include"]
    }
    roots |= {
        ROOT / "Scripts" / p
        for p in project["tool"].get("fontlab-install", {}).get("scripts", [])
    }
    return sorted(roots | {ROOT / "Scripts"})


@pytest.mark.parametrize("helper", HELPERS)
def test_helper_when_distributions_listed_then_absent(helper):
    shipped = [
        path
        for root in _distribution_roots()
        for path in ([root] if root.is_file() else root.rglob("*"))
        if path.name == helper
    ]
    assert shipped == [], (
        f"{helper} must stay outside Scripts and distributions: {shipped}"
    )


@pytest.mark.parametrize("name", ["install.vfpy", "MIGRATION.json"])
def test_installer_when_read_then_no_helper_activated(name):
    text = (ROOT / name).read_text()
    assert [h for h in HELPERS if h.removesuffix(".py") in text] == []
