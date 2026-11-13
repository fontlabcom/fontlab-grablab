---
this_file: WORK.md
---

# Current round — Issue 255 authored consumers

The earlier short WORK status is retained in this round's private external
baseline evidence. Older history remains in CHANGELOG and the existing archive.

Migrated the two provider-consuming menu scripts, native smoke example and
`grab.py` main example to Fly. Source consumer requirements now include
Fly >=1.3.0; library App requirements and shared installer bytes remain unchanged.
Current teaching and exact installer tests agree with that distribution boundary.

Verification: eight new consumer cases failed before migration; 206 runtime tests
now pass on arm64 CPython 3.11.14. Complete changed production module coverage has
zero exclusions: F5/F6 36/36 statements and 6/6 branches; Save 3/3 statements and
no branches; native smoke 19/19 statements and no branches; grab.py 374/435
statements (85.98%) and 135/164 branches (82.32%). The native-smoke result uses
stand-ins, including failure cleanup, rather than executing the native host.
Ruff 0.17.5 retains the same 31 inherited findings. Independent source review reports SPEC PASS / QUALITY PASS. Controller reruns
pass all 206 runtime tests and the same four strict module gates. The actual
hash-locked documentation build and all 36 documentation tests pass; a second
clean rebuild has exact 50-file parity. Final containing-commit output and
ordinary artifacts remain separate checks.

An ordinary released Fly 1.3.0/App 1.2.15 environment confirms App, legacy PrefLib
and hotkey module identity. Native Qt routing preserves a stand-in's identity
and null import spec. Explicit source origin checks keep the GrabLab probe
separate from ordinary GrabLab distribution acceptance.

Scoped pre-edit graph analysis had 618 nodes/1,268 edges. Hotkey impact was
UNKNOWN (dynamic callback references unresolved), and external Application was
not indexed. AST-grep confirms the actual F5/F6 registrations, Save signal and
Application call sites. Process tracing is capped: 31 entry points unexplored,
34 callees skipped and eight walks cut. Missing graph edges are not absence
proof. Both graph locations are task-owned and extension installation is
load-only; shared exclusion/index bytes remained unchanged at the pre-edit check.
Final refresh has 634 nodes/1,290 edges; detect-changes reports 16 files,
17 symbols, zero affected processes and low risk. That result remains bounded
by the unresolved dynamic callbacks and capped process tracing above; source
inspection and stand-in behavior checks provide the missing consumer evidence.

Remaining: containing-commit artifact/docs qualification, then authorized
integration/release separately.
Native D43, private Pages and Issue 123 holds remain. No host handlers, native
capture, owner installation, commit or push occurred. Generated documentation
is a qualified controller preview until its containing-commit rebuild.
