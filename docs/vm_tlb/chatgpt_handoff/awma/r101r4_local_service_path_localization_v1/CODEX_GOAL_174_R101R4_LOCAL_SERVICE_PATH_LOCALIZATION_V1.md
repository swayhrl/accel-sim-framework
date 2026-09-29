# CODEX Goal — Lane E / 174-new
## AWMA R101R4 local-service path localization V1

Date: 2026-09-29

This is one continuous, solve-and-continue Goal for **Lane E = 174-new**.
Do not rename Lane E/F/G. Do not start Lane F or Lane G.

## 0. Scientific purpose

Accepted authorities:

- R101R2 O2:
  `97d5be184b7f7f35c06d3ee111a8c5ba6efad896`
  - B0 measured ROI = 2,985,319 cycles
  - O2 measured ROI = 1,130,670 cycles
  - O2 improvement vs B0 = 62.1256555832%
  - O2 is post-translation / pre-L1, one-cycle, unbounded service.

- R101R3 S1:
  `364998600d9f49953752fbec982233d5b8c5895a`
  - S1 measured ROI = 2,963,656 cycles
  - S1 improvement vs B0 = 0.7256510946%
  - S1 preserves normal VM + L1 + request ICNT + existing L2-subpartition hit/return path.
  - S1 serves all 29,937,568 legal measured transient transactions.
  - measured L2 misses / DRAM reads fall to 3,209 / 3,209.
  - H1/L3 were correctly not triggered.

Stage A from R101R3 also established:

- O2 observed maximum scheduled / ready depths = 1 / 16.
- 27,594,584 of 27,594,656 measured reads have a legal producer in an earlier completed kernel.
- therefore lack of a producer is not the reason S1 failed to retain O2's response.

This Goal asks one bounded localization question:

> Did O2's large response primarily require its unbounded pre-L1 queueing, or does it collapse specifically when normal L1 behavior is restored?

Only two new candidate points are allowed:

1. `P0_FINITE_PREL1_SERVICE`
2. `P1_POST_L1_LOCAL_SERVICE` — only if P0 survives.

This Goal is diagnostic localization, not a hardware mechanism and not a novelty claim.

## 1. Exact starting authority

Repository:
`swayhrl/accel-sim-framework`

Create the execution branch/worktree from exact parent:

`364998600d9f49953752fbec982233d5b8c5895a`

Must read:

- `docs/vm_tlb/review_packs/AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1/FINAL_DECISION.md`
- `.../S1_CONTEXT2_RESULTS.tsv`
- `.../S1_DESIGN_AND_COST.md`
- `.../STAGE_A_EXISTING_EVIDENCE.tsv`
- `.../REGION_OPCODE_COMPOSITION.tsv`
- `.../PRODUCER_CONSUMER_AVAILABILITY.tsv`
- R101R2 O2:
  - `docs/vm_tlb/review_packs/AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1/O2_DESIGN_AND_SCOPE.md`
  - `.../O2_CONTEXT2_RESULTS.tsv`
  - `.../O2_CORE.patch`
  - `.../FINAL_DECISION.md`
- accepted platform:
  `AWMA_RTX4080_SIM_BASELINE_V1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`

Large traces/raw stay on node164.
Do not stage/copy large traces to 174 local disk.

## 2. Hard inherited constraints

- All new functionality opt-in, default OFF.
- Functional and diagnostic selectors separate.
- OFF must reproduce accepted comparator.
- Preserve accepted VM translation, addresses, trace bytes, global instructions, coalescing, dependencies, CTA/kernel order, compute and region/generation semantics.
- Preserve LDG scoreboard, LDGSTS pending/DEPBAR and store ACK semantics.
- No future-trace knowledge.
- No cache/queue/latency sweep.
- No H1, scratchpad, DSMEM, cluster, persistent buffer or producer-consumer mechanism in this Goal.
- No FULL5.
- No new 109 capture/NCU/NVBit/native execution.
- No baseline/platform retuning.
- No additive interpretation such as `O2-P1 = L1 time`.
- Negative results remain negative; do not move hooks until a positive point appears.

Engineering-only issues: solve and continue.
P2/P3/P4 missing wrappers/index/tmp are deterministically reconstructed under existing V5 policy.
STOP only for unrecoverable scientific payload/identity, required semantic change, or claim-boundary change.

## 3. Stage A — source-path audit only, no long simulation

Before P0/P1 implementation, publish a compact source/path map for the accepted R101R3 binary:

```text
translation completion
  -> LD/ST access queue / coalesced transaction
  -> L1D access / reservation / merge / miss outcome
  -> request injection / request ICNT
  -> L2-subpartition ingress
  -> L2 data/tag service
  -> return queue / return ICNT
  -> LD/ST return arbitration
  -> LDG scoreboard or LDGSTS/DEPBAR completion
```

Bind the exact source functions/files for each boundary.

