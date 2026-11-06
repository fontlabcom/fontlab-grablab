---
this_file: src_docs/md/development-and-limits.md
---

# Development and limits

The maintained 090234b source/main and ordinary artifact milestone passed 149 tests per recorded run, with 85.12% grab and 96.65% SVG module coverage. These are source and ordinary results. G2 checks installer presence only; version and marker enforcement remain open. Native capture, macOS Accessibility, owner installation and script activation remain separate gates. No FontLab runtime, private historical helper or source installer is executed by this documentation build.

MIGRATION.json and the source installer remain unchanged. The five retained historical helpers (`copy_statusid.py`, `copy_statusid2.py`, `print_menu.py`, `print_uimenu.py`, `ui_hider.py`) remain private historical/manual evidence, not newly delivered or activated scripts. Recovery does not authorize restoring them over current source.

Development uses the repository test recipe and its existing arm64 Python 3.11 host environment. Preserve the App adapter floor of 1.2.0 and the direct Darwin Quartz dependency declared for source installation. One runtime owns application state. See the installation and capture pages for the complete public contracts and provenance. Private Pages configuration and publication remain owner-held.
