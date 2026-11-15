---
this_file: AGENTS.md
---

## Current scope — 2026-11-05

Issue 230 documentation reconciliation is current. Issue 123 remains paused. The qualified Issue 207 isolated candidate is separate from canonical source, installed artifacts, native acceptance and publication. Reconcile that candidate with later work before integration. Issue 210 specifies future architecture; Issue 211 retains unfinished follow-up checks. Retained dated receipts describe their original source and acceptance surface only.

Canonical source inspected for this proposal: `91a03a858f50`. This is a dated source observation, not an installed or native acceptance claim.

Keep capture and SVG/icon modes aligned with reviewed App APIs and current supported native bindings.

Qualify genuine distributions and owned native capture/rendering separately; preserve archived source and existing input provenance.

## Organization and checks

`src/` holds capture utilities; `examples/` shows their use; `tests/` covers offline behavior. `MIGRATION.json` records `legacy/source.tar.gz` at immutable Git revision `e74a8abc3888f2b829c2d3702f0b1f7fbeb6c0cb`; that path is historical, absent from the current tree and both distributions.

Run `uv venv --python cpython-3.11-macos-aarch64-none`, then `uv pip install -e ../fontlab-fontlabapp -e ".[test,svg]"`, then `./test.sh`. The wrapper uses `--no-sync`, so prepare the environment first. Build with `uv build`.

# Agent guidance: fontlab-grablab

## Owner priority: functional progress first (2026-11-15)

Future agents must make large, swift advances in working functionality. Prioritize visible user problems and useful, coherent feature increments. This instruction sets the work order and supersedes older requirements to complete exhaustive testing or build test infrastructure before ordinary implementation.

Keep packages coherent and compatible. Check shared APIs, imports and lazy aliases, data formats, dependency direction, object ownership and lifetime, installers, launchers and examples. Update affected providers and consumers together; preserve existing supported behavior and avoid dependency cycles.

During implementation, use the smallest meaningful smoke checks and focused regression tests for the changed behavior and affected package boundaries. Detailed testing, exhaustive coverage, broad performance studies and full acceptance matrices can follow in a later testing pass. Do not let test harnesses, sandbox/supervisor design, repeated unchanged suites, evidence machinery or review paperwork become the main project. Build such infrastructure only when a concrete functional defect or necessary safety constraint requires it.

Record deferred checks and known limits plainly. Do not call untested native, installed or published behavior verified. Keep existing mandatory delivery hooks, preservation rules, licence/privacy obligations, repository exclusions and explicit native/publication holds intact. When one action is held, continue other authorized functional work instead of expanding unrelated infrastructure.

Choose the next substantial useful feature or shared fix and carry its affected providers and consumers together. Timebox supporting investigation; once focused checks establish a usable increment, continue functionality work. Queue detailed testing for a later pass with its concrete remaining checks instead of letting test infrastructure displace product delivery.


## Live font testing in FontLab (owner instruction, 2026-11-10)

Test, verify and edit in the font that is open in FontLab 9. Don't hold back
because the owner might be working on it. Just work in it. If no font is open,
open a VFJ from `~/Desktop` first (File > Open, or `fontlab.flPackage(path)`
and `flWorkspace.instance().addPackage`). Those VFJs are for agents. Add glyphs,
kerning pairs, elements, contours, masters or anything else the test needs,
and save the files when that helps. This replaces older rules that required an
empty FontLab session or forbade editing open fonts. `fl-native.sh --mutating`
now runs with fonts open (`FL_REQUIRE_EMPTY=1` restores the old check). The
serialized lock still applies: one native run at a time. Don't quit or restart
FontLab, and don't close fonts from Python, because that has crashed the host.

`grablab`: screenshot, widget/canvas SVG and PDF capture helpers for FontLab. Read the workspace AGENTS.md and DECISIONS.md first; this file adds repo rules only.

## Rules