Also carry forward, without rerunning O2/S1:

- O2 max scheduled depth = 1;
- O2 max ready depth = 16;
- accepted B0/O2/S1 ROI values;
- S1 ingress/return observations;
- exact context signature.

This source audit exists to prevent P1 from silently skipping L1 semantics it is supposed to retain.

## 4. P0 — finite pre-L1 service

### 4.1 Question

O2 was post-translation/pre-L1 and used unbounded queues.

P0 keeps the **same scientific placement and one-cycle admission→READY semantics as O2**, but makes service storage finite using the exact maximum depths observed in accepted O2:

- scheduled capacity = **1 transaction per LD/ST unit**, matching accepted O2 max scheduled depth;
- ready capacity = **16 transactions per LD/ST unit**, matching accepted O2 max ready depth.

Do not change these values and do not scan them.

P0 answers only:

> Was O2's 62.13% response an artifact of unlimited scheduled/ready queue capacity?

### 4.2 Semantics

Placement remains exactly R101R2 O2:

- after accepted VM translation/frontend observation;
- before normal L1D access and request ICNT.

Qualified A/B/X live transient READ/WRITE only.

Service:

- admission at cycle t;
- READY at t+1;
- same original return/writeback/dependency arbitration as O2;
- same original LDG, LDGSTS and store completion paths.

Finite capacity behavior:

- if scheduled queue capacity is unavailable, the original memory instruction/access remains pending and backpressures naturally; do not fall through to normal hierarchy merely to avoid queueing;
- if READY capacity is full, READY transition stalls until capacity exists;
- no request may be dropped, duplicated or reclassified;
- no extra response/writeback port.

Record:

- scheduled-full cycles/events;
- ready-full cycles/events;
- max observed depths;
- admission→READY latency violations;
- exact transaction accounting.

### 4.3 P0 L1 qualification

Directed/integrated tests must prove:

- absent/none OFF-equivalence;
- capacity-1 scheduled backpressure;
- capacity-16 ready backpressure;
- no drop/fallback caused by full local queues;
- LDG;
- LDGSTS;
- WRITE/store ACK;
- atomic/unsupported/partial/multi-region/stale fail-closed;
- duplicate=0;
- full drain;
- accepted VM/controller regressions;
- positive six-kernel small integration.

No long B0 rerun is required if OFF-equivalence is exact.

## 5. L2 screen #1 — one P0 CONTEXT2 point

Run exactly one P0 CONTEXT2 after qualification.

Reuse accepted:

- B0 ROI = 2,985,319 cycles
- O2 ROI = 1,130,670 cycles
- S1 ROI = 2,963,656 cycles

Primary P0 metric:

`ROI = end(kernel6) - end(kernel3)`

Report:

- P0 ROI and improvement vs B0;
- kernel4/5/6 boundaries;
- exact context match;
- instructions/CTAs;
- served LDG/LDGSTS/WRITE;
- scheduled/ready full counters;
- max queue depths;
- L1/L2/DRAM counters;
- correctness/exactly-once/full-drain gates.

### P0 gate

Use the existing materiality threshold:

`P0 improvement >= 5%` → P0 survives; proceed to P1.

`P0 improvement < 5%` → STOP P1.

Interpret only:

> The accepted O2 response does not survive finite pre-L1 queue capacity under the frozen 1/16 configuration.

Do not try 2/32, 4/64 or any queue sweep.

## 6. P1 — post-L1 local miss service
### Only implement/run if P0 survives

### 6.1 Question

P1 asks:

> If normal L1 access/reservation/merge/miss behavior is retained, but a qualified L1 miss is serviced locally before request-ICNT/L2/return-ICNT traversal, does material response remain?

This distinguishes the **pre-L1/L1 side** from the **post-L1 downstream round trip** without building a mechanism.

### 6.2 Placement requirement

P1 must be downstream of the normal L1 decision.

A request satisfied by L1 is fully baseline and never enters P1.

For a qualified transient request that the normal L1 path has determined must request lower-level service:

1. preserve the normal L1 lookup;
2. preserve legal L1 reservation/MSHR/merge state required for that miss;
3. instead of injecting the lower-level request into request ICNT, send it to P1 local service;
4. return the response through the **same L1-miss completion/fill/MSHR-release path** that a real lower-level response would use, so L1 fill/replacement semantics are not silently deleted;
5. preserve the original LD/ST return arbitration and scoreboard/DEPBAR completion.

The scientific intervention is therefore:

`normal L1 miss -> bounded local lower-level response`

not:

`pretend the access was an L1 hit`.

If the source cannot support this without deleting or fabricating L1 miss/fill semantics, STOP rather than moving the hook to an easier but different location.

### 6.3 P1 finite service envelope

Use the same fixed local service envelope as P0:

- scheduled capacity = 1 per LD/ST unit;
- ready capacity = 16 per LD/ST unit;
- admission→READY = one modeled cycle;
- no extra response/writeback port;
- queue full causes backpressure, never request loss/fallback.

