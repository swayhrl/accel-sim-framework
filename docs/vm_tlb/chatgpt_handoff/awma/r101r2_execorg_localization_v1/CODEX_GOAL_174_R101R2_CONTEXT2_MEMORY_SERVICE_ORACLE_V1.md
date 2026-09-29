# CODEX GOAL — 174-new R101R2 CONTEXT2 Memory-Service Oracle V1

Run on **174-new** in Lane E.

Suggested execution branch:

`hrl/awma-r101r2-context2-memory-service-174-v1`

Coordination branch:

`hrl/awma-r101r2-execorg-localization-v1-handoff`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/r101r2_execorg_localization_v1/START_HERE.md`

Stage:

`AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1`

## 1. Question

The accepted FULL5 transient-L2 experiment already showed:

- writeback -92%;
- DRAM reads -71%;
- L2 misses -19%;
- cycles only -0.50% to -0.91%.

Do not design another cache/writeback mechanism.

Instead ask one stronger upper-bound question:

> If the **data service** for legal transient A/B/X accesses is almost free, while the original global-memory instructions, warp issue, coalescing, dependencies and kernel decomposition remain, how much cycle headroom is left?

This is a localization oracle, not hardware.

## 2. Authorities

Accepted full producer:

`hrl/awma-r101-transient-l2-sim-capture-109-v1 @ bb902283b7ce9e1902b460383fbd3e0bedbd884d`

Stable input:

`SIM_INPUT_R101_L512_TRANSIENT_V1`

Accepted FULL5 architecture result:

`hrl/awma-r101-transient-l2-arch-174-v1 @ 8da4057b3c168543603401b1b42a99b556d98042`

Accepted simulator baseline:

`AWMA_RTX4080_SIM_BASELINE_V1`

Do not recapture on109.

Do not modify producer raw bytes.

## 3. L2 experiment level

This Goal is **L2 CONTEXT2 screening**.

No FULL5 replay is authorized.

Derive a deterministic view:

`R101_L512_NS_CONTEXT2_EXECORG_V1`

from the accepted FULL5 trace.

Use exactly these original ROI launch indices:

- 3: iteration0 XXT
- 4: iteration0 BA
- 5: iteration0 BMM-add
- 6: iteration1 XXT
- 7: iteration1 BA
- 8: iteration1 BMM-add

All 44 L512 tiles remain.

The first complete iteration is **context only**.

The second complete iteration is the **measured ROI**.

Do not include normalization in this derived view.

Do not change trace bytes.

Use a derived kernelslist/manifest that references the immutable node164 members.

## 4. Context2 sidecar derivation

Derive a new runtime sidecar from the already admitted FULL5 sidecar, not from prose.

Initial state before original kernel 3 must equal the accepted state after original normalization kernel 2.

Preserve:
- A/B/X0/X1 base/limit;
- region IDs;
- generation semantics;
- live/dead states;
- producer PRE activations;
- completion POST deaths.

Renumber only the derived kernel ordinals.

Create a deterministic receipt proving:

- original producer commit;
- original trace-member hashes;
- exact selected members/order;
- original-sidecar SHA;
- derived-sidecar SHA;
- initial-state mapping;
- measured ROI start/end boundaries.

No per-line future-last-use information may be introduced.

## 5. Matched-context experimental design

### B0_CONTEXT2

Run the full two-iteration derived view with all new oracle behavior OFF.

### O2_CONTEXT2

The first context iteration must execute **identically to B0**.

O2 is activated only at the start of the second iteration XXT, after the context iteration BMM-add has completed and all accepted boundary transitions have applied.

Thus B0 and O2 enter the measured ROI from the same simulated context state.

Verify this with a pre-ROI state receipt/counter hash where possible.

Do not activate O2 during the context iteration.

## 6. O2 semantics

Working name:

`O2_TRANSIENT_1C_SERVICE_ORACLE`

This is an upper bound, not a realizable mechanism.

For a coalesced global-memory transaction in the measured ROI:

O2 applies only when:

1. the address intersects one of the admitted A/B/X0/X1 transient regions;
2. the region/generation is legally active according to the derived PRE/POST sidecar state;
3. the access is ordinary global READ or WRITE supported by the trace.

If any ATOMIC or unsupported memory semantic targets a transient region in the measured ROI:

`R101R2_O2_SEMANTICS_NOT_QUALIFIED`

and STOP O2 interpretation.

### What O2 preserves

- original dynamic global-memory instruction;
- warp/CTA identity;
- instruction issue;
- coalescing;
- address calculation;
- scoreboard/dependency completion path;
- kernel sequence;
- compute instructions;
- CTA scheduling;
- non-transient accesses.

### What O2 removes

After the ordinary coalesced transaction is formed/admitted to the memory-service boundary:

- do not perform normal L1/L2/DRAM service for the qualified transient transaction;
- complete it through the normal response/dependency path after exactly **1 modeled cycle**;
- do not allocate/update normal cache state for that transaction;
- do not generate DRAM traffic/writeback for it.

The oracle service has no modeled bandwidth/queue limit.

This is intentionally optimistic and must be labeled:

`ORACLE_ONE_CYCLE_UNBOUNDED_SERVICE`.

It estimates an upper bound on transient **memory-service** cost while retaining the global instruction/execution organization.

For trace-driven stores, no data-value claim is made; the simulator does not use application values for downstream numerical correctness. Consumer loads in the measured ROI are likewise serviced by the oracle only when legally qualified.

## 7. New code isolation

Use one opt-in selector, default OFF, for example:

`AWMA_R101R2_TRANSIENT_SERVICE_MODE=none|oracle_1c`

The exact name may follow project conventions.

Default OFF and explicit none must preserve existing behavior.

Do not modify:
- L2 size/assoc/latency;
- DRAM parameters;
- VM/TLB parameters;
- translation semantics;
- trace;
- CTA scheduling;
- compute latencies.

## 8. Directed tests

Before formal CONTEXT2:

At minimum test:

1. non-transient access uses normal memory hierarchy;
2. transient access before O2 activation uses normal hierarchy;
3. transient READ in measured ROI gets one-cycle oracle completion;
4. transient WRITE gets one-cycle oracle completion and no normal cache/DRAM service;
5. unsupported ATOMIC fails closed;
6. region generation/liveness mismatch does not oracle-service;
7. PRE producer activation makes the just-produced region eligible;
8. POST death removes eligibility;
9. scoreboard/response completion occurs exactly once;
10. terminal queues drain;
11. selector OFF equivalence.

Reuse existing R101 transient-region parser/sidecar code where semantically identical.

Do not re-run the 29-hour FULL5 matrix.

## 9. Formal execution and efficiency

After host resource audit, B0_CONTEXT2 and O2_CONTEXT2 may execute **speculatively in parallel** in isolated run directories.

This is allowed because:
- simulated cycles/counters do not depend on wall-clock speed;
- scientific interpretation remains gated on B0 qualification;
- no shared mutable binary/config/output is allowed.

Use at most **2 formal workers**.

If RAM/swap/I/O pressure makes simulator correctness or completion unstable, serialize instead.

Large trace/raw remain on node164 mounted storage because 174 local disk is constrained.

Do not require local trace staging.

## 10. Measured ROI timing

Record both:

- full CONTEXT2 total cycles;
- measured iteration1 ROI cycles.

Primary R101R2 metric:

`ROI_CYCLES = cycle_after_iteration1_BMM - cycle_after_iteration0_BMM`

or the exact equivalent boundary snapshots in the simulator.

B0 and O2 must use the same boundary definition.

The context iteration cycle count is secondary and should be identical or nearly identical because O2 is not active.

If pre-ROI counters/state differ unexpectedly:

`R101R2_CONTEXT_NOT_MATCHED`

and do not interpret ROI speedup.

## 11. Required counters

For B0 and O2 measured ROI record:

### Execution
- ROI cycles;
- instructions;
- CTAs;
- active/terminal status.

### Oracle
- qualified transient read transactions/bytes;
- qualified transient write transactions/bytes;
- one-cycle completions;
- unsupported/skipped transactions;
- duplicate completion count.

### Normal hierarchy
- L1/L2 accesses where available;
- L2 misses;
- L2 writeback;
- DRAM read/write;
- reservation/queue/stall counters useful for the accepted simulator.

### Correctness
- exact kernel coverage;
- translated/unobserved/duplicate gates;
- writeback/accounting consistency where applicable;
- full terminal drain.

Non-transient hierarchy activity must remain normal.

## 12. Baseline qualification

The derived B0_CONTEXT2 must:

- admit exact six trace members;
- preserve order/identity;
- close 6/6 coverage;
- close controller/translation correctness;
- generate expected A/B/X region accesses;
- generate real normal-memory service;
- terminal drain cleanly.

Compare B0_CONTEXT2 structural traffic against the corresponding first-two-iteration slice from accepted FULL5 B0 if that slice can be reconstructed from existing per-kernel telemetry.

Do not demand exact whole-run equality.

No platform tuning.

## 13. Decision gate

Primary:

`O2_ROI_IMPROVEMENT = (B0_ROI_CYCLES - O2_ROI_CYCLES) / B0_ROI_CYCLES`

### If >= 5%

Final 174 state:

`R101R2_O2_MEMORY_SERVICE_HEADROOM_PRESENT`

This authorizes later ChatGPT review of a bounded cross-kernel/local-service mechanism.

O2 itself is not a mechanism and no FULL5 confirmation runs now.

### If < 5%

Final 174 state:

`R101R2_O2_MEMORY_SERVICE_HEADROOM_LOW`

This is strong evidence that memory hierarchy service latency/bandwidth cannot explain the accepted ~20% Native fused response by itself.

Do not design another cache/local-buffer mechanism in this Goal.

### Near-threshold repeat

Only if improvement is between **3% and 7%**, run one exact repeat of B0/O2 CONTEXT2 to confirm deterministic/stable ROI cycles.

Outside that band, no repeat is needed if the simulator is deterministic and all gates close.

## 14. No extra mechanisms

Forbidden:

- O3 instruction deletion;
- scratchpad mechanism;
- DSMEM model;
- bigger L2;
- cache-policy sweep;
- latency sweep;
- bandwidth sweep;
- FULL5;
- holdout.

Those require joint review with Lane F.

## 15. Publication

Durable root:

`/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1/`

Minimum:

- README.md
- R101_INHERITANCE.md
- CONTEXT2_DERIVATION_RECEIPT.json
- CONTEXT2_KERNELS.tsv
- CONTEXT2_RUNTIME_SIDECAR.tsv
- O2_DESIGN_AND_SCOPE.md
- O2_DIRECTED_TESTS.tsv
- OFF_EQUIVALENCE.tsv
- B0_CONTEXT2_RESULTS.tsv
- O2_CONTEXT2_RESULTS.tsv
- ROI_COMPARISON.tsv
- FINAL_DECISION.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Final states:

- `R101R2_O2_MEMORY_SERVICE_HEADROOM_PRESENT`
- `R101R2_O2_MEMORY_SERVICE_HEADROOM_LOW`
- `R101R2_CONTEXT_NOT_MATCHED`
- `R101R2_O2_SEMANTICS_NOT_QUALIFIED`
- `R101R2_CONTEXT2_SIM_NOT_QUALIFIED`

Closure:
science -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree -> clean -> STOP.

No auto merge.
