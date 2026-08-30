# EP-L2 Final Calibration Convergence — Lane D Handoff

Ownership: ChatGPT research specification.

Status: **AUTHORIZED TO START**.

## 1. Objective

Converge the reviewed/promoted calibration evidence into one causal resource picture without changing simulator behavior or launching new simulator runs.

The final convergence must answer two different questions separately:

1. **What is the calibrated primary research baseline?**
2. **Which L2 structural limitations and workload classes should the first EP-L2 mechanisms target?**

Do not collapse these into a single "which configuration is fastest" question.

The long-lived project objective is:

> Under comparable L2 storage budget and basic L2 timing, improve the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling. End-to-end speedup is stronger evidence, but is not the only valid evidence of a better L2 when an L2-local ceiling is replaced by a downstream bottleneck.

Read `docs/ep_l2/project_spec/` as the architectural authority.

## 2. Reviewed/promoted inputs

### Formal D256 base

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
config    85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
26/26 formal COMPLETE_VALID
```

Review pack:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1/
```

### Promoted D512 base

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
config    a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
26/26 PROMOTED_VALID_CALIBRATION
```

Review pack:

```text
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
```

Contract:

```text
docs/ep_l2/calibration/contracts/D512_BASE.json
```

### Promoted L1 causality cells

```text
D256_META_HR
D256_BANK_HR
D512_META_HR
D512_BANK_HR
```

Review pack:

```text
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
```

Contracts:

```text
docs/ep_l2/calibration/contracts/D256_META_HR.json
docs/ep_l2/calibration/contracts/D256_BANK_HR.json
docs/ep_l2/calibration/contracts/D512_META_HR.json
docs/ep_l2/calibration/contracts/D512_BANK_HR.json
```

### Supplemental Line-MSHR causal probe

Review pack:

```text
docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/
```

Key result already locally reviewed:

```text
convolution / D512:
MSHR128 -> MSHR256
Line-MSHR-full 931,416 -> 0
cycles 292,211 -> 291,108 (~0.38% improvement)
classification: MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED
```

Treat this as a **supplemental causal sensitivity**, not another primary matrix dimension.

## 3. Mandatory execution phases

### D-F1 — immediate workload-characterization checkpoint

Do this first, before the full convergence narrative.

Using the accepted D256/D512/L1/Line-MSHR evidence, classify all 13 workloads into resource/temporal archetypes. Produce:

```text
WORKLOAD_ARCHETYPES.csv
WORKLOAD_ARCHETYPES.md
MECHANISM_TARGET_MAP.md
```

At minimum classify:

```text
descriptor pressure: none / bursty / sustained
Line-MSHR pressure: none / near-capacity / exact-full
per-address pressure
Tag/set pressure
WAD pressure
payload-role/capacity observations
bank conflict pressure
L1 sensitivity from causal headroom
L2->DRAM/scheduler pressure
native physical DRAM bus regime
temporal regime
observed bottleneck-substitution chain
```

For every classification, distinguish:

```text
MEASURED
INFERRED_FROM_CONTROLLED_SENSITIVITY
UNKNOWN_NEEDS_TELEMETRY
```

Do not invent read-only eligibility, TVD opportunity, or unified-payload benefit when current telemetry does not measure them.

Publish this checkpoint into the final convergence review pack as soon as it is ready, then continue autonomously.

### D-F2 — final six-cell calibration matrix

Use Lane-D V3 unchanged except bug fixes and consume the V2 contracts:

```text
D256_BASE
D512_BASE
D256_META_HR
D256_BANK_HR
D512_META_HR
D512_BANK_HR
```

Produce provenance-safe final matrix/deltas and corrected temporal/native-DRAM outputs.

### D-F3 — supplemental causal evidence

Integrate Lane-E as a separate section:

```text
Descriptor x Line-MSHR convolution 2x2
spmv MSHR negative control
```

Do not force MSHR256 into the six-cell L1 matrix.

### D-F4 — baseline-decision evidence

Produce a recommendation, not an autonomous architecture change.

Evaluate D256 vs D512 using:

```text
hardware metadata plausibility
structural pressure removal
performance sensitivity
bottleneck substitution
L1 interaction
Line-MSHR sensitivity
lower-path exposure
workload coverage
```

The recommendation must explicitly allow a result such as:

```text
D512 is a better research baseline because it removes a cheap/artificial metadata ceiling,
even if it does not improve application cycles by itself.
```

But it must not prefer D512 merely because it produces a more convenient MSHR story.

### D-F5 — mechanism-priority recommendation

Map the workload archetypes to the future mechanism families in `project_spec/ARCHITECTURE_BLUEPRINT.md`:

```text
Unified payload borrowing
read-only pending-tag / no-traditional-MSHR path
WAD-backed TVD / payload-lifetime decoupling
cross-mechanism resource elasticity
```

For each family state:

```text
current supporting evidence
missing evidence
best target workloads
expected L2-local metric
expected service-effectiveness metric
performance-headroom axis if needed
implementation priority
```

Do not make a functional mechanism claim.

## 4. Required final outputs

Create/update:

```text
docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1/
  README.md
  INPUT_CONTRACTS.md
  WORKLOAD_ARCHETYPES.csv
  WORKLOAD_ARCHETYPES.md
  MECHANISM_TARGET_MAP.md
  CALIBRATION_MATRIX_FINAL.csv
  CALIBRATION_DELTAS_FINAL.csv
  TEMPORAL_SUMMARY_FINAL.csv
  NATIVE_DRAM_SUMMARY_FINAL.csv
  LINE_MSHR_CAUSAL_SUPPLEMENT.md
  BASELINE_DECISION_EVIDENCE.md
  MECHANISM_PRIORITY_RECOMMENDATION.md
  PERFORMANCE_HEADROOM_CANDIDATES.md
  VALIDATION_SUMMARY.md
  ANALYSIS_MANIFEST.json
  SHA256SUMS
```

Update:

```text
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

Status on successful completion:

```text
FINAL_CALIBRATION_CONVERGENCE_REVIEW_READY
```

## 5. Hard boundaries

This Lane-D stage is analysis/decision-evidence only.

Do NOT:

```text
launch new simulator runs
modify B/C/E result roots
change Lane-D V3 semantics except a demonstrated bug fix
choose a primary baseline as a code/config default
implement Unified borrowing
implement RO no-MSHR
implement TVD
run 1GHz headroom experiments
```

STOP after publishing the final convergence pack and request ChatGPT review.