No tuning and no alternative latency.

### 6.4 Writes

A qualified WRITE must also preserve the normal L1 policy outcome before local lower-level completion.

Do not silently treat a write as an L1 hit if the baseline path would send it lower.
Preserve store ACK/token accounting and any required cache bookkeeping.

### 6.5 P1 L1 qualification

Directed/integrated tests must prove:

- L1 hit bypasses P1 completely;
- L1 miss takes P1;
- normal L1 reservation/merge state is allocated/released correctly;
- a P1-served miss produces the same legal L1 fill/update class as a baseline lower-level response;
- later accesses can observe that retained L1 state normally;
- finite scheduled/ready backpressure;
- LDG scoreboard;
- LDGSTS DEPBAR;
- WRITE/store ACK;
- nontransient normal path;
- fail-closed categories;
- duplicate=0;
- full drain;
- OFF-equivalence.

## 7. L2 screen #2 — one P1 CONTEXT2 point

Only if P0 >=5%.

Run exactly one P1 CONTEXT2.

Report the same identity/context/per-kernel/traffic/queue/correctness fields as P0, plus:

- L1 hits bypassing P1;
- qualified L1 misses serviced by P1;
- L1 miss merges;
- L1 reservation-failure behavior;
- local-service queue pressure.

### Interpretation

#### P1 >= 5%

Material response survives normal L1 behavior but disappears at S1's partition-side placement.

Allowed conclusion:

> In this accepted simulator scope, the material O2 opportunity lies after the L1 miss decision but before / across the downstream request+return path represented by S1.

Do **not** assign it specifically to request ICNT, return ICNT, ingress queue or any one component without another authorized experiment.

#### P1 < 5%

P0 was material but restoring normal L1 behavior collapses the response.

Allowed conclusion:

> In this accepted simulator scope, the large pre-L1 response depends materially on bypassing the normal L1/front-end miss path; lower-level service removal alone is insufficient.

Do not call the numerical difference "L1 latency".

#### P0 < 5%

P1 not run.
The unbounded nature of O2 remains a material modeling dependency under the frozen 1/16 finite envelope.

## 8. Native decision boundary

**Do not run 109 in this Goal.**

After P0/P1 closes, the final report must state whether a minimal Native realism check is scientifically warranted.

Possible recommendations only:

- `NATIVE_CHECK_NOT_WARRANTED_R101_CLOSE`
- `NATIVE_CHECK_WARRANTED_L1_FRONTEND`
- `NATIVE_CHECK_WARRANTED_POST_L1_DOWNSTREAM`

No Native metric names are to be invented here.
If warranted, ChatGPT will separately design a small 109 task after reviewing this result.

## 9. R101 directions frozen/closed during this Goal

Do not reopen:

- transient L2 replacement / M1;
- writeback/dead-drop variants;
- L2 capacity expansion;
- DRAM service;
- partition-side S1;
- H1 4 MiB handoff;
- persistence/discard variants.

The purpose of R101R4 is to decide whether the remaining O2 response is a near-SM path opportunity worth validating natively, or a simulator-local sensitivity that should close R101 as an architecture mechanism line.

## 10. Execution efficiency

Before long simulation check CPU/RAM/I/O/node164 health.

P1 long simulation is scientifically gated on P0 >=5%.

While P0 runs, CPU-only P1 source audit/directed-test preparation may proceed if it cannot mutate P0 binary/config/output.
Do not launch P1 formal run speculatively before P0 gate.

Each formal run has independent output/config/log/tmp/receipt.
Immutable traces are read-shared.
Do not high-frequency poll.

## 11. Deliverables

Suggested review pack:

`docs/vm_tlb/review_packs/AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1/`

At minimum:

- `README.md`
- `SOURCE_PATH_MAP.md`
- `INHERITED_COMPARATORS.tsv`
- `P0_DESIGN_AND_COST.md`
- `P0_DIRECTED_TESTS.tsv`
- `P0_CONTEXT2_RESULTS.tsv`
- `P1_DESIGN_AND_COST.md` only if P0 survives
- `P1_DIRECTED_TESTS.tsv` only if P0 survives
- `P1_CONTEXT2_RESULTS.tsv` only if executed
- `FINAL_DECISION.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `CHANGED_FILES.md`
- `SHA256SUMS`

Large raw stays on node164.

## 12. Closure

At final STOP:

- commit exact source/tools/review pack;
- push exact commit;
- bounded transport fallback if needed:
  HTTPS -> HTTP/1.1 -> GitHub SSH -> gh/API;
- fetch-back / remote SHA+tree verify;
- clean worktree;
- preserve all accepted raw;
- report exact branch/commit/tree/node164 root/hashes.

Do not auto-merge.
Do not start 109.
Do not launch another R101 mechanism after closure.
