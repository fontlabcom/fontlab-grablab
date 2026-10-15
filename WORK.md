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
