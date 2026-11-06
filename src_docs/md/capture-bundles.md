---
this_file: src_docs/md/capture-bundles.md
---

# Capture bundles

## Issue 131 capture bundles

`grabWidget`, panel/window/menu captures, and standalone `grabWidgetPNG` / `grabWidgetSVG` reserve one basename across
`.png`, `.svg`, `.json` and `.ui`. Image names no longer append physical pixel dimensions, so DPR 2 PNG and logical SVG
stay paired. Existing image-only path list returns (and single-path methods) remain compatible; discover additive
sidecars with `path.with_suffix(".json")` and `path.with_suffix(".ui")`. The enabled image formats remain configurable.
A failed image or sidecar aborts the bundle; exclusive publication never replaces existing files and rolls back this
capture's published members on failure.

JSON uses the FontSnap version-2 field shapes with `manifest.tool="grablab"` and
`extensions.schema="grablab.capture/1"`; this describes compatibility, not FontSnap authorship or an identical capture
policy. Identical records are embedded in PNG text key `grablab` and SVG `<metadata id="grablab-metadata">`. `size`,
`rects`, and widget coordinates are logical units; `pixels` records actual PNG dimensions and `dpr` its device ratio.
Use `pixels / size` per axis for fractional-scale mapping. Widget SVG-only captures leave raster measurements null.

`extensions.widgets` records the bounded visible QWidget hierarchy (at most 2,000 widgets), root-relative `rect`,
parent-relative `geometry`, original semantic statusTip/objectName, unique XML-safe `id`, allowlisted control content,
and local action associations. The `.ui` is Qt Designer XML with runtime geometry/content; JSON retains details
unsuitable for Designer. Separate child windows, hidden children, models and arbitrary Qt properties are never
traversed. The root may be hidden for owned test captures; descendants use `isVisibleTo(root)` so explicitly shown
children painted by `render()` remain represented. Password text is omitted; other editable content is captured and may
contain document data. No source code is copied from FontSnap.

Runtime capture cannot recreate layouts, signal connections, custom painting or icon resources. Original custom widget
plugins are needed to load their classes. Coordinates describe widget rectangles, including portions clipped by
ancestors; they do not prove pixel ownership. Directly owned named actions absent from rectangles populate
`context.outside`; remote `reaches`, opener, build, theme and background stay explicitly unknown where unmeasured.
Truncation and limitations are disclosed in JSON and the UI comment. Native SVG/PDF primitives retain their existing
interfaces; high-level non-widget bundles are described below. Issue 131 ordinary-artifact and owned native acceptance
is recorded in WORK.md.

Designer content uses writable properties for known standard controls; read-only progress/spin display text and
unknown-class content remain in JSON. Numeric ranges/precision precede values, and checkable precedes the deduplicated
checked property. QMenu/QMenuBar actions have their visible, nonempty rectangles measured only when wholly inside the
widget and captured image; hidden/null/clipped owned actions stay outside. Designer action/addaction elements preserve
supported QAction labels/state; submenu structure and signal wiring remain runtime-only.

## Screen and canvas bundles

`grabScreens()` respects the screen-selection and PNG/SVG flags, captures each chosen screen once, and publishes
requested images plus one JSON sidecar under a shared basename. Its SVG embeds that same PNG in logical screen
coordinates: `extensions.capture_kind="screen-raster"` explicitly discloses a raster-backed representation, not desktop
vectorization. Actual PNG pixels/DPR and desktop geometry are retained. SVG-only still embeds a temporary PNG; it
publishes no standalone PNG. `grabScreenPNG` retains its single PNG-path/None interface.

`grabCanvas()` keeps its four native workspace vector variants and optional PDF. Each enabled PNG renders the exact
paired SVG through Qt QSvgRenderer into an owned QImage, with transparent initialization and guaranteed painter cleanup.
`extensions.capture_kind="canvas-export"`, `source_viewBox` and `frame_mapping` describe the native vector frame,
logical dimensions and raster scale. PNG uses DPR1 at ceil(viewBox width/height); it does not claim correspondence to
another editor viewport. PNG-only keeps its source SVG temporary; SVG-only skips rendering.

These non-widget captures have empty semantic records and no fabricated `.ui`. They reuse exclusive staged publication,
collision checks and failure rollback; rendering preferences and alternative/dark toggles restore on failure. Return
lists still contain only image paths (plus the existing optional PDF). Source tests alone do not qualify native
behavior. The four canvas variants were also checked in FontLab 9.0.9794; whole-desktop capture remains unqualified.
