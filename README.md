---
this_file: README.md
---

# GrabLab

Install `fontlab-grablab` for the `grablab` namespace, alongside
`fontlab-fontlabapp`. Python 3.11+ and native FontLab APIs are required for capture.
Importing `grablab` itself is host-free; requesting Grab loads native APIs.

```python
from grablab import Grab
capture = Grab(grab_canvas=False, grab_screens=False)
capture.newGrab()
paths = capture.grabPanel("elements")
```

Screenshots, native widget SVG, canvas SVG/PDF, panels, menus, glyph/font windows
and screen capture retain the source interfaces. An optional
`Grab(application=app, **preferences)` reuses an existing context, useful for
controlled capture and temporary preference-library paths.

Construction no longer alters rendering preferences or opens a confirmation
dialog. Actual capture calls temporarily adjust OpenGL, outline thickness and
pixel rendering, then restore them and the dark-glyph preference even on failure.
Alternative-view exports pair their view toggles in finally blocks. Explicit
`setAppPrefs()` applies settings directly; use capture methods for restoration.
The preference library still saves GrabLab configuration when explicitly used.

A failed QImage.save returns None even when a stale target exists. Filename
collisions are handled iteratively, including existing directories. Menu
capture returns all submenu paths. Failed screen saves are omitted from returned
artifact lists. PNG and SVG preserve title/description metadata. `optimizeSVG(..., restyle=True)`
explicitly opts into the old font/stroke substitutions; raw capture preserves them.

```sh
# Install the sibling dependency locally (arm64 Python 3.11, as in FontLab):
uv venv --python cpython-3.11-macos-aarch64-none
uv pip install -e ../fontlab-fontlabapp -e '.[test]'
./test.sh
uv build
```

`./test.sh` runs with `--no-sync`, so create this environment first.

Seven regression tests verify stale-file failure, many collisions, submenu
aggregation, preference restoration, alternative-view failure and SVG metadata.
Installed native smoke verifies a hidden QWidget PNG/SVG capture, actual
ApplicationUI, metadata, and restoration after a deliberately failed capture.
Test files/windows are removed; open fonts and persistent user preferences are
untouched. Whole-desktop capture, open-font canvas export and every panel/window
configuration remain later integration checks.

Both source files and BSD-3-Clause licenses are retained and tracked in
MIGRATION.json. Versions derive from Git tags through hatch-vcs. Source originals
remain preserved until migration acceptance. See WORK.md for evidence.

## Status

Issue 101 migration is complete and released as verified v0.2.0 (RELEASE.md): both
original sources and licences migrated with hashes, wheel/sdist installs, native
PNG/SVG capture of hidden widgets and FontLab windows, and rendering-preference
restoration verified in FontLab. All three v0.2.0 project iterations passed.

## Issue 131 capture bundles

`grabWidget`, panel/window/menu captures, and standalone `grabWidgetPNG` /
`grabWidgetSVG` reserve one basename across `.png`, `.svg`, `.json` and `.ui`.
Image names no longer append physical pixel dimensions, so DPR 2 PNG and logical
SVG stay paired. Existing image-only path list returns (and single-path methods)
remain compatible; discover additive sidecars with `path.with_suffix(".json")`
and `path.with_suffix(".ui")`. The enabled image formats remain configurable.
A failed image or sidecar aborts the bundle; exclusive publication never replaces
existing files and rolls back this capture's published members on failure.

JSON uses the FontSnap version-2 field shapes with `manifest.tool="grablab"` and
`extensions.schema="grablab.capture/1"`; this describes compatibility, not
FontSnap authorship or an identical capture policy. Identical records are embedded
in PNG text key `grablab` and SVG `<metadata id="grablab-metadata">`.
`size`, `rects`, and widget coordinates are logical units; `pixels` records actual
PNG dimensions and `dpr` its device ratio. Use `pixels / size` per axis for
fractional-scale mapping. SVG-only captures leave raster measurements null.

`extensions.widgets` records the bounded visible QWidget hierarchy (at most 2,000
widgets), root-relative `rect`, parent-relative `geometry`, original semantic
statusTip/objectName, unique XML-safe `id`, allowlisted control content, and local
action associations. The `.ui` is Qt Designer XML with runtime geometry/content;
JSON retains details unsuitable for Designer. Separate child windows, hidden
children, models and arbitrary Qt properties are never traversed. The root may
be hidden for owned test captures; descendants use `isVisibleTo(root)` so explicitly
shown children painted by `render()` remain represented. Password text is omitted; other editable
content is captured and may contain document data. No source code is copied
from FontSnap.

Runtime capture cannot recreate layouts, signal connections, custom painting or
icon resources. Original custom widget plugins are needed to load their classes.
Coordinates describe widget rectangles, including portions clipped by ancestors;
they do not prove pixel ownership. Directly owned named actions absent from
rectangles populate `context.outside`; remote `reaches`, opener, build, theme and
background stay explicitly unknown where unmeasured. Truncation and limitations
are disclosed in JSON and the UI comment. Low-level canvas/screen exports retain
their existing surfaces; full widget sidecars belong to widget capture methods.
Native artifact and runtime acceptance of this new bundle is pending.

Designer content uses writable properties for known standard controls; read-only
progress/spin display text and unknown-class content remain in JSON. Numeric
ranges/precision precede values, and checkable precedes the deduplicated checked
property. QMenu/QMenuBar actions have their visible, nonempty rectangles measured
only when wholly inside the widget and captured image; hidden/null/clipped owned
actions stay outside. Designer action/addaction elements preserve supported
QAction labels/state; submenu structure and signal wiring remain runtime-only.
