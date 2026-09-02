# Track-A M2-M3 target progress

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

Status: `BLOCKED`
Core SHA: `c1431e01f593719f9201d4ad4d7666bebead8a4f`
Framework SHA: `a63e243c350ea3628e9dab68620ee77982a6b0b9`

Directed replay/store/atomic/cross-page checks and the standard build pass.
Evidence: `review_packs/M2_FUNCTIONAL_TRANSLATION/G2_4_RUNNING.md`.

Blocked acceptance: three reproducible real-runtime attempts cannot reach
cache-path replay. A one-kernel diagnostic reproduced about 65 GiB RSS growth,
and a 10 GiB-address-space run deterministically throws `std::bad_alloc` just
after memory-subpartition initialization. This rules out full trace-list
preload but leaves no safe local run capacity for the required evidence.

Required external change: a simulator host with sufficient isolated memory, or
an approved diagnosis/fix for the pre-trace memory allocation. Do not advance
to M2 closeout or M3 before a completed VM-mode replay run passes.
