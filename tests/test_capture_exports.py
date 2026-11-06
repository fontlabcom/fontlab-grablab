# this_file: tests/test_capture_exports.py
"""Screen/canvas bundle contracts; real Qt/FontLab qualification stays separate."""

import base64
import json
import sys
import types
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from test_capture import grab as capture_fixture

grab = capture_fixture


def screen(grab, fail=False):
    captured = {"calls": 0, "text": {}}

    def save(path):
        if fail:
            return False
        Path(path).write_bytes(b"screen-pixels")
        return True

    image = types.SimpleNamespace(
        width=lambda: 160,
        height=lambda: 120,
        devicePixelRatio=lambda: 2,
        dotsPerMeterX=lambda: 1,
        dotsPerMeterY=lambda: 1,
        setDotsPerMeterX=lambda n: None,
        setDotsPerMeterY=lambda n: None,
        setText=lambda k, v: captured["text"].update({k: v}),
        save=save,
    )

    def capture(*args):
        captured["calls"] += 1
        return types.SimpleNamespace(toImage=lambda: image)

    geometry = types.SimpleNamespace(
        x=lambda: 500, y=lambda: 40, width=lambda: 80, height=lambda: 60
    )
    item = types.SimpleNamespace(geometry=geometry, name="Display", grabWindow=capture)
    grab.app.qapp = types.SimpleNamespace(screens=lambda: [item])
    grab.pref.grab_screens_only = []
    return captured


def test_screen_pair_uses_one_capture_and_raster_wrapper_at_logical_size(grab):
    captured = screen(grab)
    grab.pref.grab_svg = True
    paths = grab.grabScreens()
    assert [p.suffix for p in paths] == [".png", ".svg"]
    assert paths[0].stem == paths[1].stem and captured["calls"] == 1
    record = json.loads(paths[0].with_suffix(".json").read_text())
    assert (
        record["size"] == [80, 60]
        and record["pixels"] == [160, 120]
        and record["dpr"] == 2
    )
    assert record["extensions"]["capture_kind"] == "screen-raster"
    assert record["extensions"]["widgets"] == []
    assert json.loads(captured["text"]["grablab"]) == record
    root = ET.parse(paths[1]).getroot()
    image = root.find("{http://www.w3.org/2000/svg}image")
    assert (
        base64.b64decode(image.get("{http://www.w3.org/1999/xlink}href").split(",")[1])
        == paths[0].read_bytes()
    )
    assert image.get("width") == "80" and root.get("viewBox") == "0 0 80 60"
    assert json.loads(root.find("{http://www.w3.org/2000/svg}metadata").text) == record
    assert not paths[0].with_suffix(".ui").exists()


def test_screen_svg_only_and_sidecar_collision(grab):
    screen(grab)
    grab.pref.grab_png = False
    grab.pref.grab_svg = True
    (grab.grab_folder / "fl_sc0_test.ui").write_text("owner")
    paths = grab.grabScreens()
    assert (
        len(paths) == 1 and paths[0].suffix == ".svg" and paths[0].stem.endswith("_1")
    )
    assert not paths[0].with_suffix(".png").exists()
    assert (grab.grab_folder / "fl_sc0_test.ui").read_text() == "owner"


def test_failed_screen_save_publishes_nothing_and_restores(grab):
    screen(grab, fail=True)
    before = vars(grab.app.pref).copy()
    assert grab.grabScreens() == []
    assert list(grab.grab_folder.iterdir()) == []
    assert vars(grab.app.pref) == before


