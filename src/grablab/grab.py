#!/usr/bin/env python3
# this_file: src/grablab/grab.py
# -*- coding: utf-8 -*-
# Copyright (c) 2022 Adam Twardoch
# License: BSD 3-Clause License
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import base64
import json
import math
import os
import shutil
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterator

from fontlab import CurrentFont
from fontlabapp import Application
from fontlabapp.qt.views import GlyphWindow
from fontlabapp.utils import attribdict as adict
from fontlabapp.utils import slugify, timestamp
from PythonQt.Qt import QBuffer
from PythonQt.QtGui import QMenu, QMessageBox
from PythonQt.QtSvg import QSvgGenerator

from .snapshot import embed_svg, free_bundle, native_list, snapshot, ui_xml, value

svg_ns = "http://www.w3.org/2000/svg"
ET.register_namespace("", svg_ns)

@contextmanager
def capture_preferences(grab: Any) -> Iterator[None]:
    """Restore only capture-related native preferences even after failure."""
    keys = ("developerOpenGL", "editorOutlineThickness", "editorFocus", "generalDarkGlyph")
    saved = {key: getattr(grab.app.pref, key) for key in keys if hasattr(grab.app.pref, key)}
    try:
        grab.setAppPrefs()
        yield
    finally:
        for key, value in saved.items():
            setattr(grab.app.pref, key, value)
        grab.app.ws.updateActiveViewport()


def with_capture_preferences(function: Callable[..., Any]) -> Callable[..., Any]:
    """Scope preference adjustments to actual capture operations."""
    @wraps(function)
    def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        with capture_preferences(self):
            return function(self, *args, **kwargs)
    return wrapped


@contextmanager
def alternative_view(action: Any) -> Iterator[None]:
    """Pair temporary view toggles even if an export raises."""
    action.trigger()
    try:
        yield
    finally:
        action.trigger()