- `import grablab` must stay host-free; native APIs load only when `Grab` is requested. Keep imports lazy; offline tests depend on it.
- Capture calls temporarily change OpenGL, outline thickness, pixel rendering and the dark-glyph preference. Every change is restored in `finally`, including alternative-view toggles. Any new capture path needs a failure-path restoration test.
- Requires `fontlab-fontlabapp>=1.2.0`; its supported `qt.views.GlyphWindow` adapter resolves direct and named-child viewports. Use a qualified ordinary App artifact in isolated acceptance environments.
- `MIGRATION.json` and the retained BSD-3-Clause notices record the source files. Preserve its Git-history recovery revision and hashes; do not restore the removed archive into current source.
- Source sdists include the four current `Scripts/GrabLab` scripts and byte-exact `install.vfpy`; wheels remain library-only. The source override explicitly requests App >=1.2.0, Fly >=1.3.0 for authored consumers and Darwin Quartz >=10. The library-only wheel keeps App as its runtime dependency. With uv, the installer resolves the full declared requirement list; its no-uv fallback remains presence-only; native capture/installation and private Pages remain separate and held as applicable.

## Commands

- Setup: `uv venv --python cpython-3.11-macos-aarch64-none && uv pip install -e ../fontlab-fontlabapp -e '.[test]'` (verify with `lipo -archs`).
- Tests: `./test.sh` (= `uv run --no-sync python -m pytest "$@"`; `--no-sync` means the environment above must already exist). Build: `uv build`.

## Host rules that apply here

- Never mutate user-open fonts, persistent preferences or the Output panel. Native checks use owned fixtures and hidden owned widgets, destroyed afterwards, via `verification/issue-104/fl-native.sh`.
- Do not read Qt property values generically (`QSvgRenderer.currentFrame` without a loaded document segfaults FontLab). Use class-level lookup or `indexOfProperty`.
- A Python exception escaping a `paintEvent` while a `QPainter` is active crashes FontLab: wrap paint bodies in try/except, end the painter in `finally`.
- Convert native widget lists (`topLevelWidgets()`, `allWidgets()`, `findChildren`) with GC disabled; prefer direct accessors such as `fontlab.MainWindow()`.
- No unary minus on PythonQt wrappers (`-QPoint`, `-rect.topLeft()`); negate components.
- PythonQt does not convert enums implicitly; some overloaded constructors take positional arguments only, others keywords only. Check the stub.
- `QApplication.primaryScreen` is a property: use `QApplication.screens()[0]`.
- `QColorDialog`/`QFileDialog` touch process-global state (NSColorPanel, lastVisitedDir). Hold dialog-based capture cases until owned restoration is proved; `DontUseNativeDialog` alone is insufficient.
- FontLab resolves relative save paths against its own cwd: always pass absolute paths.
- Disconnect signals before `deleteLater()`/close.

## Proof and git

- Offline tests (the 7 regression tests) are not native proof. Whole-desktop capture, open-font canvas export and every panel/window configuration are unproven; do not claim them.
- The canonical checkout is editable-installed into the owner's FontLab: preserve it and use an isolated successor for the current task. Do not move or re-create `v0.2.*` tags.

## Milestones and delivery

Read [PLAN.md](PLAN.md), [TODO.md](TODO.md) and [WORK.md](WORK.md) before work.
Make the smallest complete MVP for one named acceptance task. Find all callers,
tests, fixtures, exports and documentation first. Use graph impact before source
symbol edits; confirm stale or unknown graph results against current source.
Keep product work in isolated successors and preserve the owner's checkout.

Run this repository's exact checks and the unchanged 80% gate for each complete
changed production module. Use an independent review before a milestone commit.
Under the current owner task, commit and push reviewed, passing milestones;
verify remote heads rather than inferring delivery from local tracking refs.
Before main integration, reconcile concurrent work and all consumers, run graph
change analysis and repeat the required acceptance on the combined source.