def canvas(grab, monkeypatch):
    state = {"alternative": False, "exports": [], "renders": []}

    def trigger():
        state["alternative"] = not state["alternative"]

    grab.app.ui = types.SimpleNamespace(
        menu=types.SimpleNamespace(
            view=types.SimpleNamespace(
                alternative_view=types.SimpleNamespace(trigger=trigger)
            )
        )
    )
    grab.pref.grab_pdf = False
    grab.pref.grab_svg = True

    def export(path, **kwargs):
        state["exports"].append((state["alternative"], grab.app.pref.generalDarkGlyph))
        path.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 20 40 30"><path d="M10 20h40v30z"/></svg>'
        )
        return path

    def render(source, destination):
        state["renders"].append(source.read_bytes())
        destination.write_bytes(b"rendered-png")
        return destination

    monkeypatch.setattr(grab, "getCanvasSVG", export)
    monkeypatch.setattr(grab, "_renderCanvasPNG", render, raising=False)
    return state


def test_canvas_png_is_rendered_from_the_exact_paired_native_svg(grab, monkeypatch):
    state = canvas(grab, monkeypatch)
    grab.dark = "d"
    before = vars(grab.app.pref).copy()
    paths = grab.grabCanvas()
    assert len(paths) == 8 and len(state["renders"]) == 4
    for number, source in enumerate([p for p in paths if p.suffix == ".svg"]):
        assert source.read_bytes() == state["renders"][number]
        record = json.loads(source.with_suffix(".json").read_text())
        assert record["extensions"]["capture_kind"] == "canvas-export"
        assert record["extensions"]["source_viewBox"] == [10, 20, 40, 30]
        assert record["size"] == [40, 30] and record["pixels"] == [40, 30]
        assert source.with_suffix(".png").exists()
    assert state["exports"] == [
        (False, True),
        (True, True),
        (False, False),
        (True, False),
    ]
    assert vars(grab.app.pref) == before and not state["alternative"]


def test_canvas_png_only_keeps_native_svg_temporary(grab, monkeypatch):
    state = canvas(grab, monkeypatch)
    grab.pref.grab_svg = False
    paths = grab.grabCanvas()
    assert len(paths) == 4 and all(p.suffix == ".png" for p in paths)
    assert len(state["renders"]) == 4
    assert not list(grab.grab_folder.glob("*.svg"))


def test_canvas_render_failure_restores_dark_and_alternative_state(grab, monkeypatch):
    state = canvas(grab, monkeypatch)
    grab.dark = "d"
    before = vars(grab.app.pref).copy()

    def fail(source, destination):
        if not grab.app.pref.generalDarkGlyph and state["alternative"]:
            raise RuntimeError("render failed")
        destination.write_bytes(b"png")
        return destination

    monkeypatch.setattr(grab, "_renderCanvasPNG", fail)
    with pytest.raises(RuntimeError, match="render failed"):
        grab.grabCanvas()
    assert vars(grab.app.pref) == before and not state["alternative"]
    assert not hasattr(grab, "_bundle_record")
    assert len(list(grab.grab_folder.glob("*.json"))) == 3


