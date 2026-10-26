# this_file: src/grablab/svg.py
"""Explicit, host-free SVG postprocessing. Install the ``svg`` extra.

Trees are edited in memory; write_svg exclusively creates a NEW output. Raw
captures are never rewritten. Data URIs must match known decoded PNG pixels;
named source aliases explicitly distinguish vector provenance from equivalence.
Semantic bounds indicate containment, not pixel ownership.
"""

from __future__ import annotations

import base64
import binascii
import copy
import hashlib
import io
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SVG = "http://www.w3.org/2000/svg"
XLINK = "{http://www.w3.org/1999/xlink}href"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def read_svg(path: str | Path) -> ET.Element:
    """Read trusted local capture/export XML without touching the source."""
    root = ET.parse(path).getroot()
    if root.tag != f"{{{SVG}}}svg":
        raise ValueError("Expected a namespaced SVG document")
    return root


def write_svg(root: ET.Element, output: str | Path) -> Path:
    """Publish a new processed artifact; refuse raw/existing destinations."""
    output = Path(output)
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with output.open("xb") as stream:
        stream.write(data)
    return output


def pixel_key(data: bytes) -> str:
    """Hash dimensions and unpremultiplied RGBA, ignoring only invisible RGB."""
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        if image.format != "PNG":
            raise ValueError("Expected PNG")
        rgba = image.convert("RGBA")
        pixels = bytearray(rgba.tobytes())
        for i in range(0, len(pixels), 4):
            if pixels[i + 3] == 0:
                pixels[i : i + 3] = b"\0\0\0"
        return hashlib.sha256(
            f"{rgba.width}x{rgba.height}:".encode() + pixels
        ).hexdigest()


def build_raster_index(
    manifest: str | Path, source_dirs: list[str | Path] = ()
) -> dict:
    """Index exported PNG variants and exact-pixel authoritative source aliases.

    Authoritative source PNGs may associate by unique original asset_name (only
    @2x suffix is normalized). The mapping records source-name provenance, which
    is not a pixel-equivalence claim for the exported vector. Errors fail loudly.
    """
    manifest = Path(manifest).resolve()
    index: dict = {"schema": "grablab.raster-index/1", "pixels": {}, "sources": []}
    names: dict = {}
    for asset in json.loads(manifest.read_text())["assets"]:
        files = asset["files"]
        vector = (manifest.parent / files["svg"]["path"]).resolve()
        if not vector.is_file():
            raise FileNotFoundError(vector)
        names.setdefault(asset.get("asset_name", asset["basename"]), []).append(
            {"asset": asset["basename"], "svg": str(vector)}
        )
        for kind, entry in files.items():
            if not kind.startswith("png"):
                continue
            raster = (manifest.parent / entry["path"]).resolve()
            key = pixel_key(raster.read_bytes())
            row = {
                "asset": asset["basename"],
                "png": str(raster),
                "svg": str(vector),
                "match": "pixel-exact",
            }
            if row not in index["pixels"].setdefault(key, []):
                index["pixels"][key].append(row)
    sources = []
    for folder in source_dirs:
        if not Path(folder).is_dir():
            raise NotADirectoryError(folder)
        for raster in sorted(Path(folder).rglob("*.png")):
            key = pixel_key(raster.read_bytes())
            sources.append((raster, key))
            name = re.sub(r"@2x$", "", raster.stem)
            for candidate in names.get(name, []):
                row = dict(candidate, png=str(raster.resolve()), match="source-name")
                if row not in index["pixels"].setdefault(key, []):
                    index["pixels"][key].append(row)
    for raster, key in sources:
        candidates = index["pixels"].get(key, [])
        index["sources"].append(
            {
                "png": str(raster.resolve()),
                "pixel_key": key,
                "status": _status(candidates),
                "candidates": candidates,
            }
        )
    return index


def _status(candidates: list[dict]) -> str:
    count = len({row["svg"] for row in candidates})
    return "matched" if count == 1 else "ambiguous" if count else "unmatched"


