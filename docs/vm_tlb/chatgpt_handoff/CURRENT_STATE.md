# Current state

## Track A status after independent M2 review

`M1_VM_CORE_FOUNDATION`: **PASS**.

Codex completed and pushed an M2 closeout at:

- Core M2 source: `e7999554200760b31b4efe16d98e050370e1ea71`
- Framework M2 source/dependency repair: `4012be3606c300d11e7b34826ee1cb22b0852b93`
- Framework M2 closeout/report head: `a7020e603d6081f1f16f26b5ad1ead5ca17d7756`

The prior 32–65 GiB runtime-memory blocker was correctly diagnosed as a stale Framework/Core C++ layout artifact and fixed through Framework dependency generation; a subsequent one-line Core stall-classification fix preserves VM semantics. Cold-build disabled/ideal transparency, directed tests, and real functional LUD/BFS replays pass.

However, independent ChatGPT review has **reopened M2 before further M3 work** because the current waiting-request retry path re-probes L1/L2 TLBs every cycle before noticing that the same waiter UID is already registered in the translation MSHR. This artificially consumes TLB ports and pollutes access/miss statistics as PTW latency grows.

Concrete evidence already present in the M2 closeout: BFS keeps 7 walks while increasing fixed walk latency from the baseline to 50 cycles increases reported L2 misses from 42 to 357. This makes the current counters/timing path unsuitable as the basis for M3 realistic PTW or later Segmentation-paper L2-TLB miss-rate analysis.

## M3 status

G3-0 read-only entry/freeze completed.

Before this independent review update reached the Codex window, one G3-1 Core commit was already pushed:

`8c613a356e6a146951cd59c9929046c6c4cfd856` — `vm(m3): add replaceable PTE backend contract`

Do not rewrite/force-push it. Treat it as **PROVISIONAL / NOT YET ACCEPTED**. No G3-2 or later M3 semantic work is authorized until M2-RF below passes and is reviewed.

## Current authorization

Execute only:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M2_REVIEW_FIX_BEFORE_M3.md`

Active gate:

`M2-RF — pending-retry semantics, observability, and review-pack completion`

Key required repairs:

- an already registered pending waiter must not repeatedly consume/probe L1/L2 TLB ports while waiting for the same walk;
- add exact non-reprobe/non-starvation directed evidence;
- make TLB miss-rate event semantics clean/separable from retries/backpressure;
- close MSHR observability gaps needed for research analysis;
- provide explicit kernel-boundary TLB-persistence evidence;
- complete the M2 review-pack minimum files required by `AGENTS.md`;
- rerun cold M1/M2 regressions and fixed-latency sensitivity;
- rerun the provisional G3-1 PTE-backend tests after the M2 repair.

After M2-RF, STOP for ChatGPT review before G3-2.

## Frozen source anchors

Core/GPGPU-Sim:

- baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- G2-1: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`
- G2-2: `740d96f8be80977c150ffc911063969cafd25b8f`
- G2-3: `e579c40d907c201728331a1208c64bb18b869549`
- M2 closeout source: `e7999554200760b31b4efe16d98e050370e1ea71`
- provisional G3-1: `8c613a356e6a146951cd59c9929046c6c4cfd856`

Framework/Accel-Sim:

- baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- M2 dependency fix: `4012be3606c300d11e7b34826ee1cb22b0852b93`
- M2 closeout: `a7020e603d6081f1f16f26b5ad1ead5ca17d7756`
- G3-0 entry freeze: `65a6e68d35cded7b78293b92a253e09c75c5aa36`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Frozen modeling decisions

- trace address is simulator `SimVA` by modeling contract;
- translation produces `SimPA`; preserve both identities;
- identity bring-up keeps `SimPPN = SimVPN`;
- translation is on approved coalesced transactions before real L1D/data access;
- M1-M3 study resident-memory translation only: no page fault/migration/UVM oversubscription;
- TLB persists across ordinary kernels in one simulated context unless invalidated/reset;
- M2 uses functional zero-hit-latency TLB lookup with finite ports; timing-realistic configurable lookup latency is an M3 requirement, not a paper-exact M2 claim;
- PTE requests in M3 are physical and non-recursive.

## STOP boundary

Do not begin G3-2 real PTE L2/DRAM integration until M2-RF is complete and independently accepted.

Stop on baseline transparency regression, request loss, duplicate wakeup/store/atomic, retry-induced starvation that cannot be resolved within the frozen semantics, or a conflict between the M2 repair and the provisional G3-1 backend contract.
