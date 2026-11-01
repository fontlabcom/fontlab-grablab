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


def test_pixels_compare_exact_premultiplied_rendering():
    assert svg.pixel_key(png((1, 2, 3, 255), 0)) == svg.pixel_key(
        png((1, 2, 3, 255), 9)
    )
    assert svg.pixel_key(png((1, 2, 3, 0))) == svg.pixel_key(png((7, 8, 9, 0)))
    assert svg.pixel_key(png((255, 0, 0, 1))) != svg.pixel_key(png((0, 0, 0, 1))), (
        "Visible premultiplied channels remain distinct"
    )
    assert svg.pixel_key(png((60, 60, 60, 16))) == svg.pixel_key(
        png((64, 64, 64, 16))
    ), "Qt PNG round-trip preserves the same RGBa pixel"
    assert svg.pixel_key(png((60, 60, 60, 240))) == svg.pixel_key(
        png((59, 59, 59, 240))
    ), "Qt premultiplication rounding is not an icon difference"
    assert svg.pixel_key(png((60, 60, 60, 255))) != svg.pixel_key(
        png((64, 64, 64, 255))
    ), "Opaque color differences must not collapse"
    assert svg.pixel_key(png((60, 60, 60, 16))) != svg.pixel_key(
        png((60, 60, 60, 17))
    ), "Alpha differences must not collapse"


def test_mapping_refuses_stale_fingerprint_indexes_before_editing():
    root = tree(f'<image href="{uri(png((60, 60, 60, 16)))}"/>')
    before = ET.tostring(root)
    with pytest.raises(ValueError, match="Rebuild"):
        svg.map_images(root, {"schema": "grablab.raster-index/1", "pixels": {}})
    assert ET.tostring(root) == before, "Stale index refusal leaves input intact"


@pytest.mark.parametrize("duplicate", [False, True])
def test_native_quantization_maps_only_unambiguous_vectors(tmp_path, duplicate):
    assets(tmp_path, duplicate)
    (tmp_path / "one.png").write_bytes(png((60, 60, 60, 16)))
    if duplicate:
        (tmp_path / "two.png").write_bytes(png((64, 64, 64, 16)))
    index = svg.build_raster_index(tmp_path / "manifest.json")
    root = tree(f'<image href="{uri(png((64, 64, 64, 16)))}"/>')
    mapping = svg.map_images(root, index)
    row = next(iter(mapping.values()))
    assert row["status"] == ("ambiguous" if duplicate else "matched"), (
        "Quantization must not choose between distinct vectors"
    )
    assert row["pixel_format"] == "RGBa8", "Mapping discloses the exact representation"
    assert svg.inline_images(root, mapping)["replaced"] == (0 if duplicate else 1)


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
    assert root[1].get("fill") == "white"


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
    assert root[0].get("stroke") == "#333333" and root[0].get("fill") == "white"
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


def test_source_name_conflicts_with_existing_export_pixels_remain_ambiguous(tmp_path):
    assets(tmp_path, True)
    (tmp_path / "two.png").write_bytes(png((1, 2, 3, 255)))
    sources = tmp_path / "sources"
    sources.mkdir()
    old_two = png((8, 9, 10, 255))
    (sources / "two.png").write_bytes(old_two)
    index = svg.build_raster_index(tmp_path / "manifest.json", [sources])
    root = tree(f'<image href="{uri(old_two)}"/>')
    mapping = svg.map_images(root, index)
    assert mapping[uri(old_two)]["status"] == "ambiguous"
    assert {
        (row["asset"], row["match"]) for row in mapping[uri(old_two)]["candidates"]
    } == {("one", "pixel-exact"), ("two", "source-name")}
    assert svg.inline_images(root, mapping)["replaced"] == 0


@pytest.mark.parametrize("reverse", [False, True])
def test_equal_widget_siblings_are_ambiguous_independent_of_input_order(reverse):
    widgets = [
        {"id": "left", "parent": "root", "rect": [0, 0, 20, 20]},
        {"id": "right", "parent": "root", "rect": [0, 0, 20, 20]},
    ]
    root = tree('<path d="M0 0h10v10z"/>')
    stats = svg.tag_widgets(
        root,
        {
            "size": [100, 100],
            "extensions": {"widgets": widgets[::-1] if reverse else widgets},
        },
    )
    assert root[0].get("data-widget") is None
    assert stats["ambiguous"] == 1 and stats["tagged"] == 0
    assert stats["ambiguities"][0]["widgets"] == ["left", "right"]


