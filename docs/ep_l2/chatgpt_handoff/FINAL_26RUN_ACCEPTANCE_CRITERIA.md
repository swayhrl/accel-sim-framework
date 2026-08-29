# EP-L2 Final 26-Run Acceptance Criteria

This file defines when the expensive Target-Baseline campaign is complete and review-ready.

## A. Source/config uniformity — mandatory

PASS only if all 26 formal runs share:

```text
one FINAL_CORE_SHA
one runtime FINAL_FRAMEWORK_SHA
one frozen base config hash
one B0-Legacy overlay hash
one B0-Banked overlay hash
one trace identity per frozen workload
850 MHz primary frequency
```

If runtime source/config changes after any formal run begins, all affected previously completed formal runs must be quarantined and the formal campaign restarted on the new accepted pair.

Pure post-processing-only Framework changes may preserve raw simulation logs only if simulator runtime/producer output is unchanged and runtime-vs-analysis SHAs are explicitly recorded.

## B. Run completeness — mandatory

PASS requires:

```text
COMPLETE_VALID = 26/26
FAILED = 0
TIMEOUT = 0
```

Every workload must have both Legacy and Banked variants.

## C. Provenance — mandatory

Every run must have a manifest/status record proving:

```text
Core SHA
Framework runtime SHA
config hashes
trace path/hash or frozen trace identity
variant
frequency
normal simulator exit
terminal cycle
wall time
```

The campaign root must contain one authoritative immutable campaign manifest.

## D. Terminal correctness — mandatory

PASS only if every run reports all required invariants as valid, including at least:

```text
descriptor/resource drain
WAD drain
pending resident-sector drain
bypass drain
bank pending drain
resident-tag/payload ownership consistency
no double owner
no stale response violation
no credit leak where applicable
```

No invariant may be weakened or disabled to obtain 26/26.

## E. Required parsed artifacts — mandatory

Every formal run must contain all applicable final-schema artifacts:

```text
target_summary.csv
target_slice.csv
target_kernel.csv
target_bank.csv
target_window.csv
target_l1.csv
target_dram.csv
manifest.json
run_status.json
```

Empty tables are acceptable only when semantically valid and explicitly documented (for example no overlapping kernels); mandatory application-level telemetry may not be absent.

## F. Mandatory telemetry coverage — mandatory

The final aggregate must have measured, not inferred, values for:

```text
Tag-way need/block
Line-MSHR need/full block
Descriptor need/pool-full block
Per-address-cap checks/block
Descriptor chain depth
WAD occupancy/full/hazard/lifetime
Payload resident/dirty/pending/bypass roles
Payload service vs capacity denial
Bank true contention and wait
L1D accesses/misses/failure classes/bank conflict
MissQ
L2->DRAM FIFO
successful DRAM read/write issues
successful DRAM read/write bytes
scheduler causal block and time-weighted occupancy
internal DRAM ReturnQ occupancy/full
per-slice DRAM->L2 FIFO pressure
DRAM bandwidth utilization
5K temporal data
```

If a mandatory field is `NOT_EMITTED`, semantically mislabeled, or missing from a substantial subset of runs, the campaign is not accepted.

## G. Legacy/Banked attribution sanity — mandatory

For every pair compare:

```text
cycles
traffic
payload operation mix
bank logical ops
true conflict rate
wait cycles
other resource blockers
```

Flag `ATTRIBUTION_WARNING` when Legacy/Banked performance changes materially but measured bank/service differences cannot plausibly explain the direction or when unrelated traffic/config differs.

Warnings do not automatically fail the campaign, but unresolved source/config mismatch does.

## H. Temporal and kernel integrity — mandatory

PASS only if:

```text
5K windows cover the long-running intervals of representative workloads
window sample ranges are monotonic/non-overlapping as defined
sequential-kernel additive counters reconcile with application totals where they should
kernel overlap is explicitly marked
channel-level DRAM records are not duplicated and double-counted as per-slice values
```

## I. Aggregate analysis artifacts — mandatory

The campaign is not complete until these are generated and internally consistent:

```text
TARGET_BASELINE_FINAL_STATUS.tsv
target_baseline_comparison.csv
target_resource_pressure.csv
target_blocking_matrix.csv
target_bank_pressure.csv
target_lower_path.csv
target_l1_pressure.csv
target_temporal_summary.csv
target_kernel_summary.csv
TARGET_BASELINE_BOTTLENECK_ANALYSIS.md
TARGET_BASELINE_CLOSEOUT.md
campaign_manifest.json
RAW_LOG_INDEX.tsv
SHA256SUMS
```

## J. Scientific interpretation discipline — mandatory

The first-pass report must distinguish:

```text
high utilization
actual blocking
correlation/association
causal sensitivity evidence
```

Do not state that a resource is a performance bottleneck solely because occupancy is high.

Use conservative labels such as:

```text
DOMINANT_OBSERVED_BLOCKER
SECONDARY_BLOCKER
HIGH_UTIL_NOT_BLOCKING
MIXED
NO_CLEAR_INTERNAL_BOTTLENECK
```

where appropriate.

Do not claim RO/TVD/Unified opportunity magnitude from baseline data alone.

## K. Review packaging — mandatory

Create and push a directly browsable review directory:

```text
docs/ep_l2/review_packs/FINAL_TARGET_BASELINE_850_r1/
```

and update the permanent coordination-branch entry:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
```

Large raw logs/build artifacts must not be committed; they must be indexed.

## L. Final campaign result

The stage ends with exactly one of:

```text
TARGET_BASELINE_26RUN_PASS
```

or

```text
TARGET_BASELINE_26RUN_FAIL
```

`PASS` requires A-K to pass.

After PASS, STOP. Do not automatically launch 1 GHz or opportunity experiments.
