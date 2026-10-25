---
this_file: DEPENDENCIES.md
---

# Dependencies

- hatchling and hatch-vcs: standard builds and Git-tag versioning.
- pytest: regression tests; native host checks run separately.
- fontlab-fontlabapp: migrated application/UI/preferences and utility context.
- Native PythonQt QtGui/QtSvg/Qt and FontLab: supplied by the host for capture.
- Standard pathlib, tempfile and ElementTree: existing file/SVG implementation.
- Optional `svg` extra: Pillow >=10 decodes PNGs into exact RGBA pixel keys;
  svgelements >=1.9.6 supplies maintained pure-Python SVG path/shape/transform
  bounds, avoiding a custom geometry parser or NumPy/SciPy dependency. Both are
  also test dependencies and are imported lazily only by postprocessing helpers.
- Optional `svg`/test extras also include cssselect2 >=0.8 and tinycss2 >=1.4:
  maintained pure-Python selector matching and CSS parsing for paint specificity,
  source order, importance and inheritance. Avoid a custom CSS parser and preserve
  CSS-defined `none` during ordinary recoloring; capture does not import them.
