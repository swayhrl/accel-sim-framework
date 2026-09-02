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

Status: `RUNNING`
Core SHA: `740d96f8be80977c150ffc911063969cafd25b8f`
Framework SHA: `ed43cc81e3f5cea179281307b1ebb7f3e718e94b`

Current work: add a finite page-walk queue, finite walkers, fixed M2 service
latency, and completion into the existing MSHR fill/wakeup path.

Next goal: `G2-4` after all G2-3 checks pass.
