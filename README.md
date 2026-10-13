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
artifact lists. PNG and SVG preserve title/description
metadata; SVG optimization adds missing metadata elements when necessary.

```sh
# During initial migration, install the sibling dependency locally:
uv venv --python 3.12
uv pip install -e ../fontlab-fontlabapp -e '.[test]'
./test.sh
uv build
```

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
