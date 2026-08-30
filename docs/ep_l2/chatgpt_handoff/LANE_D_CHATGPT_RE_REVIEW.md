# EP-L2 Lane D V2 — ChatGPT Re-review

Status: **CONDITIONAL PASS — two analysis/provenance fixes remain; no simulator rerun required.**

Reviewed against coordination branch `hrl/ep-l2-exp-v0` and Lane-D source branch `hrl/ep-l2-cal-analysis-v0` at V2 source commit `2514e5d435af0f8d3d3ce62656cc427eb7210f3d`.

The V2 repair is materially improved and closes most findings from `LANE_D_CHATGPT_REVIEW.md`. Do not rerun or modify Lane A/B/C simulator jobs. The remaining issues are analysis/contract-only and must be repaired by reprocessing retained artifacts.

## 1. PASS — C7e admission-rate terminology is corrected

The V2 analyzer no longer presents C7e `bandwidth_util` as physical DRAM bus utilization. It is emitted as:

```text
lower_admission_byte_rate_norm
```

and physical per-5K-window bus utilization is explicitly `NOT_EMITTED / NOT_RETAINED_PER_5K_WINDOW`.

This is the correct interpretation of the C7e producer, which counts request bytes admitted into the DRAM path rather than low-level DRAM column/data-bus transfers.

## 2. PASS — temporal cardinality and stream-gap auditing are substantially fixed

For the current 22/26 scope the analyzer verifies:

```text
64 L2 slice streams
32 DRAM channel streams
5K window interval
expected row count == actual row count
full slice/channel ID sets
duplicate (stream,start) rejection
per-stream missing/gapped-window rejection
```

The observed 5000/5001 DRAM global-cycle cadence is documented as DRAM-clock sampling behavior and all current records pass.

The previous interim equality between L2-window and DRAM-window row counts is therefore confirmed to have been a post-processing summary bug, not a producer omission.

## 3. PASS — burst semantics and scheduler/ReturnQ cycle fractions

The previous loose `now > previous` burst rule is fixed. The metric is now explicitly:

```text
longest_high_average_window_run
```

with adjacency tied to the 5K cadence. It no longer implies the absence of sub-window bursts.

The V2 output also adds:

```text
scheduler_full_cycle_fraction
scheduler_full_window_fraction_{p50,p95,max}
returnq_full_cycle_fraction
returnq_full_window_fraction_{p50,p95,max}
```

which separates "a window had at least one full cycle" from "what fraction of time was actually full".

## 4. PASS — traffic-conditioned channel imbalance

The V2 analyzer now retains all-window imbalance for descriptive use but conditions causal interpretation on nontrivial traffic and reports active-channel and traffic-weighted metrics. This resolves the earlier `sad`-style near-idle max/mean artifact.

## 5. PASS — descriptor D512 hardware-cost analysis

Retain the existing D-COST result as reviewed PASS:

```text
additional 256 descriptors / slice
64-bit assumption:  2 KiB/slice, 128 KiB/chip
96-bit assumption:  3 KiB/slice, 192 KiB/chip
128-bit assumption: 4 KiB/slice, 256 KiB/chip
```

or about `1.39–2.78%` of the frozen 144 KiB/slice / 9 MiB chip payload budget. This remains a storage plausibility estimate, not an SRAM-area or performance claim.

## 6. PASS — validation evidence packaging and lane boundary

The V2 pack retains:

```text
12 pytest fixtures PASS
git diff --check evidence
clean-status evidence
SHA256SUMS
22-record real-data smoke
```

Lane D remains analysis/docs only; no functional RO no-MSHR, TVD, Unified borrowing, or simulator mechanism implementation was introduced.

---

# Remaining mandatory issue A — native DRAM `bwutil` is still parsed as the last channel, not a 32-channel application aggregate

This is a concrete implementation bug in V2.

GPGPU-Sim `dram_t::print()` is per DRAM channel (`DRAM[id]`) and prints that channel's:

```text
n_cmd=... bw_util=...
...
bwutil = ...
total_CMD = ...
```

The Lane-D function `native_dram_data_bus_util()` scans the whole raw log but only retains:

```text
last_util
last_n_cmd
```

It does not track `DRAM[id]` and does not aggregate the 32 channels. Therefore the single value currently written to `NATIVE_DRAM_BANDWIDTH.csv` is the last printed DRAM channel of the final observed snapshot, not a chip-wide/application aggregate physical data-bus utilization.

### Required fix

Parse the final complete native DRAM snapshot as 32 per-channel records. Prefer tracking the `DRAM[id]` block and pairing each channel's `n_cmd` with its native `bwutil/n_cmd`.

