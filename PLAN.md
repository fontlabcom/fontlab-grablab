---
this_file: PLAN.md
---

# Plan

Authority: workspace `issues/122.md`. Open work is the three items in TODO.md: native
checks of whole-desktop capture, open-font canvas export and every panel/window
configuration; holding dialog-based capture cases until QColorDialog/QFileDialog global
state restoration is proved; and re-running the installed-wheel native smoke against the
issue-122 fontlabapp refactor. Each needs native evidence from owned fixtures and hidden
owned widgets via `verification/issue-104/fl-native.sh`; offline tests do not count.


## Issue 131 capture bundles

Source candidate adds collision-safe paired image names, embedded FontSnap-shaped
records and runtime JSON/Designer XML sidecars. Relevant host-free regressions
pass; root owns ordinary artifact verification and native acceptance with owned
widgets/panels. Qualify PythonQt hierarchy/content and reopen embedded PNG/SVG
metadata before treating this candidate as native accepted.
