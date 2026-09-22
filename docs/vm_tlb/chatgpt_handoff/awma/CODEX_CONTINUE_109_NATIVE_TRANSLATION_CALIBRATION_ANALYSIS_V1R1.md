# CODEX 109 CONTINUATION — Native Translation Calibration Analysis V1R1

Date: 2026-09-22

Mode:

`GOAL MODE / CPU-ONLY ANALYZE-AND-CLOSE / solve-and-continue`

Node:

`109 / node164 read-only evidence consumer`

Stage:

`AWMA_NATIVE_TRANSLATION_CALIBRATION_ANALYSIS_109_V1R1`

Read first:

1. `REVIEW_109_NATIVE_TRANSLATION_CALIBRATION_EVIDENCE_V1_2026-09-22.md`
2. execution authority `hrl/awma-native-calibration-evidence-v1 @ 724ca2b583495c87d9cfb59e277caf81fcecec1d`
3. original `CODEX_109_NATIVE_TRANSLATION_CALIBRATION_EVIDENCE_V1.md`
4. `EXECUTION_PRIORITY_POLICY_V5.md`

This continuation is NOT a new GPU capture campaign.

## 0. Hard execution boundary

Do NOT launch:

- NSYS;
- NCU;
- NVBit;
- simulator-native recapture;
- Accel-Sim;
- any CUDA timing rerun;

unless deterministic verification proves an existing durable artifact is corrupt/unusable and continuing would otherwise require scientific review.

Default mode is CPU-only parsing, hashing, summary, and provenance closeout.

Do not modify accepted raw bundles on node164.

## 1. Native microbenchmark numerical summary