@pytest.mark.parametrize("reverse", [False, True])
def test_equal_parent_child_widget_bounds_choose_proven_descendant(reverse):
    widgets = [
        {"id": "outer", "parent": None, "rect": [0, 0, 20, 20]},
        {"id": "inner", "parent": "outer", "rect": [0, 0, 20, 20]},
    ]
    root = tree('<path d="M0 0h10v10z"/>')
    stats = svg.tag_widgets(
        root,
        {
            "size": [100, 100],
            "extensions": {"widgets": widgets[::-1] if reverse else widgets},
        },
    )
    assert root[0].get("data-widget") == "inner"
    assert stats["tagged"] == 1 and stats["ambiguous"] == 0


def test_normal_restyle_preserves_class_none_under_css_precedence():
    root = tree(
        '<style>#idpaint {fill:blue}.outline {fill:none;stroke:none}.paint {fill:green}.outline {fill:none}</style><path class="outline" d="M0 0h10v10z"/><path class="outline" id="idpaint"/><path class="outline" style="fill:red"/><path class="outline" fill="red"/><g class="outline"><path/></g>'
    )
    svg.restyle(root, fill="yellow", stroke="black")
    assert root[1].get("fill") != "yellow" and root[1].get("stroke") != "black"
    assert root[2].get("fill") == "yellow"  # ID overrides later class
    assert root[3].get("fill") == "yellow"  # inline overrides class
    assert root[4].get("fill") == "red"  # presentation is weaker than class none
    assert root[5][0].get("fill") != "yellow"  # inherited none


def test_normal_restyle_honors_important_none_over_inline_color():
    root = tree(
        '<style>.outline {fill:none !important;stroke:none !important}</style><path class="outline" style="fill:red;stroke:blue"/>'
    )
    svg.restyle(root, fill="yellow", stroke="black")
    assert root[1].get("fill") != "yellow" and root[1].get("stroke") != "black"


def test_same_vector_source_name_and_pixel_evidence_stay_uniquely_matched(tmp_path):
    assets(tmp_path)
    sources = tmp_path / "sources"
    sources.mkdir()
    raster = png((8, 9, 10, 255))
    (sources / "one.png").write_bytes(raster)
    index = svg.build_raster_index(tmp_path / "manifest.json", [sources])
    row = svg.map_images(tree(f'<image href="{uri(raster)}"/>'), index)[uri(raster)]
    assert row["status"] == "matched"
    assert {candidate["match"] for candidate in row["candidates"]} == {
        "source-name",
        "pixel-exact",
    }


@pytest.mark.parametrize("leaf", [False, True])
def test_widget_hierarchy_cycles_do_not_prove_unique_ownership(leaf):
    widgets = [
        {"id": "a", "parent": "b", "rect": [0, 0, 20, 20]},
        {"id": "b", "parent": "a", "rect": [0, 0, 20, 20]},
    ]
    if leaf:
        widgets.append({"id": "leaf", "parent": "a", "rect": [0, 0, 20, 20]})
    root = tree('<path d="M0 0h10v10z"/>')
    stats = svg.tag_widgets(
        root, {"size": [100, 100], "extensions": {"widgets": widgets}}
    )
    assert stats["ambiguous"] == 1 and root[0].get("data-widget") is None


def test_stylesheet_source_order_inline_precedence_and_keyword_inheritance():
    root = tree(
        '<style>.same {fill:green}.same {fill:NONE /*comment*/}#special {fill:green}.same {fill:none}</style><path class="same"/><path class="same" id="special"/><path class="same" style="fill:red !important;fill:none"/><g fill="none"><path fill="inherit"/></g>'
    )
    svg.restyle(root, fill="yellow")
    assert root[1].get("fill") != "yellow"
    assert root[2].get("fill") == "yellow"
    assert root[3].get("fill") == "yellow"
    assert root[4][0].get("fill") != "yellow"