@pytest.mark.parametrize(
    "failure", [None, "invalid", "null", "begin", "render", "save"]
)
@pytest.mark.parametrize("properties", [False, True])
def test_actual_qt_renderer_contract_and_finally_cleanup(
    grab, monkeypatch, failure, properties
):
    state = {"ended": False, "deleted": False, "loaded": None, "painted": None}

    def getter(result):
        return result if properties else lambda: result

    class Renderer:
        def __init__(self, path):
            state["loaded"] = Path(path).read_bytes()
            self.isValid = getter(failure != "invalid")

        def render(self, painter, rect):
            if failure == "render":
                raise RuntimeError("render failed")
            state["painted"] = rect

        def deleteLater(self):
            state["deleted"] = True

    class Image:
        Format_ARGB32_Premultiplied = 6

        def __init__(self, width, height, format):
            self.width, self.height = getter(width), getter(height)
            self.devicePixelRatio = getter(1.0)
            self.dotsPerMeterX = self.dotsPerMeterY = getter(1)
            self.isNull = getter(failure == "null")

        def fill(self, number):
            assert number == 0

        def setDotsPerMeterX(self, n):
            pass

        def setDotsPerMeterY(self, n):
            pass

        def setText(self, key, text):
            pass

        def save(self, path):
            if failure == "save":
                return False
            Path(path).write_bytes(b"pixels")
            return True

    class Painter:
        def begin(self, image):
            return failure != "begin"

        def end(self):
            state["ended"] = True

    monkeypatch.setattr(
        sys.modules["PythonQt.QtSvg"], "QSvgRenderer", Renderer, raising=False
    )
    monkeypatch.setattr(sys.modules["PythonQt.QtGui"], "QImage", Image, raising=False)
    monkeypatch.setattr(
        sys.modules["PythonQt.QtGui"], "QPainter", Painter, raising=False
    )
    core = types.ModuleType("PythonQt.QtCore")
    core.QRectF = lambda *args: args
    monkeypatch.setitem(sys.modules, "PythonQt.QtCore", core)
    source, destination = grab.grab_folder / "source.svg", grab.grab_folder / "out.png"
    source.write_bytes(b"exact SVG bytes")
    grab._bundle_record = {"pixels": [80, 60]}
    if failure in ("invalid", "null", "begin", "render"):
        with pytest.raises((ValueError, RuntimeError, MemoryError)):
            grab._renderCanvasPNG(source, destination)
    else:
        result = grab._renderCanvasPNG(source, destination)
        assert (result is None) == (failure == "save")
    assert state["loaded"] == b"exact SVG bytes" and state["deleted"]
    assert state["ended"] == (failure not in ("invalid", "null"))
    if failure is None:
        assert state["painted"] == (0, 0, 80, 60)


def test_screen_selection_and_primitive_png_return_are_preserved(grab):
    captured = screen(grab)
    assert grab.grabScreens(screens=[1]) == []
    grab.pref.grab_screens_only = [1]
    assert grab.grabScreens() == [] and captured["calls"] == 0
    item = grab.app.qapp.screens()[0]
    path = grab.grabScreenPNG(item, "0")
    assert isinstance(path, Path) and path.suffix == ".png"


def test_canvas_svg_only_skips_png_renderer_and_pdf_stays_additive(grab, monkeypatch):
    canvas(grab, monkeypatch)
    grab.pref.grab_png = False
    grab.pref.grab_pdf = True
    monkeypatch.setattr(
        grab,
        "_renderCanvasPNG",
        lambda *args: pytest.fail("SVG-only must not render PNG"),
    )

    def pdf(path):
        path.write_bytes(b"pdf")
        return path

    monkeypatch.setattr(grab, "getCanvasPDF", pdf)
    paths = grab.grabCanvas()
    assert [p.suffix for p in paths] == [".svg"] * 4 + [".pdf"]
    assert all(
        json.loads(p.with_suffix(".json").read_text())["pixels"] is None
        for p in paths[:-1]
    )


def test_screen_publication_collision_rolls_back_only_its_files(grab, monkeypatch):
    screen(grab)
    grab.pref.grab_svg = True
    module = sys.modules["grablab.grab"]
    link = module.os.link

    def collide(source, destination):
        if destination.suffix == ".json":
            destination.write_text("owner")
        link(source, destination)

    monkeypatch.setattr(module.os, "link", collide)
    with pytest.raises(FileExistsError):
        grab.grabScreens()
    assert [p.suffix for p in grab.grab_folder.iterdir()] == [".json"]
    assert next(grab.grab_folder.iterdir()).read_text() == "owner"


@pytest.mark.parametrize("format", ["SVG", "PDF"])
def test_native_export_exception_removes_owned_temporary_file(
    grab, monkeypatch, format
):
    temporary = grab.grab_folder / "owned-temporary"
    monkeypatch.setattr(grab, "tmpPath", lambda **kwargs: temporary)

    def export(path, kind):
        path.write_bytes(b"partial")
        raise RuntimeError("export failed")

    grab.app.ws.exportTo = export
    before = vars(grab.app.pref).copy()
    with pytest.raises(RuntimeError, match="export failed"):
        getattr(grab, "getCanvas" + format)(grab.grab_folder / "out")
    assert not temporary.exists() and vars(grab.app.pref) == before


