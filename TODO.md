---
this_file: TODO.md
---

- [ ] Issue 271: independently review and integrate the generated installer through repository gates, verify exact-SHA CI/archives, and qualify macOS/Windows native execution after serialized admission.


## Next steps (prioritised, 2026-11-17)

1. P0 reconcile capture/restoration with the matching App/Fly consumers (source).
2. P1 Issue 255 installed lifecycle: F5/F6 and Save, native smoke `examples/native_smoke.py` from the installed wheel/sdist, glyph viewport capture against the matching App.
3. P2 whole-desktop capture and panel/window configurations (native).
4. HOLD dialog-based capture until QColorDialog/QFileDialog restoration is proved. Private Pages publication hold stays.

# Open tasks

- [ ] Reconcile capture/restoration and installer behavior with the matching App/Fly consumers; keep the installer synchronization decision and detailed installed/native capture pass open.

- [ ] Issue 255: After explicit D43 recovery and admission, qualify matching installed App/Fly/GrabLab lifecycle, F5/F6 and Save behavior, native glyph capture and restoration; execute the published sdist example examples/native_smoke.py against the genuine installed GrabLab 1.1.14 wheel, asserting library imports resolve to that wheel and recording loaded paths.

- [ ] Qualify current native glyph viewport capture against the matching App artifact; keep SVG/icon mode and restoration contracts.

- [ ] Native check of whole-desktop capture and every panel/window configuration (README lists these as integration checks; WORK.md lists global hotkey capture and desktop screens as open).
- [ ] Hold dialog-based capture cases until QColorDialog/QFileDialog global state restoration is proved (workspace AGENTS.md).
- [ ] Re-run `examples/native_smoke.py` from the installed wheel (the 2026-11-10 run passed from source against App origin/main; the wheel run is still open).

- [ ] Retain owned-fixture and restoration requirements before later native capture/export verification.

- [ ] Retain private Pages configuration and publication holds while native and owner-install gates remain separate.

## Deprioritised test-infrastructure rows

- [ ] Run the exact repository checks on the integrated source, obtain independent review, commit/push the scoped milestone and verify its remote head.
- [ ] After qualified main integration, inventory obsolete branches/files, preserve unique work and remove only proven stale items with recovery evidence.
- [ ] Qualify actual FontLab source installation separately from owned uv resolution tests; retain the explicit no-uv presence-only limitation.
- [ ] Qualify owned lifecycle/persistence for any historical helper before maintained activation. Dispositions and inactivity are pinned by `tests/test_historical_helpers.py`; the five preserved sources are not on GrabLab `main` (they remain in the workspace's confidential historical corpus), so the tests assert absence only. Next check: before activating one, copy its preserved source into an isolated lane and add owned lifecycle tests.
