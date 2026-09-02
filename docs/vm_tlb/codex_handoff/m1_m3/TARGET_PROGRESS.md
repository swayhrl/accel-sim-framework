# Track-A M2-M3 target progress

## Active goal and review-repair boundary

Goal: `M2_FUNCTIONAL_TRANSLATION -> M3_TIMING_REALISTIC_BASELINE ->
M1_M3_VM_BASELINE_CLOSEOUT`.

Current authorized gate: `M2-RF closeout — STOP FOR CHATGPT REVIEW`
Status: `PASS`
Core SHA: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`
Framework SHA: `e6b8d6b6034acd34f5f5176c3b0f4c3a865c09dc`

The independently reviewed M2 retry-pollution finding reopens M2.  G3-1 is
preserved as `PROVISIONAL`; its uncommitted G3-2 work was safely stashed and
all further M3 work is paused.  RF1-RF8 now pass and require independent
ChatGPT review before this goal can resume M3.  Evidence/review path:
`review_packs/M2_FUNCTIONAL_TRANSLATION/README.md`.

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

Next gate: no M3 gate is authorized.  Push both repositories, then STOP FOR
CHATGPT REVIEW.

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
