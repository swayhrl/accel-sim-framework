# Track-A M2-M3 target progress

## Active goal and current review boundary

Goal: `M2_FUNCTIONAL_TRANSLATION -> M3_TIMING_REALISTIC_BASELINE ->
M1_M3_VM_BASELINE_CLOSEOUT`.

Current authorized gate: `G3-2 — real PTE L2/DRAM integration`
Status: `BLOCKED — correctness STOP`
Core SHA: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`
Framework handoff SHA: `198b32b278d30f04d113028cf4c328d457a134b9`

M2-RF and G3-1-RF are accepted historical prerequisites.  G3-2 local
integration demonstrated physical/non-recursive PTE traffic through real L2,
DRAM, and both interconnect directions, but a BFS trace later asserted because
its VPN exceeded the frozen generic 49-bit backend contract.  This is a hard
correctness STOP, not a performance result.  Evidence/review path:
`review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_BLOCKED.md`.

## G3-2 — real PTE L2/DRAM integration

Status: `BLOCKED — correctness STOP`

Completed before the stop: standalone out-of-order response-identity test;
standard rebuild; one-kernel cold PTE DRAM replay (4 PTE requests/responses,
zero misassociations, zero active VM state); BFS small-TLB replay that exercised
both lower-memory and L2-resident PTE responses.  Current work stopped when a
later BFS kernel issued a VPN outside the accepted 49-bit backend range and
triggered `vm_translation.cc:73`.

Core SHA: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9` plus uncommitted,
unpushable G3-2 review work.  Framework handoff SHA:
`198b32b278d30f04d113028cf4c328d457a134b9`.

Evidence: `review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_BLOCKED.md` and
`/tmp/g3-2-runtime/{one-kernel.log,bfs-small-tlb.log}`.

Next gate: none.  Do not start G3-3 until the address-namespace semantic
decision is reviewed and a repaired G3-2 reruns its acceptance suite.

## G3-1-RF — PTE address namespace injectivity

Status: `PASS — STOP FOR CHATGPT REVIEW`

Acceptance: former 64KB/2MB collision is explicitly non-aliasing; min/max VPN
boundaries across every supported page-size class/level are separated; PTE
physical/non-recursive and reserved-range contracts plus replacement-backend
seam pass; M1/G2/M2-RF regressions and cold one-kernel functional replay pass
and quiesce.  Evidence:
`review_packs/M3_TIMING_REALISTIC_BASELINE/G3_1_ADDRESS_NAMESPACE_FIX.md`.

Next gate: none.  Do not start G3-2 before ChatGPT review.

## M2-RF — independent review repair

| Gate | Status | Core / Framework | Completed acceptance and evidence |
| --- | --- | --- | --- |
| RF1 pending-waiter fast path | PASS | `3b93e243` / `e6b8d6b6` | registered `(key, UID)` bypasses before TLB ports/probes; `M2_RF_REPAIR.md` |
| RF2 directed non-reprobe/non-starvation | PASS | `3b93e243` / `e6b8d6b6` | `vm_m2_rf_pending_retry_test PASS`; exact A/B counts |
| RF3 clean counter semantics | PASS | `3b93e243` / `e6b8d6b6` | probe counters, lookup attempts, bypasses, merge/backpressure documented |
| RF4 MSHR observability | PASS | `3b93e243` / `e6b8d6b6` | page size, occupancy HWM, depth and lifetime aggregate/max added |
| RF5 kernel persistence | PASS | `3b93e243` / `e6b8d6b6` | focused boundary test and constructor/init/done source proof |
| RF6 review-pack completeness | PASS | `3b93e243` / `e6b8d6b6` | standard anchors/history/files/validation/issues present |
| RF7 cold regression + real replays | PASS | `3b93e243` / `e6b8d6b6` | M1/G2, cold build, one-kernel/LUD/BFS, 5/50 sensitivity in `/tmp/m2-rf-evidence/` |
| RF8 provisional G3-1 compatibility | PASS | `3b93e243` / `e6b8d6b6` | `vm_m3_g3_1_test PASS`; `8c613a35` stays provisional |

M2-RF is accepted historical evidence; its prior stop boundary is superseded
by the currently authorized G3-1-RF review fix.

## G2-0 — M2 entry/provenance check

Status: `PASS`  
Core SHA: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`  
Framework SHA: `8959f40ba88a28c6dffb7d5530064ea7c3710f2f`

Evidence: both Track-A worktrees are clean; Core HTTPS fetch confirmed
`research/hrl/vm-m1-m3-v0` at the M1 head; Framework was fast-forwarded to the
required handoff commit. Required M1 review evidence, long-lived specs, and all
M2/M3 target-mode materials were read.

Next goal: `G2-1`.

## G2-1 — deterministic mapper + finite L1/L2 TLB

Status: `PASS`  
Core SHA: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`  
Framework SHA: `8959f40ba88a28c6dffb7d5530064ea7c3710f2f`