Before removing obsolete branches or files, prove integration, retain recoverable
unique work and check fresh owner/worktree attachments. Preserve sealed reports,
licences, archives and private data. Do not rewrite history by implication.
Remove verified completed work from PLAN/TODO and record scoped evidence in
CHANGELOG. Keep implemented-only native/artifact checks open in TODO. Issue 123
remains paused; no instruction here authorizes driving the owner's FontLab,
installing into its user folder or publishing a site.

## Private source/build-only documentation

Author pages under `src_docs/md` and use the separate hash-locked docs environment with `sh src_docs/build.sh`. Generated `docs` is immutable output. The main workflow qualifies direct source/output lineage and full ignored-output parity. Twelve private P/L operations remain owner-held; no Pages request or permission belongs here. Preserve runtime sources and native boundaries.

## Integration rounds

After each round of important changes, integrate it into `main` and upstream:
fetch `origin/main`, build the change on top of it in an isolated branch or
worktree, and resolve conflicts by keeping both our work and teammates' work.
Never discard upstream commits, and never force-push. Run the repository's
checks on the merged result, then push to `origin main`. Record the change in
CHANGELOG.md, move verified-solved TODO.md items into CHANGELOG.md, update
PLAN.md, and continue with the next TODO.md item until the list is clear.
`install.vfpy` is shared: keep it byte-identical in every installer repository.

## Agent workflow (Issue 250, 2026-11-10)

- Plan with `superpowers:subagent-driven-development`: one fresh implementer per task, a separate read-only reviewer, then the controller runs the gates and commits.
- Send bulk, well-specified work to Codex via the `codex-delegate` skill (`node ~/.agents/skills/codex-delegate/scripts/relay.mjs --brief BRIEF --cd WORKTREE`, in the background). Use `claude-delegate` or `cursor-delegate` for second opinions or independent lanes. Delegates never commit, push or tag.
- Work in a fresh worktree of `origin/main` on the workspace data volume; never pull, switch or reset the owner checkout. Merge `origin/main` again before pushing, keep both sides' CHANGELOG/PLAN/TODO entries, rerun the full suite, lint and graph change analysis, push through the pre-push hook where one is installed (never force), verify the remote SHA and the CI run where a workflow is configured. Held private Pages operations (workspace D41) stay held.
- Release: tag the next semver above the latest tag and publish a GitHub release. Install released, gated packages into `~/Library/Application Support/FontLab/FontLab 9/` and test live in FontLab 9. This owner route (Issue 250) supersedes, for released packages only, every older line in this guide that forbids installing into the FontLab user folder or its site-packages, owner-managed editable installs, or starting FontLab for a live test (the owner's canonical editable checkouts themselves stay owner-managed): record the previous installed distribution first so it can be restored, and never touch FontLab preferences (owner fonts and documents: see live font editing below); native work goes through the workspace `verification/issue-104/fl-native.sh` gate.
- Documents: CHANGELOG holds verified completed work; TODO only open or to-verify items; PLAN the major remaining changes; WORK.md the current round only (older WORK bytes are archived on the owner's workspace data volume, not public).
- Native defects: issues at github.com/fontlab/fl; fixes as pull requests to fontlab/Proteus, fontlab/FontGate or fontlab/pyfontgate. Never commit to the local C++ snapshot.
- Older "work directly" or "no delegation" lines in this guide are superseded by this section (Issue 250).
- Live font editing (owner, 2026-11-10; workspace D44): test, verify and edit the font open in FontLab 9, and do not stop because the owner might be working in it. Open a VFJ from `~/Desktop` first (those files are for agents), then add glyphs, kerning pairs, elements, contours, masters or whatever the test needs, and save them freely. This supersedes, for live testing, every older line here that forbids mutating owner fonts or documents or requires owned fixtures only. FontLab preferences, Output folders and global update queues stay untouched. Keep the serialized host lock (`fl-native.sh`, one native run at a time; `--mutating` now allows open fonts); do not quit or restart FontLab and do not close fonts from Python, which has crashed the host.
