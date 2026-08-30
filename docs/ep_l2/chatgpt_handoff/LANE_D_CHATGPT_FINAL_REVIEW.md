# EP-L2 Lane D V3 — ChatGPT Final Review

Date: 2026-08-30

Final review status: **PASS**

Reviewed source:

```text
Framework analysis branch: hrl/ep-l2-cal-analysis-v0
V3 source commit: cb83606eb8640382b7c1932d8981b70608d9d130
Coordination review pack: docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/
```

This PASS applies to the Lane-D analysis / provenance / cost infrastructure. It does **not** complete `CAL-ANALYSIS` scientifically because D512/L1 calibration inputs are still arriving, and it does not authorize `BASELINE-DECISION`.

## 1. Final-complete native DRAM aggregation — PASS

The V2 last-channel bug is fixed.

`native_dram_data_bus_util_from_lines()` now:

- recognizes native `DRAM[id]` blocks;
- builds snapshots keyed by channel ID;
- discards incomplete snapshots;
- selects the final snapshot containing exactly all configured channels;
- emits `native_dram_channels_observed`;
- computes `native_dram_data_bus_util_weighted_mean = sum(util_i * n_cmd_i) / sum(n_cmd_i)`;
- emits channel p50/p95/max and total `n_cmd`;
- fails closed when no complete snapshot exists.

The unequal-weight fixture proves this is not the old last-channel behavior. The 22 existing formal interim runs all report `PASS_FINAL_COMPLETE_CHANNEL_SNAPSHOT` with 32 channels.

Interpretation boundary remains correct: this is the application-level native physical DRAM data-bus metric. No native physical 5K-window bus metric was retained.

## 2. C7e admission-rate semantics — PASS

The old C7e field previously called `bandwidth_util` is no longer interpreted as physical DRAM utilization. Lane D exposes it as:

```text
lower_admission_byte_rate_norm
```

The temporal physical bus metric is explicitly:

```text
NOT_EMITTED / NOT_RETAINED_PER_5K_WINDOW
```

This closes the semantic issue found during V1 review.

## 3. Runtime config <-> contract binding — PASS

Calibration contracts are now schema:

```text
EP_L2_CALIBRATION_CONTRACT_V2
```

Each consumed cell must provide:

```text
runtime_config_composite_sha256
config_delta_gate.status = PASS
config_delta_gate.evidence_path
```

`artifact_run()` obtains the actual runtime digest from the run/campaign manifest and calls `contract_binding_status()` before accepting the record. A mismatch raises an error and prevents analysis.

The contract still carries normalized effective configuration and exact allowed fields, so later pair comparison also rejects hidden effective-config deltas.

For the current D256 formal input, the contract binds exactly to:

```text
85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
```

and the 22-row matrix records `PASS_RUNTIME_CONFIG_BOUND`.

## 4. Cross-SHA lineage / equivalence — PASS

The analyzer no longer requires identical source SHAs for every calibration cell. Changed source SHAs are accepted only when the candidate contract:

- names the formal base Core/Framework SHA pair;
- names the actual candidate SHA pair;
- shares the same semantic base ID;
- supplies an equivalence gate with `status=PASS`, ID, and evidence path;
- declares a non-NONE allowed source-delta class.

This is the correct model for Lane B's timing-equivalent descriptor telemetry generalization and later derived Lane-C cells.

Future B/C gate evidence remains subject to normal review; a contract-declared PASS is not by itself a ChatGPT scientific acceptance decision.

## 5. Temporal stream integrity — PASS

For each run Lane D now checks:

```text
expected vs actual row cardinality
unique stream ID sets
duplicate (stream,start) keys
per-stream missing/gapped windows
exact per-time-group full stream membership
```

All 22 interim records pass:

```text
L2  : 64 slices
DRAM: 32 channels
interval: 5000 cycles
```

The verified 5000/5001 DRAM global-start cadence is handled explicitly without treating it as missing data.

## 6. Burst / full-cycle / imbalance semantics — PASS

The V1/V2 interpretation issues are closed:

- burst output is named as a **longest high-average-window run**, not absence/presence of sub-window bursts;
- scheduler/ReturnQ expose full-cycle fractions plus per-window p50/p95/max;
- channel imbalance requires both numerator and denominator fields;
- every imbalance time group must contain exactly all configured channels;
- near-idle windows are separated via traffic-conditioned metrics;
- traffic-weighted imbalance is retained;
- missing fields remain `NOT_EMITTED`, never silently zero or silently dropped.

## 7. Tests / reproducibility / packaging — PASS

V3 retains:

```text
17/17 pytest PASS
git diff --check PASS
clean-status evidence
VALIDATION_SUMMARY.md
SHA256SUMS
reproduction command
ANALYSIS_MANIFEST.json
```

The 17 fixtures cover the important failure modes including weighted native aggregation, incomplete native snapshots, config-hash mismatch, changed-SHA equivalence, unauthorized config changes, missing denominators, stream gaps/alignment, missing values, and duplicate records.

## 8. Descriptor-512 hardware metadata cost — PASS

The previously reviewed cost result remains accepted:

```text
increment for D256 -> D512:
  2-4 KiB / L2 slice
  128-256 KiB / 64-slice chip
  about 1.39-2.78% of the frozen payload-byte budget
```

It is correctly labeled as raw hardware metadata storage estimation, not technology-area or performance estimation.

## 9. Scope / non-interference — PASS

V3 is analysis/docs/test-only relative to the previous Lane-D source. No Lane-A/B/C simulator runtime source/results were modified or rerun, and no functional RO no-MSHR, TVD, or Unified mechanism was implemented.

## Final decision

Lane D has satisfied the mandatory infrastructure gates:

```text
TEMPORAL_ANALYSIS_READY          PASS
CALIBRATION_ANALYZER_READY      PASS
D512_COST_READY                  PASS
```

Therefore:

```text
LANE_D_INFRASTRUCTURE_PASS
```

Lane D should now freeze the analysis semantics except for bug fixes. As Lane A/B/C outputs arrive it may ingest speculative data for provisional dashboards, but accepted `CAL-ANALYSIS` deltas must use promoted evidence plus the V2 calibration contracts. `BASELINE-DECISION` remains a later combined ChatGPT review gate.
