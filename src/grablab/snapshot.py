# this_file: src/grablab/snapshot.py
"""Bounded, host-free runtime snapshots; never inspect arbitrary Qt properties."""
import gc
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

EXTENSIONS = (".png", ".svg", ".json", ".ui")
SVG_NS = "http://www.w3.org/2000/svg"
# Read-only display getters remain in JSON, never as Designer setter properties.
UI_CONTENT = {
    "QLabel": {"text": "text"},
    "QLineEdit": {"text": "text", "placeholderText": "placeholderText"},
    "QTextEdit": {"toPlainText": "plainText", "placeholderText": "placeholderText"},
    "QPlainTextEdit": {"toPlainText": "plainText", "placeholderText": "placeholderText"},
    "QSpinBox": {key: key for key in ("minimum", "maximum", "prefix", "suffix", "value")},
    "QDoubleSpinBox": {key: key for key in ("decimals", "minimum", "maximum", "prefix", "suffix", "value")},
    "QProgressBar": {key: key for key in ("minimum", "maximum", "value")}, "QSlider": {"value": "value"},
    "QDial": {"value": "value"}, "QScrollBar": {"value": "value"},
    "QMenu": {"title": "title"},
    "QGroupBox": {"title": "title", "checked": "checked", "isChecked": "checked", "checkable": "checkable", "isCheckable": "checkable"},
}
for _class in ("QPushButton", "QToolButton", "QCheckBox", "QRadioButton", "QCommandLinkButton"):
    UI_CONTENT[_class] = {"text": "text", "checked": "checked", "isChecked": "checked", "checkable": "checkable", "isCheckable": "checkable"}


def unique_id(semantic: str, fallback: str, used: set) -> str:
    base = re.sub(r"[^\w.-]+", "_", semantic).strip("_.") or fallback
    ident, number = base, 1
    while ident in used:
        ident, number = f"{base}_{number}", number + 1
    used.add(ident)
    return ident


def visible_to(item: Any, root: Any) -> bool:
    """Mirror QWidget.render children even when the owned root is hidden."""
    method = getattr(item, "isVisibleTo", None)
    try:
        return bool(method(root)) if callable(method) else bool(value(item, "isVisible", value(item, "visible", False)))
    except (TypeError, RuntimeError):
        return False


def write_property(element: Any, name: str, val: Any) -> None:
    prop = ET.SubElement(element, "property", name=name)
    kind = "bool" if isinstance(val, bool) else "number" if isinstance(val, int) else "double" if isinstance(val, float) else "string"
    ET.SubElement(prop, kind).text = str(val).lower() if isinstance(val, bool) else str(val)



def value(obj: Any, name: str, default: Any = None) -> Any:
    """Read a deliberately allowlisted Qt property or zero-argument getter."""
    try:
        result = getattr(obj, name, default)
        return result() if callable(result) else result
    except (AttributeError, TypeError, RuntimeError):
        return default


def native_list(obj: Any, name: str) -> list:
    """Keep Python-owned widgets alive during PythonQt list conversion."""
    enabled = gc.isenabled()
    gc.disable()
    try:
        return list(value(obj, name, []) or [])
    finally:
        if enabled:
            gc.enable()


def free_bundle(path: Path) -> Path:
    """Choose a basename unused by any bundle member, including directories."""
    number = 0
    while True:
        suffix = "_" + str(number) if number else ""
        candidate = path.with_name(f"{path.stem}{suffix}{path.suffix}")
        if not any(candidate.with_suffix(ext).exists() or candidate.with_suffix(ext).is_symlink() for ext in EXTENSIONS):
            return candidate
        number += 1


def geometry(widget: Any) -> list[int]:
    rect = value(widget, "geometry")
    return [int(value(rect, key, 0)) for key in ("x", "y", "width", "height")]


