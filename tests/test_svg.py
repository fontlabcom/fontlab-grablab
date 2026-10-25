# this_file: tests/test_svg.py
"""Host-free controls; rendering/native fidelity remains a separate gate."""

import base64
import io
import json
import xml.etree.ElementTree as ET

import pytest
from PIL import Image

from grablab import svg


def tree(body):
    return ET.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">{body}</svg>'
    )


def png(color, compression=6):
    data = io.BytesIO()
    Image.new("RGBA", (2, 2), color).save(data, "PNG", compress_level=compression)
    return data.getvalue()


def uri(data):
    return "data:image/png;base64," + base64.b64encode(data).decode()


def assets(tmp_path, duplicate=False):
    rows = []
    for name in ["one", "two"] if duplicate else ["one"]:
        (tmp_path / f"{name}.png").write_bytes(png((8, 9, 10, 255)))
        (tmp_path / f"{name}.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="5 6 2 2"><defs><clipPath id="clip"><rect width="2" height="2"/></clipPath></defs><path clip-path="url(#clip)" d="M5 6h2v2z"/></svg>'
        )
        rows.append(
            {
                "basename": name,
                "files": {
                    "png": {"path": f"{name}.png"},
                    "svg": {"path": f"{name}.svg"},
                },
            }
        )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"assets": rows}))
    return svg.build_raster_index(manifest)


def test_pixels_ignore_encoding_and_only_fully_transparent_rgb():
    assert svg.pixel_key(png((1, 2, 3, 255), 0)) == svg.pixel_key(
        png((1, 2, 3, 255), 9)
    )
    assert svg.pixel_key(png((1, 2, 3, 0))) == svg.pixel_key(png((7, 8, 9, 0)))
    assert svg.pixel_key(png((1, 2, 3, 1))) != svg.pixel_key(png((7, 8, 9, 1)))


def test_mapping_and_inline_preserve_viewport_and_namespaced_refs(tmp_path):
    index = assets(tmp_path)
    root = tree(
        f'<g transform="translate(3 4)" clip-path="url(#outer)"><image x="9" y="10" width="20" height="30" preserveAspectRatio="none" href="{uri(png((8, 9, 10, 255), 0))}"/><image width="5" height="5" href="{uri(png((8, 9, 10, 255)))}"/></g>'
    )
    mapping = svg.map_images(root, index)
    assert all(item["status"] == "matched" for item in mapping.values())
    assert svg.inline_images(root, mapping)["replaced"] == 2
    nested = root.findall(".//{http://www.w3.org/2000/svg}svg")
    assert nested[0].get("x") == "9" and nested[0].get("viewBox") == "5 6 2 2"
    assert nested[0].get("preserveAspectRatio") == "none"
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    assert len(ids) == len(set(ids))
    assert root[0].get("transform") == "translate(3 4)"
    assert root[0].get("clip-path") == "url(#outer)"
    assert all(
        "url(#icon-" in node.get("clip-path")
        for node in root.iter()
        if node.tag.endswith("path")
    )


def test_ambiguous_unmatched_and_invalid_stay_raster(tmp_path):
    index = assets(tmp_path, True)
    root = tree(
        "".join(
            f'<image href="{value}"/>'
            for value in [
                uri(png((8, 9, 10, 255))),
                uri(png((1, 1, 1, 255))),
                "data:image/png;base64,broken",
            ]
        )
    )
    mapping = svg.map_images(root, index)
    assert {row["status"] for row in mapping.values()} == {
        "ambiguous",
        "unmatched",
        "invalid",
    }
    assert svg.inline_images(root, mapping)["replaced"] == 0
    assert len(list(root)) == 3


def test_semantics_use_transformed_path_bounds_and_do_not_reorder():
    root = tree(
        '<g transform="translate(20 30)"><path id="original" d="M0 0h10v10h-10z"/><path d="M60 60h5v5z"/></g>'
    )
    record = {
        "size": [100, 100],
        "extensions": {
            "widgets": [
                {"id": "button", "rect": [20, 30, 10, 10]},
                {"id": "root", "rect": [0, 0, 100, 100]},
            ]
        },
    }
    stats = svg.tag_widgets(root, record)
    assert stats["tagged"] == 2
    assert root[0][0].get("data-widget") == "button"
    assert root[0][0].get("id") == "original"
    assert root[0][1].get("data-widget") == "root"
    assert root[0][1].get("d") == "M60 60h5v5z"