class Grab(object):
    def __init__(self, application: Any = None, **kwargs: Any) -> None:
        self.app = application if application is not None else Application()
        self.dark = ""
        if self.app.pref.isDark:
            self.dark = "d"
        self.setGrabPrefs(**kwargs)

    def setGrabPrefs(self, **kwargs: Any) -> Any:
        self.pref = self.app.preflib.getpref(
            self.app.preflib.lib.com.fontlab.grablab,
            {
                "folder_base": Path(self.app.paths.sysUserPicturesFolder, "GrabLab"),
                "folder_save_with_font": False,
                "naming_prefix": "fl_",
                "grab_also_invisible": False,
                "grab_canvas": True,
                "grab_glyph_windows": True,
                "grab_font_windows": True,
                "grab_panels": True,
                "grab_menu": False,
                "grab_toolbar": True,
                "grab_screens": True,
                "grab_screens_only": [],
                "grab_svg": True,
                "grab_png": True,
                "grab_pdf": True,
            },
        )
        self.app.preflib.save()
        if kwargs:
            self.app.preflib.update(self.pref, kwargs)

    def setAppPrefs(self) -> Any:
        """Apply temporary rendering settings; capture contexts restore them."""
        self.app.pref.developerOpenGL = False
        self.app.pref.editorOutlineThickness = 1
        self.app.pref.editorFocus = False
        self.app.ws.updateActiveViewport()

    def tmpPath(self, suffix: Any="") -> Any:
        tmpFile = tempfile.NamedTemporaryFile(suffix=suffix)
        tmpPath = self.path(tmpFile.name)
        tmpFile.close()
        return tmpPath

    def addSizeToPath(self, path: Any, width: Any, height: Any) -> Any:
        return path.with_name(f"{path.stem}_{width}x{height}{path.suffix}")

    def path(self, path: Any, folder: Any=False) -> Any:
        path = Path(path)
        if folder:
            if not path.is_dir():
                path.mkdir(parents=True, exist_ok=True)
        elif not path.parent.is_dir():
            path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def getBaseFolder(self) -> Any:
        font = CurrentFont()
        if font and self.pref.folder_save_with_font:
            return self.path(Path(font.path).parent, folder=True)
        else:
            return self.path(self.pref.folder_base, folder=True)

    def getGrabPath(self, name: Any, format: Any, dup: Any=0) -> Any:
        if getattr(self, "_bundle_base", None) is not None:
            return self._bundle_base.with_suffix("." + format)
        while True:
            dupstr = f"_{dup}" if dup else ""
            path = self.path(Path(self.grab_folder,
                f"{self.pref.naming_prefix}{name}_{self.timestamp}{self.grab_suffix}{dupstr}.{format}"))
            if not path.exists():
                return free_bundle(path) if format in ("png", "svg") else path
            dup += 1

    @with_capture_preferences
    def getCanvasSVG(self, path: Any, title: Any="", description: Any="") -> Any:
        tmp = self.tmpPath(suffix=".svg")
        try:
            self.app.ws.exportTo(tmp, "SVG")
            self.optimizeSVG(tmp, title, description)
            return shutil.move(tmp, self.path(path)) if self.path(tmp).is_file() else None
        finally:
            tmp.unlink(missing_ok=True)

    @with_capture_preferences
    def getCanvasPDF(self, path: Any, title: Any="", description: Any="") -> Any:
        tmp = self.tmpPath(suffix=".pdf")
        try:
            self.app.ws.exportTo(tmp, "PDF")
            return shutil.move(tmp, self.path(path)) if self.path(tmp).is_file() else None
        finally:
            tmp.unlink(missing_ok=True)

    @with_capture_preferences
    def getPixmapPNG(self, pixmap: Any, path: Any, title: Any="", description: Any="") -> Any:
        return self._saveImagePNG(pixmap.toImage(), path, title, description)

    def _saveImagePNG(self, image: Any, path: Any, title: str="", description: str="") -> Any:
        """Save the owned image with the current bundle's complete metadata."""
        path = self.path(path)
        if path.exists():
            raise FileExistsError(path)
        record = getattr(self, "_bundle_record", None)
        if record is not None:
            record["pixels"] = [value(image, "width"), value(image, "height")]
            record["dpr"] = value(image, "devicePixelRatio")
            image.setText("grablab", json.dumps(record, ensure_ascii=False, sort_keys=True))
        image.setDotsPerMeterX(value(image, "dotsPerMeterX") * value(image, "devicePixelRatio"))
        image.setDotsPerMeterY(value(image, "dotsPerMeterY") * value(image, "devicePixelRatio"))
        image.setText("Title", title)
        image.setText("Description", description)
        saved = image.save(path)
        return path if saved and path.is_file() else None

    @with_capture_preferences
    def getWidgetSVG(self, widget: Any, path: Any, title: Any="", description: Any="") -> Any:
        tmp = self.tmpPath(suffix=".svg")
        path = self.path(path)
        if path.exists():
            raise FileExistsError(path)
        svg_gen = QSvgGenerator()
        svg_io = QBuffer()
        svg_gen.setSize(widget.size)
        svg_gen.setViewBox(widget.rect)
        svg_gen.setTitle(title)
        svg_gen.setDescription(description)
        svg_gen.setOutputDevice(svg_io)
        #svg_gen.setFileName(tmp)
        widget.render(svg_gen)
        svg = svg_io.data().data().decode("utf-8")
        tmp.write_text(svg, encoding="utf-8")
        self.optimizeSVG(tmp, title, description)
        if getattr(self, "_bundle_record", None) is not None:
            embed_svg(tmp, self._bundle_record)
        return shutil.move(tmp, self.path(path)) if self.path(tmp).is_file() else None

    def optimizeSVG(self, path: Any, title: Any="", description: Any="", *, restyle: bool=False) -> Any:
        if not self.path(path).is_file():
            return
        root = ET.parse(path).getroot()
        if "viewBox" in root.attrib:
            x0, y0, width, height = root.attrib["viewBox"].split()
            root.attrib["width"] = width
            root.attrib["height"] = height
        if title:
            el = root.find(f"./{{{svg_ns}}}title")
            if el is None:
                el = ET.SubElement(root, f"{{{svg_ns}}}title")
            el.text = title
        if description:
            el = root.find(f"./{{{svg_ns}}}desc")
            if el is None:
                el = ET.SubElement(root, f"{{{svg_ns}}}desc")
            el.text = description
        for el in root.findall(".//*[@font-family='.AppleSystemUIFont']"):
            if restyle:
                el.attrib["font-family"] = "system-ui"
        for el in root.findall(".//*[@stroke-width='1']"):
            if restyle:
                el.attrib["stroke-width"] = "0.75"
        svg = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        with open(self.path(path), "w", encoding="utf-8") as f:
            f.write(svg)

    def newGrab(self) -> Any:
        self.timestamp = f"{timestamp()}"
        if font := CurrentFont():
            self.grab_suffix = f"_{slugify(Path(font.path).stem)}"
        else:
            self.grab_suffix = ""
        self.grab_subfolder = (
            f"{self.pref.naming_prefix}{self.timestamp}{self.grab_suffix}"
        )
        self.grab_folder = self.path(
            Path(self.getBaseFolder(), self.grab_subfolder), folder=True
        )

    @with_capture_preferences
    def grabScreenPNG(self, screen: Any, screenid: Any) -> Any:
        paths = self._grabScreen(screen, screenid, formats=("png",))
        return next((path for path in paths if path.suffix == ".png"), None)

    def _exportRecord(self, target: Path, kind: str, size: list) -> dict:
        """Describe non-widget image frames without inventing Designer controls."""
        return {"manifest": {"tool": "grablab", "version": 2, "build": "", "units": "Logical image frame, origin top-left; pixels / size maps to raster"},
            "shot": 1, "target": kind, "root": kind, "scope": kind, "class": "",
            "title": target.stem, "titlebar": False, "file": target.name, "size": size,
            "pixels": None, "dpr": None, "colorspace": "unknown", "theme": "unknown", "background": None,
            "state": "", "note": "", "parts": [], "opened_from": "", "popup_parent": "", "opener": {},
            "context": {"window": "", "checked": [], "outside": {}, "reaches": {}},
            "taken": time.strftime("%Y-%m-%d %H:%M:%S"), "rects": {}, "texts": {}, "x_ray": False, "nodes": [],
            "extensions": {"schema": "grablab.capture/1", "capture_kind": kind, "widgets": [], "truncated": False,
                "limits": ["No QWidget semantics or Designer UI for this export; no document mutation"]}}

    def _publishBundle(self, target: Path, paths: list, record: dict, *, designer: bool=False) -> list:
        """Reuse staged exclusive links and roll back only this bundle's links."""
        sidecar = self._bundle_base.with_suffix(".json")
        sidecar.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        sources = list(paths) + [sidecar]
        if designer:
            ui = self._bundle_base.with_suffix(".ui")
            ui.write_text(ui_xml(record), encoding="utf-8")
            sources.append(ui)
        published = []
        try:
            for source in sources:
                destination = target.with_suffix(source.suffix)
                os.link(source, destination)
                published.append(destination)
        except BaseException:
            for path in published:
                path.unlink()
            raise
        return [path for path in published if path.suffix in (".png", ".svg")]

    @with_capture_preferences
    def _grabScreen(self, screen: Any, screenid: Any, *, formats: Any=None) -> list:
        formats = formats if formats is not None else tuple(fmt for fmt in ("png", "svg") if getattr(self.pref, "grab_" + fmt))
        if not formats:
            return []
        target = self.getGrabPath(f"sc{screenid}{self.dark}", formats[0])
        geometry = value(screen, "geometry")
        size = [value(geometry, "width"), value(geometry, "height")]
        if not all(isinstance(n, (int, float)) and math.isfinite(n) and n > 0 for n in size):
            raise ValueError("Screen geometry requires a positive logical size")
        record = self._exportRecord(target, "screen-raster", size)
        record["extensions"].update(representation="raster-backed SVG wrapper", screen_name=value(screen, "name", ""),
            desktop_geometry=[value(geometry, "x"), value(geometry, "y"), *size])
        record["extensions"]["limits"].append("Screen SVG embeds one actual screen raster; it is not desktop vectorization")
        with tempfile.TemporaryDirectory(dir=self.grab_folder) as folder:
            self._bundle_base, self._bundle_record = Path(folder) / target.name, record
            try:
                png = self._bundle_base.with_suffix(".png")
                if self.getPixmapPNG(screen.grabWindow(0), png, target.stem, f"Screen {screenid}") is None:
                    return []
                paths = [png] if "png" in formats else []
                if "svg" in formats:
                    width, height = size
                    root = ET.Element(f"{{{svg_ns}}}svg", width=str(width), height=str(height), viewBox=f"0 0 {width} {height}")
                    ET.SubElement(root, f"{{{svg_ns}}}title").text = target.stem
                    ET.SubElement(root, f"{{{svg_ns}}}desc").text = "Raster-backed screen capture; not a vectorized desktop"
                    ET.SubElement(root, f"{{{svg_ns}}}image", {"x": "0", "y": "0", "width": str(width), "height": str(height), "preserveAspectRatio": "none",
                        "{http://www.w3.org/1999/xlink}href": "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode("ascii")})
                    svg = self._bundle_base.with_suffix(".svg")
                    ET.ElementTree(root).write(svg, encoding="utf-8", xml_declaration=True)
                    embed_svg(svg, record)
                    paths.append(svg)
                return self._publishBundle(target, paths, record)
            finally:
                del self._bundle_base
                del self._bundle_record

    def grabScreens(self, screens: Any = None) -> Any:
        paths = []
        for screenid, screen in enumerate(self.app.qapp.screens()):
            if (
                len(self.pref.grab_screens_only)
                and screenid not in self.pref.grab_screens_only
            ):
                continue
            elif (
                screens
                and screenid not in screens
            ):
                continue
            paths.extend(self._grabScreen(screen, f"{screenid}"))
        return paths

    def grabWidgetPNG(self, widget: Any, abbrtype: Any, name: Any, descriptor: Any="") -> Any:
        if getattr(self, "_bundle_base", None) is None:
            paths = self.grabWidget(widget, abbrtype, name, descriptor, _formats=("png",))
            return next((path for path in paths if path.suffix == ".png"), None)
        grab_path = self.getGrabPath(f"{abbrtype}{self.dark}_{name}", "png")
        if path := self.getPixmapPNG(
            widget.grab(),
            grab_path,
            title=grab_path.stem,
            description=f"{descriptor}: {name}",
        ):
            return path
        else:
            return None

    def grabWidgetSVG(self, widget: Any, abbrtype: Any, name: Any, descriptor: Any="") -> Any:
        if getattr(self, "_bundle_base", None) is None:
            paths = self.grabWidget(widget, abbrtype, name, descriptor, _formats=("svg",))
            return next((path for path in paths if path.suffix == ".svg"), None)
        grab_path = self.getGrabPath(f"{abbrtype}{self.dark}_{name}", "svg")
        if path := self.getWidgetSVG(
            widget,
            grab_path,
            title=grab_path.stem,
            description=f"{descriptor}: {name}",
        ):
            return path
        else:
            return None

    @with_capture_preferences
    def grabWidget(self, widget: Any, abbrtype: Any, name: Any, descriptor: Any="", *, _formats: Any=None) -> Any:
        if not widget:
            return []
        target = self.getGrabPath(f"{abbrtype}{self.dark}_{name}", "png")
        formats = _formats if _formats is not None else tuple(fmt for fmt in ("png", "svg") if getattr(self.pref, "grab_" + fmt))
        record = snapshot(widget, target.stem, target.with_suffix("." + (formats[0] if formats else "png")).name)
        # Stage a complete bundle; exclusive links never replace another capture.
        with tempfile.TemporaryDirectory(dir=self.grab_folder) as folder:
            self._bundle_base = Path(folder) / target.name
            self._bundle_record = record
            try:
                paths = []
                if "png" in formats:
                    path = self.grabWidgetPNG(widget, abbrtype, name, descriptor)
                    if path is None:
                        return []
                    paths.append(Path(path))
                if "svg" in formats:
                    path = self.grabWidgetSVG(widget, abbrtype, name, descriptor)
                    if path is None:
                        return []
                    paths.append(Path(path))
                if not paths:
                    return []
                return self._publishBundle(target, paths, record, designer=True)
            finally:
                del self._bundle_base
                del self._bundle_record

    def _renderCanvasPNG(self, source: Path, destination: Path) -> Any:
        """Rasterize this exact exported SVG with owned, bounded Qt objects."""
        from PythonQt.QtCore import QRectF
        from PythonQt.QtGui import QImage, QPainter
        from PythonQt.QtSvg import QSvgRenderer
        renderer = QSvgRenderer(str(source))
        try:
            if not value(renderer, "isValid", False):
                raise ValueError("Invalid exported canvas SVG")
            width, height = self._bundle_record["pixels"]
            image = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
            if value(image, "isNull", True):
                raise MemoryError("Cannot allocate canvas PNG")
            image.fill(0)
            painter = QPainter()
            try:
                if not painter.begin(image):
                    raise RuntimeError("Cannot paint canvas PNG")
                renderer.render(painter, QRectF(0, 0, width, height))
            finally:
                painter.end()
            return self._saveImagePNG(image, destination, source.stem, "Canvas SVG rasterization")
        finally:
            renderer.deleteLater()

    def _grabCanvasBundle(self, name: str) -> list:
        formats = tuple(fmt for fmt in ("png", "svg") if getattr(self.pref, "grab_" + fmt))
        if not formats:
            return []
        target = self.getGrabPath(name, formats[0])
        with tempfile.TemporaryDirectory(dir=self.grab_folder) as folder:
            source = Path(folder) / target.with_suffix(".svg").name
            if self.getCanvasSVG(source, title=target.stem, description=f"Glyph canvas export: {name}") is None:
                return []
            viewbox = [float(n) for n in ET.parse(source).getroot().attrib["viewBox"].replace(",", " ").split()]
            if len(viewbox) != 4 or not all(math.isfinite(n) for n in viewbox) or min(viewbox[2:]) <= 0:
                raise ValueError("Canvas SVG requires a finite positive viewBox")
            record = self._exportRecord(target, "canvas-export", viewbox[2:])
            record["extensions"].update(source_viewBox=viewbox, representation="native workspace vector export",
                frame_mapping={"source_origin": viewbox[:2], "logical_size": viewbox[2:], "raster_scale": None})
            if "png" in formats:
                record["pixels"] = [math.ceil(n) for n in viewbox[2:]]
                record["dpr"] = 1.0
                record["extensions"]["frame_mapping"]["raster_scale"] = [record["pixels"][i] / viewbox[i + 2] for i in (0, 1)]
            self._bundle_base, self._bundle_record = source, record
            try:
                embed_svg(source, record)
                paths = []
                if "png" in formats:
                    png = source.with_suffix(".png")
                    if self._renderCanvasPNG(source, png) is None:
                        return []
                    paths.append(png)
                if "svg" in formats:
                    paths.append(source)
                return self._publishBundle(target, paths, record)
            finally:
                del self._bundle_base
                del self._bundle_record

    @with_capture_preferences
    def grabCanvas(self) -> Any:
        paths = []
        original_dark = self.app.pref.generalDarkGlyph
        for name, alternative, dark in (("gc", False, False), ("gca", True, False), ("gd", False, True), ("gad", True, True)):
            if self.dark:
                self.app.pref.generalDarkGlyph = not original_dark if dark else original_dark
            if alternative and (self.pref.grab_svg or self.pref.grab_png):
                with alternative_view(self.app.ui.menu.view.alternative_view):
                    paths.extend(self._grabCanvasBundle(name))
            else:
                paths.extend(self._grabCanvasBundle(name))
        self.app.pref.generalDarkGlyph = original_dark
        if self.pref.grab_pdf:
            grab_path = self.getGrabPath("gc", "pdf")
            if path := self.getCanvasPDF(grab_path):
                paths.append(path)

        return paths

    def grabPanel(self, name: Any, force_visible: Any=False) -> Any:
        paths = []
        panel = self.app.ui.panels[name]
        widget = panel.widget
        if widget:
            if widget.visible or force_visible:
                if (
                    widget.parentWidget()
                    and widget.parentWidget().className() == "QStackedWidget"
                ):
                    widget = widget.parentWidget()
                if (
                    widget.parentWidget()
                    and widget.parentWidget().className() == "YTabWidget"
                ):
                    widget = widget.parentWidget()
                if (
                    widget.parentWidget()
                    and widget.parentWidget().className() == "YPanel"
                ):
                    widget = widget.parentWidget()
                paths.extend(self.grabWidget(widget, "p", name, f"{name} panel"))
        return paths

    def grabPanels(self, force_visible: Any=False) -> Any:
        paths = []
        for name in self.app.ui.panels.keys():
            if name not in ["font_map", "toolbar"]:
                paths.extend(self.grabPanel(name, force_visible))
        return paths

    def grabGlyphWindows(self) -> Any:
        paths = []
        for title, widget in self.app.ui.glyphWindows().items():
            if widget.visible or self.pref.grab_also_invisible:
                name = "_".join(
                    [slugify(part.strip()) for part in reversed(title.split("@"))]
                )
                paths.extend(
                    self.grabWidget(
                        GlyphWindow(widget, self.app.ws).viewport,
                        "gv", name, "Glyph window viewport"
                    )
                )
                paths.extend(self.grabWidget(widget, "gw", name, "Glyph window"))
        return paths

    def grabMenu(self, menu: Any, text: Any) -> Any:
        paths = []
        paths.extend(self.grabWidget(menu, "m", text, f"Menu: {text}"))
        for action in native_list(menu, "actions"):
            if action.isVisible() and action.menu():
                name = f"{slugify(text)}_{slugify(action.text)}"
                paths.extend(self.grabMenu(action.menu(), name))
        return paths

    def grabMainMenu(self) -> Any:
        paths = []
        for qmenu in native_list(self.app.ui.qmenus, "children"):
            if isinstance(qmenu, QMenu):
                name = f"{slugify(qmenu.title)}"
                paths.extend(self.grabMenu(qmenu, name))
        return paths

    def grabFontWindows(self) -> Any:
        paths = []
        for title, widget in self.app.ui.fontWindows().items():
            if widget.visible or self.pref.grab_also_invisible:
                paths.extend(
                    self.grabWidget(widget, "fw", slugify(title), "Font window")
                )
        return paths

    @with_capture_preferences
    def grabAll(self) -> Any:
        self.newGrab()
        paths = []
        if self.pref.grab_canvas:
            paths.extend(self.grabCanvas())
        if self.pref.grab_glyph_windows:
            paths.extend(self.grabGlyphWindows())
        if self.pref.grab_font_windows:
            paths.extend(self.grabFontWindows())
        if self.pref.grab_panels:
            paths.extend(self.grabPanels())
        if self.pref.grab_menu:
            paths.extend(self.grabMainMenu())
        if self.pref.grab_toolbar:
            paths.extend(self.grabPanel("toolbar"))
        if self.pref.grab_screens:
            paths.extend(self.grabScreens())
        return paths


if __name__ == "__main__":
    # from grablab.grab import Grab
    app = Application()
    Grab().grabAll()
    grab = Grab(grab_also_invisible=True, grab_screens_only=[0])
    grab.newGrab()
    grabbed = grab.grabCanvas() + grab.grabPanel("elements") + grab.grabScreens()
    print(f"Saved {len(grabbed)} files in {grab.getBaseFolder()}")
