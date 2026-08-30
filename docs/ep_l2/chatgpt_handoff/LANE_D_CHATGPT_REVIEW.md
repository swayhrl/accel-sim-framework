# EP-L2 ChatGPT Review — Lane D Analysis / Cost Infrastructure

Updated: 2026-08-30

Overall status: **CONDITIONAL PASS**.

Lane D respected its isolation boundary and did not implement functional RO/TVD/Unified mechanisms. The temporal-cardinality repair and descriptor-cost analysis are useful. However, the current analyzer must be repaired before it can safely ingest the planned D512/L1 calibration cells.

No item below requires rerunning the current Lane-A simulator campaign. The required fixes are analysis/provenance/post-processing unless a later audit proves otherwise.

## 1. PASS — temporal stream topology/cardinality

The original interim summary's identical L2/DRAM window counts were a post-processing summary error, not a producer omission.

The raw parsed streams show:

```text
L2 windows:   64 physical slice streams
DRAM windows: 32 physical channel streams
interval:     5000 cycles
only complete windows emitted
```

For the 22 completed formal runs, expected and actual row counts agree, and all expected slice/channel IDs are present.

This closes the earlier concern that C7e may have emitted only one L2 stream per channel.

### Required hardening

The analyzer should additionally reject duplicate or missing `(stream_id, window_start)` keys, not only verify total row count and unique stream count. A missing window in one stream and duplicate in another could otherwise cancel in the aggregate count.

## 2. PASS — Descriptor-512 hardware-cost estimate as a planning range

`DESCRIPTOR_METADATA_COST.md` correctly separates proposed hardware metadata from C++/host storage.

The 64/96/128-bit packed planning range implies that adding 256 descriptors/slice costs approximately:

```text
2--4 KiB / slice
128--256 KiB / 64-slice chip
1.39--2.78% of the frozen 144 KiB/slice (9 MiB chip) payload budget
```

This is sufficient to justify D512 as a plausible calibration experiment. It is **not** yet an SRAM-area or implementation-timing result and must remain labeled that way.

Review: `D-COST = PASS`.

## 3. BLOCKING FOR FUTURE CALIBRATION INGESTION — cross-SHA pairing logic

Current `pair_status()` requires exact equality of:

```text
Core SHA
Framework SHA
```

between D256 base and every candidate cell.

That is too strict for the actual parallel plan. Lane B has already generalized descriptor-cardinality telemetry on isolated source commits. Even if its mandatory D256 backward-equivalence gate proves semantic/timing equivalence, a valid D512 result will naturally have a different source SHA and the current Lane-D analyzer will reject it as a source mismatch.

### Required fix

Do **not** remove source checking. Introduce an explicit reviewed compatibility/lineage contract, for example:

```text
semantic_base_id
base_core_sha
base_framework_sha
candidate_core_sha
candidate_framework_sha
equivalence_gate_id / evidence path
allowed_source_delta_class
```

A changed SHA may be paired only if the candidate manifest explicitly declares derivation from the approved formal base and references a PASS equivalence gate. Unreviewed source changes must still be rejected.

Add fixtures for:

```text
same-SHA compatible pair
reviewed-equivalent changed-SHA pair -> accepted
changed-SHA without equivalence evidence -> rejected
wrong base lineage -> rejected
```

Until this is fixed, `CALIBRATION_ANALYZER_READY` is only CONDITIONAL.

## 4. BLOCKING FOR CAUSAL SAFETY — config-hash delta is not sufficient

Current logic accepts a differing config hash whenever descriptor capacity or `l1_config_class` differs. It does **not** prove that the hash changed *only* because of the authorized experimental dimensions.

Therefore a D512 cell that accidentally also changed a queue, DRAM parameter, or other resource could still be accepted as `COMPATIBLE_DECLARED_CELL_DELTA`.

### Required fix

Consume a machine-readable effective-config contract from Lane B/C. At minimum compare either:

```text
normalized effective config key/value map
```

or

```text
frozen_config_fingerprint excluding explicitly allowed experimental fields
+ explicit allowed-field diff
```

For example:

```text
D512_BASE:
  allowed diff = descriptor_pool_size only

D256_META_HR:
  allowed diff = L1 MSHR, merge cap, MissQ only

D256_BANK_HR:
  allowed diff = L1 bank count only

D512_META_HR:
  allowed diff = descriptor pool + named META-HR fields only
```

Add rejection fixtures for an extra hidden config change.

The current test named `test_calibration_pairing_accepts_only_declared_dimensions` does not actually prove this; it changes only the opaque hash and trusts the cell label.

## 5. IMPORTANT SEMANTIC CORRECTION — current C7e `bandwidth_util` is not physical DRAM data-bus utilization

Source audit of C7e Core `ece1a3a7...` shows:

