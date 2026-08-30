# EP-L2 Lane A Final 26/26 — ChatGPT Independent Review

Date: 2026-08-30

Independent review status: **PASS**

Accepted final status:

```text
TARGET_BASELINE_26RUN_PASS
```

Reviewed runtime identity:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
Runtime config composite
          85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
```

Reviewed analysis identity:

```text
Lane-D V3 Framework
cb83606eb8640382b7c1932d8981b70608d9d130
```

Review pack:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1/
```

This PASS closes the frozen 850-MHz D256 Target Baseline campaign. It does **not** select D256 as the calibrated primary baseline over D512, and it does not authorize 1GHz or functional RO/TVD/Unified work before the later calibration/BASELINE-DECISION gate.

## 1. Source and configuration provenance — PASS

The accepted set contains exactly 26 direct `(workload, variant)` rows and uses one runtime source/config identity throughout.

Both exact runtime source commits are independently resolvable from GitHub and match the accepted provenance tables. The runtime Framework commit and Core commit are therefore independently source-auditable.

All accepted rows carry the same runtime config composite SHA-256 and frozen trace identity/hash per workload.

## 2. Completion / parser / invariants — PASS

The accepted set is exactly:

```text
13 workloads x {B0-Legacy, B0-Banked} = 26
```

Every accepted direct row is `COMPLETE_VALID`; parser/artifact checks and terminal/payload invariants pass.

The reviewed runner's `COMPLETE_VALID` state is produced only after successful simulator return, terminal-exit detection, parsing, and invariant checks. The supplement's `normal_exit` presentation is therefore redundant evidence rather than a missing acceptance gate.

## 3. 3mm duplicate-write incident — PASS

The earlier duplicate-writer incident is correctly quarantined.

Excluded diagnostic paths:

```text
C7E_DUPLICATE_WRITE_DIAGNOSTIC/B0-Legacy/3mm
C7E_DUPLICATE_WRITE_DIAGNOSTIC/B0-Banked/3mm
```

are explicitly listed as `EXCLUDED` and are outside the direct `B0-*/*` discovery used by the accepted analysis.

The clean direct replacements:

```text
B0-Legacy/3mm
B0-Banked/3mm
```

are both `COMPLETE_VALID`, use the frozen runtime source/config/trace identity, and both report 1,661,135 cycles. Exactly one clean row per `(3mm, variant)` enters the 26-row aggregate.

No rerun is required.

## 4. Final telemetry semantics / Lane-D V3 — PASS

The isolated Lane-D V3 analyzer reprocessed all 26 accepted rows with corrected semantics.

The analysis manifest reports exactly 26 records.

For all accepted rows:

```text
runtime-config contract binding       PASS
L2 stream/cardinality                 PASS
DRAM stream/cardinality               PASS
exact per-time-group alignment        PASS
final complete 32-channel DRAM snapshot PASS
```

The old producer field named `bandwidth_util` is used only as `lower_admission_byte_rate_norm`; it is not interpreted as physical bandwidth.

Physical application-level DRAM data-bus utilization comes from the final complete 32-channel native snapshot. No physical 5K-window bus metric is invented; it remains explicitly `NOT_EMITTED`.

## 5. Legacy vs Banked attribution — PASS

The final formal set supports the intended B0-Legacy/B0-Banked sanity result.

Twelve workload pairs have identical Legacy/Banked cycles. `cfd_097k` is the only accepted workload with a material Banked difference:

```text
Legacy 79,555 cycles
Banked 81,443 cycles
ratio  1.023732...
```

and the Banked row has measured true bank conflicts/wait cycles. `gemm` and clean `3mm` have zero measured true Banked conflicts and identical Legacy/Banked cycles, reinforcing that the old pre-C6d artificial Banked penalty is absent from the formal evidence.

## 6. Resource-pressure conclusions — PASS as observational baseline evidence

The final 26 rows preserve the 22/26 picture:

- descriptor-pool pressure is strong but workload-specific;
- no accepted D256 row has exact Line-MSHR-full blocking;
- per-address-cap blocks appear only in selected workloads;
- scan has tag-way/all-reserved pressure;
- WAD full/hazard pressure is workload-specific;
- payload-capacity allocation denial is zero in all accepted rows;
- small Legacy payload-service denials remain explicitly separate from capacity;
- lower/scheduler pressure is concentrated in traffic-heavy workloads;
- internal ReturnQ/DRAM->L2 return path is not a broad observed bottleneck;
- L1 retry/queue/bank pressure is substantial in several workloads and remains a competing causal candidate.

These are observed pressure signals, not mechanism-benefit claims.

## 7. Late gemm / 3mm rows — PASS / no conclusion reversal

The four late clean rows do not overturn the interim conclusions.

```text
gemm pair cycles: 556,340 / 556,340
3mm pair cycles:  1,661,135 / 1,661,135
```

Both workloads have:

```text
zero descriptor-pool-full
zero Line-MSHR-full
zero per-address-cap block
zero WAD-full
zero payload-capacity/service denial
zero tag-way block
zero L2->DRAM-full
zero Banked true conflict
```

Their descriptor maxima remain below 256 and Line-MSHR maxima below 128. Their native DRAM bus utilization is very low (~0.00735 for gemm and ~0.00575 for 3mm), while large L1 pressure remains visible. They therefore reinforce workload heterogeneity rather than adding a new EP-L2 bottleneck.

## 8. Temporal / physical-DRAM audit — PASS

All 26 Lane-D V3 records use:

```text
64 L2 slices
32 DRAM channels
5000-cycle completed windows
```

with expected/actual row counts equal and exact time-group stream membership.

Application-level native physical DRAM bus values are available for all 26 rows from complete 32-channel snapshots. Examples from the final Banked set include approximately:

```text
scan        0.81865
vectorAdd   0.79584
spmv        0.66605
convolution 0.65109
FWT_7_21    0.16292
cfd         0.17225
gemm        0.00735
3mm         0.00575
```

Thus high scheduler pressure at low aggregate physical bus utilization remains meaningful evidence of burst/channel/local scheduling effects rather than simple chip-wide bandwidth saturation.

## 9. Packaging / reproducibility — PASS

The review-ready supplement contains:

```text
accepted-run set
excluded diagnostic set
A-K matrix
source/analysis anchors
formal provenance audit
raw-log index/hashes
Lane-D V3 source copy and contract
final aggregate tables
interim-to-final reconciliation
SHA256SUMS
```

The original final pack is preserved separately and the supplement is documentation/analysis-only.

## Final decision

All mandatory Target Baseline acceptance gates are independently accepted.

```text
LANE_A_FINAL_26OF26_PASS
TARGET_BASELINE_26RUN_PASS
```

The D256 850-MHz campaign is now a valid frozen reference dataset for calibration and mechanism research.

Next scientific decision is **not** another Lane-A run. It is the combined calibration decision using promoted D512, L1-causality, Line-MSHR-causality, and Lane-D evidence.