Completed acceptance: deterministic present mapper; finite per-SM L1 and
single shared L2; `(ASID, VPN, page-size)` tags; deterministic replacement;
finite lookup ports; translation-before-data source gate; directed TLB tests;
standard build and diff check.

Evidence path: `review_packs/M2_FUNCTIONAL_TRANSLATION/G2_1_MAPPER_TLB.md`.

Runtime note: bounded functional LUD smoke attempts did not reach end
statistics in their 120/180-second local budgets. They are non-evidence, not
silently treated as PASS; no correctness diagnostic was emitted.

Next goal: `G2-2`.

## G2-2 — translation MSHR, same-key merge, and backpressure

Status: `PASS`
Core SHA: `740d96f8be80977c150ffc911063969cafd25b8f`
Framework SHA: `ed43cc81e3f5cea179281307b1ebb7f3e718e94b`

Completed acceptance: one active key; same-key merge; replay registration only
once; finite MSHR full backpressure; fill/release; active and quiescent
allocation/release and waiter-registration/wakeup conservation.

Evidence path: `review_packs/M2_FUNCTIONAL_TRANSLATION/G2_2_MSHR.md`.

Next goal: `G2-3`.

## G2-3 — fixed-latency PWQ and walkers

Status: `PASS`
Core SHA: `e579c40d907c201728331a1208c64bb18b869549`
Framework SHA: `ed43cc81e3f5cea179281307b1ebb7f3e718e94b`

Evidence path: `review_packs/M2_FUNCTIONAL_TRANSLATION/G2_3_PWQ_WALKERS.md`.

Next goal: `G2-4`.

## G2-4 — real stall/replay correctness

Status: `PASS`
Core SHA: `e7999554200760b31b4efe16d98e050370e1ea71`
Framework SHA: `4012be3606c300d11e7b34826ee1cb22b0852b93`

Directed replay/store/atomic/cross-page checks, a cold build, and a real
one-kernel functional replay pass.  The latter ends with 85 translation
requests, one MSHR/walk, waiter registration/wakeup 1/1, and no active
translation state.  Evidence: `review_packs/M2_RUNTIME_MEMORY_DIAG/`.

## M2-D — runtime memory diagnosis

Status: `PASS`
Core SHA: `e7999554200760b31b4efe16d98e050370e1ea71`
Framework SHA: `4012be3606c300d11e7b34826ee1cb22b0852b93`

Completed D0–D6: same-head 0/1/2 control, cold checkpoint isolation, effective
configuration/footprint, standalone controller, allocation phase diagnosis,
minimal fixes, and bounded post-fix regression.  Evidence:
`review_packs/M2_RUNTIME_MEMORY_DIAG/`.

## G2-CLOSEOUT — M2 full acceptance

Status: `PASS`
Core SHA: `e7999554200760b31b4efe16d98e050370e1ea71`
Framework SHA: `4012be3606c300d11e7b34826ee1cb22b0852b93`

Completed acceptance: all M1/G2 directed regressions; cold clean build;
disabled/ideal transparency; G2-4 real replay; regular/memory-path LUD and
irregular BFS functional replays; L2, MSHR, walker, and fixed-latency sweeps;
review-pack/provenance integrity.  Directed tests demonstrate finite MSHR/PWQ/
walker backpressure; all real functional replays quiesce with no loss,
duplicate wakeup, or duplicate store/atomic diagnostic.

Evidence: `review_packs/M2_FUNCTIONAL_TRANSLATION/README.md` and
`review_packs/M2_RUNTIME_MEMORY_DIAG/README.md`.

Next goal: `G3-0` (M3 entry snapshot/freeze).  M3 source semantics must not
change before its entry checks pass.

## G3-0 — M3 entry snapshot / M2 regression freeze

Status: `PASS`
Core SHA: `e7999554200760b31b4efe16d98e050370e1ea71`
Framework SHA: `a7020e603d6081f1f16f26b5ad1ead5ca17d7756`

Completed acceptance: M2 pack/source anchors reviewed; M1 and G2-1 through
G2-4 compact directed regressions rerun PASS; M2 transparency and real replay
evidence linked; M3 reference, specification, project specs, and paper
known/unknown boundary reread; parameter/evidence ledger recorded.

Evidence: `review_packs/M3_TIMING_REALISTIC_BASELINE/README.md`.

Next goal: `G3-1` (replaceable PTE backend and non-recursive request contract).

## G3-1 — PTE backend / request contract

Status: `PROVISIONAL / NOT ACCEPTED`
Core SHA: `8c613a356e6a146951cd59c9929046c6c4cfd856`
Framework SHA: `65a6e68d35cded7b78293b92a253e09c75c5aa36`

This already-pushed commit is retained without rewrite.  Its prior test result
is historical only until RF8 reruns the backend/no-recursion unit test on the
repaired M2 head.  No G3-2 work is authorized.

Evidence: `review_packs/M3_TIMING_REALISTIC_BASELINE/G3_1_PTE_BACKEND.md`.

Next authorized goal: `M2-RF / RF1`; `G3-2` is paused.
