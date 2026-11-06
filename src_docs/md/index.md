---
this_file: src_docs/md/index.md
---

# GrabLab


Install `fontlab-grablab` for the `grablab` namespace, alongside `fontlab-fontlabapp>=1.2.0`. Python 3.11+ and native FontLab
APIs are required for capture. Importing `grablab` itself is host-free; requesting Grab loads native APIs.

```python
from grablab import Grab
capture = Grab(grab_canvas=False, grab_screens=False)
capture.newGrab()
paths = capture.grabPanel("elements")
```

Screenshots, native widget SVG, canvas SVG/PDF, panels, menus, glyph/font windows and screen capture retain the source
interfaces. An optional `Grab(application=app, **preferences)` reuses an existing context, useful for controlled capture
and temporary preference-library paths.

Construction no longer alters rendering preferences or opens a confirmation dialog. Actual capture calls temporarily
adjust OpenGL, outline thickness and pixel rendering, then restore them and the dark-glyph preference even on failure.
Alternative-view exports pair their view toggles in finally blocks. Explicit `setAppPrefs()` applies settings directly;
use capture methods for restoration. The preference library still saves GrabLab configuration when explicitly used.

A failed QImage.save returns None even when a stale target exists. Filename collisions are handled iteratively,
including existing directories. Menu capture returns all submenu paths. Failed screen saves are omitted from returned
artifact lists. PNG and SVG preserve title/description metadata. `optimizeSVG(..., restyle=True)` explicitly opts into
the old font/stroke substitutions; raw capture preserves them.

```sh
# Install the sibling dependency locally (arm64 Python 3.11, as in FontLab):
uv venv --python cpython-3.11-macos-aarch64-none
uv pip install -e ../fontlab-fontlabapp -e '.[test,svg]'
./test.sh
uv build
```

`./test.sh` uses `--no-sync`; create the environment first. The suite covers capture, source-installer contracts and the four icon modes.
Ordinary-wheel capture in FontLab 9.0.9794 verified actual Font/Glyph windows, canvas and four panels, paired metadata,
DPR2 and preference restoration. Four public grabCanvas variants also passed native PNG/SVG/JSON checks; six actual
Designer files passed Qt5 uic. An owned CC0 sample was closed afterward with its source unchanged. Whole-desktop capture
and every panel/window configuration remain separate integration checks.

Migration provenance/licences are in MIGRATION.json; verification is in WORK.md. Versions derive from Git tags through
hatch-vcs.


## Documentation map

Read [installation](installation.md), [capture bundles](capture-bundles.md), [SVG and icons](svg-and-icons.md), [development and limits](development-and-limits.md), and [licences](licence.md).