def map_images(root: ET.Element, index: dict) -> dict:
    """Return a JSON-serializable data-URI mapping with all candidate paths."""
    mapping = {}
    for node in root.iter(f"{{{SVG}}}image"):
        href = node.get("href", node.get(XLINK, ""))
        if not href.startswith("data:") or href in mapping:
            continue
        row = {"status": "unsupported", "candidates": []}
        if href.startswith("data:image/png;base64,"):
            try:
                key = pixel_key(base64.b64decode(href.split(",", 1)[1], validate=True))
                candidates = index["pixels"].get(key, [])
                row = {
                    "status": _status(candidates),
                    "pixel_key": key,
                    "candidates": candidates,
                }
            except (ValueError, OSError, binascii.Error) as exc:
                row = {"status": "invalid", "candidates": [], "error": str(exc)}
        mapping[href] = row
    return mapping


def _namespace(root: ET.Element, prefix: str) -> None:
    """Namespace local IDs, fragment/url references and Illustrator CSS classes."""
    existing = [node.get("id") for node in root.iter() if node.get("id")]
    if len(existing) != len(set(existing)):
        raise ValueError("Cannot namespace duplicate source IDs")
    ids = {
        node.get("id"): prefix + node.get("id")
        for node in root.iter()
        if node.get("id")
    }
    classes = {
        name: prefix + name
        for node in root.iter()
        for name in node.get("class", "").split()
    }

    url_reference = re.compile(r"url\(\s*(['\"]?)#([^'\"\s)]+)\1\s*\)")

    def refs(value: str) -> str:
        if "url(" not in value:
            return value

        def replace(match: re.Match) -> str:
            target = ids.get(match[2])
            return f"url(#{target})" if target is not None else match[0]

        return url_reference.sub(replace, value)

    for node in root.iter():
        for key, value in list(node.attrib.items()):
            if key == "id":
                value = ids[value]
            elif key in ("href", XLINK) and value.startswith("#"):
                value = "#" + ids.get(value[1:], value[1:])
            elif key == "class":
                value = " ".join(classes[name] for name in value.split())
            node.set(key, refs(value))
        if node.tag == f"{{{SVG}}}style" and node.text:
            text = refs(node.text)

            # Rewrite selectors only: a color literal in declarations is not an ID.
            def selectors(match: re.Match) -> str:
                value = match[1]
                for marker, names in (("#", ids), (".", classes)):
                    for old, new in names.items():
                        value = re.sub(
                            re.escape(marker + old) + r"(?![\w-])", marker + new, value
                        )
                return value + "{"

            node.text = re.sub(r"([^{}]+)\{", selectors, text)


def _prefix(root: ET.Element, stem: str) -> str:
    existing = {node.get("id", "") for node in root.iter()}
    n = 0
    while any(value.startswith(f"{stem}-{n}-") for value in existing):
        n += 1
    return f"{stem}-{n}-"


def inline_images(root: ET.Element, mapping: dict) -> dict:
    """Replace uniquely matched rasters in place with nested SVG viewports.

    The outer group retains image transforms/clipping/opacity; the nested SVG
    retains exported viewBox, drawing/defs and image placement/aspect ratio.
    """
    stats = {"replaced": 0, "retained": 0}
    for parent in list(root.iter()):
        for position, node in enumerate(list(parent)):
            if node.tag != f"{{{SVG}}}image":
                continue
            row = mapping.get(node.get("href", node.get(XLINK, "")), {})
            if (
                row.get("status") != "matched"
                or _status(row.get("candidates", [])) != "matched"
            ):
                stats["retained"] += 1
                continue
            vector = read_svg(row["candidates"][0]["svg"])
            prefix = _prefix(root, "icon")
            _namespace(vector, prefix)
            if not vector.get("id"):
                vector.set("id", prefix + "viewport")
            viewport = {
                key: node.get(key, default)
                for key, default in (
                    ("x", "0"),
                    ("y", "0"),
                    ("width", "100%"),
                    ("height", "100%"),
                    ("preserveAspectRatio", "xMidYMid meet"),
                )
            }
            vector.attrib.update(viewport)
            vector.set("overflow", "hidden")
            group = ET.Element(
                f"{{{SVG}}}g",
                {
                    key: val
                    for key, val in node.attrib.items()
                    if key not in {*viewport, "href", XLINK}
                },
            )
            group.append(vector)
            group.tail = node.tail
            parent.remove(node)
            parent.insert(position, group)
            stats["replaced"] += 1
    return stats


