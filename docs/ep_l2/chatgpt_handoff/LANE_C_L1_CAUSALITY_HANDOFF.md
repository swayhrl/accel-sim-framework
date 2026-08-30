# EP-L2 Lane C — L1 Causality / Headroom Handoff

Owner: dedicated Codex Window C.

## Objective

Determine whether observed L1D pressure is:

```text
1. an independent L1-local bottleneck,
2. mostly downstream backpressure from L2/DRAM,
3. or an upstream throttle that materially masks L2 opportunity.
```

Do not enlarge L1 capacity in this first stage. Keep hit-rate/capacity semantics fixed and vary only flow-control or bank throughput.

## Base source / isolation

Use the exact C7e source semantics used by the current formal D256 campaign. Create separate Lane C branches/worktrees/result roots; never modify Lane A or Lane B runtime directories.

Suggested branches:

```text
Core      hrl/ep-l2-l1-causality-v0
Framework hrl/ep-l2-l1-causality-v0
```

Initial experiments are **B0-Banked only**. Legacy does not need to be duplicated for this causal screening unless a specific anomaly requires a paired control.

## Workload screening set

Use these seven first:

```text
vectorAdd_4M
scan
spmv
convolutionSeparable
btree
sad
FWT_7_21
```

Rationale:

```text
vectorAdd   descriptor/lower positive
scan        strongest mixed L1 + descriptor + WAD + scheduler case
spmv        descriptor + per-address cap
convolution L1 line-allocation + descriptor
btree       merge-control workload
sad         L1-pressure / L2-light negative control
FWT_7_21    descriptor + L1 + bursty lower pressure
```

## Frozen L1 geometry

For all first-stage cells keep:

```text
capacity = 64 KiB
sets     = 4
ways     = 128
line     = 128 B
latency  = 20 cycles
```

No L1 capacity/associativity/line-size change is allowed.

## C1 — D256 + L1 META-HR

From the D256 C7e baseline change only:

```text
L1 MSHR       512 -> 1024
L1 merge cap    8 -> 32
L1 MissQ       16 -> 64
L1 banks        4 unchanged
```

Run the seven workloads above with B0-Banked.

## C2 — D256 + L1 BANK-HR

From D256 C7e baseline change only:

```text
L1 banks 4 -> 8
```

Keep MSHR=512, merge=8, MissQ=16 and all other parameters unchanged.

Run the same seven workloads.

## C3/C4 — D512 interaction cells

Do not start D512 cells until Lane B marks `D512-PREFLIGHT` DONE/PASS in the shared workboard and publishes an exact D512 branch/config identity.

Then run:

```text
D512 + L1 META-HR
D512 + L1 BANK-HR
```

on the same seven B0-Banked workloads.

Use Lane B's exact D512 semantics; do not independently create a second descriptor512 implementation.

## Experimental matrix

```text
                         L1 BASE       L1 META-HR       L1 BANK-HR
Descriptor 256          formal data    Lane C run       Lane C run
Descriptor 512          Lane B data    Lane C run       Lane C run
```

The new Lane C run count is initially:

```text
7 x 4 = 28 B0-Banked calibration runs
```

D256 cells may launch immediately; D512 cells wait only for Lane B's preflight handshake.

## Measurements

For every cell compare against the matching BASE descriptor configuration:

```text
cycles / speedup
L1D accesses/misses
L1D LINE_ALLOC_FAIL
L1D MissQ-full
L1D MSHR-entry-full
L1D merge-full
L1D RW-pending
L1 bank/latency conflict

L2 tag-way need/block
Line MSHR need/full/avg/p95/max
Descriptor need/pool-full/avg/p95/max
Per-address-cap check/block
WAD
payload
bank true contention
MissQ
L2->DRAM
scheduler
internal ReturnQ
DRAM->L2
successful DRAM bytes / BW
5K temporal pressure
```

Do not treat retry-event counts as unique-request probabilities.

## Causal classification

Use both performance and downstream movement:

```text
A. <~2% speedup and little L2/lower change
   -> L1 pressure mostly non-causal/symptomatic.

B. clear speedup with little L2/lower demand increase
   -> independent L1-local bottleneck.

C. clear speedup plus material increase in L2 descriptor/lower pressure
   -> L1 was throttling demand and masking L2 opportunity.

D. L1 events fall, speedup small, downstream scheduler/BW pressure rises
   -> bottleneck moved downstream; L1 was not ultimate ceiling.
```

Screening thresholds:

```text
<2%   weak
2-5%  moderate
>5%   strong enough to decompose
```

These are decision heuristics, not physical laws.

## Follow-up decomposition

Only for workloads with material sensitivity, perform one-at-a-time sweeps to identify the responsible L1 resource, e.g.:

```text
MSHR 512 -> 1024 only
merge 8 -> 32 only
MissQ 16 -> 64 only
banks 4 -> 8 only
```

Do not automatically run full one-at-a-time sweeps for insensitive workloads.

## Acceptance criteria

Lane C first-stage closeout requires:

```text
[ ] all new configs differ only in authorized L1 headroom variables
[ ] L1 capacity/tag geometry/latency are unchanged
[ ] exact source/config manifests retained
[ ] all runs COMPLETE_VALID with terminal invariants
[ ] D256 and D512 cells use the correct matching descriptor base
[ ] causal analysis reports performance and downstream movement together
[ ] no claim that raw L1 retry count alone proves a causal bottleneck
```

## Deliverables

Use a dedicated report and review pack:

```text
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/review_packs/L1_CAUSALITY_r1/
```

At minimum include:

```text
README.md
CONFIG_MATRIX.md
RUN_STATUS.csv
L1_CAUSALITY_COMPARISON.csv
L1_ONE_AT_A_TIME.csv   # only if triggered
TEMPORAL_SUMMARY.csv
CAUSAL_CLASSIFICATION.md
VALIDATION_SUMMARY.md
OPEN_ISSUES.md
RAW_LOG_INDEX.tsv
SHA256SUMS
```

Update workboard rows:

```text
L1-D256-META
L1-D256-BANK
L1-D512-META
L1-D512-BANK
```

after each transition.

## STOP boundaries

Do not alter L1 capacity/associativity/latency in this lane without a new reviewed decision.
Do not alter descriptor capacity except by consuming Lane B's published D256/D512 bases.
Do not implement RO/TVD/Unified functional mechanisms.