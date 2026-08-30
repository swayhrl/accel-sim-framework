# EP-L2 Lane C L1 Causality — ChatGPT Interim Review

Date: 2026-08-30

Review status: **CONDITIONAL PASS — LOCAL EXECUTION ACCEPTED; D512 PROMOTION AND FINAL PACKAGING PENDING**

Reviewed pack:

```text
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
```

## 1. D256 source/config/provenance — PASS

Lane C uses the exact C7e Core and an isolated Framework descendant. The pack records exact D256 base reproduction on vectorAdd_4M, spmv and FWT_7_21, plus release/regression/config/parser/invariant checks.

The intended first-stage L1 geometry remains frozen at 64 KiB, 4 sets x 128 ways x 128 B, 20 cycles. The authorized deltas are:

```text
META-HR: MSHR 512->1024, merge 8->32, MissQ 16->64
BANK-HR: banks 4->8 only
```

No L2/DRAM baseline variable is intentionally changed in these D256 cells.

## 2. D256 14/14 local results — PASS

All seven META-HR and seven BANK-HR B0-Banked runs are `COMPLETE_VALID`.

META-HR speedups are reported as:

```text
vectorAdd   +0.36%
scan        +0.32%
spmv        -1.21%
convolution +0.07%
btree       +2.17%
sad         +0.79%
FWT_7_21    -1.09%
```

BANK-HR responses are similarly small, with the largest positive response about +1.91% on btree.

No workload reaches the acceptance-defined ~5% decomposition trigger or the documented strong downstream-movement trigger. Therefore no mandatory MSHR-only / merge-only / MissQ-only decomposition is required from the current screen.

Scientific interpretation: the very large native L1 retry/block counters seen in C7e are mostly not evidence of a dominant performance-causal L1 resource limit under this baseline. btree retains modest (~2%) L1 sensitivity but not enough to justify changing the primary L1 configuration.

## 3. D512 14/14 local results — PASS locally, promotion pending

All D512 META-HR/BANK-HR descendants are locally `COMPLETE_VALID` and derive from the exact frozen Lane-B candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Reported provisional speedups remain small:

```text
META-HR / BANK-HR
vectorAdd   +0.60% / +0.46%
scan        +0.64% / -0.10%
spmv        +0.22% / +0.49%
convolution +0.67% / -0.53%
btree       +2.17% / +1.91%
sad         +0.79% / +0.90%
FWT_7_21    -0.15% / +0.36%
```

Thus Descriptor relief does not reveal a strong hidden L1 metadata/bank bottleneck in this selected set.

These rows remain `SPECULATIVE_PENDING_GATE` until Lane B publishes `D512_PREFLIGHT_PASS` for this exact parent candidate.

## 4. Current causal conclusion — accepted provisionally

Across both descriptor capacities, increasing the selected L1 flow-control resources or bank count produces only weak cycle sensitivity. This supports:

```text
L1 pressure is mostly non-dominant / symptomatic at the current baseline,
with small workload-specific sensitivity (especially btree),
not a broad primary performance ceiling.
```

Do not enlarge the primary L1 baseline solely because C7e retry counters are numerically large.

## 5. Packaging gap before final Lane-C PASS

The current Git review pack contains the provenance and narrative summary, but the full machine-readable comparison and temporal tables are referenced only by server-local paths under `/workspace/results/...`.

Before final `L1_CAUSALITY_SCREEN_COMPLETE`, after D512 promotion, mirror compact reviewable copies into the Git review pack, including at least:

```text
D256_L1_CAUSALITY_COMPARISON.csv
D512_L1_CAUSALITY_COMPARISON.csv
L1_TEMPORAL_SUMMARY.csv
CONFIG_DIFF / contract evidence
final run/promotion status table
```

Do not copy large raw logs; keep them indexed.

This is a review-pack completeness requirement, not a simulator rerun requirement.

## 6. Promotion / completion rule

If Lane B publishes `D512_PREFLIGHT_PASS` for the exact frozen candidate, Lane C may promote all matching completed D512 META/BANK rows without rerun, refresh the compact evidence tables, set the final status `L1_CAUSALITY_SCREEN_COMPLETE`, and request final ChatGPT review.

If Lane B supersedes the D512 candidate because of a real source/config/producer/timing defect, only the D512 descendants require invalidation/rerun; the D256 14/14 result remains accepted.
