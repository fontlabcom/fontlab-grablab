---
this_file: AGENTS.md
---

<!-- workspace-handoff:2026-11-03 -->
## Workspace documentation handoff —2026-11-03

Issue 123 implementation is paused by the owner. The present request authorizes
only documentation maintenance; preserve all source, owner edits and branch state.
FontLab-owned capture/export tools. Observed canonical checkout: `main` at `3ebbf85b0128`. No source integration is performed by this update.

No new November 2–3 runtime delivery is attributed here; historical export evidence and current access holds remain retained.

No capture, export, preference change or native acceptance is implied by documentation maintenance.

Read workspace AGENTS/DECISIONS and local project guidance before later work.
Use direct execution unless a new request explicitly authorizes agents. Product
work stays isolated; this docs-only request does not authorize native actions,
installs, merges, pushes, releases, generated-site updates or legacy retirement.
<!-- /workspace-handoff -->

# Agent guidance: fontlab-grablab

`grablab`: screenshot, widget/canvas SVG and PDF capture helpers for FontLab. Read the workspace AGENTS.md and DECISIONS.md first; this file adds repo rules only.

## Rules

- `import grablab` must stay host-free; native APIs load only when `Grab` is requested. Keep imports lazy; offline tests depend on it.
- Capture calls temporarily change OpenGL, outline thickness, pixel rendering and the dark-glyph preference. Every change is restored in `finally`, including alternative-view toggles. Any new capture path needs a failure-path restoration test.
- Depends on `fontlab-fontlabapp`; install it editable from the sibling checkout.
- `MIGRATION.json` and the retained BSD-3-Clause notices record the source files. Leave `legacy/` unchanged.

## Commands

- Setup: `uv venv --python cpython-3.11-macos-aarch64-none && uv pip install -e ../fontlab-fontlabapp -e '.[test]'` (verify with `lipo -archs`). The README's `--python 3.12` is not FontLab's interpreter.
- Tests: `./test.sh` (= `uv run --no-sync python -m pytest "$@"`; `--no-sync` means the environment above must already exist). Build: `uv build`.

## Host rules that apply here

- Never mutate user-open fonts, persistent preferences or the Output panel. Native checks use owned fixtures and hidden owned widgets, destroyed afterwards, via `verification/issue-104/fl-native.sh`.
- Do not read Qt property values generically (`QSvgRenderer.currentFrame` without a loaded document segfaults FontLab). Use class-level lookup or `indexOfProperty`.
- A Python exception escaping a `paintEvent` while a `QPainter` is active crashes FontLab: wrap paint bodies in try/except, end the painter in `finally`.
- Convert native widget lists (`topLevelWidgets()`, `allWidgets()`, `findChildren`) with GC disabled; prefer direct accessors such as `fontlab.MainWindow()`.
- No unary minus on PythonQt wrappers (`-QPoint`, `-rect.topLeft()`); negate components.
- PythonQt does not convert enums implicitly; some overloaded constructors take positional arguments only, others keywords only. Check the stub.
- `QApplication.primaryScreen` is a property: use `QApplication.screens()[0]`.
- `QColorDialog`/`QFileDialog` touch process-global state (NSColorPanel, lastVisitedDir). Hold dialog-based capture cases until owned restoration is proved; `DontUseNativeDialog` alone is insufficient.
- FontLab resolves relative save paths against its own cwd: always pass absolute paths.
- Disconnect signals before `deleteLater()`/close.

## Proof and git

- Offline tests (the 7 regression tests) are not native proof. Whole-desktop capture, open-font canvas export and every panel/window configuration are unproven; do not claim them.
- The canonical checkout is editable-installed into the owner's FontLab: do not edit, commit or switch it; work in the issue-122 worktree. Do not move or re-create `v0.2.*` tags.
