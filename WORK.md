---
this_file: WORK.md
---

# Migration evidence

## Issue 131 Task 3 — 2026-10-25 host-free SVG candidate

Scope: new `grablab.svg`, its tests, optional dependencies and these docs only;
capture/snapshot files and canonical/live installations remain untouched. Based
on reviewed c685e24. Read the full issue/brief, global plan and local guidance.
Reviewed official svgelements README/API and installed parser source before use:
https://github.com/meerk40t/svgelements (SVG.parse/reify, bbox, transforms).
Pillow + pure-Python svgelements are lazy optional imports; no custom path parser.

Tests-first collection initially failed because the module did not exist. The
first focused implementation run passed 7/8: the test's translated second path
actually exceeded the root rectangle; corrected the fixture, preserving the
containment rule. Extended tests now cover pixel encodings/transparent RGB,
candidate ambiguity, named authoritative associations/conflicts, viewport/ID/CSS
namespacing, transformed paths/text anchors, dedup safety, composition, restyling
and output protection. Invalid path data that svgelements represents as an empty
shape is counted unsupported, never silently tagged.

Environment is task-owned external `../svg-env`, Python 3.11.17/arm64. Initial
full run there had 11 missing-fontlabapp setup errors; installed the existing
local dependency into that environment. A trial using the canonical interpreter
with 3.11 site-packages failed because that interpreter is actually 3.12; no
canonical environment was altered. Final commands (all exit 0):

```
rtk proxy uv venv --python /opt/homebrew/bin/python3.11 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env
rtk proxy uv pip install --python /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python svgelements
rtk proxy uv pip install --python /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -e /Users/adam/Developer/vcs3/github.fontlabcom/fontlab-scripting/fontlab-fontlabapp
rtk proxy uv pip install --python /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python pytest-cov
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q tests/test_svg.py
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -p pytest_cov --cov=grablab.svg --cov-branch --cov-report=term-missing --cov-report=json:/Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-coverage.json -q
rtk proxy uvx ruff check src/grablab/svg.py tests/test_svg.py
```

Final full suite and coverage are recorded in task-3-report.md and the retained
coverage receipt (zero exclusions). Ruff import-order
findings were corrected, and only the two owned Python files were formatted.

Actual manifest audit reads all 531 exports / 1062 PNG variants (1042 exact
pixel groups), and all 3658 PNGs in the three authoritative Proteus folders.
Initial strict pixel audit: 54 source matches, 1 ambiguity, 3603 unmatched.
Per root's explicit clarification, original asset names also associate source
PNG bytes with their authoritative vector; only `@2x` is stripped. Data URIs
must still equal known PNG pixels. Final source census: 1045 matched (54
pixel-exact, 991 source-name), 50 ambiguous, 2563 unmatched. No fuzzy matching
or arbitrary conflict selection. External receipts preserve both audits:
`../svg-raster-index.json`, `../svg-raster-index-named.json`,
`../svg-index-summary.json`, `../svg-coverage.json`.

Wait, but: source-name means provenance, not render equivalence. Geometry tags
express coordinate containment; text has anchor-only tags. General CSS,
clipping/text extents/use-instance ownership and processed rendering need runtime
review. Dedup is opt-in because repeated opaque antialiased edges can differ.
Root owns native calls, actual screenshot/artifact acceptance and promotion;
none was run or claimed in this task. No push or live install.

2026-10-13: Preserved complete source files and licenses, with source revision and
SHA256 in MIGRATION.json. Native source baseline is recorded in workspace evidence.
Copied all source before scoped fixes; original repository remains unchanged.
Tests written first reproduced eager host imports and specific behavior failures.
Two test setup issues (an escaped subprocess newline and lazy getattr during
monkeypatch) were corrected before using the tests as implementation evidence.
Final source suite: 6 passed. Both wheel and sdist build successfully.
Conservative Any annotations preserve legacy native/utility call boundaries;
precise native signatures are not invented. New sources use this_file markers.

Installed-wheel acceptance used native FontLab 9.0.9780 / Qt 5.15.19 via MCP.
ApplicationUI initialized, a temporary preference library round-tripped, a hidden
80x60 QWidget produced a 482-byte PNG and 835-byte SVG with expected metadata.
Four rendering preferences were restored after success and deliberate failure.
The first native assertion incorrectly expected an unformatted description;
corrected it to the preserved 'descriptor: name' format and reran successfully.
No open font edits, persistent user preference changes or leftover test windows.

Final HEAD artifact installs/audits and further integration are pending below.
Global hotkey capture, desktop screens, open-font canvas and all panel/window
configurations have not been exercised. Three project iterations and releases
remain with the workspace goal; this is not whole-project completion.

Integration review found grabScreens counted None for a failed native screen save.
New regression failed with [None]; filtering failed results fixes saved-file
counts and removes the mutable default screens list. Seven tests now pass.

Whole-project iteration2: current eight-package wheel/sdist audits and joint
clean installs,16 Twine checks,457 runtime-suite tests and live native control,
drawing, remote, aliases and Aidus integration pass. Original migration files
are byte-verified in destination recovery; selected source cleanup is committed.
Iteration3/tagged builds and actual release verification follow.

