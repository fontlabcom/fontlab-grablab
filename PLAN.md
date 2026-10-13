---
this_file: PLAN.md
---

# fontlab-grablab

Migrate and modernize the complete screenshot/SVG capture package, preserving preference restoration.

Authority: workspace issues/101.md and PLAN.md. Task details: workspace .superpowers/sdd/issue-101/app-grab-brief.md.

1. Read original source, licenses and existing tests; record baseline and full source hashes.
2. Write meaningful behavior and packaging tests before changes.
3. Implement the grablab namespace with a modern hatch-vcs distribution; preserve native API and source features.
4. Build wheel and sdist, install each independently, audit licensing, completeness and distribution privacy.
5. Test applicable behavior from the installed wheel in live FontLab 9, including clear failure paths.
6. Review implementation independently and fix important findings with scoped verification.
7. Participate in three full project iterations and the cross-package integration audit.
8. Commit, push, tag and release reviewed artifacts; verify remote tag and downloadable assets.

Keep source repositories unchanged until destination verification and recovery evidence are complete. Never treat script submission or mocked tests as proof of native execution. Runtime-dependent operations must fail clearly outside FontLab. Source annotations and this_file headers accompany new code.
