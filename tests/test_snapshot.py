# this_file: tests/test_snapshot.py
"""Host-free runtime structure and bundle regressions."""
import json
import shutil
import pytest
from types import SimpleNamespace as NS
import xml.etree.ElementTree as ET

from grablab.snapshot import snapshot, ui_xml, free_bundle


def widget(name="root", children=(), x=0, y=0, text=""):
    rect = NS(x=lambda: x, y=lambda: y, width=lambda: 80, height=lambda: 60)
    return NS(objectName=name, statusTip="", className=lambda: "QLabel",
              width=80, height=60, geometry=rect, visible=True, text=text,
              children=lambda: children, actions=lambda: [])


def test_logical_structure_and_designer_content(tmp_path):
    child = widget("label", x=4, y=7, text="A & B")
    record = snapshot(widget(children=[child]), "Title", "capture.png")
    assert record["rects"]["label"] == [4, 7, 80, 60]
    assert record["texts"]["label"] == "A & B"
    root = ET.fromstring(ui_xml(record))
    assert root.find("widget/widget/property[@name='text']/string").text == "A & B"
    assert json.loads(json.dumps(record)) == record


def test_collision_in_any_sidecar_reserves_whole_bundle(tmp_path):
    (tmp_path / "capture.ui").touch()
    assert free_bundle(tmp_path / "capture.png").name == "capture_1.png"


def test_hidden_children_are_omitted_and_bounds_disclosed():
    hidden = widget("hidden")
    hidden.visible = False
    record = snapshot(widget(children=[hidden, widget("visible")]), "", "x.png", max_widgets=1)
    assert "hidden" not in record["rects"]
    assert record["extensions"]["truncated"]


def test_password_and_model_data_are_not_read():
    secret = widget("password", text="private")
    secret.echoMode = 2
    secret.model = lambda: (_ for _ in ()).throw(AssertionError("model traversal"))
    model = NS(children=lambda: (_ for _ in ()).throw(AssertionError("QObject traversal")))
    record = snapshot(widget(children=[secret, model]), "", "x.png")
    assert "private" not in json.dumps(record)


def test_native_list_restores_gc_on_failure():
    import gc
    import pytest
    from grablab.snapshot import native_list
    def broken():
        raise ValueError("conversion")
    before = gc.isenabled()
    with pytest.raises(ValueError, match="conversion"):
        native_list(NS(children=broken), "children")
    assert gc.isenabled() == before


def test_owned_actions_are_named_outside_without_guessing_reaches():
    root = widget()
    root.actions = lambda: [NS(parent=lambda: root, statusTip="root.command", objectName="", text="Apply")]
    record = snapshot(root, "", "x.png")
    assert record["context"]["outside"] == {"root.command": ["root"]}
    assert record["context"]["reaches"] == {}


def test_designer_properties_are_writable_and_checked_is_unique(tmp_path):
    import subprocess
    progress = widget("progress", text="42%")
    progress.className = lambda: "QProgressBar"
    progress.value = 42
    spin = widget("spin", text="17")
    spin.className = lambda: "QSpinBox"
    spin.value = 170
    spin.maximum = 200
    abstract = widget("abstract", text="read only")
    abstract.className = lambda: "QAbstractSpinBox"
    button = widget("button", text="Check")
    button.className = lambda: "QCheckBox"
    button.checked, button.isChecked = True, lambda: True
    button.isCheckable = lambda: True
    record = snapshot(widget(children=[progress, spin, abstract, button]), "", "x.png")
    xml = ui_xml(record)
    tree = ET.fromstring(xml)
    for name in ("progress", "spin", "abstract"):
        node = tree.find(f".//widget[@name='{name}']")
        assert node.find("property[@name='text']") is None
    assert len(tree.findall(".//widget[@name='button']/property[@name='checked']")) == 1
    assert record["extensions"]["widgets"][1]["content"]["text"] == "42%"
    path = tmp_path / "controls.ui"
    path.write_text(xml)
    result = subprocess.run([uic_path(), str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "progress->setText(" not in result.stdout
    assert "spin->setText(" not in result.stdout
    assert result.stdout.count("button->setChecked(") == 1
    assert result.stdout.index("button->setCheckable(") < result.stdout.index("button->setChecked(")
    assert result.stdout.index("spin->setMaximum(") < result.stdout.index("spin->setValue(")


def test_hidden_root_uses_relative_visibility_for_rendered_children():
    child, hidden = widget("shown", x=3, y=5, text="Shown"), widget("hidden")
    child.visible = False
    child.isVisibleTo = lambda root: True
    hidden.visible = False
    hidden.isVisibleTo = lambda root: False
    root = widget(children=[child, hidden])
    root.visible = False
    record = snapshot(root, "", "x.png")
    assert record["rects"]["shown"] == [3, 5, 80, 60]
    assert "hidden" not in record["rects"]


@pytest.mark.parametrize("class_name", ["QMenu", "QMenuBar"])
def test_menu_action_geometry_and_designer_actions(tmp_path, class_name):
    import subprocess
    root = widget("menu")
    root.className = lambda: class_name
    def action(name, visible=True):
        return NS(parent=lambda: root, statusTip=name, objectName=name,
                  text=name.title(), isVisible=lambda: visible,
                  isEnabled=lambda: True, isCheckable=lambda: False, isChecked=lambda: False)
    shown, hidden, empty, clipped = action("shown"), action("hidden", False), action("empty"), action("clipped")
    root.actions = lambda: [shown, hidden, empty, clipped]
    rects = {id(shown): NS(x=lambda: 2, y=lambda: 3, width=lambda: 70, height=lambda: 15),
             id(empty): NS(x=lambda: 0, y=lambda: 0, width=lambda: 0, height=lambda: 0),
             id(clipped): NS(x=lambda: 75, y=lambda: 3, width=lambda: 70, height=lambda: 15)}
    def action_geometry(item):
        assert item is not hidden, "hidden actions must not evaluate geometry"
        return rects[id(item)]
    root.actionGeometry = action_geometry
    record = snapshot(root, "", "x.png")
    assert record["rects"]["shown"] == [2, 3, 70, 15]
    assert record["texts"]["shown"] == "Shown"
    assert record["context"]["outside"] == {"hidden": ["menu"], "empty": ["menu"], "clipped": ["menu"]}
    tree = ET.fromstring(ui_xml(record))
    assert len(tree.findall("widget/action")) == 4
    assert len(tree.findall("widget/addaction")) == 4
    path = tmp_path / "menu.ui"
    path.write_text(ui_xml(record))
    result = subprocess.run([uic_path(), str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "addAction(shown)" in result.stdout


def uic_path():
    """Use available Qt5 uic without requiring a dependency install."""
    path = shutil.which("uic") or "/opt/homebrew/opt/qt@5/bin/uic"
    from pathlib import Path
    if not Path(path).is_file():
        pytest.skip("Qt uic is unavailable; XML/assertion controls still run")
    return path