def tag_widgets(root: ET.Element, record: dict) -> dict:
    """Tag original paint shapes by smallest containing root-logical widget rect.

    svgelements computes actual path/shape bounds with inherited transforms and
    viewports. Text metrics, clipping and use-instance ownership are not inferred.
    Existing IDs remain intact to preserve references; data-widget is always set.
    """
    from svgelements import SVG as GeometrySVG
    from svgelements import Image as GeometryImage
    from svgelements import Point, Shape, Text

    nodes = list(root.iter())
    nonpaint = {
        id(child)
        for node in nodes
        if node.tag.rsplit("}", 1)[-1]
        in ("defs", "clipPath", "mask", "pattern", "symbol", "marker")
        for child in node.iter()
    }
    probe = copy.deepcopy(root)
    originals = {}
    existing = [node.get("id") for node in nodes if node.get("id")]
    if len(existing) != len(set(existing)):
        raise ValueError("Semantic tagging requires unique source SVG IDs")
    probe_prefix = _prefix(root, "grablab-probe")
    for number, (source, target) in enumerate(zip(nodes, probe.iter())):
        ident = source.get("id", f"{probe_prefix}{number}")
        target.set("id", ident)
        if id(source) not in nonpaint:
            originals[ident] = source
    width, height = record["size"]
    if not all(math.isfinite(value) and value > 0 for value in (width, height)):
        raise ValueError("Capture logical size must be positive and finite")
    geometry = GeometrySVG.parse(
        io.StringIO(ET.tostring(probe, encoding="unicode")),
        width=width,
        height=height,
        on_error="raise",
    )
    # Root physical dimensions may use Qt's mm units; logical capture frame wins.
    sx, sy = width / float(geometry.width), height / float(geometry.height)
    widgets = sorted(
        record["extensions"]["widgets"],
        key=lambda node: node["rect"][2] * node["rect"][3],
    )
    by_id = {widget["id"]: widget for widget in widgets}
    if len(by_id) != len(widgets):
        raise ValueError("Widget records must have unique IDs")
    stats = {
        "tagged": 0,
        "text_anchors": 0,
        "unmatched": 0,
        "unsupported": 0,
        "ambiguous": 0,
        "ambiguities": [],
        "limits": [
            "Bounds containment is not paint ownership; clipping and text metrics are not resolved"
        ],
    }
    used = {node.get("id") for node in nodes if node.get("id")}
    for shape in geometry.elements():
        source = originals.get(shape.id)
        if source is None or source.tag.rsplit("}", 1)[-1] in ("svg", "g", "defs"):
            continue
        if isinstance(shape, Text):
            point = Point(shape.x, shape.y) * shape.transform
            bounds = (point.x, point.y, point.x, point.y)
        elif isinstance(shape, (Shape, GeometryImage)):
            bounds = shape.bbox()
        else:
            stats["unsupported"] += 1
            continue
        if bounds is None:
            stats["unsupported"] += 1
            continue
        x0, y0, x1, y1 = bounds
        matches = [
            widget
            for widget in widgets
            if widget["rect"][0] <= x0 * sx
            and widget["rect"][1] <= y0 * sy
            and x1 * sx <= widget["rect"][0] + widget["rect"][2]
            and y1 * sy <= widget["rect"][1] + widget["rect"][3]
        ]
        if not matches:
            stats["unmatched"] += 1
            continue
        area = matches[0]["rect"][2] * matches[0]["rect"][3]
        tied = [
            widget
            for widget in matches
            if widget["rect"][2] * widget["rect"][3] == area
        ]
        winners = [
            widget
            for widget in tied
            if all(_descends_from(widget["id"], other["id"], by_id) for other in tied)
        ]
        if len(winners) != 1:
            stats["ambiguous"] += 1
            stats["ambiguities"].append(
                {
                    "element": source.get("id", shape.id),
                    "widgets": sorted(widget["id"] for widget in tied),
                }
            )
            continue
        ident = winners[0]["id"]
        source.set("data-widget", ident)
        if isinstance(shape, Text):
            source.set("data-widget-method", "text-anchor")
            stats["text_anchors"] += 1
        if not source.get("id"):
            safe = re.sub(r"[^A-Za-z0-9_.-]", "-", ident)
            name, n = "widget-" + safe, 1
            while name in used:
                name, n = f"widget-{safe}-{n}", n + 1
            source.set("id", name)
            used.add(name)
        stats["tagged"] += 1
    return stats


