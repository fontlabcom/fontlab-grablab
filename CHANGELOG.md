---
this_file: CHANGELOG.md
---

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