@pytest.mark.parametrize(
    "style",
    ["@media print {.a {fill:none}}", ".a {fill:var(--paint)}", ".a {fill:revert}"],
)
def test_unresolved_css_fails_before_mutating_paint(style):
    root = tree(f'<style>{style}</style><path class="a"/>')
    original = ET.tostring(root)
    with pytest.raises(ValueError):
        svg.restyle(root, fill="yellow")
    assert ET.tostring(root) == original


@pytest.mark.parametrize("mode", ["monochrome", "wireframe"])
def test_monochrome_retained_png_keeps_pixels_geometry_and_effects(mode):
    href = uri(png((255, 0, 0, 255)))
    root = tree(
        f'<defs><filter id="effect"><feGaussianBlur stdDeviation="3"/></filter><clipPath id="clip"/></defs><path id="before"/><image id="raster" x="4" y="5" width="20" height="30" transform="rotate(5)" clip-path="url(#clip)" filter="url(#effect)" href="{href}"/><path id="after"/>'
    )
    image = root[2]
    original = dict(image.attrib)
    stats = svg.restyle(root, **{mode: True})
    assert stats["filtered_images"] == 1
    if mode == "monochrome":
        assert root[2] is image and image.attrib == original
        assert "grayscale(1)" in root.get("style", "")
        return
    wrapper = root[2]
    assert wrapper.tag == "{http://www.w3.org/2000/svg}g" and wrapper[0] is image
    assert image.attrib == original
    assert root[1].get("id") == "before" and root[3].get("id") == "after"
    assert wrapper.get("data-grablab-monochrome") == "true"
    assert "grayscale(1)" in wrapper.get("style", "")


def test_monochrome_is_explicit_and_repeated_styling_does_not_nest_wrappers():
    root = tree('<image href="data:image/png;base64,retained" width="10" height="10"/>')
    image = root[0]
    assert svg.restyle(root)["filtered_images"] == 0 and root[0] is image
    assert svg.restyle(root, monochrome=True)["filtered_images"] == 1
    assert root[0] is image
    assert svg.restyle(root, wireframe=True)["filtered_images"] == 1
    wrapper = root[0]
    assert wrapper[0] is image and len(wrapper) == 1
    assert svg.restyle(root, wireframe=True)["filtered_images"] == 1
    assert root[0] is wrapper and wrapper[0] is image


def test_composed_monochrome_preserves_existing_filter_and_clip_references(tmp_path):
    source = tmp_path / "mono.svg"
    root = tree(
        '<defs><filter id="effect"/><clipPath id="clip"/></defs><image filter="url(#effect)" clip-path="url(#clip)" href="data:image/png;base64,raw"/>'
    )
    svg.restyle(root, monochrome=True)
    svg.write_svg(root, source)
    composed = svg.compose([(source, 0, 0), (source, 100, 0)], width=200, height=100)
    for number, panel in enumerate(composed):
        image = panel.find(".//{http://www.w3.org/2000/svg}image")
        assert image.get("filter") == f"url(#panel-{number}-effect)"
        assert image.get("clip-path") == f"url(#panel-{number}-clip)"
        assert "grayscale(1)" in panel.get("style", "")


@pytest.mark.parametrize(
    "style",
    [
        "svg > image { transform:translate(10px,0); filter:url(#effect) }",
        "g { opacity:0.5; clip-path:url(#clip) }",
    ],
)
@pytest.mark.parametrize("mode", ["monochrome", "wireframe"])
def test_raster_wrapping_refuses_author_styles_before_any_mutation(style, mode):
    root = tree(f'<style>{style}</style><image href="data:image/png;base64,raw"/>')
    before = ET.tostring(root)
    with pytest.raises(ValueError, match="Unsupported stylesheet.*raster"):
        svg.restyle(root, **{mode: True})
    assert ET.tostring(root) == before


