---
this_file: WORK.md
---

# Current round — Issue 255 post-release reconciliation

[fontlab-grablab v1.1.14](https://github.com/fontlabcom/fontlab-grablab/releases/tag/v1.1.14) is qualified at `0de4c56f07605560309e47b774c8060a246141ce`.

The F5/F6 and Save consumers, native smoke example and guarded Grab example use Fly; the wheel remains library-only.

206 runtime tests and all four complete changed-module gates pass (grab.py: 85.98% statements, 82.32% branches; the other three modules: 100%). All 36 documentation tests and exact 50-file parity pass. Genuine wheel/sdist ordinary cohorts each contain 29 compatible packages and match all 7 installed payload files; eight extracted-sdist consumer cases use stand-ins. Normal main/tag hooks, CI and actual downloads are qualified.

The source, artifact, ordinary external-install, release and download gates above are verified. This round reconciles their progress records after release; it changes no runtime source, installer, dependency declaration, generated documentation or immutable release asset. Menu scripts and the smoke example are sdist/source payloads. Native acceptance must execute the published sdist example against the genuine installed GrabLab 1.1.14 wheel and assert that library imports resolve to that wheel.

Remaining: After explicit D43 recovery and admission, qualify matching installed App/Fly/GrabLab lifecycle, F5/F6 and Save behavior, native glyph capture and restoration; execute the published sdist example examples/native_smoke.py against the genuine installed GrabLab 1.1.14 wheel, asserting library imports resolve to that wheel and recording loaded paths.

D43 native acceptance remains held and unproved. Issue 123 remains paused; existing private Pages holds and every unrelated acceptance task remain in PLAN/TODO. Prior WORK bytes are retained exactly in the private external delivery ledger, SHA256 `73c732904e341a330c34f225fbee2923923ee4481e8de7c6a21d56c68cb892fe`.