def _descends_from(ident: str, ancestor: str, widgets: dict) -> bool:
    """Require an observed parent chain; missing links/cycles prove nothing."""
    seen = set()
    found = False
    while ident in widgets:
        if ident in seen:
            return False
        found = found or ident == ancestor
        seen.add(ident)
        ident = widgets[ident].get("parent")
    return found


def _effective_paints(root: ET.Element) -> dict:
    """Resolve author paint cascade before edits, including inherited no-paint."""
    import cssselect2
    import tinycss2

    def declarations(content: str | list) -> list:
        result = tinycss2.parse_blocks_contents(
            content, skip_comments=True, skip_whitespace=True
        )
        if any(part.type != "declaration" for part in result):
            raise ValueError("Unsupported or malformed CSS declarations")
        return [part for part in result if part.lower_name in ("fill", "stroke")]

    matcher = cssselect2.Matcher()
    for style in root.iter(f"{{{SVG}}}style"):
        for rule in tinycss2.parse_stylesheet(
            style.text or "", skip_comments=True, skip_whitespace=True
        ):
            if rule.type != "qualified-rule":
                raise ValueError("Unsupported or malformed SVG stylesheet rule")
            payload = declarations(rule.content)
            for selector in cssselect2.compile_selector_list(
                rule.prelude, namespaces={None: SVG}
            ):
                matcher.add_selector(selector, payload)
    computed = {}
    for wrapper in cssselect2.ElementWrapper.from_xml_root(root).iter_subtree():
        node = wrapper.etree_element
        inherited = (
            computed[wrapper.parent.etree_element]
            if wrapper.parent is not None
            else {"fill": "black", "stroke": "none"}
        )
        cascade = {
            key: ((False, (0, 0, 0, 0), -1), node.get(key, "inherit"))
            for key in ("fill", "stroke")
        }
        rules = [
            (specificity, order, payload)
            for specificity, order, pseudo, payload in matcher.match(wrapper)
            if pseudo is None
        ]
        rules = [
            ((0,) + specificity, order, payload)
            for specificity, order, payload in rules
        ]
        rules.append(((1, 0, 0, 0), 0, declarations(node.get("style", ""))))
        for specificity, order, payload in rules:
            for declaration in payload:
                key = declaration.lower_name
                weight = (declaration.important, specificity, order)
                if weight >= cascade[key][0]:
                    cascade[key] = (
                        weight,
                        tinycss2.serialize(declaration.value).strip(),
                    )
        effective = {}
        for key, (_, value) in cascade.items():
            value = tinycss2.serialize(
                [
                    token
                    for token in tinycss2.parse_component_value_list(value)
                    if token.type != "comment"
                ]
            ).strip()
            keyword = value.lower()
            if keyword in ("inherit", "unset"):
                value = inherited[key]
            elif keyword == "initial":
                value = "black" if key == "fill" else "none"
            elif (
                keyword in ("revert", "revert-layer", "context-fill", "context-stroke")
                or "var(" in keyword
            ):
                raise ValueError("Contextual CSS paint cannot be resolved safely")
            elif keyword == "none":
                value = "none"
            effective[key] = value
        computed[node] = effective
    return computed


