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
uv pip install -e ../fontlab-fontlabapp -e '.[test,svg]'
./test.sh
uv build
```

`./test.sh` uses `--no-sync`; create the environment first.
The issue 131 suite has 122 tests. Ordinary-wheel capture in FontLab 9.0.9794
verified actual Font/Glyph windows, canvas and four panels, paired metadata, DPR2
and preference restoration. Four public grabCanvas variants also passed native
PNG/SVG/JSON checks; six actual Designer files passed Qt5 uic. An owned CC0 sample
was closed afterward with its source unchanged. Whole-desktop capture and every
panel/window configuration remain separate integration checks.

Migration provenance/licences are in MIGRATION.json; verification is in WORK.md.
Versions derive from Git tags through hatch-vcs.

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
fractional-scale mapping. Widget SVG-only captures leave raster measurements null.

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
are disclosed in JSON and the UI comment. Native SVG/PDF primitives retain their
existing interfaces; high-level non-widget bundles are described below.
Issue 131 ordinary-artifact and owned native acceptance is recorded in WORK.md.

Designer content uses writable properties for known standard controls; read-only
progress/spin display text and unknown-class content remain in JSON. Numeric
ranges/precision precede values, and checkable precedes the deduplicated checked
property. QMenu/QMenuBar actions have their visible, nonempty rectangles measured
only when wholly inside the widget and captured image; hidden/null/clipped owned
actions stay outside. Designer action/addaction elements preserve supported
QAction labels/state; submenu structure and signal wiring remain runtime-only.

## Screen and canvas bundles

`grabScreens()` respects the screen-selection and PNG/SVG flags, captures each
chosen screen once, and publishes requested images plus one JSON sidecar under
a shared basename. Its SVG embeds that same PNG in logical screen coordinates:
`extensions.capture_kind="screen-raster"` explicitly discloses a raster-backed
representation, not desktop vectorization. Actual PNG pixels/DPR and desktop
geometry are retained. SVG-only still embeds a temporary PNG; it publishes no
standalone PNG. `grabScreenPNG` retains its single PNG-path/None interface.

`grabCanvas()` keeps its four native workspace vector variants and optional PDF.
Each enabled PNG renders the exact paired SVG through Qt QSvgRenderer into an
owned QImage, with transparent initialization and guaranteed painter cleanup.
`extensions.capture_kind="canvas-export"`, `source_viewBox` and `frame_mapping`
describe the native vector frame, logical dimensions and raster scale. PNG uses
DPR1 at ceil(viewBox width/height); it does not claim correspondence to another
editor viewport. PNG-only keeps its source SVG temporary; SVG-only skips rendering.

These non-widget captures have empty semantic records and no fabricated `.ui`.
They reuse exclusive staged publication, collision checks and failure rollback;
rendering preferences and alternative/dark toggles restore on failure. Return
lists still contain only image paths (plus the existing optional PDF). Source
tests alone do not qualify native behavior. The four canvas variants were also
checked in FontLab 9.0.9794; whole-desktop capture remains unqualified.

## Host-free SVG processing

Install `fontlab-grablab[svg]` outside FontLab for postprocessing. Pillow decodes
PNG pixels; pure-Python svgelements measures transformed SVG geometry. Neither
dependency loads during native capture or ordinary `import grablab`.

```python
import json
from pathlib import Path
from grablab import svg

root = svg.read_svg("panel.svg")
index = svg.build_raster_index("assets-manifest.json", source_dirs=["source-pngs"])
mapping = svg.map_images(root, index)  # JSON-serializable URI -> candidates/status
stats = {"inline": svg.inline_images(root, mapping)}
stats["widgets"] = svg.tag_widgets(root, json.loads(Path("panel.json").read_text()))
svg.write_svg(root, "panel-processed.svg")  # refuses any existing output
svg.restyle(root, wireframe=True, background="white")
svg.write_svg(root, "panel-wireframe.svg")
```

Every data URI must match known decoded PNG dimensions and 8-bit premultiplied
RGBa pixels exactly. This preserves Qt's rendered pixels despite lossy PNG
unpremultiplication at translucent edges; it is not fuzzy or alpha-only matching.
Index schema 2 records `pixel_format="RGBa8"`; rebuild older indexes before use.
Candidates disclose `match="pixel-exact"` for exported
PNG matches and `match="source-name"` for authoritative source PNGs associated by
unique original asset name (only `@2x` is normalized). The latter preserves
provenance but does not claim the new vector renders exactly like the old PNG.
Multiple distinct SVG candidates are ambiguous and stay rasterized; unknown,
unsupported and malformed images also remain untouched. Retain mapping and index
JSON as receipts; paths may contain local/private information.

Nested SVGs retain image viewport/aspect ratio, ancestor transforms and clipping;
local IDs, fragment/url references and CSS classes are namespaced. `tag_widgets`
tags original elements in place using transformed bounds and the smallest
containing `extensions.widgets[].rect`, preserving paint order and existing IDs.
Equal-area ties require one proven descendant through the recorded parent chain;
otherwise elements stay untagged, with sorted candidate IDs in ambiguity stats.
New IDs derive from widget IDs; `data-widget` records the exact widget identity.
Text uses its transformed anchor, disclosed by `data-widget-method="text-anchor"`,
rather than invented font metrics. Bounds containment is approximate ownership:
clipping, text extents, use-instance ownership and arbitrary CSS are not inferred.
Unsupported/unmatched counts and limits remain in returned stats.

`compose([(path, x, y), ...], width=..., height=...)` uses explicit logical
positions, input paint order, source viewBox sizes and collision-free local IDs.
`restyle` changes stroke/fill/width/background/font (`system-ui` by default),
including inline CSS. Documents containing `<mask>` are refused before any
mutation, including font-only changes: inherited paint and text geometry affect
mask opacity. Wireframe keeps readable monochrome text and outlines on opaque surfaces.
Monochrome applies a root grayscale filter, preserving luminance and existing
filter effects. It refuses author stylesheets, important root filters and CSS-wide
root-filter values before mutation. Wireframe alone wraps retained rasters with
grayscale groups; combining rasters with author stylesheets is refused because
wrapping can change selectors. Stylesheet-only vector inputs remain supported
for wireframe and ordinary restyling. Image bytes/geometry remain intact;
filtered_images reports the affected raster count. CSS grayscale needs a
supporting SVG renderer.
Ordinary color changes preserve effective `none` from presentation attributes,
class/ID CSS and inline styles using specificity, source order, inheritance and
`!important`. Conditional stylesheet rules and unresolved contextual paints fail
before mutation. cssselect2/tinycss2 provide the selector and declaration parsing.
External resources, global CSS selectors and `!important` rules need separate
review; helpers target trusted Qt captures and the known Illustrator assets.

Optional `deduplicate_paths` removes only consecutive identical opaque fill-only
paths without IDs, strokes or inherited opacity/effects. Repeated antialiased
edges can differ; compare processed renders or leave cleanup disabled when exact
pixels matter. Raw inputs remain separate. Host-free tests and asset indexing do
not establish native screenshot fidelity.
