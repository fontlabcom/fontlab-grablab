---
this_file: WORK.md
---

## 2026-11-15 — Shared installer source alignment

Copied the reviewed shared installer exactly: dependency constraints and managed origins remain protected; inactive conditional dependencies are filtered before sibling execution in the resolver target Python. FontLab imports remain standard-library-only. Package identity, runtime APIs, dependency declarations, scripts, bundles and legal files are unchanged. Existing source-archive installer selection is retained. GrabLab contracts now require no-uv constraint refusal before script changes, preserve unlogged foreign scripts through uninstall, and verify managed-origin pins and declared optional metadata.

Focused checks: 46 passed in 0.40s. This qualifies the local source candidate only. Independent review, combined-main/full delivery gates, genuine release/downloads, installed provider closure and admitted FontLab/native workflows remain separate. No owner-folder installation or native operation ran.



# Current round — Issue 255 post-release reconciliation

## 2026-11-14 — Functional work order documented

Updated AGENTS, PLAN and TODO to prioritize useful functional changes and compatible package boundaries, with detailed testing deferred. Existing backlog and prior records are retained. Documentation preservation and policy consistency were checked; no runtime, installed or native checks ran in this documentation-only pass.

Next: reconcile capture/restoration and installer behavior with the matching App/Fly consumers; keep the installer synchronization decision and detailed installed/native capture pass open.

[fontlab-grablab v1.1.14](https://github.com/fontlabcom/fontlab-grablab/releases/tag/v1.1.14) is qualified at `0de4c56f07605560309e47b774c8060a246141ce`.

The F5/F6 and Save consumers, native smoke example and guarded Grab example use Fly; the wheel remains library-only.

206 runtime tests and all four complete changed-module gates pass (grab.py: 85.98% statements, 82.32% branches; the other three modules: 100%). All 36 documentation tests and exact 50-file parity pass. Genuine wheel/sdist ordinary cohorts each contain 29 compatible packages and match all 7 installed payload files; eight extracted-sdist consumer cases use stand-ins. Normal main/tag hooks, CI and actual downloads are qualified.

The source, artifact, ordinary external-install, release and download gates above are verified. This round reconciles their progress records after release; it changes no runtime source, installer, dependency declaration, generated documentation or immutable release asset. Menu scripts and the smoke example are sdist/source payloads. Native acceptance must execute the published sdist example against the genuine installed GrabLab 1.1.14 wheel and assert that library imports resolve to that wheel.

Remaining: After explicit D43 recovery and admission, qualify matching installed App/Fly/GrabLab lifecycle, F5/F6 and Save behavior, native glyph capture and restoration; execute the published sdist example examples/native_smoke.py against the genuine installed GrabLab 1.1.14 wheel, asserting library imports resolve to that wheel and recording loaded paths.

D43 native acceptance remains held and unproved. Issue 123 remains paused; existing private Pages holds and every unrelated acceptance task remain in PLAN/TODO. Prior WORK bytes are retained exactly in the private external delivery ledger, SHA256 `73c732904e341a330c34f225fbee2923923ee4481e8de7c6a21d56c68cb892fe`.
