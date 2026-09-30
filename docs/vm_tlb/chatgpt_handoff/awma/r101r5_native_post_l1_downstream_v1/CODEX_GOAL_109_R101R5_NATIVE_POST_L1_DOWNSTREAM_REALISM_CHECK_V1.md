# CODEX Goal — Lane F / 109
## AWMA R101R5 Native post-L1 downstream realism check V1

Date: 2026-09-30

This is one continuous, bounded Goal for **Lane F = 109 / RTX4080 SM89**.
Lane E and Lane G remain STOP.
Do not run Accel-Sim on 109.

## 0. Scientific purpose

Accepted simulator authority:

`d96a64da8311c1bdee8f23f3d83ce665395060d1`

R101R4 established, in the accepted L512 CONTEXT2 simulator scope:

| Arm | ROI cycles | Improvement vs B0 |
|---|---:|---:|
| B0 | 2,985,319 | 0% |
| O2 pre-L1 | 1,130,670 | 62.1257% |
| P0 finite pre-L1 1/16 | 1,130,670 | 62.1257% |
| P1 post-L1 local | 2,737,282 | 8.3086% |
| S1 partition-side | 2,963,656 | 0.7257% |

Allowed simulator conclusion only:

> material response survives normal L1 miss handling but disappears by the accepted partition-side S1 placement.

P1 did **not** locally serve LDGSTS in the formal run. It served:

- 1,126,400 ordinary LDG reads;
- 2,342,912 writes;
- zero LDGSTS;
- finite scheduled/ready capacities 1/16 with real full-pressure events.

Therefore this Native check must focus on whether real RTX4080 execution of the exact L512 XXT / BA / BMM-add kernels exposes a credible **ordinary global load/store post-L1/downstream dependency or throughput pressure**. Do not use LDGSTS volume as the primary hypothesis.

This Goal does **not** attempt to reproduce the simulator's 8.31% intervention on hardware and does not design a mechanism.

## 1. Authorities and exact existing assets

Repository:
`swayhrl/accel-sim-framework`

Scientific parent:
`d96a64da8311c1bdee8f23f3d83ce665395060d1`

Native R101 authority:
`cfbe6503585fa1b10d979db5d26fb9be3a80e563`

Must read:

- `docs/vm_tlb/review_packs/AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1/FINAL_DECISION.md`
- `.../P1_CONTEXT2_RESULTS.tsv`
- `.../SOURCE_PATH_MAP.md`
- `docs/vm_tlb/review_packs/AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1/ENVIRONMENT_RECEIPT.json`
- `.../R101_SOURCE_RECEIPT.json`
- `.../R101_INPUT_RECEIPT.json`
- `.../NCU_DIAGNOSTIC.tsv`
- `.../NCU_SUMMARY.json`
- `.../RAW_DATA_INDEX.tsv`

Accepted existing L512 NCU authority includes:

- `raw/ncu/L512/L512.ncu-rep`
- `raw/ncu/L512/L512.raw.csv`
- `raw/ncu/L512/PROFILE_TARGET_RECEIPT.json`

The durable R101 root is recorded by the accepted raw index under node164.
Use the accepted RAW_DATA_INDEX to locate exact artifacts; do not guess or move accepted raw.

Known accepted environment includes RTX4080 / SM89, driver 580.178.04,
PyTorch 2.6.0+cu124, Triton 3.2.0 and pinned HiMuon source
`af89eda9a0176effed99e1fe19cc1f8a1a2c9588`.

## 2. Hard scope

- **Audit existing NCU raw first.**
- If existing raw already supports the required evidence, do **zero new GPU profiling**.
- Only if a concrete metric/source-attribution gap remains may Phase B use the GPU.
- No new model/input download.
- No new NVBit trace.
- No new simulator-native trace.
- No R101 graph timing redo.
- No F128/K128 timing redo.
- No discard/persistence test.
- No synthetic ICNT or memory microbenchmark.
- No hardware emulation of P1.
- No change to HiMuon, NS coefficients, five-step map, L512 population or accepted numerical input.
- NCU replay duration is not primary performance timing.
- Do not silently substitute unsupported metric names.
- Do not call NCU cache control a TLB control.
- Do not claim Native 8.31% from any counter.
- Lane E/G stay untouched.

Normal engineering issues: solve and continue.
A failure to obtain one optional profiler counter is not a scientific blocker; record it as unavailable and continue with supported evidence.

## 3. Phase A — audit existing L512 NCU report, NO GPU required

Use the accepted `L512.ncu-rep`, raw CSV, stdout/receipt and accepted source/cubin bindings.

### A1. Inventory exactly what was already collected

Using the installed/compatible Nsight Compute tooling, inspect/import the accepted report and list:

- report NCU version / target GPU identity if present;
- profiled launch identities and occurrence order;
- all collected metric names and units;
- all collected sections;
- whether warp-stall / issue-state metrics exist;
- whether SourceCounters / PC-sampling / source-SASS attribution exists;
- whether L1/TEX request/sector and L2 traffic counters exist;
- whether direct LDG/ST and LDGSTS instruction counts exist.

