---
this_file: WORK.md
---

# Migration evidence

## Issue 131 Task 10 review fix round1 — 2026-10-26

Refuse CSS-wide root filter keywords before monochrome mutation, preventing
invalid keyword/function lists from silently preserving coloured output. Covers
initial, unset, inherit, revert and revert-layer, case-insensitively, in inline
styles and presentation attributes. All12new parametrized controls failed first.
Conservative refusal preserves the complete document; no cascade resolver added.

Fresh commands (exit0):
```
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q
rtk proxy uvx ruff check src/grablab/svg.py tests/test_svg.py
rtk proxy git diff --check
```
119tests pass and Ruff/diff clean. Wait, but: actual screenshot rerenders and
ordinary artifacts remain the root's separate gate; no native or tooling changes.

## Issue 131 Task 10 rendered acceptance correction — 2026-10-26

Actual Chrome captures exposed two presentation failures. Monochrome now applies
standard grayscale to the complete SVG drawing, preserving the light/dark paint
hierarchy, geometry and existing root/descendant filter effects. The actual
process_captures.py caller no longer overrides every stroke/fill with dark grey.
Wireframe keeps originally painted surfaces white (or the requested background),
retains none paints and sibling order, and uses readable dark text/outlines.
Definition/clip/pattern/filter/marker descendants remain unchanged; container paint
is not overridden so resource inheritance remains intact. Retained raster
wireframe wrappers and their existing effects remain supported and idempotent.
Author stylesheets in monochrome and important root filters are refused before
mutation; masks retain their existing refusal. No new dependency or color parser.

Reviewed W3C Filter Effects 1 sections5,6,13 for full-drawing filtering and ordered
filter function composition: https://www.w3.org/TR/filter-effects-1/#FilterProperty
Two new contrast/occlusion tests failed before implementation. Fresh checks:

```
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q
rtk proxy uvx ruff check src/grablab/svg.py tests/test_svg.py
rtk proxy git diff --check
```

All107tests pass; Ruff and diff checks exit0. Wait, but: this proves source
regressions, not the root's separately required actual rendered acceptance or
ordinary wheel qualification. No native call, live install, push or font work.


## Issue 131 Tasks 8–9 review fix1 — 2026-10-26

Read task-8-9-review.md; four new parametrized SVG controls failed first because
selector-sensitive retained-image wrapping was accepted. Smallest safe fix refuses
any retained-raster monochrome/wireframe input containing author style elements,
before all mutation. Vector-only styles and ordinary restyle remain supported.
No CSS engine expansion, dependency, native call, installation or font work.

Fresh validation (exit0), from this checkout:

```
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q
rtk proxy uvx ruff check src/grablab/svg.py tests/test_svg.py
rtk proxy git -C /Volumes/Falstaff4T/fontlab-scripting-data/issue131/grablab diff --check
```

Full suite97passed; Ruff clean. Wait, but: stylesheet-bearing raster input is now
explicitly unsupported for these structural modes; rendered/native/installed
acceptance remains the root's separate check. Task8 tools remain uncommitted.

## Issue 131 Task 9 — 2026-10-26 retained raster monochrome

Base c959bc9. Root's Chrome probe measured retained red PNG RGB255,0,0 despite
wireframe styling. Four new tests failed first: explicit monochrome kwarg and
wireframe raster treatment were absent. Added standard filter:grayscale(1) on an
outer group at each retained image's sibling slot. Image attributes/bytes stay
unchanged, including its prior filter/clip/transform; own wrapper is reused on
repeated styling. No filter IDs are needed or added; compose still namespaces
the preserved existing filter/clip refs. Normal restyling does not add treatment.
The one allowed canonical process_captures.py mono caller now asks monochrome=True;
canonical icon tooling was not committed and no other tool files were edited.

Reviewed W3C Filter Effects sections6.1,13.1.1,13.2: grayscale() is the platform
feColorMatrix shorthand, whose UA-defined region includes overflowing visual
content. This avoids clipping existing blur/shadow output with a guessed finite
SVG filter rectangle. No custom color parser or PNG pixel rewrite/dependency.
Original image filters remain on the original image, before the grayscale group.

Focused tests40passed. Full suite93passed, SVG338/347statements and155/168branches,
zero exclusions (combined96%). Exact commands, exit0:

```
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q tests/test_svg.py
rtk proxy env COVERAGE_FILE=/Volumes/Falstaff4T/fontlab-scripting-data/issue131/task9.coverage PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -p pytest_cov --cov=grablab.svg --cov-branch --cov-report=term-missing --cov-report=json:/Volumes/Falstaff4T/fontlab-scripting-data/issue131/task9-coverage.json -q
rtk proxy uvx ruff check src/grablab/svg.py tests/test_svg.py
```

Retained processed source probe externally at
issue131/wireframe-retained-red-probe-task9.svg; root owns browser pixel proof.
Wait, but: this is deliberate presentation styling, not vectorization or changed
raster identity. Actual renderer support and pixel output remain root checks;
native hosts/live installations and raw probe are untouched.

## Issue 131 Task 7 — 2026-10-26 high-level screen/canvas bundles

Base2644bef, isolated checkout only. Read AGENTS/README/WORK/CHANGELOG, issue131
Task7 brief and all repository callers of grabCanvas/grabScreens/grabScreenPNG.
Root holds the native modal/fence; no native calls, installs or icon-tool edits.
No dependencies added. Read official Qt5.15 source documentation for
QSvgRenderer validity/render bounds, QImage transparent initialization and
QPainter begin/end through the Qt GitHub mirrors; archive/qt.io URLs failed.

