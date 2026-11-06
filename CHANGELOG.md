---
this_file: CHANGELOG.md
---

## 2026-11-05 — independently approved documentation applied

[Task 2 final review](../verification/issue-230/task-2-fix2-review.md) records
SPEC PASS / QUALITY APPROVED. The [78-file application receipt](../verification/issue-230/task-2-apply.json)
includes this repository's six guides and preserves all 21 repository heads,
branches, indexes and non-selected diffs. This is applied documentation evidence,
not a new product test, installed artifact, native result or publication.

The complete earlier handoff/history below retains its proposal-stage statements
and dated source pins. Later review, application and delivery status belong in the
[live workspace ledger](../verification/issue-230/progress.md). Original future,
native, artifact and preservation contracts remain binding.

## 2026-11-05 — documentation reconciliation proposal

Prepared repository-specific organization, test and MVP/delivery guidance from current source/test configuration and retained Issue 207–211 evidence. Distinguished current canonical layout from qualified candidates, future plugin ownership and unfinished native/artifact gates. Preserved all prior work and changelog evidence; no runtime completion, installation or publication is claimed. Completed historical task rows were removed from the active checklist and consolidated below from existing local CHANGELOG/WORK receipts. Unfinished native, artifact and integration checks remain open.

## Retained scoped completion receipts — corrected evidence map

These are dated results at the stated source/version and acceptance surface. They do not establish current integrated, installed, native or published acceptance. Full receipts and hashes are indexed in the workspace Issue 230 task-2 manifest. Canonical-preimage line ranges below refer to the unchanged historical documents, before these new entries.

- Four-mode icon follow-up:141package tests;48actual-wheel tool tests;466d986 source/artifact identity;156SVG/24gallery/12embedding checks.
  Historical receipt: WORK.md:5–41.

- Issue131 paired widget/runtime metadata implementation;source90c1842;122 full/installed tests;85.09/94.93/95.68% changed-module coverage.
  Historical receipt: CHANGELOG.md:235–255; WORK.md:431–452.

- Issue1310.2.1.dev18+g90c1842e6:ordinary parity/122 installed tests;owned native captures/preferences and6 browser variants;owner font creation/export waiver.
  Historical receipt: WORK.md:431–459.

- Issue1310.2.1.dev18+g90c1842e6:composed Font/Glyph captures and six vector/mono/wireframe variants reviewed;ambiguous rasters retained.
  Historical receipt: WORK.md:431–459.

## 2026-11-05 — planning chronology reconciliation

Four-mode icon source466d986 and paired screenshot source90c1842 are bounded verified deliveries, not current implementation tasks. Whole-desktop/all-configurations/dialog restoration/Issue122Appsmoke remain open, with owner font creation/export waiver intact. Historical passing results retain their dated source and acceptance scope in the entries above and original history below. This documentation change creates no new runtime acceptance.

---
this_file: CHANGELOG.md
---

## 2026-11-03 — fixes from runs inside FontLab 9

