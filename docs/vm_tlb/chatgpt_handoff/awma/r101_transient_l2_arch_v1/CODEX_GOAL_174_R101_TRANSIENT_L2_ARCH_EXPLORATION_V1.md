# CODEX GOAL — 174-new R101 Transient-L2 Architecture Exploration V1

Run on **174-new** in a fresh worktree/branch.

Suggested execution branch:

`hrl/awma-r101-transient-l2-arch-174-v1`

Coordination authority:

`hrl/awma-r101-transient-l2-architecture-v1-handoff`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/r101_transient_l2_arch_v1/START_HERE.md`

Accepted Native authorities:
- R101 `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- R101R1 `422faf4d8fcdb5ac49068dcf19a6e783954a29a8`

Literature/architecture authority:

`hrl/awma-chatgpt-literature-notes-v1 @ a63574628b2daf20dd3c9256f53d5cd3ff7df26f`

Accepted simulator comparator:

`AWMA_RTX4080_SIM_BASELINE_V1`

Platform authority remains the promoted RTX4080/Ada Accel-Sim configuration and V1 frontend from the accepted review packs.

Stage:

`AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1`

## 1. Goal

Close, in one merged round:

1. simulator/source audit for L2 dirty writeback semantics;
2. producer-independent directed tests;
3. admission of the exact R101 trace when Lane F publishes READY;
4. bounded L2/writeback baseline requalification;
5. O1 DEAD_DROP_ORACLE;
6. M1 BOUNDED_LIVE_RETENTION_DEAD_DROP;
7. mechanism/cost diagnosis;
8. compact review pack and STOP.

Do not create an extra review round for ordinary engineering.

Do not run Native GPU work from this Goal.

## 2. Scope warning

The promoted simulator baseline is accepted for AWMA memory/translation studies.

It is **not automatically paper-qualified** for:
- L2 writeback amount;
- dirty eviction timing;
- HiMuon optimizer kernel cycle fidelity.

Before interpreting M1, explicitly qualify this new scope against accepted R101/R101R1 structural evidence.

Do not tune platform parameters to match Native.

If the simulator fundamentally cannot represent writeback/lifetime behavior credibly, STOP with:

`R101_TRANSIENT_L2_SIM_MODEL_NOT_QUALIFIED`

rather than producing a fake mechanism win.

## 3. Start immediately before producer arrival

Do not wait for Lane F before useful work.

CPU-only preparation:

- inventory exact GPGPU-Sim/Accel-Sim L2 cache source;
- identify write-back generation path;
- identify replacement/victim path;
- identify kernel-boundary hooks;
- identify access address and kernel launch identity available to cache controller;
- verify line size and accepted L2 geometry;
- audit counters for L2 hits/misses, dirty evictions, writebacks, DRAM writes;
- find the narrowest opt-in implementation point.

Run existing cache/controller regressions first.

Build in isolated paths.

Do not modify a binary used by another lane.

## 4. Mandatory OFF-equivalence

All new behavior is default OFF.

Central selector preferred:

`AWMA_TRANSIENT_L2_MODE=none|oracle_dead_drop|bounded_live_retention`

or an equivalent config/enum.

With `none`:
- source path must reproduce accepted baseline behavior;
- existing translation V1 behavior remains unchanged;
- no transient metadata affects replacement;
- no dirty line is dropped by new code.

Run existing controller/cache regressions and one accepted baseline smoke.

Any OFF mismatch must be repaired before producer input is admitted.

## 5. Input consumer preparation

Prepare admission for:

`SIM_INPUT_R101_L512_TRANSIENT_V1`

Expected sidecars:
- exact kernelslist/trace payload hashes;
- exact R101 scientific payload relation;
- A/B/X0/X1 region map;
- kernel-phase lifetime table;
- terminal/drop/overflow status.

Actual trace bytes are immutable after producer READY.

If a wrapper/path/index is missing but deterministically reconstructible from the producer manifest, build a derived view; do not mutate raw.

Reject:
- synthetic matrices;
- missing region identity;
- future per-line last-use annotations;
- truncated/overflow trace;
- altered tile count;
- different NS coefficients/steps.

## 6. Bounded replay scope

Preferred:
- full captured five-step L512 trace if runtime is reasonable.

If the producer preregistered `R101_L512_NS_CONTEXT2_V1`, use exactly that.

For CONTEXT2:
- first complete NS iteration establishes context;
- second complete NS iteration is measured ROI;
- all 44 L512 tiles remain;
- no per-tile or address subset.