Tests-first RED: five new route controls failed (unpaired screens, ignored PNG
canvas format, missing same-source rendering and render-failure restoration).
Reused the widget route's same-filesystem staging/exclusive links via one shared
publisher, preserving its rollback tests. Existing screen filtering test now
stubs the high-level bundle boundary; alternative-export test supplies a real
minimal SVG before triggering its existing failure. New tests measure screen
DPR2/single-capture/wrapper bytes, format flags, sidecar collisions, exact native
SVG bytes fed to PNG rendering, alternative/dark ordering, PDF retention,
property/callable Qt getters, invalid/null images, begin/render/save failures,
renderer disposal, painter end, temporary export cleanup and public aggregation.

Exact full-suite command (exit0):

```
rtk proxy env COVERAGE_FILE=/Volumes/Falstaff4T/fontlab-scripting-data/issue131/task7.coverage PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -p pytest_cov --cov=grablab.grab --cov-branch --cov-report=term-missing --cov-report=json:/Volumes/Falstaff4T/fontlab-scripting-data/issue131/task7-coverage.json -q
```

Focused capture tests and full source suite pass; final counts/coverage are in
task-7-report.md and the external coverage receipt. Ruff passes for the new test
file and runtime-error selection on touched source; broader legacy lint has
pre-existing shebang/import/style findings and was not globally reformatted.

Wait, but: screen SVG is deliberately raster-backed. Canvas PNG is a Qt render
of a native vector export, not another viewport screenshot. Non-widget semantic
UI is unknown and no .ui is fabricated. Native screen permission/DPR/renderer
bindings, actual variants and installed-artifact acceptance remain root gates.

## Issue 131 Task 3 — 2026-10-25 host-free SVG candidate

### Review fix round1

Read `verification/issue-131/task-3-review.md` verbatim. Added regressions first:
seven failing cases reproduced the three review findings. Source-name evidence
now always joins pixel-exact evidence; distinct vectors remain ambiguous, same
vector stays uniquely matched with both provenance records retained. Equal-area
semantic ties require a unique observed descendant; siblings/cycles remain
untagged and disclose sorted candidate IDs, independent of record order.

Restyling resolves paint cascade before editing using cssselect2/tinycss2, whose
official API docs and installed Matcher.match source were inspected. This covers
class/ID specificity, source order, inline/presentation precedence, !important,
inheritance, comments and keyword case. Unsupported conditional/contextual CSS
fails before any mutation. No native path imports these lazy dependencies.

Exact commands, exit0 (the initial tests-first run was exit1 as expected):

```
rtk proxy uv pip install --python /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python cssselect2
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q tests/test_svg.py
rtk proxy env COVERAGE_FILE=/Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-fix1.coverage PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -p pytest_cov --cov=grablab.svg --cov-branch --cov-report=term-missing --cov-report=json:/Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-coverage-fix1.json -q
rtk proxy uvx ruff check src/grablab/svg.py tests/test_svg.py
```

Full suite57passes (36SVG controls); module325/334statements and145/158branches,
zero exclusions. Actual531asset/3658source-PNG audit rerun:1044matched,
51ambiguous,2563unmatched. One actual old source contradiction is now retained;
previous1045/50counts are superseded. Matched provenance sets:991source-name,
40both same-vector pixel/name,13pixel-exact only. New receipts `../svg-raster-index-fix1.json`,
`../svg-index-summary-fix1.json`, `../svg-coverage-fix1.json`, `../svg-fix1.coverage`
preserve prior receipts unchanged. Root owns actual captures/rendered acceptance.

Wait, but: no-paint cascade correctness does not prove browser rendering or
arbitrary stylesheet rewriting. Conditional CSS fails closed; raw inputs, native
hosts, canonical installations and icon tools remain untouched.

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


## Issue 131 final SVG review fixes — 2026-10-26

Replaced the per-ID URL rewrite loop with one compiled expression and dictionary
lookup; non-reference attributes bypass regex work. Existing quoted local URL,
href, class/selector and color controls stay green. Added a realistic semantic
fixture with 1,600 rect IDs, quoted clip references, per-element marker references,
unknown external fragments and two composed panels. Its measured pytest call is
0.02 s; the regression allows 5 s to catch the prior multi-minute stall.

Restyle now refuses every mask-bearing document before mutation. This deliberately
includes default/font-only changes because inherited fonts can change text masks;
skipping mask children alone would not preserve inherited paint. Six controls
assert whole-document byte equality after refusal, including background requests.
No dependency, native call or live install changed.

Exact commands in this isolated checkout (existing external environment):
- `PYTHONPATH=src /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q` — exit 0, 104 passed in 0.37 s.
- `PYTHONPATH=src /Volumes/Falstaff4T/fontlab-scripting-data/issue131/svg-env/bin/python -m pytest -q tests/test_svg.py --durations=3` — exit 0, 51 passed in 0.09 s, many-ID call 0.02 s.
- `git diff --check` — exit 0.

Wait, but: these host-free controls do not establish the actual capture pipeline's
rendering or installed-artifact identity. Root retains wheel rebuild, actual
composition and native/browser acceptance ownership. Masks are an explicit API
limitation, not a claim of correct mask recoloring.
