---
this_file: DEPENDENCIES.md
---

# Dependencies

- hatchling and hatch-vcs: standard builds and Git-tag versioning.
- pytest: regression tests; native host checks run separately.
- fontlab-fontlabapp >=1.2.0: application/UI/preferences and the supported
  `qt.views.GlyphWindow` viewport adapter, including named-child lookup.
- Source installation explicitly requests `pyobjc-framework-Quartz>=10;
  sys_platform == 'darwin'` for the macOS F5/F6 hotkey script. App retains its
  optional `hotkeys` extra; the linked installer metadata writes Requires-Dist
  without optional dependency/Provides-Extra metadata, so the explicit override
  is needed. The library-only wheel does not activate that script or require Quartz.
- `install.vfpy` detects dependency presence by distribution name only. Missing
  dependencies are passed unchanged to uv, which resolves their versions/markers;
  present but too-old versions can be skipped, and marker-false missing packages
  can trigger unnecessary uv invocation. Full installed-version/marker enforcement
  remains separate work. Without uv, missing requirements are reported as guidance.
- Native PythonQt QtGui/QtSvg/Qt and FontLab: supplied by the host for capture.
- Standard pathlib, tempfile and ElementTree: existing file/SVG implementation.
- Optional `svg` extra: Pillow >=10 decodes PNGs into exact8-bit premultiplied RGBa pixel keys;
  svgelements >=1.9.6 supplies maintained pure-Python SVG path/shape/transform
  bounds, avoiding a custom geometry parser or NumPy/SciPy dependency. Both are
  also test dependencies and are imported lazily only by postprocessing helpers.
- Optional `svg`/test extras also include cssselect2 >=0.8 and tinycss2 >=1.4:
  maintained pure-Python selector matching and CSS parsing for paint specificity,
  source order, importance and inheritance. Avoid a custom CSS parser and preserve
  CSS-defined `none` during ordinary recoloring; capture does not import them.