Do not infer an uncollected metric from a similarly named metric.

### A2. Map the exact L512 NS targets

The accepted L512 family has 5 occurrences each of:

- `XXT_kernel`, grid `(2816,1,1)`, block `(128,1,1)`;
- `ba_plus_cAA_kernel`, grid `(2816,1,1)`, block `(128,1,1)`;
- `bmm_add_kernel`, grid `(16,44,1)`, block `(128,1,1)`.

Bind the **second NS recurrence** target for each exact function when possible, because simulator CONTEXT2 measures the second recurrence after one context recurrence.

Use accepted launch/order/source evidence to establish the occurrence identity.
Do not rely on kernel name alone if occurrence selection is ambiguous.

If the existing NCU report used a different recurrence, retain it as historical evidence but do not silently relabel it as the second recurrence.

### A3. Existing-evidence decision

The minimum desired evidence categories are:

1. **Issue/stall composition**
   - supported warp issue-stall categories, especially memory-dependency / long-scoreboard-like, LSU/LG throttle, MIO/short-scoreboard-like categories, barrier and not-selected/eligible context;
2. **Ordinary global-memory activity**
   - direct global LDG/LD and STG/ST instruction evidence;
   - LDGSTS separately;
   - L1/TEX requested sectors/bytes or closest supported equivalent;
   - L2 requested traffic and DRAM traffic;
3. **Source/PC attribution if available**
   - source/SASS-PC attribution of the relevant stall samples or sampled issue reasons.

If the accepted report already contains enough evidence to evaluate these three categories for the exact targets, proceed directly to Phase C and do not acquire the GPU lock.

If category 3 is unavailable but categories 1 and 2 are already strong enough to form a bounded descriptive conclusion, do not automatically re-profile just to obtain PC attribution. Explain the limitation and proceed to Phase C.

Only enter Phase B when the existing report lacks the **core issue/stall evidence** required to evaluate post-L1/downstream realism.

## 4. Phase B — bounded Native supplement, only if Phase A demonstrates a real gap

### 4.1 GPU admission

Before any CUDA/NCU run:

- acquire the existing campaign lock:
  `/data/c16/locks/c16_gpu_campaign.lock`;
- verify no conflicting GPU campaign/process;
- reuse the accepted R101 environment and assets;
- verify exact model/input/source identities against accepted receipts;
- verify sufficient local/output space;
- release the GPU lock and resident allocations cleanly at closure.

Do not modify other lanes.

### 4.2 Query actual SM89 profiler capability first

On the actual 109 NCU installation run the appropriate:

- metric query;
- section listing;

and save the outputs.

Build the metric/section request from what the actual tool supports.

Preferred semantic evidence, **not hard-coded metric names**:

- warp issue/stall composition:
  - memory dependency / long scoreboard class;
  - global/LSU throttle class;
  - MIO / short scoreboard class;
  - barrier/wait;
  - not-selected / eligible-warp context;
- direct global LDG/LD instructions;
- global STG/ST instructions;
- LDGSTS separately;
- L1/TEX global load/store request/sector traffic;
- L2 requested traffic / hit-miss information if actually exposed;
- DRAM reads/writes;
- active cycles / occupancy / eligible warps;
- SourceCounters / PC or SASS-source sampling for issue-stall attribution if supported and reasonably bounded.

Unsupported fields must be marked `COUNTER_UNAVAILABLE` or `SOURCE_ATTRIBUTION_UNAVAILABLE`.
Never replace them silently with a different metric.

### 4.3 Exact three targets only

Profile exactly one target occurrence for each:

1. second-recurrence `XXT_kernel`;
2. second-recurrence `ba_plus_cAA_kernel`;
3. second-recurrence `bmm_add_kernel`.

The selected target must run inside the accepted natural L512 execution path / graph context.
Do not create a standalone synthetic microbenchmark.

Bind each target by exact function + grid/block + verified occurrence/launch identity.

If NCU filtering cannot select the second recurrence safely, use the closest exact, explicitly documented selection method supported by the current tool and prove which occurrence was profiled before accepting it.

### 4.4 Measurement settings

Inherit accepted R101 profiling policy unless the actual tool requires a documented compatibility change:

- cache control: none;
- clock control: none;
- do not treat NCU replay duration as primary timing.

Use the smallest section/metric set that answers the question.
Do not collect an all-metrics report.

Each target gets one bounded profiling job. Multiple internal NCU passes required by the selected supported metrics are allowed and must be recorded, but do not repeat the target to hunt for a preferred result.

Preserve individual raw reports and exact CLI receipts.

### 4.5 Numerical / target identity

The profiler run must not change the accepted numerical input or NS contract.

If normal NCU profiling permits an output/canary check, verify it against the accepted target path.
Do not weaken numerical gates merely because profiling is enabled.