- The SVG asset manifest is read as UTF-8 (FontLab's Python defaults to ASCII).

## 2026-11-03 — installer options, licence and cleanup

- `install.vfpy` reads optional `[tool.fontlab-install]` keys: `name` (the distribution
  record), `packages` (`[]` installs scripts only) and `dependencies` (what FontLab needs,
  instead of `project.dependencies`). Symlinks inside `Scripts/` are not copied.
- Relicensed under Apache-2.0 by the copyright owner (previously BSD-3-Clause). `LICENSE` now
  holds the Apache License 2.0 text.

## 2026-11-03 — install.vfpy fixes from runs inside FontLab 9

Verified by installing all nine packages inside FontLab 9 (Python 3.11.6, arm64).
- Dependencies with console scripts (glyphsLib, fontTools) failed: uv writes them to
  `site-packages/../../../bin`, which resolves through the venv link to the FontLab
  folder. `bin`, `share` and `include` there now link back into `.venv`.
- A failed install appends a `"failed"` record with the traceback and uv's output to
  `install.log`; List/Uninstall ignore failed records.
- Package records include `WHEEL`, so `uv pip check` accepts them.
- Scripts are copied file by file into FontLab's `Scripts` folder, from a package's
  `Scripts/` folder (exact case) and from folders listed in `[tool.fontlab-install] scripts`.
  Folders shared by several packages merge, e.g. two packages' `Scripts/Kerning`. The
  installer refuses to overwrite a file another package or the user put there; uninstall
  removes only its own files, their `.pyc`, and folders left empty. An older install's
  folder link (`Scripts/Aidus Code`) is replaced by copied files.
- `*.vfpyc` (FontLab's compiled `install.vfpy`) is ignored by Git.

## 2026-11-03 — install.vfpy creates FontLab's venv

FontLab's `python/3.11/site-packages` is now always a real folder; packages are
symlinked into it, so no `.pth` processing is needed. `install.vfpy` creates `.venv` with
uv from FontLab's exact Python version and processor type, and links the venv's
site-packages to FontLab's folder, so `uv pip install --python .venv/bin/python` installs
into FontLab. An older layout (FontLab's folder linked into `.venv`) is migrated.

## 2026-11-03 — reverse-domain extension id and install.log

`[tool.fontlab-install] id = "com.fontlab.grablab"` names this extension. `install.vfpy` keeps
`Extensions/com.fontlab.grablab/install.log` (JSON Lines; the last line lists every installed file),
puts copied code in `Extensions/com.fontlab.grablab/lib/`, and adds Scripts > Extensions >
List Extensions and Uninstall com.fontlab.grablab.

## 2026-11-03 — install.vfpy without uv

`install.vfpy` now needs only FontLab's Python. It asks FontLab for its data folder
(`flPreferences().dataPathDefault`), links a Git checkout or copies a plain folder into
`Extensions/`, and writes a `.pth` plus `.dist-info` into `python/3.11/site-packages`.
uv is used only to add missing dependencies. It never replaces folders it does not own.

## 2026-11-03 — release scripts

Added `build.sh` (uv build into dist/), `publish.sh` (`uv publish`; refuses a dirty
tree or an untagged HEAD) and `install.vfpy` (editable install into FontLab's venv
from inside FontLab). Version stays hatch-vcs from `vX.Y.Z` tags.

<!-- workspace-handoff:2026-11-03 -->
## 2026-11-03 — documentation handoff for November 2–3

No new November 2–3 runtime delivery is attributed here; historical export evidence and current access holds remain retained.

No capture, export, preference change or native acceptance is implied by documentation maintenance.

Observed canonical checkout: `main` at `3ebbf85b0128`. No source integration is performed by this update.

Updated the requested AGENTS/TODO/PLAN/CHANGELOG/README documentation and
recorded the paused state. Existing project text, examples and history remain;
no runtime source, installation, native session, branch/ref, release or site was
changed by this documentation maintenance. Source/archive/ordinary/native and
promotion acceptance remain separate claims. Detailed workspace evidence is
recorded in the root CHANGELOG and retained verification reports.
<!-- /workspace-handoff -->

# Changelog

## 2026-11-03 — Issue 201 audit

- No file removed: every tracked file is referenced by code, tests, packaging or docs (evidence in the
  workspace `verification/issue-201/task-15-report.md`). Imports of `fontlabapp` (`Application`,
  `utils.attribdict/slugify/timestamp`, `application.preflib`) resolve in the issue-201 App.
  Removed a stale AGENTS.md sentence about a README `--python 3.12`.

## 2026-10-26 — icon representation modes

- Add host-free base64, PNG URL, SVG URL and default inline SVG processing,
  named asset links, outcome receipts, and output-aware composition.
- Preserve existing inline_images callers and capture behavior.

## Issue 131 Task 10 review fix round1 — 2026-10-26

Refuse CSS-wide root filter keywords before monochrome mutation, preventing
invalid keyword/function lists from silently preserving coloured output. Covers
initial, unset, inherit, revert and revert-layer, case-insensitively, in inline
styles and presentation attributes. All12new parametrized controls failed first.
Conservative refusal preserves the complete document; no cascade resolver added.

Fresh commands (exit0):
```
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 <svg-env>/bin/python -m pytest -q
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
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 <svg-env>/bin/python -m pytest -q
rtk proxy uvx ruff check src/grablab/svg.py tests/test_svg.py
rtk proxy git diff --check
```

All107tests pass; Ruff and diff checks exit0. Wait, but: this proves source
regressions, not the root's separately required actual rendered acceptance or
ordinary wheel qualification. No native call, live install, push or font work.


## 2026-10-26 — issue 131 final SVG review fixes

- Rewrite local URL references in one dictionary-backed pass, avoiding per-ID
  regex compilation on every attribute during large semantic capture composition.
- Refuse mask-bearing restyling before mutation, including font changes, to
  preserve luminance masks and inherited text geometry.

## 2026-10-26 — issue 131 Task 9 review fix

- Refuse stylesheet-bearing retained-raster monochrome/wireframe input before
  mutation, preserving selector-dependent geometry/effects by failing explicitly.

## 2026-10-26 — issue 131 retained raster monochrome treatment

- Add explicit monochrome raster presentation to restyle, also enabled by
  wireframe. Preserve image bytes, geometry, existing effects and sibling order;
  reuse marked grayscale wrappers on repeated calls and report filtered counts.

## 2026-10-26 — issue 131 screen/canvas pairing

- Pair high-level screen captures as PNG plus explicitly raster-backed SVG;
  preserve one capture, logical geometry, physical pixels/DPR and metadata.
- Pair all native canvas vector variants with PNG rendered from that same SVG;
  record source viewBox/frame mapping and preserve flags, dark/alternative/PDF
  behavior, painter cleanup and preference restoration.
- Reuse exclusive staged bundle publication and JSON sidecars for non-widget
  captures without inventing Designer UI. Preserve primitive return interfaces.

## 2026-10-25 — issue 131 host-free SVG pipeline

- Review fix round1: retain contradictory authoritative-name candidates beside
  exported-pixel matches; fail closed on unresolved equal-area widget ties; use
  maintained CSS cascade parsing to preserve effective no-paint during restyling.

- Add explicit SVG postprocessing: provenance-aware raster/vector mapping,
  namespaced inlining, coordinate widget tags on original paint elements,
  conservative opt-in duplicate cleanup, logical composition and restyling.
- Preserve raw captures through exclusive new output files. Disclose ambiguous,
  unmatched and unsupported raster/semantic cases; distinguish source-name vector
  associations from exported pixel-equivalent matches.
- Add optional Pillow/svgelements dependencies and host-free regression controls.
  Native screenshot and rendered-geometry acceptance remain separate.

## 2026-10-15 — completed checklist (moved from TODO.md)

- Record source provenance and baseline.
- Implement complete package migration and scoped modernization.
- Verify wheel, sdist, isolated installs and privacy.
- Verify relevant native behavior in FontLab.
- Pass review and scoped fixes.
- Complete all three project iterations.
- Push, tag, release and verify assets.

## v0.2.1 (2026-10-16)

Documentation and ignore-rule reconciliation since v0.2.0 (issue 101/104/106); no runtime changes. Release review: verification/issue-106/reviews/X5-fontlab-grablab.md.


- Preserve all source functionality and license notices with migration hashes.
- Add hatch-vcs wheel/sdist packaging, lazy imports and source annotations.
- Restore rendering preferences and alternative-view toggles around capture.
- Fix failed-save stale-file reporting, recursive collision handling and dropped
  submenu paths; preserve SVG metadata and add missing elements.
- Allow reuse of an Application context through an optional constructor argument.
- Verify source regressions and installed native hidden-widget capture.
- Exclude failed screen captures from saved-file lists; avoid mutable screen default.

## v0.2.0 publication verified

Actual publication and independent downloaded-asset verification complete.
Three full-project iterations pass; installed tagged wheel/sdist each457tests.
Downloaded native smoke covers all eight packages and both formats, including
production ACP/native UI and TypeRig composition. Exact release URLs, immutable
code commit and asset digests are in RELEASE.md. This follow-up changes only
completion evidence; release code and tag are unchanged.

## 2026-10-15 — workspace plan and checklist reconciliation

Completed repository scope archived after reading WORK.md and checking the
workspace evidence. Workspace release/integration gates remain in the parent
PLAN.md. Historical verification limits below remain part of the record.

### Archived PLAN.md

# Plan

No open work in this repository. Its issue 101 migration scope is complete and released as verified v0.2.0 (see README.md "Status" and RELEASE.md). Cross-package work for the expanded ecosystem (joint regression in the three expanded iterations, R050/P11, and any new release) is tracked in the workspace PLAN.md.

### Archived TODO.md

# Tasks

No open tasks. Workspace-level work is tracked in the parent TODO.md.


## Issue 131 — source candidate, native acceptance pending

- Pair widget PNG/SVG by one collision-safe basename across image/JSON/UI members,
  independently of DPR; preserve image-only returns and add automatic sidecars.
- Embed FontSnap-shaped extended records in PNG/SVG and retain bounded visible
  runtime widget geometry/content in JSON and Qt Designer XML without model walks.
- Stage bundles and publish exclusively with rollback; retain preference restoration.
- Make the former SVG font/stroke substitutions explicit `restyle=True` opt-in.


### Issue 131 Task 1 review fixes

- Restrict Designer properties to writable standard-control allowlists; retain
  read-only progress/spin display text in JSON and deduplicate checked state.
- Include rendered descendants of hidden owned roots via relative visibility.
- Measure visible contained menu/menu-bar action geometry/text; classify hidden,
  empty and clipped owned actions outside, and emit supported action/addaction UI.
- Validate generated standard-control and menu XML with actual Qt5 uic.

- Keep unnamed measured menu/menu-bar QAction content in FontSnap-compatible
  parts; reserve generated IDs for runtime extensions and Designer references.

## Issue 131 premultiplied PNG matching

- Match exact8-bit premultiplied pixels across Qt PNG round-trips, preserving ambiguity and visible channel/alpha differences. Rebuild schema1indexes as schema2.

### Issue 131 verified delivery — 2026-10-26

- Qualify paired native window/panel/canvas snapshots and actual composed vector, mono and wireframe screenshots; preserve ambiguous raster content.
- Verify ordinary artifacts, 122 tests and changed-module coverage above80%; record the owner font-work waiver and remaining native integration limits.


## 2026-11-06 — bounded source reconciliation candidate

- Reuse App >=1.2.0's GlyphWindow viewport adapter with direct/named/missing,
  visibility/order/return and failure-restoration regression controls.
- Restore the explicit source-installer App/Darwin Quartz requirements; keep
  install.vfpy unchanged and disclose its presence-only version/marker limitation.
- Include the four current Scripts and installer in sdists; wheels remain library-only.
- Bind the removed recovery archive to its immutable ancestor revision while
  preserving migration hashes/keys, fixture/licence/screenshot provenance and
  the five historical helpers' individual dispositions outside active payloads.
- Source, ordinary artifacts, current native/owner installation, remote delivery
  and private Pages publication retain separate acceptance boundaries.

### Retained historical owner report

Historical owner report from 2026-11-05, retained verbatim from acb33b0a. Its native installation, live viewport, and 53-test statements are owner-reported history, not controller acceptance for current source. The presence-only installer check does not evaluate version ranges or markers; uv evaluates submitted requirement strings. Current supported behavior and ordinary proof are recorded separately.

## 2026-11-05 — F5/F6 hotkey script: Quartz dependency installed

`Scripts/GrabLab/grablab_on_f5_mac.py` failed with `ModuleNotFoundError: No module named 'Quartz'`:
`fontlabapp.hotkey` imports `Quartz` on macOS, which App only declares in its optional
`hotkeys` extra, and GrabLab's installer dependencies never asked for it. Following the
fontport/glyport pattern, `[tool.fontlab-install] dependencies` now lists
`fontlab-fontlabapp>=1.2.0` and `pyobjc-framework-Quartz>=10; sys_platform == 'darwin'`
(spelled out: linked App records carry no extras metadata, so `fontlab-fontlabapp[hotkeys]`
would resolve to nothing). `install.vfpy` is unchanged; its presence check and
`uv pip install` already handle markers. Reinstalled through the native runner into the
owner's FontLab 9: pyobjc-core, -cocoa and -quartz 13.0 landed in `.venv`/site-packages,
the dist-info record lists both requirements, and inside the running host
`fontlabapp.hotkey.HotkeyManager` resolves to `fontlabapp.core.hotkey.mac`. The owner's
pre-existing hand-copied `Scripts/GrabLab` (byte-identical to the repo's) was moved aside so
the installer could own the folder.

`Scripts/GrabLab/grablab_on_save.py` connected `Grab().grabAll` straight to
`QAction.triggered`, which emits `checked: bool`, so every save raised
`TypeError: Grab.grabAll() takes 1 positional argument but 2 were given`. The slot is now a
lambda that drops the argument. The installed copy in FontLab's Scripts folder was updated
in place (same content the installer would copy).

`Grab.grabGlyphWindows` read `widget.widgetViewport`, which FontLab 9's PythonQt does not
expose as an attribute (`AttributeError: GlyphWindow has no attribute named 'widgetViewport'`).
It now takes the viewport from App's `fontlabapp.qt.views.GlyphWindow`, which falls back to
the child widget with that objectName. Verified in the running host: the open glyph window's
viewport resolves to a `YLighterWidget`. Tests: 53 pass.

## 2026-11-06 — Private documentation candidate

Added the product-specific light ProperDocs/MaterialX source/generated site and every-main source/output qualification workflow without private Pages operations. Pythonqtside preserves and relocates its authored compatibility guide and private planning source, updates the sdist path and verifies actual archive contents. Runtime products and native acceptance are unchanged.
