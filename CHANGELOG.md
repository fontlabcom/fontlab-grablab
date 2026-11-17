---
this_file: CHANGELOG.md
---

## Unreleased

- Task-list cleanup (Issue 258): closed the shared-installer rows and the installer-sync-set decision. Evidence: `install.vfpy` is the fontlab-instamix stub (entry below); v1.1.16 is released at `90940e7`. Dropped the genuine-distribution matrix and docs-lineage rows as paperwork; test-infrastructure rows moved to the end of TODO.md.
- `install.vfpy` is now the short fontlab-instamix stub. It installs
  fontlab-instamix from PyPI when it is missing, then installs this checkout from
  its `[tool.fontlab-install]` table. The large legacy installer is gone.
- `tests/test_install_contract.py` keeps the declaration check and tests the stub and sdist;
  `tests/test_install_lifecycle.py` (legacy installer internals only) is removed.
- README describes the stub install.

## 2026-11-15 — Shared installer source alignment

Copied the reviewed shared installer exactly: dependency constraints and managed origins remain protected; inactive conditional dependencies are filtered before sibling execution in the resolver target Python. FontLab imports remain standard-library-only. Package identity, runtime APIs, dependency declarations, scripts, bundles and legal files are unchanged. Existing source-archive installer selection is retained. GrabLab contracts now require no-uv constraint refusal before script changes, preserve unlogged foreign scripts through uninstall, and verify managed-origin pins and declared optional metadata.

Focused checks: 46 passed in 0.40s. This qualifies the local source candidate only. Independent review, combined-main/full delivery gates, genuine release/downloads, installed provider closure and admitted FontLab/native workflows remain separate. No owner-folder installation or native operation ran.


## 2026-11-14 — Functional work order documented

- Added the owner's functional-progress-first guidance and repository-specific priorities, including cross-package compatibility and a later detailed testing pass. Existing mandatory hooks, holds and unfinished work remain in force.
- This change updates guidance and planning only; it establishes no new runtime, installed, native or release result.

## 2026-11-13 — Issue 255 verified release qualification

