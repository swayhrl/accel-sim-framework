# C16 E1 Semantic NCU Selector Design V1

## 1. Research question

The clean E1 timing interaction is accepted. The next question is narrower:

> **For the selected semantic operator `up_proj`, what exact GPU kernel set implements one RAW_FP16 or AWQ module invocation at M1 and M256, and what L1/L2/DRAM traffic does that whole semantic invocation generate?**

The goal is not to select “one representative kernel”.

The goal is to qualify one exact semantic module-call range and aggregate every GPU kernel that belongs to that invocation.

---

# 2. Selected points are frozen

Do not reselect the role.

Accepted independent selection:

`up_proj`

Points:

1. M1 RAW_FP16
2. M1 AWQ_FP16_INPUT
3. M256 RAW_FP16
4. M256 AWQ_FP16_INPUT

Use the exact canonical FP16 activation SHAs and module/runtime identities from the accepted producer review pack:

`docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_109_V1/`

No new shape sweep.

---

# 3. Standalone semantic replay

Build or reuse a minimal standalone replay for each of the four points.

Requirements:

- load the exact frozen canonical activation tensor;
- load the same RAW_FP16 or AWQ module state/runtime used by the accepted clean matrix;
- warm up outside the profiled range;
- execute exactly one target semantic module invocation inside one uniquely named NVTX range;
- synchronize before/after the range as needed for unambiguous attribution;
- emit output SHA;
- output SHA must match the accepted clean-baseline point;
- lightweight kernel fingerprint must match the accepted path family.

Suggested unique range names:

- `C16_E1_NCU_UP_M1_RAW_FP16`
- `C16_E1_NCU_UP_M1_AWQ`
- `C16_E1_NCU_UP_M256_RAW_FP16`
- `C16_E1_NCU_UP_M256_AWQ`

The replay must not execute another target-module call inside the selected range.

---

# 4. Selector qualification

Use the installed profiler/runtime authority only.

First inspect the installed NCU CLI/help/version and confirm the supported NVTX/range selection syntax.

Do not assume a command-line option from documentation for another NCU version.

Qualification requires:

1. one exact NVTX range occurrence;
2. range name matches the requested point;
3. all selected kernels occur within that range;
4. no target kernels from warmup or another semantic point are included;
5. standalone output SHA matches accepted clean baseline;
6. kernel names/launches are persisted.

For AWQ, multiple kernels inside one module call are expected and valid.

The selector status is:

`SEMANTIC_MODULE_RANGE_QUALIFIED`

only after these gates close.

If NCU cannot honor the NVTX range reliably, a fallback may use a standalone one-target-call process plus an exact launch inventory, but the fallback must prove no other candidate target invocation exists. Do not use launch-order guessing in a multi-call process.

---

# 5. Metrics

After selector qualification, collect a minimal metric set.

Before profiling:
- query installed NCU for exact metric availability;
- record exact metric names and units.

Preferred semantic categories:

- L1/TEX requested bytes;
- L2 requested bytes;
- DRAM bytes;
- achieved occupancy / active warps where available;
- SM/tensor/math utilization where available.

Do not invent or rename unsupported metrics.

For each selected GPU kernel preserve:
- kernel name;
- launch geometry;
- metric value/unit.

For each semantic module invocation compute:

`SEMANTIC_MODULE_SUM`

by summing only additive byte/event metrics over all kernels inside the qualified range.

Do not blindly sum percentages/utilization. For non-additive metrics retain per-kernel values and, only if a documented aggregation is meaningful, report it separately.

---

# 6. Normalization

For each point report raw semantic-module traffic and:

- bytes / output element;
- bytes / input element;
- bytes / semantic RAW_FP16 dense weight bytes;
- for AWQ, bytes / packed-weight storage bytes where the exact storage size is available.

These are descriptive normalizations.

Do not infer cache hit rate or TLB behavior unless an explicit corresponding metric is collected and validated.

---

# 7. Required comparisons

At minimum:

## M1
- RAW_FP16 vs AWQ semantic-module kernel composition
- L1/L2/DRAM traffic ratio where metrics are valid

## M256
- same

## Shape interaction
For each implementation:
- M256/M1 traffic scaling

Then compare traffic interaction with accepted timing interaction.

Possible interpretations:

- timing and traffic move together;
- traffic differs but timing does not scale proportionally;
- timing interaction exists without a comparable traffic interaction.

All are valid outcomes.

---

# 8. No causal leap

Even if AWQ shows much more or less traffic, allowed wording is:

> traffic behavior is associated with the deployed implementation/path under the tested semantic module call.

Not allowed in this stage:

- “cache causes the slowdown”;
- “TLB causes the slowdown”;
- “this cache mechanism will fix it”;
- “quantization itself causes it”.

---

# 9. 109 deliverables

Review pack:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_109_V1/`

At minimum:

- `UPSTREAM_E1_AUTHORITY.json`
- `REPLAY_POINT_BINDINGS.tsv`
- `STANDALONE_REPLAY_QUALIFICATION.json`
- `NVTX_SELECTOR_CONTRACT.json`
- `SELECTED_KERNELS.tsv`
- `NCU_METRIC_AVAILABILITY.tsv`
- `NCU_KERNEL_METRICS.tsv`
- `SEMANTIC_MODULE_TRAFFIC.tsv`
- `TRAFFIC_NORMALIZATION.tsv`
- `TIMING_TRAFFIC_COMPARISON.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Update:
`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

---

# 10. Stop boundary

This entire semantic-NCU qualification + measurement is one node109 Goal.

Do not stop after building the standalone replay if selector qualification can continue.

If selector qualifies, continue directly to all four selected points and closure.

If selector still cannot be proven:
- record exact failure mode;
- do not fabricate traffic;
- close the Goal with `SEMANTIC_NCU_SELECTOR_UNRESOLVED_V2`.

Do not launch:
- NVBit;
- full address trace;
- TLB/cache mechanism.

---

# 11. 174-new parallel role

174-new can run concurrently to:

- independently audit the semantic-range aggregation contract;
- prepare an NCU CSV/raw parser;
- pre-register additive vs non-additive aggregation rules;
- build synthetic tests;
- after prep, fetch producer once;
- if producer is complete, independently recompute semantic-module sums and ratios;
- otherwise stop at `READY_FOR_E1_SEMANTIC_NCU_109`.

No polling loop and no GPU work.