def test_compose_many_semantic_ids_rewrites_each_url_once(tmp_path):
    import time

    source = tmp_path / "semantic.svg"
    root = tree('<defs><clipPath id="clip"/></defs>')
    for number in range(1600):
        ET.SubElement(
            root,
            f"{{{svg.SVG}}}rect",
            {
                "id": f"widget-panel-control-{number}",
                "x": str(number),
                "width": "1",
                "height": "2",
                "fill": "#333333",
                "clip-path": "url( '#clip' )",
                "style": f'marker-start:url("#widget-panel-control-{number}");marker-end:url(#external)',
            },
        )
    source.write_bytes(ET.tostring(root))
    started = time.monotonic()
    result = svg.compose([(source, 0, 0), (source, 100, 0)], width=200, height=100)
    elapsed = time.monotonic() - started
    assert elapsed < 5, f"1600-element composition took {elapsed:.3f}s"
    for panel_number, panel in enumerate(result):
        for number, node in enumerate(list(panel)[1:]):
            assert (
                node.get("id") == f"panel-{panel_number}-widget-panel-control-{number}"
            )
            assert node.get("clip-path") == f"url(#panel-{panel_number}-clip)"
            assert node.get("style") == (
                f"marker-start:url(#panel-{panel_number}-widget-panel-control-{number});marker-end:url(#external)"
            )
            assert node.get("fill") == "#333333" and node.get("x") == str(number)


@pytest.mark.parametrize(
    "options",
    [
        {"fill": "#333333", "monochrome": True},
        {"wireframe": True},
        {"stroke": "black"},
        {"stroke_width": 2},
        {"font": "Example"},
        {},
    ],
)
def test_restyle_refuses_masks_before_mutating_inherited_paint_or_font(options):
    root = tree(
        '<g fill="white" font-family="serif"><defs><mask id="m">'
        '<rect width="100" height="100"/><text>Mask</text></mask></defs>'
        '<rect fill="red" mask="url(#m)"/></g>'
    )
    before = ET.tostring(root)
    with pytest.raises(ValueError, match="Restyling SVG masks is unsupported"):
        svg.restyle(root, background="yellow", **options)
    assert ET.tostring(root) == before, "Refusal must preserve the whole document"


def test_monochrome_keeps_contrast_paints_and_filter_chain():
    root = tree('<rect fill="white"/><text fill="#222">Text</text>')
    root.set("filter", "url(#effect)")
    svg.restyle(root, monochrome=True)
    assert root[0].get("fill") == "white"
    assert root[1].get("fill") == "#222"
    assert "url(#effect) grayscale(1)" in root.get("style")
    assert root[1].get("font-family") == "system-ui"


def test_wireframe_preserves_occlusion_none_and_resource_geometry():
    root = tree(
        '<defs><pattern id="p"><path fill="red" d="M0 0h2"/></pattern></defs>'
        '<path id="row" fill="red"/><rect id="footer" fill="#eee"/>'
        '<path fill="none"/><text>Footer</text>'
    )
    resource = ET.tostring(root[0])
    svg.restyle(root, wireframe=True, background="white")
    assert ET.tostring(root[1]) == resource
    assert [node.get("id") for node in root[2:4]] == ["row", "footer"]
    assert root[2].get("fill") == root[3].get("fill") == "white"
    assert root[4].get("fill") == "none"
    assert root[5].get("fill") == "#333333"


def test_monochrome_repeated_filter_and_important_filter_refusal():
    root = tree('<rect fill="red"/>')
    root.set("style", "filter:blur(2px)")
    svg.restyle(root, monochrome=True)
    svg.restyle(root, monochrome=True)
    assert root.get("style").count("grayscale(1)") == 1
    assert "blur(2px) grayscale(1)" in root.get("style")
    root.set("style", "filter:blur(2px)!important")
    before = ET.tostring(root)
    with pytest.raises(ValueError, match="important root filter"):
        svg.restyle(root, monochrome=True)
    assert ET.tostring(root) == before


@pytest.mark.parametrize(
    "keyword", ["initial", "unset", "inherit", "revert", "revert-layer", "INITIAL"]
)
@pytest.mark.parametrize("location", ["style", "attribute"])
def test_monochrome_css_wide_root_filter_refused_before_mutation(keyword, location):
    root = tree('<rect fill="red"/><text font-family="serif">Label</text>')
    if location == "style":
        root.set("style", f"filter: {keyword} ")
    else:
        root.set("filter", keyword)
    before = ET.tostring(root)
    with pytest.raises(ValueError, match="CSS-wide root filter"):
        svg.restyle(root, monochrome=True, background="white")
    assert ET.tostring(root) == before, (
        "Refusal must preserve paints, fonts and geometry"
    )