Consume the durable raw files already published under:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/native_translation_calibration_109_v1_20260922T101218Z/`

including:

- `NATIVE_TLB_RECON_RAW_CORE.tsv`
- `NATIVE_TLB_RECON_FOLLOWUPS.tsv`

Use only the actual captured rows.

Create:

`NATIVE_MICROBENCH_SUMMARY.tsv`

For every admitted configuration report, as applicable:

- stride_bytes;
- locations;
- bytes;
- warps;
- steps;
- samples;
- policy;
- warmup/thrash setting;
- sample count;
- mean / median / p10 / p90 cycles_per_load;
- mean / median overhead_cycles;
- net cycles/load only if the subtraction is mathematically and methodologically justified; otherwise omit it;
- coefficient of variation or robust dispersion;
- source row/file authority.

Do not remove outliers solely to improve the curve. If malformed rows exist, report the exclusion rule explicitly.

## 2. Behavioral calibration matrix

Create:

`NATIVE_TRANSLATION_BEHAVIOR_MATRIX.tsv`

Answer quantitatively, without asserting hidden hardware structure:

### A. Working-set exposure

For dependent 1-warp 4 KiB-spacing chains:

- how cycles/load changes with increasing locations/footprint;
- any reproducible knee / plateau / discontinuity;
- exact compared configurations.

### B. Concurrency hiding

For matched working set and stride:

- compare 1 warp vs multi-warp configurations;
- compute per-warp cycles/load distribution and relative change;
- distinguish latency exposure from aggregate throughput where the raw data permit.

The key comparison must include the representative pair underlying:

- M1_DEPENDENT_LARGE
- M2_MULTIWARP_HIGH

### C. Spacing sensitivity

Compare matched or nearest-valid 4 KiB vs 64 KiB spacing conditions.

Do NOT call either spacing the RTX4080 hardware page size.

### D. Cache-policy / thrash controls

If follow-up rows contain `cg`, default-cache, or thrash controls:

- report them separately;
- identify whether the apparent working-set behavior persists when cache reuse is reduced;
- do not mix unlike policies into one curve.

Final interpretation must be one of:

- `NATIVE_CONCURRENCY_HIDING_SUPPORTED`
- `NATIVE_CONCURRENCY_HIDING_PARTIAL`
- `NATIVE_CONCURRENCY_HIDING_NOT_OBSERVED`
- `NATIVE_BEHAVIOR_INSUFFICIENTLY_ISOLATED`

This classification is behavioral only; it does not assign a TLB latency/capacity.

## 3. Microbenchmark resource-control summary

Consume existing durable NCU microbenchmark diagnostics.

Create:

`NATIVE_MICROBENCH_RESOURCE_SUMMARY.tsv`

For each selector-qualified representative configuration, report available:

- DRAM bytes;
- L2/LTS bytes;
- L1TEX bytes;
- active-warps metric;
- exact metric name / unit;
- selector status;
- replay/cache-control settings if present.

Use these only to judge whether compared Native timing points also changed data-cache/DRAM regime substantially.

If a selector cannot be proven, mark the row `NOT_ADMITTED_SELECTOR_UNRESOLVED`.

Do not create a synthetic TLB metric.

## 4. Exact T0 Native page-footprint closure

Use the accepted Route-B parser already qualified by the prior producer work.

Input authority:

- exact T0 Route-B durable bundle;
- trace SHA256 `48d2485ceddc44203c31b29ff365b400874c9e0fa754888aea14392f5d02cd904`;
- zero drop/overflow;
- durable ACK already PASS.

Create:

`T0_NATIVE_FOOTPRINT.tsv`

At minimum:

- raw dynamic records;
- memory instruction records;
- effective lane addresses;
- unique 4 KiB address regions;
- unique 64 KiB address regions;
- parser/source/version/hash authority.

Do not interpret 4 KiB/64 KiB aggregation as proof of hardware TLB page size.

No fresh capture.

## 5. Representative microtrace qualification receipts

For each existing trace:

- M0_COMPACT
- M1_DEPENDENT_LARGE
- M2_MULTIWARP_HIGH
- M3_STRIDE64K

Create:

`MICROTRACE_QUALIFICATION_RECEIPTS.tsv`

Include:

- trace_id;
- exact configuration;
- executable/source authority;
- exact selector identity;
- run ID;
- durable node164 path;
- source manifest SHA;
- destination verification/manifest SHA;
- trace payload filename;
- trace payload SHA256;
- record count;
- drop count;
- overflow count;
- xz integrity status;
- frozen grammar-validator status, if the trace format requires/has that validator;
- final admission status.

Use surviving manifests/receipts/logs deterministically.

Missing P2/P3 wrappers must follow EXECUTION_PRIORITY_POLICY_V5:
reconstruct if deterministic; do not recapture a P1 trace merely because a wrapper is missing.

Do not mark `ACCEPTED` unless payload identity and integrity are actually closed.

Also reconcile the prior review-pack metadata inconsistency: `RAW_DATA_INDEX.tsv` still says `DURABLE_SHA256_VERIFY_PASS_44_MEMBERS` while the final durable ACK reports 76 verified members after adding four microtrace bundles. Correct this in V1R1 provenance without mutating historical V1 files.

## 6. Exact-target Native timing interpretation

Carry forward the already captured values without rerun.

Create:

`EXACT_TARGET_NATIVE_TIMING_SUMMARY.tsv`

Include mean/median/std/CV and interpretation:

- T0 Q05: 5-run mean 152717.0 ns; CV ~4.567%; label `MEASURED_WITH_VARIABILITY`.
- T1 GEMM: 5-run mean 203591.2 ns; CV ~0.286%; label `STABLE_NATIVE_TIMING_ANCHOR`.
- T2 GEMV: 5-run mean 4422.4 ns; CV ~1.073%; label `STABLE_NATIVE_TIMING_ANCHOR`.

Recompute these values from source rows; do not copy blindly from this instruction.

Do not fit simulator cycles to these timings.

## 7. External-calibration readiness decision

Create:

`NATIVE_CALIBRATION_READINESS.md`

Separate:

### ADMITTED for future Legacy/V1/V2 cross-calibration

Only evidence with identity + provenance + measurement semantics closed.

### SUPPORTING_ONLY

Useful but not exact-target or not directly translation-specific.

### NOT_ADMITTED

Unresolved selector, missing summary, invalid evidence class, etc.

The decision should answer:

> Are the four representative simulator-native microtraces and corresponding Native behavioral measurements now sufficiently closed to be handed to 174 for Legacy/V1/V2 simulator comparison?

Allowed outcomes:

- `READY_FOR_SIMULATOR_CROSS_CALIBRATION`
- `READY_WITH_SCOPE`
- `NOT_READY_MISSING_IDENTITY_OR_BEHAVIORAL_CLOSURE`

## 8. Review pack / publication

Report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_TRANSLATION_CALIBRATION_ANALYSIS_109_V1R1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_TRANSLATION_CALIBRATION_ANALYSIS_109_V1R1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
NATIVE_MICROBENCH_SUMMARY.tsv
NATIVE_TRANSLATION_BEHAVIOR_MATRIX.tsv
NATIVE_MICROBENCH_RESOURCE_SUMMARY.tsv
T0_NATIVE_FOOTPRINT.tsv
MICROTRACE_QUALIFICATION_RECEIPTS.tsv
EXACT_TARGET_NATIVE_TIMING_SUMMARY.tsv
NATIVE_CALIBRATION_READINESS.md
RAW_DATA_INDEX.tsv
RUN_RECEIPTS.json
SHA256SUMS
```

CPU analysis can run in parallel across independent raw files.

Do not spend GPU time on documentation symmetry.

Publish commit and push; fetch-back and remote-tree verify; clean worktree; STOP for ChatGPT review.

This continuation does not affect or wait for 174-new V2.