Do not retrospectively select a cheaper/faster iteration after mechanism results.

## 7. Baseline L2/writeback requalification

Before O1/M1 claims, run `none`.

Correctness/identity:
- exact selected kernel sequence;
- expected CTA/instruction/trace coverage;
- no simulator assert/fatal;
- memory operations fully consumed;
- terminal cache/memory queues drained;
- translation/controller invariants still close;
- region sidecar addresses actually intersect the expected access streams.

Record:
- L2 line size, capacity, associativity/banks;
- L2 hit/miss;
- dirty eviction count;
- generated writeback transactions/bytes;
- DRAM read/write transactions/bytes;
- cycles/stalls;
- per-kernel/phase breakdown where existing telemetry supports it.

### Structural Native anchors

Accepted Native L512:
- source A/B/C logical writes across five steps: ~346.03 MB;
- R101 NS-family DRAM writes: ~344.72 MB;
- R101R1 B0: 346.92 MB;
- R101R1 D1: 255.81 MB (-26.26%).

Do not force exact equality.

Minimum credibility:
- simulator must generate real dirty L2 writebacks for transient regions;
- their byte/transaction accounting must be internally consistent;
- baseline traffic must be the same order of magnitude as the source/native phenomenon after accounting for replay scope and simulator line/sector semantics;
- any large discrepancy must be explained before mechanism timing is interpreted.

If baseline produces essentially no dirty writeback for the target regions, STOP as model-not-qualified.

## 8. O1 — DEAD_DROP_ORACLE

Purpose:
diagnostic cross-check, not hardware proposal.

At the exact software-declared region-death boundary:
- find resident L2 lines belonging to that region/generation;
- invalidate/drop them;
- if dirty, do **not** generate lower-level writeback.

O1 may use a zero-cost whole-cache/range scan.

Charge no scan latency, but label it explicitly:

`ORACLE_ZERO_COST_SCAN`.

It must not:
- drop live lines;
- suppress writeback of lines that already evicted before death;
- use future per-line last-read;
- add capacity.

Expected use:
- if O1 reduces writeback directionally, simulator represents the same basic phenomenon as Native D1;
- exact 26.26% agreement is not required.

If O1 causes zero writeback reduction despite verified resident dead dirty lines, debug semantics before proceeding.

## 9. M1 — BOUNDED_LIVE_RETENTION_DEAD_DROP

This is the first finite exploratory mechanism.

No extra L2 data capacity.

### Region descriptors

Maximum active transient regions:

`4`

for A/B/X0/X1.

Descriptor contains at least:
- base;
- limit/size;
- region ID;
- current generation;
- live/dead state.

Generation is bounded and wrap behavior must be safe.

### Per-line metadata

Store only finite metadata needed to identify transient region/generation.

Publish exact metadata bits per L2 line and total KiB/percentage of tag/data capacity.

Do not hide metadata cost.

### Replacement order

For each candidate victim set:

1. invalid;
2. dead transient;
3. ordinary/non-transient according to baseline policy;
4. live transient.

If all legal victims are live transient:
- choose the baseline legal victim;
- if dirty, issue normal writeback;
- never deadlock or pin indefinitely.

### Correctness

Dirty live-transient lines are never dropped.

Dirty line may be dropped only when its software-declared region/generation is dead.

No future trace knowledge.

### Region transitions

Use only the producer lifetime sidecar:
- A becomes dead after BA;
- B and old X become dead after BMM;
- new X becomes live/current.

No finer last-read knowledge.

### Dead-line reclamation

No whole-L2 zero-cost scan in M1.

Region death updates bounded descriptor state.

Dead transient lines are recognized lazily by descriptor/generation and become highest-priority victims.

A full physical tag sweep would require separate modeled hardware and is forbidden in M1.

## 10. First configuration is fixed

No parameter sweep.

Use:
- existing accepted L2 capacity/assoc/latencies;
- four descriptors;
- replacement order above;
- no extra victim/data storage;
- no enlarged L2;
- no new ports;
- no artificial faster DRAM.

Do not tune protection fraction or cache size after results.

## 11. Directed mechanism tests

Before formal trace:

At minimum create small deterministic tests for:

1. transient clean live line replacement pressure;
2. transient dirty live line — must write back if forced out;
3. dead dirty transient — may drop without writeback;
4. dead line preferred over ordinary live line;
5. all-ways-live fallback;
6. generation reuse;
7. region boundary alignment/partial lines;
8. non-transient address unaffected;
9. mode OFF equivalence;
10. terminal quiescence/no writeback queue leak.

Tests must fail if the implementation incorrectly drops a live dirty line.

## 12. Formal matrix

Once input/baseline qualifies:

Run one fixed replay under:

- B0 = `none`;
- O1 = `oracle_dead_drop`;
- M1 = `bounded_live_retention`.

Repeat B0 once for deterministic/stable counters if practical.

No mechanism combination.

For each record:
- cycles;
- L2 hit/miss;
- dirty eviction;
- writeback count/bytes;
- DRAM read/write;
- queue/stall counters;
- transient line admissions;
- live-transient protected-victim deflections;
- forced live-transient evictions;
- dead-transient drops;
- descriptor transitions;
- fallback count;
- terminal drain.

## 13. Interpretation

### Gate A — O1 mapping/semantic check

If O1 does not reduce any target-region writeback and investigation cannot explain why:

`R101_TRANSIENT_L2_ORACLE_NOT_ALIGNED_WITH_NATIVE`

STOP mechanism interpretation.

### Gate B — M1 structural response

Report:

`M1 writeback reduction vs B0`

and:

`M1 cycle change vs B0`.

No universal percent decides novelty, but predeclare material performance flag:

`abs(cycle change) >= 5%`

and require deterministic/stable direction.

### Allowed outcomes

#### `R101_TRANSIENT_L2_REGION_POLICY_NO_MATERIAL_EFFECT`
M1 does not materially reduce the relevant writeback/traffic.

Interpretation:
kernel-boundary region lifetime is too coarse or capacity pressure dominates; do not build this mechanism further.

#### `R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`
M1 materially reduces traffic but cycles change <5%.

Interpretation:
traffic is not performance-primary in this simulator scope.

#### `R101_TRANSIENT_L2_FIRST_PASS_PROMISING`
Allowed only if:
- input and baseline scope qualify;
- O1 is directionally credible;
- M1 reduces relevant writeback substantially;
- cycles improve >=5%;
- no correctness/terminal regression;
- no extra data capacity;
- finite metadata/cost published.

This is still exploratory, not paper proof.

#### `R101_TRANSIENT_L2_SIM_MODEL_NOT_QUALIFIED`
Baseline/cache model cannot support the claim.

## 14. If M1 is promising, continue within this same Goal

Do **not** STOP merely to request another round.

Freeze M1 source/config first.

Then add exactly two follow-ups:

### C0 resource-matched control
Same region lookup/metadata bookkeeping but baseline replacement/drop behavior.

Purpose:
separate metadata/control overhead from retention/drop benefit.

### H0 independent validation
Use one already-available admissible held-out trace if Lane F captured a second preregistered input **without consulting M1 results**.

If none exists:
record `HOLDOUT_INPUT_NOT_AVAILABLE`;
do not automatically start another109 capture inside this Goal.

Also broaden closest-work comparison using Round13 anchors.

Then STOP for ChatGPT review.

## 15. Do not claim

- hardware speedup on RTX4080;
- universal LLM benefit;
- final novelty;
- full-application training improvement;
- equivalence to persistent scratchpad/DSMEM;
- that all R101 20% fused benefit is explained by L2 writeback.

This first simulator study tests only whether bounded region-aware L2 lifetime management can reproduce a meaningful part of the residual.

## 16. Publication

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1/`

Minimum:

- README.md
- SOURCE_ANCHORS.md
- SIMULATOR_SCOPE_REQUALIFICATION.md
- INPUT_ADMISSION.tsv
- BASELINE_L2_ACCOUNTING.tsv
- TRANSIENT_REGION_CONTRACT.md
- O1_ORACLE_RESULTS.tsv
- M1_DESIGN_AND_COST.md
- M1_DIRECTED_TESTS.tsv
- EXPLORATION_MATRIX.tsv
- TRAFFIC_AND_CYCLE_RESULTS.tsv
- optional C0_RESOURCE_MATCHED_CONTROL.tsv
- optional H0_VALIDATION.tsv
- CLOSEST_WORK_BOUNDARY.md
- FINAL_DECISION.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Report:

`docs/vm_tlb/codex_handoff/awma/R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1_REPORT.md`

Closure:

`input/science -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree -> clean worktree -> STOP`.

No auto merge into the simulator baseline.
