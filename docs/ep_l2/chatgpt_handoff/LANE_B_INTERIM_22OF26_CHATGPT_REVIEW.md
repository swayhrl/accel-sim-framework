# EP-L2 Lane B D512 Interim 22/26 — ChatGPT Review

Date: 2026-08-30

Review status: **CONDITIONAL PASS — CONTINUE THE FOUR LIVE RUNS**

This review covers the interim pack:

```text
docs/ep_l2/review_packs/D512_CALIBRATION_INTERIM_22OF26_r1/
```

and does not authorize `D512_READY`, `D512_MIRROR_COMPLETE`, `BASELINE_DECISION`, or any functional RO/TVD/Unified mechanism.

## 1. Execution / provenance — PASS for continuing

The 22 completed D512 rows are locally `COMPLETE_VALID`, use one frozen candidate pair and one D512 runtime composite digest:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
D512 runtime composite SHA-256
a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
Descriptor pool = 512
Frequency = 850 MHz
```

The completed rows correctly remain `SPECULATIVE_PENDING_GATE` pending D512 preflight promotion. No completed row should be rerun on the evidence currently reviewed.

The four live rows are:

```text
B0-Banked / scan
B0-Legacy / scan
B0-Legacy / 3mm
B0-Banked / 3mm
```

The supplied health snapshot shows all four active with growing logs. Do not disturb them.

## 2. D256 backward equivalence — PASS

The generalized Core source configured back to D256 reproduces formal C7e on:

```text
vectorAdd_4M
spmv
scan
```

All seven parsed artifacts are reported byte-identical for each workload, with exact cycles/instructions/L1/DRAM/descriptor/invariant agreement. This is strong evidence that the D512 telemetry/cardinality generalization is observation/parameterization-only at the original D256 configuration.

The formal semantic base remains:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
runtime   85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
```

### Packaging correction required

`D256_EQ_SCAN_GATE.json` currently records the gate itself with:

```text
maturity = PROMOTED_VALID_CALIBRATION
promotion_dependencies = [D256_EQ_SCAN_PASS, D512_PREFLIGHT_PASS]
```

The D256 equivalence gate is independent of D512 preflight and must not depend on itself. In the final Lane-B pack, represent the D256 equivalence gate simply as a PASS validation/equivalence gate. Only D512 descendant runs require `D512_PREFLIGHT_PASS` for promotion.

This is a metadata/packaging correction, not a simulator rerun requirement.

## 3. >256 descriptor telemetry — PASS

Natural D512 rows already prove that telemetry is no longer clipped at the former 256 boundary:

```text
vectorAdd_4M: descriptor p95/max = 339 / 368
spmv:         descriptor p95/max = 382 / 403
FWT_7_21:     descriptor p95/max = 280 / 383
convolution:  descriptor p95/max = 321 / 427
```

This satisfies the main natural-workload cardinality requirement independently of the directed boundary tests.

## 4. Descriptor relief — strong pressure relief, no performance win in completed heavy cases

For the completed descriptor-heavy workloads, D256 descriptor-pool-full blocks collapse to zero under D512:

```text
vectorAdd_4M       2,176,663 -> 0
spmv                 361,635 -> 0
convolutionSeparable 3,373,327 -> 0
FWT_7_21           1,189,823 -> 0
FWT_11_19            119,765 -> 0
```

But D512 does not speed these completed workloads up:

```text
vectorAdd_4M       73,325 -> 73,873   (~0.75% slower)
spmv               23,453 -> 23,560   (~0.46% slower)
convolution        290,308 -> 292,211 (~0.66% slower)
FWT_7_21          493,466 -> 495,811  (~0.48% slower)
FWT_11_19         171,549 -> 171,778  (~0.13% slower)
```

Thus the completed subset supports a conservative statement: D256 descriptor capacity is a real admission-pressure ceiling, but simply enlarging it to 512 does not by itself improve performance. Pressure is redistributed to other resources.

## 5. MATERIAL CORRECTION: convolution exposes real Line-MSHR full blocking

The interim research-findings document incorrectly states that convolution reaches Line-MSHR capacity while exact Line-MSHR full blocking remains zero.

The actual D512 data show:

```text
convolutionSeparable / D256:
  descriptor_pool_full_block = 3,373,327
  line_mshr_avg/p95/max       = 42 / 112 / 126
  line_mshr_full_block        = 0
  cycles                      = 290,308

convolutionSeparable / D512:
  descriptor_pool_full_block = 0
  line_mshr_avg/p95/max       = 46 / 128 / 128
  line_mshr_full_block        = 931,416
  cycles                      = 292,211
```