- [fontlab-grablab v1.1.14](https://github.com/fontlabcom/fontlab-grablab/releases/tag/v1.1.14) is released at `0de4c56f07605560309e47b774c8060a246141ce`. Reviewed main/tag delivery, applicable CI and actual downloads match the qualified artifacts.
- The F5/F6 and Save consumers, native smoke example and guarded Grab example use Fly; the wheel remains library-only.
- 206 runtime tests and all four complete changed-module gates pass (grab.py: 85.98% statements, 82.32% branches; the other three modules: 100%). All 36 documentation tests and exact 50-file parity pass. Genuine wheel/sdist ordinary cohorts each contain 29 compatible packages and match all 7 installed payload files; eight extracted-sdist consumer cases use stand-ins. Normal main/tag hooks, CI and actual downloads are qualified.
- Ordinary external installation is qualified; installed FontLab/native acceptance remains unproved under D43. Menu scripts and the smoke example are sdist/source payloads. Native acceptance must execute the published sdist example against the genuine installed GrabLab 1.1.14 wheel and assert that library imports resolve to that wheel.

## 2026-11-13 — Fly imports for authored consumers (Issue 255)

- Route the F5/F6 and Save scripts, native smoke example and guarded Grab example
  through Fly App/Qt aliases. Preserve App wildcard exports, deferred Save capture,
  hotkey timestamp/modal/canvas behavior and smoke cleanup. Library imports stay
  canonical; GrabLab itself still uses `grablab`.
- Declare `fontlab-fly>=1.3.0` in the source installer's consumer requirements,
  alongside App and Darwin Quartz. The library-only wheel keeps its App dependency;
  shared `install.vfpy` bytes and historical provenance remain unchanged.
- Eight new offline consumer cases failed before migration. All 206 runtime tests
  pass on arm64 CPython 3.11.14 afterward, including owned success/failure cleanup
  and installer metadata/argv checks. Each complete changed production module
  passes the 80% statement/branch gate with zero exclusions: hotkey/save/smoke
  100%; grab.py 85.98% statements and 82.32% branches. Ruff retains the same 31
  inherited findings; none added. Locked external docs preview and all 36 docs
  tests pass. This qualifies source and stand-ins, not native capture or artifacts.
- Ordinary Fly 1.3.0/App 1.2.15 imports preserve App and PrefLib/hotkey module
  identity. Native Qt identity uses a stand-in with `__spec__ = None`; no native
  provider or real handler was activated. GrabLab remains source-only in this probe.
- Independent source review reports SPEC PASS / QUALITY PASS. Controller reruns
  pass 206 runtime tests and all four strict module gates; the exact-lock docs
  build, 36 documentation tests and 50-file clean-rebuild parity pass. Final
  containing-commit output, artifact installation and native proof remain separate.


## 2026-11-12 — D46 documentation pass (Issue 250)

- Landed on `main` this session: `e3644bd` (2026-11-10 entry), `e71be0f` (historical helper dispositions, 2026-11-11), `3d5209b` (install-contract fake matches installed App metadata, owner change) and `3022a89` (TODO: decide whether Grablab joins the `install.vfpy` sync set). No source changed in this pass.
- Grablab's `install.vfpy` (a46f3d19) was deliberately not synced to App's canonical `install.vfpy` (Issue 254 propagation covered App, pens, fontport, echopy, fly, glyport and scriptmix); the decision stays an open TODO row.
- `WORK.md` is a short status stub; its earlier 43,685-byte content (SHA-256 `0a8a5eea588b92b5b112242189e6645081f65f288f348b5a1b4e5e58116eb4a3`) stays archived on the workspace data volume.

## 2026-11-12 — install contract fake matches installed App metadata (owner change)

- The owner changed `tests/test_install_contract.py`. The `distribution` fake now compares normalised names (`i.norm`), as `install.vfpy` does. It also reports `INSTALLER` as `install.vfpy`, because App was installed earlier from its sibling checkout and uv must not look it up again. Landed by lander1 from the owner's working-tree edit; no other bytes changed.

## 2026-11-11 — historical helper dispositions pinned (Issue 250)

- New `tests/test_historical_helpers.py`. Each of `copy_statusid.py`, `copy_statusid2.py`, `print_menu.py`, `print_uimenu.py` and `ui_hider.py` must keep exactly one README disposition line. None may appear under `Scripts`, the wheel packages, the sdist `only-include` inputs or `[tool.fontlab-install]` script folders, and neither `install.vfpy` nor `MIGRATION.json` may name them.
- The preserved sources are not on GrabLab `main`; they remain in the workspace's confidential historical corpus. The tests therefore assert absence, not content.
- Mutants: a `Scripts/Help Dev/ui_hider.py` file, a `src/grablab/legacy/print_uimenu.py` file, a removed `print_menu.py` README line and a `copy_statusid` mention in `install.vfpy` each fail 1 test (7 pass).

## 2026-11-10 — native smoke passed against App main (Issue 250)

`examples/native_smoke.py` ran inside FontLab 9 through `fl-native.sh` with
`sys.path` swapped to App origin/main and this source: it printed "Native PNG and
SVG passed" (widget capture wrote a PNG and an SVG to a temporary folder). The
installed-wheel run remains open. No code changed.

## 2026-11-10 — live font editing rule (Issue 250, D44)

- AGENTS.md: agents test and edit the font open in FontLab 9, starting from the Desktop VFJs, and may save them.

## 2026-11-10 — install.vfpy always reinstalls scripts and dependencies

- Every install copies all files from `Scripts/` afresh and replaces any file
  already at the same path. A symlinked script folder is replaced by a real
  folder; the link target is never written. A directory where a script file
  belongs is still refused.
- Required packages are installed on every run. Packages that no package
  index carries (the fontlab-* packages, pythonqtside) are installed from
  checkouts beside this one through their own `install.vfpy`, once per run
  and safe against cycles. uv receives every other requirement, so version
  ranges, markers and extras are enforced. Without uv, sibling checkouts are
  still installed and only the remaining missing requirements are reported.
- The installer is byte-identical across all eleven installer repositories.

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

## 2026-11-10 — Issue 250 documentation round

- AGENTS.md describes the delegation, integration and release workflow.
- WORK.md reset to the current round; the earlier bytes are archived on the owner's workspace data volume, not public.

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

Added the product-specific light ProperDocs/MaterialX source/generated site and every-main source/output qualification workflow without private Pages operations. Runtime products and native acceptance are unchanged.


## 2026-11-07 — Exact frontend notices and English search assets

Added exact upstream frontend notices and source-map provenance for the existing MaterialX 10.1.8 payload. Explicit English configuration and a small build hook reject language, corpus, reference, asset-set or hash drift before omitting the 35 unused language helpers. All nine retained core assets, original product legal files, guides, catalogue rows, media, runtime and dependency/build locks are preserved.

The strict site build and all 35 documentation tests pass. The complete new hook has 100% statement/branch coverage; real Git staging, checkout and archives preserve exact legal bytes. An independently installed matching lock reproduces all 50 output bytes and modes. Existing immutable source/output, epoch, concurrency and full-parity workflow checks remain active. Browser and independent review evidence are separate from these local checks.

Private Pages configuration, grants, requests and publication remain owner-held; this source follow-up adds none.
No product release or installation is claimed. Prior ordinary artifacts remain bound to their recorded revisions; a later Git revision changes genuine hatch-vcs metadata. Full current source archives include these documentation additions; no unchanged-sdist or whole-wheel identity is asserted. Native acceptance and owner installation remain separate.


## 2026-11-07 — installed icon path-tuple inventory refinement

The current HTML/CSS contains 45 distinct ordered SVG path tuples. A complete scan of the four installed MaterialX icon families finds 43 exact installed matches and two unmatched Lucide tuples, refining the earlier known-candidate inventory. The additional installed match is the Font Awesome version caret-down. Its existing CSS header and full notice retain Font Awesome Free 7.1.0, Fonticons and CC-BY-4.0 icon attribution. The official NPM caret SVG has different raw path bytes; no unmodified-primary SVG, whole-geometry or optimizer-recipe equivalence is claimed. The two unmatched Lucide tuples retain their pinned SCSS source attribution.

A new actual-output regression derives these counts and checks installed matches, unmatched CSS references and the caret header. It fails against the prior 42 count and passes with the corrected metadata. All 36 current documentation tests pass; full strict and independent exact-lock builds match every output byte and mode. Only the legal paragraph, corresponding inventory and legal search row change in the site. Runtime, packaging, generators, vendor assets, full notices, existing guidance and the Fly search fix remain exact. Fresh browser verification and independent review are recorded separately. No private Pages operation, delivery, installed-product upgrade or native acceptance is claimed.


## 2026-11-07 — Release-note attribution correction

Removed the Pythonqtside-only relocation and sdist sentence from the Task11 documentation entry. All history before that entry remains byte-exact. The existing documentation checks and normal installed pre-push gate pass; WORK.md records their scope and limits.


## 2026-11-07 — Resolve complete source-installer requirements with uv

The source installer now sends every declared requirement unchanged to uv,
including versions, markers and extras, when uv is available. It retains empty
requirements, both Python target routes, normal satisfied-package behavior and
the explicit limited presence-only fallback without uv. No runtime dependency
or custom requirement parser is added.

All 189 source tests pass; the complete installer reaches 95.77% combined
statement/branch coverage with no exclusions. Owned offline resolver experiments
prove too-old upgrade, false-marker omission, requested extras, satisfied no-op
and real failure/payload preservation on both target routes. Genuine precommit
wheel/sdist and ordinary tests qualify their recorded candidate bytes separately
from final delivery. Native/owner installation, full G2 and private Pages remain
separate. All earlier history, including the qualified owner report, is retained.