1. `c7e_record_dram_success()` counts `mf->get_data_size()` when a request leaves L2->DRAM arbitration and enters the DRAM-latency/DRAM path.
2. C7e computes `bandwidth_util_denominator_bytes = dram_cycles * dram_atom_size`.
3. In the actual `dram_t`, a request whose `nbytes > dram_atom_size` is transferred over multiple column/data beats; `issue_col_command()` advances `txbytes` by exactly `dram_atom_size` per data command and native `bwutil` tracks those actual issued column beats.

Therefore the C7e numerator can credit an entire multi-atom request at admission time while the denominator assumes one atom/cycle. This is why Lane-D window output can exceed 1.0 (for example scan and dwt2d have window maxima above 1).

### Consequence

Do not call the existing C7e field physical `DRAM bandwidth utilization` in scientific analysis.

Rename/relabel it in Lane-D outputs to something like:

```text
lower_admission_byte_rate_norm
```

or

```text
accepted_request_bytes_per_dram_atom_cycle
```

and document that it measures lower-path admission intensity, not data-bus occupancy.

### Recover physical utilization without rerunning Lane A

Prefer parsing the simulator's existing native DRAM `bwutil / n_cmd` (or another source-audited native data-bus metric) from the already-retained raw logs for application-level physical BW. Preserve the C7e admission-byte metric separately.

For 5K temporal analysis, if no native physical data-bus window metric was retained, report it as unavailable rather than treating the C7e normalized admission bytes as physical BW. Scheduler occupancy/full-cycle telemetry remains valid and useful.

This correction changes interpretation, not simulator validity.

## 6. Temporal burst semantics need tightening

Current `longest_burst()` treats any strictly increasing timestamp as consecutive. It should require the next timestamp to equal `previous + interval_cycles`.

Also, current descriptor/scheduler `high_burst_windows` is based on the **window average** crossing 90% capacity. It cannot detect a short full episode inside a 5K window.

This matters for workloads such as `FWT_11_19`: application telemetry records real descriptor-pool-full events, but the 5K descriptor average remains low enough that no `>=90% average` window is observed.

### Required fix

Rename the metric to reflect what it actually proves, e.g.:

```text
longest_high_average_window_run
```

and never interpret zero as `no burst`.

If the producer does not emit within-window max/block deltas, explicitly state that sub-5K bursts cannot be localized by this telemetry.

Add a fixture with a missing time window to ensure a gap breaks a run.

## 7. Scheduler-full temporal metric should include cycle fraction

`scheduler_full_active_fraction` currently means:

> fraction of 5K channel-window records containing at least one full cycle.

That is useful, but it can make a workload look sustained when each 5K window contains only a handful of full cycles.

Also report:

```text
sum(scheduler_full_cycles) / sum(dram_cycles)
per-window scheduler_full_cycle_fraction p50/p95/max
```

and the analogous ReturnQ metric where useful.

Keep `window-active fraction` and `cycle fraction` as separate semantics.

## 8. Channel-imbalance metric needs traffic conditioning

Raw `max/mean` and CV can explode when total traffic in a window is tiny. The current output demonstrates this: sparse `sad` windows can report max/mean=32 even though the lower path is not a performance bottleneck.

Add traffic-conditioned summaries, for example:

```text
active channel count
aggregate bytes in the window
imbalance only for windows above an explicitly documented traffic threshold
traffic-weighted imbalance summary
```

Do not use extreme max/mean values from near-idle windows as evidence of a memory-channel bottleneck.

## 9. Review-evidence packaging gap

`LANE_D_LATEST.md` reports 7 tests PASS, but the browsable review pack does not currently retain compact validation evidence.

Add at least:

```text
VALIDATION_SUMMARY.md
validation/pytest.txt
validation/git_diff_check.txt
validation/git_status.txt
```

or equivalent compact retained evidence. No large logs are needed.

## 10. Boundary compliance

PASS.

The Lane-D source commit adds only the analysis script and its test file. No functional simulator mechanism was implemented, and no RO no-MSHR/TVD/Unified performance result is claimed.

## 11. Revised Lane-D review gates

Current review state:

```text
Temporal stream cardinality:       PASS
Descriptor metadata cost:          PASS
Boundary/isolation compliance:     PASS
Temporal scientific interpretation: CONDITIONAL_PASS
Calibration analyzer provenance:   CONDITIONAL_PASS
Calibration config-delta safety:   CONDITIONAL_PASS
Validation evidence packaging:     CONDITIONAL_PASS
```

Overall:

```text
LANE_D_CONDITIONAL_PASS
```

Lane D should repair the analysis/provenance issues above, rerun only its analyzer/tests/post-processing on existing data, update `LANE_D_LATEST.md` and `CALIBRATION_ANALYSIS_INFRA_r1`, then request re-review.

Do not rerun Lane-A simulator jobs for these fixes.
