# C10-A2 acceptance matrix

Goal: `C10A2_NAMED_BLOCKER_STATIC_CLOSURE`

This matrix is authoritative together with `C10A2_NAMED_BLOCKER_STATIC_CLOSURE.md`.

| ID | Requirement | PASS evidence | Not acceptable |
|---|---|---|---|
| A2-01 | Correct baseline | Framework starts from C10-A evidence branch and Core from `c27bf0e2...`; provenance recorded | unknown parent, reset/rebase, hidden local delta |
| A2-02 | No heavy execution | no simulator/build/link/workload/C5/large trace work | any compile/link/load that competes with Window A |
| A2-03 | Atomic registration failure | semantic reject leaves zero live descriptor image and explicit fallback/result reason | assert/abort for expected architectural rejection; prefix partial install |
| A2-04 | Lifecycle explicit | install/revoke states, all-replica ack, active ASID+epoch, revoke before reuse, wrap/quiesce rule | constructor-copy-only lifecycle; inferred ack count without per-replica state |
| A2-05 | Access classes wired | every production translation caller passes real READ/WRITE/ATOMIC or documented explicit internal class | relying on default READ in production; guessing from object labels |
| A2-06 | Read-only Segment eligibility | write/atomic never Segment-hit | store/atomic can bypass via Segment |
| A2-07 | Fair arm plumbing | F0-F4,F6-F9 runtime-selectable/manifest-valid; F5 blocked until real model; H0 unselectable | static TSV only with no runtime selector; H0 reachable as official arm |
| A2-08 | G96/G32 geometry | 96 groups=6 sets, 32 groups=2 sets, 16-way, 64KiB-only | fixed 48-set assumption or 768-group official geometry |
| A2-09 | Sub-entry generation | in-flight fill binds generation; shootdown changes generation; stale commit discarded | only checking current ASID/group at fill; stale fill can resurrect |
| A2-10 | Segment epoch distinct | Segment registration epoch and conventional translation generation are documented/handled without accidental conflation | one counter reused without lifecycle semantics |
| A2-11 | C10-A spine preserved | real PA, registration eligibility, N=8, HIT_FIRST/MISS_JOIN, both-miss lower launch, no retry re-probe | identity map, OBJECT_WEIGHT eligibility, wait-both, duplicate lower launch |
| A2-12 | Telemetry preserved | install/revoke, ordering, wait/backpressure, PTE wait, cross-layer compatibility remain observable | hit/miss-only reporting |
| A2-13 | Static source audit | production callsite ledger, selector validators, source assertions, transaction/generation model checks | undocumented production defaults or source-only claims presented as runtime proof |
| A2-14 | F5 handling | either real C9 F5 source model implemented coherently or hard blocker retained | legacy generic 128-entry PWC relabeled as F5 |
| A2-15 | Review pack | required C10A2 pack files and remaining blockers published | missing provenance or unnamed deferred work |
| A2-16 | Git discipline | explicit path staging/checkpoints, normal pushes, clean intended tree | `git add .`, `git add -A`, force push |
| A2-17 | Final label | one of the three authorized C10A2 statuses; compile/runtime still explicitly deferred | runnable/PASS/C5-ready claim without build/runtime |

## Mandatory final blockers that may remain after a successful C10-A2

Even `C10A2_STATIC_BLOCKERS_CLOSED_COMPILE_AND_RUNTIME_DEFERRED` must carry at least:
- final Core compile/link not run;
- standard-mode regression not run;
- new candidate focused runtime tests not run;
- post-delta telemetry output inspection not run;
- full workload/C5 not run;
- F5 blocker if the physical PWC model was not implemented.

These are C10-B responsibilities and must not be silently cleared by static analysis.