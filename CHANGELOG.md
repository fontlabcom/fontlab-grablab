---
this_file: CHANGELOG.md
---

# Changelog

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

## Unreleased

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
