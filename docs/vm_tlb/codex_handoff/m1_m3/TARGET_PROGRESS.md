# Track-A M2-M3 target progress

## Active goal and current review boundary

Goal: `M2_FUNCTIONAL_TRANSLATION -> M3_TIMING_REALISTIC_BASELINE ->
M1_M3_VM_BASELINE_CLOSEOUT`.

Current Goal boundary: `G3-3 — generic PWC (closed)`
Completed sub-gates: `G3-2A PASS / CASE A`, `G3-2B PASS`,
`G3-2C PASS`, `G3-3 PASS`
Status: `PASS — STOP FOR CHATGPT REVIEW BEFORE G3-4`
Core SHA: `1b18b3c5da6e5ba22e4a03c20e3adce498311336`
Framework handoff SHA: `6c73a24e433f0eab2b60ec26df597649aa1a60be`

M2-RF and G3-1-RF are accepted historical prerequisites.  G3-2B applies the
approved generic trace-width decision without altering a raw/coalesced SimVA:
generic backend width is configurable, current M3 is 56 bits, 49-bit remains
directed-tested, and outside-width keys still hard-stop.  PTE requests now
traverse the real interconnect/L2/DRAM path with UID-correct response return.
G3-2C replaces flat full-VPN PTE identities with a generic balanced radix
prefix identity and validates the real PTE path again.  G3-3 adds a generic,
intermediate-only PWC with OFF/FINITE/IDEAL modes.  These are explicitly
`MODELING_DECISION`s; neither is a claim about target-paper or commercial-GPU
page-table organization.  Evidence/review path:
`review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2C_G3_3_HIERARCHY_PWC_CLOSEOUT.md`.

Next gate: none.  Do not begin G3-4 until ChatGPT review.

## G3-2B — generic trace-width extension and G3-2 closeout

Status: `PASS — STOP FOR CHATGPT REVIEW BEFORE G3-3/PWC`

Core `965bd8e1` makes generic PTE backend width configuration-derived and
sets the generic default to 56 bits.  The 56-bit application identity range is
`[0,2^56)` and the disjoint synthetic PTE reservation is
`[2^56,2^56+2^46)`; overflow, range, and all eight namespace boundaries are
directed-tested.  The retained 49-bit configuration keeps the original G3-1
namespace proof.  The exact old offender `0xfffdc0000000c0` completes unchanged
as raw/coalesced SimVA and identity-like SimPA; a >56-bit key is rejected.

The non-semantic `TRACE_ENCODING_OBSERVATION` covers all 12 complete-BFS
transactions at/above `2^49`: none is treated as canonical 49-bit and no
distinct observed values collapse under lower-49-bit projection.  Complete
default BFS exits normally with PTE `28/28`, DRAM/L2-only `20/8`, zero response
misassociation and final active MSHR/PWQ/walkers `0/0/0`.  One-kernel cold LUD
is `4/4` DRAM PTE responses; LUD disabled/ideal transparency has identical
cycle sequence.  All M1/M2/G3 directed tests pass after release build.

Framework handoff SHA: `f8a272b9b6d59f25b0a2ba8a35ee0b207ec58b64`.
Evidence: `review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2B_TRACE_WIDTH_AND_CLOSEOUT.md`.

Next gate: none.  G3-2 is closed; stop for ChatGPT review before G3-3/PWC.

## G3-2A — address provenance diagnostic

Status: `PASS — CASE A; STOP FOR CHATGPT ARCHITECTURE REVIEW`

Completed D0–D5 using the local uncommitted G3-2 path solely for observation.
The first functional offender is BFS kernel 7, `STG.E.SYS` PC `0x250`, raw
trace lane address `0x00fffdc0000000cd`, ordinarily coalesced to global
`SimVA=0xfffdc0000000c0` (56 bits).  Its 64KB VPN violates the current generic
49-bit backend assertion.  The same coalesced numeric request is accepted and
the trace completes in VM_DISABLED and VM_IDEAL_IDENTITY controls.  LUD and
the bounded BFS corpus sent no local or param-local transaction to the VM hook.

Core SHA: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9` plus local,
uncommitted, unaccepted diagnostic/G3-2 work.  Framework handoff SHA:
`971b1f46b74ed5eaaf4447d416a47f0e3e22d733`.

Evidence: `review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_ADDRESS_PROVENANCE_DIAG.md`,
supporting TSVs in that directory, and indexed `/tmp/g3-2a/` artifacts.

Next gate: none.  Do not resume G3-2 or start G3-3 until ChatGPT makes the
generic address-width/backend semantic decision.

## Historical G3-2 hard stop (superseded by G3-2B)

Status: `HISTORICAL — resolved by G3-2B`

Completed before the stop: standalone out-of-order response-identity test;
standard rebuild; one-kernel cold PTE DRAM replay (4 PTE requests/responses,
zero misassociations, zero active VM state); BFS small-TLB replay that exercised
both lower-memory and L2-resident PTE responses.  Current work stopped when a
later BFS kernel issued a VPN outside the accepted 49-bit backend range and
triggered `vm_translation.cc:73`.

Core SHA: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9` plus uncommitted,
unpushable G3-2 review work.  Framework handoff SHA:
`971b1f46b74ed5eaaf4447d416a47f0e3e22d733`.

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