## 5. Phase C — analysis

For each of XXT / BA / BMM-add, produce one row with:

- exact target identity and recurrence;
- direct LDG count;
- LDGSTS count;
- STG count;
- L1/TEX traffic;
- L2 traffic;
- DRAM read/write;
- active cycles / occupancy / eligible-warp context;
- available warp-stall composition;
- source/PC attribution status;
- top relevant stall categories with exact percentages/counts and denominator definitions.

### C1. Do not overinterpret stall names

A memory-dependency / scoreboard-like stall does not by itself prove request ICNT or return ICNT is the cause.

An LSU/LG throttle does not by itself prove L1D, ICNT or L2 is the bottleneck.

The Native task is only to determine whether the real RTX4080 exposes a **credible matching class of ordinary global load/store downstream pressure** that makes further investigation scientifically justified.

### C2. LDGSTS handling

Keep LDGSTS separate throughout.

R101R4 P1's formal local service count for LDGSTS was zero.
Therefore a Native result dominated only by LDGSTS-related behavior is **not** direct support for the specific P1-localized opportunity.

### C3. PC/source attribution

If PC/source sampling is available:

- identify whether relevant stall samples land on:
  - direct global LDG/ST instructions;
  - immediately dependent consumers;
  - LDGSTS;
  - unrelated compute/barrier/control PCs.

Do not claim an exact causal chain from PC sampling alone.

If unavailable, preserve the gap; do not fabricate a SASS attribution.

## 6. Decision categories

Use these only as bounded review labels; include the raw facts first.

### `NATIVE_POST_L1_DOWNSTREAM_SUPPORT_PRESENT`

Use only when **at least two of the three exact targets** show a consistent, meaningful ordinary LDG/ST memory-dependency or LSU/downstream-pressure signature among their dominant issue limitations, and the traffic/instruction evidence is consistent with that interpretation.

Source/PC attribution strengthens this result but is not mandatory if the profiler cannot expose it.

This does **not** validate the simulator magnitude or one specific downstream component.

### `NATIVE_POST_L1_DOWNSTREAM_SUPPORT_MIXED`

Use when:

- only one target shows clear ordinary LDG/ST downstream pressure; or
- different targets are dominated by different limitations; or
- counters suggest memory pressure but source/traffic evidence does not cleanly distinguish ordinary LDG/ST from other paths.

Do not launch another experiment automatically.

### `NATIVE_POST_L1_DOWNSTREAM_SUPPORT_NOT_OBSERVED`

Use when all three targets are instead consistently dominated by nonmatching compute/barrier/other limitations and the ordinary LDG/ST downstream evidence is weak.

This is a strong reason to close the R101 architecture-mechanism line rather than further subdivide simulator ICNT/L2 components.

### `NATIVE_EVIDENCE_INSUFFICIENT`

Use only if the actual profiler/tool permissions prevent collecting the core issue/stall evidence and the existing report also lacks it.

Do not substitute a synthetic benchmark.

## 7. Explicitly prohibited follow-on work

Even if support is present, do **not** in this Goal:

- implement near-SM handoff;
- modify L1/ICNT/L2;
- run P2/P3 simulator localization;
- run FULL5;
- capture new trace;
- add another model;
- start a closest-work mechanism comparison;
- claim paper novelty.

ChatGPT will review the Native evidence first.

## 8. Efficiency and publication

Phase A should be completed before GPU work.

If Phase B is needed, all CPU-only report/code preparation may be done before acquiring the GPU lock.
Hold the GPU lock only for the actual bounded NCU jobs/canaries.

Large profiler raw should be published under the existing node164 AWMA provenance tree; Git stores compact reports, receipts, source/metric bindings and hashes.

Do not delete accepted prior R101 raw.

## 9. Deliverables

Suggested review pack:

`docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1/`

At minimum:

- `README.md`
- `EXISTING_NCU_AUDIT.md`
- `EXISTING_METRIC_INVENTORY.tsv`
- `TARGET_BINDING.tsv`
- `NCU_CAPABILITY_QUERY.txt` if Phase B runs
- `METRIC_BINDING.tsv`
- `NATIVE_DOWNSTREAM_PROFILE.tsv`
- `SOURCE_PC_ATTRIBUTION.tsv` if available
- `FINAL_DECISION.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Also produce a compact report under the existing AWMA codex-handoff/report area.

## 10. Closure

At completion:

- close numerical/target identity;
- publish new raw only if Phase B ran;
- release GPU lock and allocations;
- commit exact review pack/tools;
- push exact commit;
- bounded Git transport fallback:
  HTTPS -> HTTP/1.1 -> GitHub SSH -> gh/API;
- fetch-back / remote SHA+tree verify;
- clean worktree;
- report whether Phase B used the GPU;
- report exact branch / commit / tree / node164 path / hashes;
- STOP.

Do not start any new 109 or 174 task automatically.