def deduplicate_paths(root: ET.Element) -> dict:
    """Remove only identical consecutive opaque fill-only paths in safe groups.

    shortcut: antialiased edges may differ even for opaque fills, inspect the
    processed render before use; disable this opt-in cleanup for exact pixels.
    """
    stats = {"removed": 0}
    allowed = {"d", "fill", "fill-rule", "transform"}

    def visit(parent: ET.Element, safe: bool) -> None:
        safe = safe and not any(
            key in parent.attrib
            for key in (
                "style",
                "opacity",
                "fill-opacity",
                "stroke",
                "filter",
                "mask",
                "clip-path",
                "class",
            )
        )
        previous = None
        for node in list(parent):
            eligible = (
                safe
                and parent.tag in (f"{{{SVG}}}g", f"{{{SVG}}}svg")
                and node.tag == f"{{{SVG}}}path"
                and set(node.attrib) <= allowed
                and not len(node)
            )
            fill = node.get("fill", "")
            eligible = eligible and bool(
                re.fullmatch(r"#[\da-fA-F]{3}|#[\da-fA-F]{6}|black|white", fill)
            )
            signature = tuple(sorted(node.attrib.items())) if eligible else None
            if signature is not None and signature == previous:
                parent.remove(node)
                stats["removed"] += 1
            else:
                visit(node, safe)
            previous = signature

    visit(root, True)
    return stats


def compose(
    panels: list[tuple[str | Path, float, float]], *, width: float, height: float
) -> ET.Element:
    """Assemble SVGs at explicit logical positions in input paint order."""
    if not all(math.isfinite(value) and value > 0 for value in (width, height)):
        raise ValueError("Composition dimensions must be positive and finite")
    root = ET.Element(
        f"{{{SVG}}}svg",
        width=str(width),
        height=str(height),
        viewBox=f"0 0 {width} {height}",
    )
    for number, (path, x, y) in enumerate(panels):
        if not all(math.isfinite(value) for value in (x, y)):
            raise ValueError("Panel positions must be finite")
        panel = read_svg(path)
        _namespace(panel, f"panel-{number}-")
        if panel.get("viewBox"):
            _, _, panel_width, panel_height = map(
                float, panel.get("viewBox").replace(",", " ").split()
            )
            panel.set("width", f"{panel_width:g}")
            panel.set("height", f"{panel_height:g}")
        panel.set("x", str(x))
        panel.set("y", str(y))
        root.append(panel)
    return root