@pytest.mark.parametrize("mode", ["base64", "png-url", "svg-url", "inline-svg"])
def test_icon_modes_preserve_geometry_and_report_outcomes(tmp_path, mode):
    from urllib.parse import unquote

    index = assets(tmp_path)
    href = uri(png((8, 9, 10, 255)))
    root = tree(
        f'<image href="{href}" x="3" y="4" width="5" height="6" transform="rotate(2)" opacity="0.7" clip-path="url(#clip)" preserveAspectRatio="none"/>'
    )
    root[0].set(svg.XLINK, "stale.png")
    before = ET.tostring(root)
    output = tmp_path / "other" / "shot.svg"
    mapping = svg.map_images(root, index)
    result = svg.process_images(root, mapping, icon_mode=mode, output=output)
    assert result["mode"] == mode
    assert result["retained"] == (mode == "base64")
    if mode == "base64":
        assert ET.tostring(root) == before, (
            "Retaining icons must preserve every attribute"
        )
    elif mode.endswith("-url"):
        assert result["linked"] == 1 and result["inlined"] == 0
        assert root[0].get(svg.XLINK) is None, "No stale competing href"
        target = (output.parent / unquote(root[0].get("href"))).resolve()
        assert target == tmp_path / ("one.png" if mode == "png-url" else "one.svg")
        assert (
            root[0].get("transform") == "rotate(2)" and root[0].get("opacity") == "0.7"
        )
        assert root[0].get("x") == "3" and root[0].get("height") == "6"
        assert (
            root[0].get("clip-path") == "url(#clip)"
            and root[0].get("preserveAspectRatio") == "none"
        )
    else:
        assert result["inlined"] == 1 and root[0][0].get("x") == "3"


def test_base64_needs_no_mapping_and_invalid_mode_is_atomic():
    root = tree('<image href="data:image/png;base64,broken"/>')
    before = ET.tostring(root)
    assert svg.process_images(root, icon_mode="base64")["reasons"] == {"base64": 1}
    with pytest.raises(ValueError, match="icon mode"):
        svg.process_images(root, icon_mode="invalid")
    with pytest.raises(ValueError, match="output"):
        svg.process_images(root, {}, icon_mode="png-url")
    assert ET.tostring(root) == before


@pytest.mark.parametrize("mode", ["png-url", "svg-url", "inline-svg"])
def test_modes_retain_unknown_ambiguous_malformed_unsupported(tmp_path, mode):
    index = assets(tmp_path, True)
    root = tree(
        "".join(
            f'<image href="{value}"/>'
            for value in [
                uri(png((8, 9, 10, 255))),
                uri(png((1, 1, 1, 255))),
                "data:image/png;base64,broken",
                "data:image/jpeg;base64,YQ==",
                "existing.png",
            ]
        )
    )
    before = ET.tostring(root)
    result = svg.process_images(
        root, svg.map_images(root, index), icon_mode=mode, output=tmp_path / "out.svg"
    )
    assert result["retained"] == 5
    assert result["reasons"] == {
        "ambiguous": 1,
        "unmatched": 1,
        "invalid": 1,
        "unsupported": 1,
        "unmapped": 1,
    }
    assert ET.tostring(root) == before


def test_link_names_escape_and_rebase_composition(tmp_path):
    from urllib.parse import unquote

    resource = tmp_path / "assets" / "Original # & ü.svg"
    resource.parent.mkdir()
    resource.write_text(ET.tostring(tree("<path/>"), encoding="unicode"))
    href = uri(png((1, 2, 3, 255)))
    root = tree('<image width="2" height="2"/>')
    root[0].set(svg.XLINK, href)
    mapping = {href: {"status": "matched", "candidates": [{"svg": str(resource)}]}}
    panel = tmp_path / "panels" / "panel.svg"
    panel.parent.mkdir()
    result = svg.process_images(root, mapping, icon_mode="svg-url", output=panel)
    assert "%23" in root[0].get("href") and "%20" in root[0].get("href")
    assert result["targets"][0]["path"] == str(resource)
    svg.write_svg(root, panel)
    output = tmp_path / "composed.svg"
    composed = svg.compose([(panel, 0, 0)], width=100, height=100, output=output)
    image = next(composed.iter(f"{{{svg.SVG}}}image"))
    assert (output.parent / unquote(image.get("href"))).resolve() == resource