## v0.2.0 publication verified

Actual publication and independent downloaded-asset verification complete.
Three full-project iterations pass; installed tagged wheel/sdist each457tests.
Downloaded native smoke covers all eight packages and both formats, including
production ACP/native UI and TypeRig composition. Exact release URLs, immutable
code commit and asset digests are in RELEASE.md. This follow-up changes only
completion evidence; release code and tag are unchanged.

2026-10-15 workspace reconciliation: fresh source suite 7passed/0skipped, exit0.
Exact command and retained initial failures: parent verification/plan-todo-audit-20261015/baseline-tests.json.
Completed repository plans were archived where no repository tasks remain;
workspace integration/release gates remain separate.


## Issue 131 Task 1 — 2026-10-25 source candidate

Base f791e5d10ee54a68ca2cd782a76ec3bae8b6e26b. Work only in isolated
issue131/grablab; canonical installation untouched. Read capture callers/tests,
FontSnap record at fontsnap.py:2533 and README schema, and official Qt 5.15
QWidget, QImage text and Designer UI schema documentation. Additive schema was
written independently; no FontSnap source copied and no dependency added.

Checks (all run through `rtk proxy`; shell cwd this isolated repository):
- `PYTHONPATH=src /Users/adam/Developer/vcs3/github.fontlabcom/fontlab-scripting/fontlab-grablab/.venv/bin/python -m pytest -q`: baseline 7 passed, exit 0.
- Same command with `tests/test_snapshot.py` before implementation: collection failed with missing `grablab.snapshot`, exit 2 (expected RED).
- First full run exposed a shell-quoting-induced f-string syntax error; next exposed a test XPath quoting error. Corrected both; retained failures in task transcript.
- Final full command: 17 passed, exit 0. Covers DPR2 pairing and embedded JSON equality, sidecar collision/publication rollback, sidecar failure preference restoration, raw/opt-in SVG styling, logical hierarchy/content/XML, password omission/no models, bounded traversal, GC restoration, and directly owned actions.
- `git diff --check`: exit 0.
- Optional `python -m pytest -q --cov=grablab.snapshot --cov-report=term-missing` in the same environment: exit 4, pytest-cov is absent; no dependency/environment mutation to add it. Coverage percentage remains unmeasured here.

Wait, but: offline doubles cannot qualify PythonQt serialization or native widget
rendering. Image-only return counts remain compatible, including native_smoke.py;
new sidecars are additive. Unsupported layouts/custom painting/icons, clipping
versus pixel ownership and unknown remote actions are disclosed. Root must run
ordinary artifact/native capture checks; no native requests, installation or
push performed here. No claim of full issue131 acceptance.


## Issue 131 Task 1 fix round 1 — 2026-10-26

Read task-1-review.md and native-widget-receipt.json. P1/P2 and the measured hidden
root child omission reproduced with tests first: 3 failed/6 passed, exit 1.
Consulted official Qt5 QProgressBar/QAbstractSpinBox read-only text, QWidget
isVisibleTo and QMenu actionGeometry documentation. Fixed writable per-control
Designer mapping, checked-state deduplication/setter order, relative visibility,
and measured menu/menu-bar actions plus QAction/addaction serialization. Numeric
range/precision setters precede value setters; read-only and unsupported data
remain JSON-only. During the implementation a duplicated nodes.append yielded
two failed assertions; removed it and reran before claiming GREEN.

Exact final command (through rtk proxy, cwd isolated checkout):
`PYTHONPATH=src /Users/adam/Developer/vcs3/github.fontlabcom/fontlab-scripting/fontlab-grablab/.venv/bin/python -m pytest -q` — 21 passed, exit 0.
Three generated UI controls invoke `/opt/homebrew/opt/qt@5/bin/uic` with exit 0:
progress/spin/abstract-spin/checkbox, QMenu, QMenuBar. Tests inspect generated
setters and order as well as XML geometry/visibility/content/classification.
`git diff --check` — exit 0. No FontLab/native requests, installs or descendants.

Wait, but: uic generation proves usable setter output, not native loading/render
equivalence. Root must rebuild ordinary artifacts and rerun owned captures to
verify actual relative visibility and menu action geometry in PythonQt. Submenu
structure, custom widgets and signal wiring retain their disclosed limits.


## Issue 131 Task 1 fix round 2 — 2026-10-26

Read task-1-fix1-review.md verbatim. Added unnamed visible menu/menu-bar actions
to the existing regression; generated IDs incorrectly entered rects/texts in
both controls (2 failed/8 deselected, exit 1). The shared action measurement now
keeps generated IDs only in extension/UI references and records unnamed measured
contents in parts with QAction class, logical rectangle and content. Named
actions retain rects/texts. No new API, dependency or native operation.

Checks through `rtk proxy`, isolated checkout: the same PYTHONPATH/canonical Python
pytest command with `tests/test_snapshot.py -k menu_action` passes 2 tests; full
`-m pytest -q` passes 21 tests (including Qt5 uic subprocesses), exit 0.
`git diff --check` passes, exit 0. Root still owns rebuilt artifact/native checks.