def test_dedup_only_adjacent_opaque_paths_without_effects_or_ids():
    opaque = '<path fill="#123456" d="M0 0h2v2z"/>'
    transparent = '<path opacity=".5" d="M0 0h2v2z"/>'
    root = tree(
        opaque
        + opaque
        + transparent
        + transparent
        + '<g opacity=".5">'
        + opaque
        + opaque
        + '</g><g filter="url(#f)">'
        + opaque
        + opaque
        + "</g>"
    )
    assert svg.deduplicate_paths(root)["removed"] == 1
    assert len(root[3]) == 2 and len(root[4]) == 2


def test_compose_namespaces_ids_and_uses_explicit_logical_positions(tmp_path):
    source = tmp_path / "panel.svg"
    source.write_text(
        ET.tostring(
            tree(
                '<defs><linearGradient id="g"/></defs><path fill="url(#g)" d="M0 0h2v2z"/>'
            ),
            encoding="unicode",
        )
    )
    root = svg.compose([(source, 10, 20), (source, 40, 50)], width=200, height=120)
    assert root[0].get("x") == "10" and root[1].get("y") == "50"
    assert root[0].get("width") == "100"
    assert root[0][0][0].get("id") != root[1][0][0].get("id")
    assert root.get("viewBox") == "0 0 200 120"


def test_restyle_changes_inline_css_and_preserves_none():
    root = tree(
        '<path style="fill:red;stroke:blue;stroke-width:2;opacity:.5" d="M0 0h2v2z"/><path fill="none" stroke="green"/><text font-family="Old">Hi</text>'
    )
    svg.restyle(root, stroke="#333", fill="#eee", stroke_width=1, background="white")
    assert root[1].get("stroke") == "#333" and root[1].get("fill") == "#eee"
    assert "opacity:.5" in root[1].get("style")
    assert root[2].get("fill") == "none"
    assert root[3].get("font-family") == "system-ui"
    svg.restyle(root, wireframe=True)
    assert root[1].get("fill") == "none"


def test_write_never_overwrites_raw_or_existing_output(tmp_path):
    path = tmp_path / "raw.svg"
    path.write_text("raw")
    with pytest.raises(FileExistsError):
        svg.write_svg(tree(""), path)
    assert path.read_text() == "raw"


def test_authoritative_source_aliases_require_exact_pixels(tmp_path):
    assets(tmp_path)
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "renamed.png").write_bytes(png((8, 9, 10, 255), 0))
    (sources / "unrelated.png").write_bytes(png((5, 6, 7, 255)))
    index = svg.build_raster_index(tmp_path / "manifest.json", [sources])
    assert {
        row["png"].rsplit("/", 1)[-1]: row["status"] for row in index["sources"]
    } == {"renamed.png": "matched", "unrelated.png": "unmatched"}
    assert (
        svg.map_images(tree('<image href="data:image/jpeg;base64,AA=="/>'), index)[
            "data:image/jpeg;base64,AA=="
        ]["status"]
        == "unsupported"
    )


def test_composition_namespaces_css_classes_selectors_and_quoted_urls(tmp_path):
    source = tmp_path / "source.svg"
    source.write_text(
        ET.tostring(
            tree(
                '<style>.paint,#p {fill:#fff;clip-path:url(\'#c\')}</style><defs><clipPath id="c"/></defs><path id="p" class="paint" fill="#fff"/><use href="#p"/>'
            ),
            encoding="unicode",
        )
    )
    root = svg.compose([(source, 0, 0), (source, 0, 0)], width=100, height=100)
    assert ".panel-0-paint,#panel-0-p" in root[0][0].text
    assert "fill:#fff" in root[0][0].text
    assert "url(#panel-0-c)" in root[0][0].text
    assert root[1][2].get("class") == "panel-1-paint"
    assert root[1][3].get("href") == "#panel-1-p"


def test_semantics_viewbox_logical_coordinates_and_text_anchors():
    root = tree(
        '<g transform="translate(20 30)"><text x="2" y="5">Hi</text><path d="M0 0h10v10z"/></g>'
    )
    root.set("width", "200")
    root.set("height", "200")
    record = {
        "size": [100, 100],
        "extensions": {"widgets": [{"id": "button", "rect": [20, 30, 10, 10]}]},
    }
    stats = svg.tag_widgets(root, record)
    assert stats["tagged"] == 2 and stats["text_anchors"] == 1
    assert root[0][0].get("data-widget-method") == "text-anchor"


def test_semantics_reports_outside_and_unknown_and_retains_drawing():
    root = tree('<path d="M80 80h10v10z"/><text x="90" y="95">Outside</text>')
    original = [node.get("d") for node in root]
    stats = svg.tag_widgets(
        root,
        {
            "size": [100, 100],
            "extensions": {"widgets": [{"id": "button", "rect": [0, 0, 10, 10]}]},
        },
    )
    assert stats["unmatched"] == 2 and stats["tagged"] == 0
    assert original == [node.get("d") for node in root]


