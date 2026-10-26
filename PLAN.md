---
this_file: PLAN.md
---

# Plan

Issue 131 capture/SVG work is implemented and reviewed. Ordinary wheel and sdist
runtime bytes match source90c1842; 122 installed-wheel tests pass. FontLab9794
owned Font/Glyph-window, canvas and panel captures verify metadata and preference
restoration. Actual six composed SVG variations pass browser and visual checks.
The owner's later correction waives font creation/export and icon-font use.
Workspace verification/issue-131/requirements-audit.md records acceptance limits.

Remaining integration work predates and exceeds this bounded screenshot delivery:
whole-desktop capture, every panel/window configuration, dialog global-state
restoration, and the separate issue122 App smoke. Use owned fixtures through
verification/issue-104/fl-native.sh; offline tests cannot close native items.
