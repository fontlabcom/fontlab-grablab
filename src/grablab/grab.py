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

import shutil
import json
import os

from .snapshot import snapshot, ui_xml, free_bundle, embed_svg, native_list
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Iterator
import tempfile
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from fontlab import CurrentFont
from fontlabapp import Application
from fontlabapp.utils import attribdict as adict, slugify, timestamp
from PythonQt.QtGui import QMessageBox, QMenu
from PythonQt.QtSvg import QSvgGenerator
from PythonQt.Qt import QBuffer

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
        self.app.ws.exportTo(tmp, "SVG")
        self.optimizeSVG(tmp, title, description)
        return shutil.move(tmp, self.path(path)) if self.path(tmp).is_file() else None

    @with_capture_preferences
    def getCanvasPDF(self, path: Any, title: Any="", description: Any="") -> Any:
        tmp = self.tmpPath(suffix=".pdf")
        self.app.ws.exportTo(tmp, "PDF")
        return shutil.move(tmp, self.path(path)) if self.path(tmp).is_file() else None

    @with_capture_preferences
    def getPixmapPNG(self, pixmap: Any, path: Any, title: Any="", description: Any="") -> Any:
        image = pixmap.toImage()
        path = self.path(path)
        if path.exists():
            raise FileExistsError(path)
        record = getattr(self, "_bundle_record", None)
        if record is not None:
            record["pixels"] = [image.width(), image.height()]
            record["dpr"] = image.devicePixelRatio()
            image.setText("grablab", json.dumps(record, ensure_ascii=False, sort_keys=True))
        image.setDotsPerMeterX(image.dotsPerMeterX() * image.devicePixelRatio())
        image.setDotsPerMeterY(image.dotsPerMeterY() * image.devicePixelRatio())
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
        grab_path = self.getGrabPath(f"sc{screenid}{self.dark}", "png")
        x = screen.geometry.x()
        y = screen.geometry.y()
        width = screen.geometry.width()
        height = screen.geometry.height()

        path = self.getPixmapPNG(
            screen.grabWindow(0, x, y, width, height),
            grab_path,
            title=grab_path.stem,
            description=f"Screen {screenid}: {screen.name}",
        )

        return path

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
            if path := self.grabScreenPNG(screen, f"{screenid}"):
                paths.append(path)
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
        published = []
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
                sidecar = self._bundle_base.with_suffix(".json")
                sidecar.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
                ui = self._bundle_base.with_suffix(".ui")
                ui.write_text(ui_xml(record), encoding="utf-8")
                paths.extend([sidecar, ui])
                for source in paths:
                    destination = target.with_suffix(source.suffix)
                    os.link(source, destination)
                    published.append(destination)
                return [path for path in published if path.suffix in (".png", ".svg")]
            except BaseException:
                for path in published:
                    path.unlink()
                raise
            finally:
                del self._bundle_base
                del self._bundle_record

    @with_capture_preferences
    def grabCanvas(self) -> Any:
        paths = []

        if self.pref.grab_svg:
            grab_path = self.getGrabPath("gc", "svg")
            if path := self.getCanvasSVG(
                grab_path,
                title=grab_path.stem,
                description=f"Glyph canvas: {grab_path.stem}",
            ):
                paths.append(path)
            with alternative_view(self.app.ui.menu.view.alternative_view):
                grab_path = self.getGrabPath("gca", "svg")
                if path := self.getCanvasSVG(
                    grab_path,
                    title=grab_path.stem,
                    description=f"Glyph canvas alternative: {grab_path.stem}",
                ):
                    paths.append(path)

        if self.dark:
            self.app.pref.generalDarkGlyph = not self.app.pref.generalDarkGlyph

        if self.pref.grab_svg:
            grab_path = self.getGrabPath("gd", "svg")
            if path := self.getCanvasSVG(
                grab_path,
                title=grab_path.stem,
                description=f"Glyph dark canvas: {grab_path.stem}",
            ):
                paths.append(path)
            with alternative_view(self.app.ui.menu.view.alternative_view):
                grab_path = self.getGrabPath("gad", "svg")
                if path := self.getCanvasSVG(
                    grab_path,
                    title=grab_path.stem,
                    description=f"Glyph dark canvas alternative: {grab_path.stem}",
                ):
                    paths.append(path)

        if self.dark:
            self.app.pref.generalDarkGlyph = not self.app.pref.generalDarkGlyph

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
                        widget.widgetViewport, "gv", name, "Glyph window viewport"
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
