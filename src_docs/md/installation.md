---
this_file: src_docs/md/installation.md
---

# Installation and retained scripts

## Source installation and retained history — 2026-11-06

The source sdist includes the four current `Scripts/GrabLab` scripts and
`install.vfpy`; the wheel installs only the library. The source installer declares
App >=1.2.0 and `pyobjc-framework-Quartz>=10; sys_platform == 'darwin'` for the
macOS F5/F6 hotkey script. App's optional `hotkeys` extra remains available;
the linked installer metadata needs the explicit Quartz requirement. See
[DEPENDENCIES.md](https://github.com/fontlabcom/fontlab-grablab/blob/090234b30453f425a6a3d5e423af428f0f9fa6fa/DEPENDENCIES.md) for its metadata boundary.

When uv is available, the source installer submits every declared requirement
unchanged, including versions, markers and extras, to uv's standard resolver.
Already satisfactory dependencies are retained without forced upgrades or reinstalls.
Without uv, the existing fallback checks distribution presence only: it reports
missing dependencies but does not enforce versions, markers or extras. Owned tests
do not establish native installation.

Glyph-window capture uses App's supported adapter for both direct and named-child
viewports. Missing viewports raise `LookupError`; visibility preferences, viewport
then window order, image-only returns and failure restoration remain unchanged.
Current native capture is a separate acceptance surface.

Five earlier helpers remain preserved historical source, outside active Scripts
and distributions, with individual dispositions:

- `copy_statusid.py`: clipboard/status-ID watcher; needs owned disconnect/traversal/clipboard acceptance.
- `copy_statusid2.py`: quick-help/clipboard watcher; needs separate lifecycle qualification.
- `print_menu.py`: manual Markdown menu-export candidate; screenshot APIs do not replace its output.
- `print_uimenu.py`: manual Designer-menu export candidate; dialog and loader state need native qualification.
- `ui_hider.py`: persisted visibility/watcher prototype; needs persistence ownership and visibility/signal restoration.

Preservation does not deliver those runtime functions. No new cleanup deletion,
owner installation, native acceptance or private Pages publication is qualified.

## Current script catalogue

The source installer owns these four current entry points. Their presence is not activation or native acceptance.

| Script | Public #FLM menu label |
| --- | --- |
| `Scripts/GrabLab/grablab_menu.py` | GrabLab: Screengrab Main Menu |
| `Scripts/GrabLab/grablab_now.py` | GrabLab: Screengrab All |
| `Scripts/GrabLab/grablab_on_f5_mac.py` | GrabLab: Screengrab on F5/F6 Mac |
| `Scripts/GrabLab/grablab_on_save.py` | GrabLab: Screengrab on Save |
