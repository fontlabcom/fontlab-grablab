---
this_file: CHANGELOG.md
---

# Changelog

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