def snapshot(widget: Any, title: str, filename: str, max_widgets: int = 2000) -> dict:
    """Capture visible QWidget descendants only; models and remote actions stay unknown."""
    nodes, rects, texts, parts, checked = [], {}, {}, [], []
    pending = [(widget, None, 0, 0)]
    used = set()
    local_actions = []
    while pending and len(nodes) < max_widgets:
        item, parent, px, py = pending.pop()
        if parent is not None and (value(item, "isWindow", False) or not visible_to(item, widget)):
            continue
        if value(item, "geometry") is None:
            continue  # QObject children such as models are deliberately not traversed.
        local = geometry(item)
        x, y, width, height = local
        if parent is None:
            x, y = 0, 0
            local = [0, 0, width, height]
        else:
            x, y = px + x, py + y
        object_name = str(value(item, "objectName", "") or "")
        status = str(value(item, "statusTip", "") or "")
        semantic = status or object_name
        ident = unique_id(semantic, f"widget_{len(nodes)}", used)
        cls = str(value(item, "className", type(item).__name__))
        content = {}
        # No model(), property(), meta-property enumeration, or password content.
        echo = value(item, "echoMode", 0)
        for key in ("text", "title", "windowTitle", "placeholderText", "currentText", "value", "checked", "isChecked", "checkable", "isCheckable", "toPlainText", "minimum", "maximum", "prefix", "suffix", "decimals"):
            if key in ("text", "toPlainText") and echo != 0:
                continue
            result = value(item, key)
            if isinstance(result, (str, int, float, bool)):
                content[key] = result
        if content.get("isChecked", content.get("checked", False)):
            checked.append(ident)
        node = dict(id=ident, semantic=semantic, objectName=object_name, statusTip=status,
                    **{"class": cls}, parent=parent, geometry=local,
                    rect=[x, y, width, height], content=content, actions=[])
        for action in native_list(item, "actions"):
            details = {key: value(action, key, "") for key in ("objectName", "statusTip", "text")}
            action_semantic = str(details["statusTip"] or details["objectName"])
            details["id"] = unique_id(action_semantic, f"action_{len(used)}", used)
            details["content"] = {key: value(action, getter, default) for key, getter, default in (
                ("text", "text", ""), ("visible", "isVisible", True), ("enabled", "isEnabled", True),
                ("checkable", "isCheckable", False), ("checked", "isChecked", False), ("separator", "isSeparator", False))}
            details["rect"] = None
            if cls in ("QMenu", "QMenuBar") and details["content"]["visible"]:
                method = getattr(item, "actionGeometry", None)
                try:
                    rect = method(action) if callable(method) else None
                except (TypeError, RuntimeError):
                    rect = None
                if rect is not None:
                    ax, ay, aw, ah = [int(value(rect, key, 0)) for key in ("x", "y", "width", "height")]
                    rw, rh = int(value(widget, "width", 0)), int(value(widget, "height", 0))
                    if aw > 0 and ah > 0 and ax >= 0 and ay >= 0 and ax + aw <= width and ay + ah <= height and x + ax >= 0 and y + ay >= 0 and x + ax + aw <= rw and y + ay + ah <= rh:
                        details["rect"] = [x + ax, y + ay, aw, ah]
                        rects[details["id"]] = details["rect"]
                        texts[details["id"]] = details["text"]
            node["actions"].append(details)
            if value(action, "parent") is item:
                local_actions.append((action_semantic, ident))
        nodes.append(node)
        if semantic:
            rects[ident] = node["rect"]
            caption = next((content[k] for k in ("text", "title", "currentText", "toPlainText") if isinstance(content.get(k), str)), "")
            if caption:
                texts[ident] = caption
        else:
            parts.append({"class": cls, "rect": node["rect"], "content": content})
        pending.extend((child, ident, x, y) for child in reversed(native_list(item, "children")))
    root = nodes[0] if nodes else {"id": "root", "class": type(widget).__name__}
    outside = {}
    measured = {node["semantic"] for node in nodes if node["semantic"]}
    measured.update(str(action["statusTip"] or action["objectName"]) for node in nodes for action in node["actions"] if action["rect"] is not None)
    for action_id, offering in local_actions:
        if action_id and action_id not in measured:
            outside.setdefault(action_id, []).append(offering)
    return {"manifest": {"tool": "grablab", "version": 2, "build": "", "units": "rects and size are logical points in the image own frame, origin top-left; use pixels / size for pixel mapping"},
            "shot": 1, "target": root["id"], "root": root["id"], "scope": "form", "class": root["class"],
            "title": title, "titlebar": False, "file": filename, "size": [int(value(widget, "width", 0)), int(value(widget, "height", 0))],
            "pixels": None, "dpr": None, "colorspace": "unknown", "theme": "unknown", "background": None,
            "state": hashlib.sha256(json.dumps(sorted(rects)).encode()).hexdigest()[:8], "note": "", "parts": parts,
            "opened_from": "", "popup_parent": "", "opener": {}, "context": {"window": value(widget, "windowTitle", ""), "checked": checked, "outside": outside, "reaches": {}},
            "taken": time.strftime("%Y-%m-%d %H:%M:%S"), "rects": rects, "texts": texts, "x_ray": False, "nodes": [],
            "extensions": {"schema": "grablab.capture/1", "widgets": nodes, "truncated": bool(pending),
                           "limits": ["Visible runtime geometry and allowlisted content only; no layout reconstruction, signals, model data, icons or custom painting", "Editable content may contain document data; password text omitted", "Outside includes directly owned named actions; reaches and opener unknown; local action associations only", "Custom widget classes require their original plugins", "Designer properties use standard-control writable allowlists; read-only/unknown content stays in JSON; submenu structure and action connections are not reconstructed"]}}


def ui_xml(record: dict) -> str:
    """Write Designer XML with local geometry; full runtime details remain in JSON."""
    root = ET.Element("ui", version="4.0")
    ET.SubElement(root, "class").text = "GrabLabSnapshot"
    ET.SubElement(root, "comment").text = "; ".join(record["extensions"]["limits"])
    elements = {}
    for node in record["extensions"]["widgets"]:
        parent = elements.get(node["parent"], root)
        element = ET.SubElement(parent, "widget", {"class": node["class"], "name": node["id"]})
        elements[node["id"]] = element
        rect = ET.SubElement(ET.SubElement(element, "property", name="geometry"), "rect")
        for key, val in zip(("x", "y", "width", "height"), node["geometry"]):
            ET.SubElement(rect, key).text = str(val)
        mapping = {"windowTitle": "windowTitle", **UI_CONTENT.get(node["class"], {})}
        properties = {mapped: node["content"][key] for key, mapped in mapping.items() if key in node["content"]}
        if "checked" in properties:
            properties["checked"] = properties.pop("checked")
        properties["statusTip"] = node["statusTip"]
        for key, val in properties.items():
            write_property(element, key, val)
        if node["class"] in ("QMenu", "QMenuBar"):
            for action in node["actions"]:
                action_element = ET.SubElement(element, "action", name=action["id"])
                for key, val in action["content"].items():
                    write_property(action_element, key, val)
                write_property(action_element, "statusTip", action["statusTip"])
                ET.SubElement(element, "addaction", name=action["id"])
    ET.SubElement(root, "resources")
    ET.SubElement(root, "connections")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def embed_svg(path: Path, record: dict) -> None:
    root = ET.parse(path).getroot()
    metadata = ET.SubElement(root, f"{{{SVG_NS}}}metadata", id="grablab-metadata")
    metadata.text = json.dumps(record, ensure_ascii=False, sort_keys=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