def test_invalid_geometry_does_not_silently_tag():
    root = tree('<path d="not a path"/>')
    stats = svg.tag_widgets(root, {"size": [100, 100], "extensions": {"widgets": []}})
    assert stats["unsupported"] == 1 and stats["tagged"] == 0


def test_invalid_dimensions_and_style_width_fail():
    with pytest.raises(ValueError):
        svg.compose([], width=-1, height=100)
    with pytest.raises(ValueError):
        svg.restyle(tree(""), stroke_width=float("nan"))


def test_dedup_retains_strokes_ids_nonadjacent_and_inherited_opacity():
    root = tree(
        '<path fill="#000" stroke="black" d="M0 0h2"/><path fill="#000" stroke="black" d="M0 0h2"/><path id="a" fill="#000" d="M0 0h2"/><path id="b" fill="#000" d="M0 0h2"/>'
    )
    assert svg.deduplicate_paths(root)["removed"] == 0
    root.set("fill-opacity", ".5")
    assert svg.deduplicate_paths(root)["removed"] == 0


def test_wireframe_text_visible_and_all_geometry_outlined():
    root = tree('<path stroke="none" fill="red"/><text fill="red">Label</text>')
    svg.restyle(root, wireframe=True, font="Example")
    assert root[0].get("stroke") == "#333333" and root[0].get("fill") == "none"
    assert root[1].get("fill") == "#333333" and root[1].get("stroke") == "none"
    assert root[1].get("font-family") == "Example"


def test_write_read_roundtrip_and_read_rejects_other_xml(tmp_path):
    output = svg.write_svg(tree('<path d="M0 0h1"/>'), tmp_path / "processed.svg")
    assert svg.read_svg(output)[0].get("d") == "M0 0h1"
    output = tmp_path / "other.xml"
    output.write_text("<other/>")
    with pytest.raises(ValueError):
        svg.read_svg(output)


def test_named_authoritative_mapping_records_distinct_provenance(tmp_path):
    assets(tmp_path)
    sources = tmp_path / "sources"
    sources.mkdir()
    old = png((55, 66, 77, 255))
    (sources / "one@2x.png").write_bytes(old)
    index = svg.build_raster_index(tmp_path / "manifest.json", [sources])
    mapping = svg.map_images(tree(f'<image href="{uri(old)}"/>'), index)
    assert mapping[uri(old)]["status"] == "matched"
    assert mapping[uri(old)]["candidates"][0]["match"] == "source-name"
    assert index["sources"][0]["candidates"][0]["png"].endswith("one@2x.png")


def test_conflicting_original_asset_names_never_choose_arbitrarily(tmp_path):
    assets(tmp_path, True)
    manifest = tmp_path / "manifest.json"
    data = json.loads(manifest.read_text())
    for row in data["assets"]:
        row["asset_name"] = "shared"
    manifest.write_text(json.dumps(data))
    sources = tmp_path / "sources"
    sources.mkdir()
    old = png((55, 66, 77, 255))
    (sources / "shared.png").write_bytes(old)
    index = svg.build_raster_index(manifest, [sources])
    mapping = svg.map_images(tree(f'<image href="{uri(old)}"/>'), index)
    assert mapping[uri(old)]["status"] == "ambiguous"
    assert len(mapping[uri(old)]["candidates"]) == 2


def test_missing_source_directory_fails_instead_of_silent_empty_index(tmp_path):
    assets(tmp_path)
    with pytest.raises(NotADirectoryError):
        svg.build_raster_index(tmp_path / "manifest.json", [tmp_path / "missing"])


def test_zero_capture_size_fails_before_geometry_parsing():
    with pytest.raises(ValueError):
        svg.tag_widgets(tree(""), {"size": [0, 100], "extensions": {"widgets": []}})


def test_semantics_never_tag_shared_defs_as_a_use_instance():
    root = tree(
        '<defs><path id="shared" d="M0 0h10v10z"/></defs><use href="#shared"/><use href="#shared" x="30"/>'
    )
    svg.tag_widgets(
        root,
        {
            "size": [100, 100],
            "extensions": {
                "widgets": [
                    {"id": "first", "rect": [0, 0, 10, 10]},
                    {"id": "second", "rect": [30, 0, 10, 10]},
                ]
            },
        },
    )
    assert root[0][0].get("data-widget") is None