Emit at minimum:

```text
native_dram_channels_observed
native_dram_data_bus_util_weighted_mean
native_dram_data_bus_util_p50
native_dram_data_bus_util_p95
native_dram_data_bus_util_max
native_dram_n_cmd_sum
```

For the aggregate mean use the native denominator:

```text
sum(util_i * n_cmd_i) / sum(n_cmd_i)
```

which is equivalent to `sum(native_bwutil_i) / sum(n_cmd_i)`.

Fail closed unless the selected final snapshot contains exactly the configured 32 unique channels. If raw logs contain multiple native-stat snapshots, select/document the final complete 32-channel snapshot rather than mixing channels across snapshots.

Add a deterministic multi-channel fixture with unequal channel utilization; it must fail the old last-channel implementation and pass the new aggregate implementation.

Reprocess the existing 22 raw logs only. **No simulator rerun is authorized or needed.**

Do not call the current one-channel-last value an application/chip-wide physical bandwidth metric.

---

# Remaining mandatory issue B — effective-config contract is not yet cryptographically/semantically bound to the actual run config

The V2 `pair_status()` correctly compares the candidate contract's `effective_config` map against the base contract and rejects fields outside the authorized D512/META-HR/BANK-HR delta.

However, the actual run's:

```text
runtime_config_composite_sha256 / config_hash
```

is not checked against an expected config hash stored in the contract. The analyzer therefore proves only:

```text
contract effective_config differs in allowed fields
```

not:

```text
the simulator run actually used the config represented by that contract
```

A stale/incorrect contract could claim `descriptor_pool_size=512` as the only change while the actual run used another hidden config delta, and the current analyzer would not detect that from the contract itself.

The current `test_hidden_effective_config_change_is_rejected()` mutates the contract map; it does not test a mismatch between a run's actual config hash and its contract.

### Required fix

Extend `EP_L2_CALIBRATION_CONTRACT_V1` (or create V2) with at least:

```text
runtime_config_composite_sha256
config_delta_gate:
  status: PASS
  evidence_path: ...
```

Then in `artifact_run()` require:

```text
actual run config_hash == contract runtime_config_composite_sha256
```

before a record is accepted.

For D512 / Lane-C cells, the contract's config-delta gate should point to the lane's machine-readable or compact evidence proving the effective configuration differs from the formal semantic base only in its authorized fields.

Recommended stronger form:

```text
effective_config
normalized_effective_config_sha256
runtime_config_composite_sha256
config_delta_gate evidence path
```

Add tests for:

```text
run config hash != contract config hash -> REJECT
correct hash + authorized effective delta -> ACCEPT
correct hash + unauthorized effective delta -> REJECT
```

This is required before Lane D consumes Lane B/C results as provenance-safe calibration deltas.

---

## 7. Recommended hardening — cross-stream time-key alignment for channel imbalance

The current per-stream gap audit is good, but `channel_imbalance()` groups rows by exact `window_start_cycle`. For full robustness, also prove that every DRAM start-cycle group contains the configured 32 unique channel IDs (and similarly that every L2 start-cycle group contains 64 slices where applicable).

A pathological stream shifted by one cycle for every window can satisfy the current per-stream count/cadence test while splitting one logical window into separate groups. Current natural data appear consistent, so this is not evidence of a producer defect; add the group-cardinality/aligned-key check as analysis hardening while fixing A/B.

Also include `bandwidth_util_denominator_bytes` in the required fields for channel-imbalance analysis so a missing denominator yields `NOT_EMITTED`/failure rather than silently dropping that channel row.

## 8. Re-review acceptance

Lane D can be promoted to full PASS when:

```text
A. native physical DRAM bandwidth is final-snapshot 32-channel aggregated, with a multi-channel fixture
B. calibration contract is bound to each run's actual runtime config hash and config-delta evidence
C. existing 22 records reprocess cleanly
D. 12+ updated fixtures PASS
E. validation evidence/SHA256SUMS refreshed
F. no simulator rerun or functional mechanism change occurs
```

At that point the infrastructure may be treated as:

```text
TEMPORAL_ANALYSIS_READY
CALIBRATION_ANALYZER_READY
D512_COST_READY
```

for ingesting reviewed Lane A/B/C outputs.

Until then:

```text
D-COST: PASS
Temporal analysis excluding native aggregate: PASS/usable
CALIBRATION_ANALYZER_READY: CONDITIONAL
Lane D overall: CONDITIONAL_PASS
```