def test_default_process_matches_existing_inline_api(tmp_path):
    import copy

    index = assets(tmp_path)
    root = tree(f'<image href="{uri(png((8, 9, 10, 255)))}"/>')
    old = copy.deepcopy(root)
    mapping = svg.map_images(root, index)
    svg.inline_images(old, mapping)
    svg.process_images(root, mapping)
    assert ET.tostring(root) == ET.tostring(old)


def test_png_links_use_named_manifest_export_for_source_alias(tmp_path):
    source = tmp_path / "sources"
    source.mkdir()
    assets(tmp_path)
    (source / "one@2x.png").write_bytes(png((200, 40, 10, 255)))
    index = svg.build_raster_index(tmp_path / "manifest.json", [source])
    root = tree(f'<image href="{uri(png((200, 40, 10, 255)))}"/>')
    result = svg.process_images(
        root,
        svg.map_images(root, index),
        icon_mode="png-url",
        output=tmp_path / "out.svg",
    )
    assert root[0].get("href") == "one.png", (
        "Use Illustrator export basename, not resource alias"
    )
    assert result["targets"][0]["selection"] == "source-name-export"


@pytest.mark.parametrize("mode", ["png-url", "svg-url", "inline-svg"])
def test_deleted_assets_remain_embedded_with_reason(tmp_path, mode):
    index = assets(tmp_path)
    root = tree(f'<image href="{uri(png((8, 9, 10, 255)))}"/>')
    mapping = svg.map_images(root, index)
    (tmp_path / ("one.png" if mode == "png-url" else "one.svg")).unlink()
    before = ET.tostring(root)
    result = svg.process_images(
        root, mapping, icon_mode=mode, output=tmp_path / "out.svg"
    )
    assert result["reasons"] == {"invalid-target": 1}
    assert ET.tostring(root) == before


def test_png_multiple_exact_candidates_choose_sorted_path(tmp_path):
    index = assets(tmp_path)
    original = tmp_path / "one.png"
    other = tmp_path / "z.png"
    other.write_bytes(png((8, 9, 10, 255), 0))
    root = tree(f'<image href="{uri(png((8, 9, 10, 255)))}"/>')
    mapping = svg.map_images(root, index)
    candidates = next(iter(mapping.values()))["candidates"]
    candidates.insert(0, dict(candidates[0], png=str(other)))
    result = svg.process_images(
        root, mapping, icon_mode="png-url", output=tmp_path / "out.svg"
    )
    assert result["targets"][0]["path"] == str(original)
    assert root[0].get("href") == "one.png"


def test_compose_preserves_data_remote_fragment_and_query_urls(tmp_path):
    hrefs = [
        "data:image/png;base64,YQ==",
        "https://example.test/a.png",
        "//example.test/a.png",
        "#local",
        "/assets/icon.png",
        "../asset.png?v=1#part",
    ]
    panel = tmp_path / "sub" / "panel.svg"
    panel.parent.mkdir()
    root = tree("".join(f'<image href="{href}"/>' for href in hrefs))
    svg.write_svg(root, panel)
    result = svg.compose(
        [(panel, 0, 0)], width=100, height=100, output=tmp_path / "out.svg"
    )
    actual = [n.get("href") for n in result.iter(f"{{{svg.SVG}}}image")]
    assert actual[:-1] == hrefs[:-1]
    assert actual[-1] == "asset.png?v=1#part"


@pytest.mark.parametrize(
    "candidates, reason",
    [
        ([], "ambiguous"),
        ([{"svg": "one.svg"}], "missing-target"),
        (
            [
                {"svg": "one.svg", "export_png": "one.png"},
                {"svg": "one.svg", "export_png": "two.png"},
            ],
            "ambiguous-target",
        ),
    ],
)
def test_incomplete_or_conflicting_png_mapping_is_retained(
    tmp_path, candidates, reason
):
    root = tree('<image href="data:image/png;base64,abc"/>')
    mapping = {root[0].get("href"): {"status": "matched", "candidates": candidates}}
    before = ET.tostring(root)
    result = svg.process_images(
        root, mapping, icon_mode="png-url", output=tmp_path / "out.svg"
    )
    assert result["reasons"] == {reason: 1}
    assert ET.tostring(root) == before
