# this_file: tests/test_snapshot.py
"""Host-free runtime structure and bundle regressions."""
import json
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