@pytest.mark.parametrize("enabled", [False, True])
def test_grab_all_aggregates_image_lists_and_keeps_enabled_callers(
    grab, monkeypatch, enabled
):
    methods = {
        "canvas": "grabCanvas",
        "glyph_windows": "grabGlyphWindows",
        "font_windows": "grabFontWindows",
        "panels": "grabPanels",
        "menu": "grabMainMenu",
        "toolbar": "grabPanel",
        "screens": "grabScreens",
    }
    called = []
    monkeypatch.setattr(grab, "newGrab", lambda: None)
    for flag, method in methods.items():
        setattr(grab.pref, "grab_" + flag, enabled)

        def capture(*args, _method=method):
            called.append(_method)
            return [Path(_method + ".png"), Path(_method + ".svg")]

        monkeypatch.setattr(grab, method, capture)
    paths = grab.grabAll()
    assert len(paths) == (14 if enabled else 0)
    assert called == (list(methods.values()) if enabled else [])


@pytest.mark.parametrize("viewport_shape", ["direct", "named", "missing"])
def test_widget_callers_keep_panel_parents_window_filtering_and_bundle_returns(
    grab, monkeypatch, viewport_shape
):
    calls = []

    def widget(kind, parent=None, visible=True):
        return types.SimpleNamespace(
            className=lambda: kind, parentWidget=lambda: parent, visible=visible
        )

    panel = widget(
        "QLabel", widget("QStackedWidget", widget("YTabWidget", widget("YPanel")))
    )
    hidden = widget("QLabel", visible=False)
    glyph = widget("GlyphWindow")
    viewport = widget("Viewport")
    viewport.objectName = "widgetViewport"
    if viewport_shape == "direct":
        glyph.widgetViewport = viewport
    gui = sys.modules["PythonQt.QtGui"]
    monkeypatch.setattr(gui, "QWidget", type("QWidget", (), {}), raising=False)
    monkeypatch.setitem(sys.modules, "PythonQt", types.SimpleNamespace(QtGui=gui))
    other = widget("Other")
    other.objectName = "other"
    glyph.findChildren = lambda cls: [other] if viewport_shape == "missing" else [other, viewport]
    grab.pref.grab_also_invisible = False
    grab.app.ui = types.SimpleNamespace(
        panels={
            "elements": types.SimpleNamespace(widget=panel),
            "hidden": types.SimpleNamespace(widget=hidden),
            "absent": types.SimpleNamespace(widget=None),
            "font_map": None,
            "toolbar": None,
        },
        glyphWindows=lambda: {"Font @ A": glyph, "Hidden": hidden},
        fontWindows=lambda: {"Font": glyph, "Hidden": hidden},
    )

    def capture(target, kind, name, descriptor):
        calls.append((target, kind))
        return [Path(name + ".png"), Path(name + ".svg")]

    monkeypatch.setattr(grab, "grabWidget", capture)
    assert len(grab.grabPanels()) == 2 and calls[0][0].className() == "YPanel"
    assert len(grab.grabPanel("hidden", force_visible=True)) == 2
    calls.clear()
    before = vars(grab.app.pref).copy()
    if viewport_shape == "missing":
        with pytest.raises(LookupError, match="no widgetViewport child"):
            grab.grabGlyphWindows()
        assert calls == [] and vars(grab.app.pref) == before
        return
    from fontlabapp.qt.views import GlyphWindow
    assert sys.modules["grablab.grab"].GlyphWindow is GlyphWindow
    expected = [Path("a_font.png"), Path("a_font.svg")] * 2
    assert grab.grabGlyphWindows() == expected
    assert calls == [(viewport, "gv"), (glyph, "gw")]
    hidden.widgetViewport = widget("HiddenViewport")
    grab.pref.grab_also_invisible = True
    calls.clear()
    assert grab.grabGlyphWindows() == expected + [Path("hidden.png"), Path("hidden.svg")] * 2
    assert calls == [(viewport, "gv"), (glyph, "gw"), (hidden.widgetViewport, "gv"), (hidden, "gw")]
    grab.pref.grab_also_invisible = False
    assert len(grab.grabFontWindows()) == 2
    assert vars(grab.app.pref) == before