def restyle(
    root: ET.Element,
    *,
    stroke: str | None = None,
    fill: str | None = None,
    stroke_width: float | None = None,
    background: str | None = None,
    font: str = "system-ui",
    wireframe: bool = False,
    monochrome: bool = False,
) -> dict:
    """Restyle presentation/inline CSS; retain opacity and none paints.

    Resolve author CSS cascade/inheritance first to preserve effective no-paint.
    Mask-bearing documents and unsupported/contextual CSS fail before edits. Wireframe explicitly changes
    paints to dark outlines/text with opaque light surfaces, retaining no-paint.
    Monochrome filters the full drawing, preserving luminance hierarchy and
    existing filters. Wireframe wraps retained images with grayscale filtering.
    Resource definitions retain their geometry and paint.
    """
    if stroke_width is not None and (
        not math.isfinite(stroke_width) or stroke_width < 0
    ):
        raise ValueError("Stroke width must be finite and nonnegative")
    # Even a font-only change can alter text-based masks through inheritance.
    if any(node.tag == f"{{{SVG}}}mask" for node in root.iter()):
        raise ValueError("Restyling SVG masks is unsupported; preserve mask painting")
    if wireframe:
        stroke, fill = stroke or "#333333", background or "white"
        stroke_width = 1 if stroke_width is None else stroke_width
    if (monochrome or wireframe) and any(
        node.tag == f"{{{SVG}}}image" for node in root.iter()
    ) and any(node.tag == f"{{{SVG}}}style" for node in root.iter()):
        # New groups change selector matches on images, wrappers and siblings.
        raise ValueError("Unsupported stylesheet with retained raster wrapping")
    # Root filtering leaves the tree and all selector relationships intact.
    # Author root filter rules need a real cascade/effect resolver; refuse them.
    if monochrome and any(node.tag == f"{{{SVG}}}style" for node in root.iter()):
        raise ValueError("Unsupported stylesheet with full-drawing monochrome")
    root_css = dict(part.split(":", 1) for part in root.get("style", "").split(";") if ":" in part)
    if monochrome and any(key.strip() == "filter" and "!important" in value for key, value in root_css.items()):
        raise ValueError("Unsupported important root filter for monochrome")
    root_css = {key.strip(): value.strip() for key, value in root_css.items()}
    root_filter = root_css.get("filter", root.get("filter", ""))
    if monochrome and root_filter.strip().lower() in {
        "initial", "unset", "inherit", "revert", "revert-layer"
    }:
        raise ValueError("Unsupported CSS-wide root filter for monochrome")
    paints = _effective_paints(root)
    resources = {
        child for node in root.iter()
        if node.tag.rsplit("}", 1)[-1] in ("defs", "clipPath", "pattern", "filter", "marker")
        for child in node.iter()
    }
    stats = {"styled": 0, "filtered_images": 0}
    for node in root.iter():
        kind = node.tag.rsplit("}", 1)[-1]
        if node in resources or kind not in (
            "svg",
            "g",
            "path",
            "rect",
            "circle",
            "ellipse",
            "polygon",
            "polyline",
            "line",
            "text",
            "tspan",
        ):
            continue
        css = dict(
            part.split(":", 1)
            for part in node.get("style", "").split(";")
            if ":" in part
        )
        css = {key.strip(): value.strip() for key, value in css.items()}
        updates = {"font-family": font}
        for key, value in (
            ("stroke", stroke),
            ("fill", fill),
            ("stroke-width", stroke_width),
        ):
            if wireframe and kind in ("svg", "g"):
                continue
            if value is not None and (
                key == "stroke-width"
                or (wireframe and key == "stroke")
                or paints[node].get(key) != "none"
            ):
                updates[key] = str(value)
        if wireframe and kind in ("text", "tspan"):
            updates.update(fill=stroke, stroke="none")
        node.attrib.update(updates)
        css.update(updates)
        node.set("style", ";".join(f"{key}:{value}" for key, value in css.items()))
        stats["styled"] += 1
    if monochrome:
        css = dict(part.split(":", 1) for part in root.get("style", "").split(";") if ":" in part)
        effect = css.get("filter", root.get("filter", "")).strip()
        if not effect.endswith("grayscale(1)"):
            effect = f"{effect} grayscale(1)" if effect and effect != "none" else "grayscale(1)"
        css["filter"] = effect
        root.set("style", ";".join(f"{key}:{value}" for key, value in css.items()))
        stats["filtered_images"] = sum(node.tag == f"{{{SVG}}}image" for node in root.iter())
    if wireframe and not monochrome:
        for parent in list(root.iter()):
            for position, image in enumerate(list(parent)):
                if image.tag != f"{{{SVG}}}image":
                    continue
                stats["filtered_images"] += 1
                if parent.get("data-grablab-monochrome") == "true":
                    continue
                # W3C grayscale() is feColorMatrix shorthand with an overflow-aware region.
                wrapper = ET.Element(
                    f"{{{SVG}}}g",
                    {"style": "filter:grayscale(1)", "data-grablab-monochrome": "true"},
                )
                wrapper.tail, image.tail = image.tail, None
                parent.remove(image)
                wrapper.append(image)
                parent.insert(position, wrapper)
    if background is not None:
        root.insert(
            0,
            ET.Element(
                f"{{{SVG}}}rect",
                {
                    "x": "0",
                    "y": "0",
                    "width": "100%",
                    "height": "100%",
                    "fill": background,
                    "data-grablab-background": "true",
                },
            ),
        )
    return stats