This is important evidence that descriptor relief can naturally move the limiting admission resource to the 128-entry Line MSHR. It is not yet proof that MSHR capacity is the ultimate performance cause, because performance is a slight slowdown and lower-path pressure remains substantial. But it materially strengthens the case for a controlled Line-MSHR sensitivity and for evaluating whether an RO path that genuinely avoids Line-MSHR allocation has opportunity.

The final research findings must correct this statement.

## 6. Other resource movement

The shift is heterogeneous rather than universal:

- vectorAdd raises Line-MSHR occupancy (max 92 -> 110) but has no Line-MSHR full block;
- spmv raises Line-MSHR max 99 -> 125 and per-address-cap blocks 8,598 -> about 21k, while descriptor block goes to zero;
- FWT_7_21 raises Line-MSHR max 102 -> 117 without full blocking;
- FWT_11_19 raises Line-MSHR max 96 -> 108 without full blocking;
- low-pressure controls such as sad, btree, sgemm, dwt2d and gemm are largely unchanged;
- cfd Banked is essentially unchanged because descriptor pressure was already absent; Legacy removes its tiny descriptor/lower block and changes cycles only slightly.

This supports a bottleneck-substitution / distributed-pressure interpretation rather than a universal single-resource story.

## 7. Lower path remains relevant

Descriptor relief does not remove lower-path pressure in the traffic-heavy workloads. For example, D512 still shows substantial L2->DRAM full and scheduler-full activity in vectorAdd and convolution. This is consistent with the observation that removing descriptor blocking does not yield a speedup.

### Bandwidth-semantics correction for final pack

The interim CSVs use a field named `dram_bandwidth_util`, while the approved Lane-D V3 semantics distinguish:

```text
lower_admission_byte_rate_norm
native_dram_data_bus_util_weighted_mean
```

The final Lane-B pack must use the Lane-D V3 terminology and, where raw logs are retained, recover the final-complete 32-channel native DRAM aggregate rather than leave an ambiguous `dram_bandwidth_util` label. No D512 simulator rerun is required if the raw logs are sufficient.

## 8. Temporal evidence — useful but not saturation proof

The D512 temporal stream shows higher descriptor and Line-MSHR window occupancy in descriptor-heavy workloads, with zero minima in many streams. This supports temporal/bursty pressure rather than a claim of whole-application saturation.

Do not use p95/max occupancy alone as causal proof. Exact blocker events and performance/lower-path movement remain required.

## 9. RO no-MSHR implication — revised interim interpretation

The previous interim conclusion `INSUFFICIENT_EVIDENCE` for an MSHR-centric decision remains appropriate at the whole-suite level, but it should no longer say that no completed row exhibits Line-MSHR full blocking.

A more accurate interim statement is:

```text
- D512 eliminates the dominant descriptor-pool blocking in several workloads.
- convolutionSeparable then develops 931,416 exact Line-MSHR-full blocks at the frozen 128-entry capacity.
- other descriptor-heavy workloads increase Line-MSHR occupancy but do not yet full-block.
- performance does not improve, indicating bottleneck substitution / downstream limitation rather than free speedup.
```

This is sufficient to justify a small controlled Line-MSHR-capacity sensitivity after/alongside current calibration, especially for convolution and any final scan result that exhibits Line-MSHR blocking. It is not sufficient to claim a functional RO no-MSHR benefit without that controlled sensitivity and the L1 factorial evidence.

## 10. Current decision

```text
D256_EQUIVALENCE:        PASS
D512_CARDINALITY/TELEM:  PASS on completed evidence
D512_SOURCE/CONFIG:      PASS for continued frozen campaign
D512_PREFLIGHT:          PENDING live Banked scan
D512_READY:              NOT YET
D512_MIRROR_COMPLETE:    NOT YET
INTERIM REVIEW:          CONDITIONAL PASS
```

Continue the four live runs and automatic promotion monitor. Do not restart or duplicate completed rows.

Before final Lane-B closeout:

1. correct the convolution Line-MSHR finding;
2. correct `D256_EQ_SCAN_GATE.json` maturity/dependency metadata;
3. use Lane-D V3 bandwidth terminology/native aggregation in the final analysis;
4. complete and promote the 26/26 mirror only after the frozen D512 Banked scan satisfies B6;
5. publish the machine-readable Lane-D V2 calibration contract for the promoted D512 cell, binding actual runtime config hash, source lineage/equivalence, and config-delta evidence.

STOP before `BASELINE_DECISION` or functional mechanism implementation.