def test_new_capture_folder_preserves_font_naming_policy(grab, monkeypatch, tmp_path):
    module = sys.modules["grablab.grab"]
    grab.pref.folder_save_with_font = False
    grab.pref.folder_base = tmp_path / "Pictures"
    monkeypatch.setattr(module, "timestamp", lambda: "now")
    grab.newGrab()
    assert grab.grab_folder == tmp_path / "Pictures" / "fl_now"
    font = tmp_path / "Font.vfj"
    monkeypatch.setattr(
        module, "CurrentFont", lambda: types.SimpleNamespace(path=str(font))
    )
    grab.pref.folder_save_with_font = True
    grab.newGrab()
    assert grab.grab_folder == tmp_path / "fl_now_font"


def test_all_image_formats_disabled_does_not_capture(grab, monkeypatch):
    captured = screen(grab)
    grab.pref.grab_png = grab.pref.grab_svg = grab.pref.grab_pdf = False
    assert grab.grabScreens() == [] and grab.grabCanvas() == []
    assert captured["calls"] == 0 and list(grab.grab_folder.iterdir()) == []


@pytest.mark.parametrize("failure", ["export", "render", "geometry"])
def test_canvas_missing_or_invalid_output_never_publishes_partial_bundle(
    grab, monkeypatch, failure
):
    canvas(grab, monkeypatch)
    if failure == "export":
        monkeypatch.setattr(grab, "getCanvasSVG", lambda *args, **kwargs: None)
    elif failure == "render":
        monkeypatch.setattr(grab, "_renderCanvasPNG", lambda *args: None)
    else:

        def bad(path, **kwargs):
            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 -1 2"/>'
            )
            return path

        monkeypatch.setattr(grab, "getCanvasSVG", bad)
    if failure == "geometry":
        with pytest.raises(ValueError, match="viewBox"):
            grab.grabCanvas()
    else:
        assert grab.grabCanvas() == []
    assert list(grab.grab_folder.iterdir()) == []


def test_invalid_screen_geometry_fails_before_capture(grab):
    captured = screen(grab)
    grab.app.qapp.screens()[0].geometry.width = lambda: 0
    with pytest.raises(ValueError, match="geometry"):
        grab.grabScreens()
    assert captured["calls"] == 0


def test_named_viewport_capture_failure_restores_preferences(grab, monkeypatch):
    from test_snapshot import widget
    viewport = widget()
    viewport.objectName = "widgetViewport"
    glyph = types.SimpleNamespace(visible=True, findChildren=lambda cls: [viewport])
    gui = sys.modules["PythonQt.QtGui"]
    monkeypatch.setattr(gui, "QWidget", type("QWidget", (), {}), raising=False)
    monkeypatch.setitem(sys.modules, "PythonQt", types.SimpleNamespace(QtGui=gui))
    grab.app.ui = types.SimpleNamespace(glyphWindows=lambda: {"Font @ A": glyph})
    grab.pref.grab_also_invisible = False
    before = vars(grab.app.pref).copy()

    def fail(*args):
        assert grab.app.pref.developerOpenGL is False
        raise RuntimeError("owned viewport save failure")

    monkeypatch.setattr(grab, "grabWidgetPNG", fail)
    with pytest.raises(RuntimeError, match="owned viewport save failure"):
        grab.grabGlyphWindows()
    assert vars(grab.app.pref) == before
    assert list(grab.grab_folder.iterdir()) == []
