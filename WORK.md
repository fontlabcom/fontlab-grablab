---
this_file: WORK.md
---

# Migration evidence

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
