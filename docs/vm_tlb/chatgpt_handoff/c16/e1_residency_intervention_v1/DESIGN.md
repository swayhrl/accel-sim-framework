# C16 E1 Residency Intervention Diagnostic V1

## 1. Scientific objective

Test the warm-cache capacity/residency hypothesis by perturbing pre-target memory/cache state while keeping the target semantic operator, input bytes, weight representation, and backend unchanged.

Primary hypothesis:

> The strong M1 RAW/AWQ timing/traffic difference is partly explained by the fact that the packed AWQ state can remain resident after warmup while the much larger RAW FP16 state cannot.

This is a controlled intervention stage, not a mechanism stage.

---

## 2. Frozen target authorities

Reuse exact accepted E1 canonical inputs/backends.

TEXT targets:

### M1 operator controls
- q_proj M1 RAW_FP16 / AWQ_FP16_INPUT
- down_proj M1 RAW_FP16 / AWQ_FP16_INPUT
- up_proj M1 RAW_FP16 / AWQ_FP16_INPUT

### Shape control
- up_proj M256 RAW_FP16 / AWQ_FP16_INPUT

### Optional input-content holdout
If the already accepted common CODE down_proj M1 authority can be reused directly:
- CODE down_proj M1 RAW_FP16 / AWQ_FP16_INPUT

No new model, token generation, operator, or shape sweep.

---

## 3. Stage A — capacity census

Before intervention, freeze exact storage sizes for all three Layer0 roles:

For RAW_FP16:
- weight bytes
- bias bytes if any
- total dense parameter bytes

For AWQ:
- qweight
- qzeros
- scales
- any other state_dict tensor used by the exact accepted module
- total packed module-state bytes

Record device L2 capacity from accepted NCU device attributes.

Do not assume q_proj/down_proj sizes from geometry; compute them from actual frozen module state.

Create a table:

`role × {RAW_FP16 bytes, AWQ packed bytes, relation to L2}`

This is descriptive authority only.

---

## 4. Stage B — perturbation harness

Use one preallocated FP32 CUDA buffer of exactly 256 MiB.

Initialize it once before the target-state preparation.

Define three target-state conditions.

### WARM

- execute exact target module twice;
- synchronize;
- measure/profile one target call.

### SPARSE_PAGE_PRESSURE

- execute exact target module twice;
- synchronize;
- read from the same 256 MiB pressure buffer with one FP32 element every 4096 bytes:
  `buffer[::1024].sum()`
- synchronize;
- measure/profile one target call.

This touches the full pressure-buffer address range with a much smaller cache-line footprint than DENSE.

It is a page-footprint control, not a proven TLB-only control.

### DENSE_CACHE_PRESSURE

- execute exact target module twice;
- synchronize;
- read the entire same 256 MiB buffer:
  `buffer.sum()`
- synchronize;
- measure/profile one target call.

The pressure operation is outside target timing and outside target semantic NVTX range.

### WARM_RECOVERY

After DENSE:
- execute target twice again;
- synchronize;
- measure one target call.

This provides a reversibility check.

Do not describe DENSE as a guaranteed hardware cache flush.

Correct label:

`DENSE_MEMORY_PRESSURE`

---

## 5. Stage C — native intervention timing

Run all TEXT target pairs:

- q_proj M1 RAW/AWQ
- down_proj M1 RAW/AWQ
- up_proj M1 RAW/AWQ
- up_proj M256 RAW/AWQ

For every point, run:

- WARM_A
- SPARSE_PAGE_PRESSURE
- DENSE_MEMORY_PRESSURE
- WARM_B

Protocol:
- 7 measured repetitions per state;
- target timing only;
- CUDA events;
- pressure operation excluded;
- retain raw samples;
- rotate target-point execution order across repetitions;
- record pressure-operation duration separately;
- preserve target input/output SHA for every state.

Required summaries:
- median/min/max/CV
- PRESSURE/WARM timing ratio
- SPARSE/WARM timing ratio
- WARM_B/WARM_A recovery ratio

Material target timing effect:
- absolute median change >= 5%;
- and greater than combined ordinary timing dispersion.

---

## 6. Stage D — semantic NCU intervention profiling

Use the already qualified application-replay semantic selector contract:

- `--replay-mode application`
- `--cache-control none`
- exact target NVTX range
- target semantic call only
- pressure outside target range

Collect only:

- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`

with exact installed-NCU names/units.

### Required NCU points

For all three M1 roles and both implementations:

- WARM
- SPARSE_PAGE_PRESSURE
- DENSE_MEMORY_PRESSURE

That is:
`3 roles × 2 implementations × 3 states = 18 semantic profiles`

For up_proj M256:

- WARM
- DENSE_MEMORY_PRESSURE

That is 4 additional profiles.

Total primary maximum:
`22 profiles`

Do not profile WARM_B with NCU.

Every profile must revalidate:
- target input/output SHA;
- semantic range identity;
- kernel inventory;
- application replay;
- cache-control none;
- replay pass count;
- metric unit.

---

## 7. Stage E — bounded pressure-dose timing sweep

Only for TEXT up_proj M1 RAW_FP16 and AWQ_FP16_INPUT.

Reuse one 256 MiB preallocated buffer.

Dense-touch prefixes:

- 0 MiB
- 16 MiB
- 32 MiB
- 64 MiB
- 128 MiB
- 256 MiB

For each dose:
- two exact target warmups;
- dense-read the selected prefix;
- synchronize;
- measure target;
- 7 repetitions.

Purpose:

> measure a pressure-dose response without claiming that pressure size equals effective L2 eviction capacity.

If native timing shows a material dose response, NCU is pre-authorized for only the 64 MiB dose, because 0 and 256 MiB are already covered.

Thus at most:
- up_proj M1 RAW 64MiB
- up_proj M1 AWQ 64MiB

two extra NCU profiles.

---

## 8. Stage F — CODE input holdout

If the accepted common CODE down_proj M1 authority is directly reusable without new scientific input construction:

Run RAW/AWQ for:

- WARM
- DENSE_MEMORY_PRESSURE
- WARM_RECOVERY

Native timing: 7 repetitions.

If TEXT down_proj M1 shows a material dense-pressure intervention effect, profile CODE down_proj M1 with NCU for:
- WARM
- DENSE_MEMORY_PRESSURE
for both implementations.

At most 4 extra NCU profiles.

If the existing CODE authority cannot be reused directly:
`CODE_INTERVENTION_NOT_RUN_AUTHORITY_NOT_DIRECTLY_REUSABLE`

Do not open a new capture campaign.

---

## 9. Pressure-kernel qualification

The pressure operation itself must be qualified once outside the target scientific range.

Record:

- pressure buffer pointer/address if accessible;
- allocation bytes = 256 MiB;
- dtype;
- sparse stride = 4096 bytes;
- sparse selected element count;
- dense selected element count;
- pressure kernel names;
- pressure durations.

Use lightweight NCU or profiler evidence once to verify:

- DENSE generates materially larger L1/L2/DRAM traffic than SPARSE;
- both traverse the same allocated buffer range by construction.

This qualification is about the intervention, not target scientific traffic.

Do not claim SPARSE and DENSE have identical TLB behavior; label SPARSE only as a page-footprint-oriented control.

---

## 10. Pre-registered predictions

These are predictions, not accepted conclusions.

### P1 — M1 up/down asymmetric residency

If:
- AWQ packed state < L2
- RAW dense state > L2

then after target warmup:

Expected:
- AWQ WARM DRAM much lower than RAW;
- DENSE pressure increases AWQ DRAM materially;
- DENSE pressure increases AWQ target time materially or reduces its timing advantage;
- RAW changes less because its dense state already exceeds L2;
- WARM_B recovers toward WARM_A.

### P2 — q_proj control

Interpret only after Stage A exact size census.

If both q_proj RAW and AWQ state fit within L2:
- both may show warm-state sensitivity;
- differential AWQ/RAW intervention effect should be smaller than up/down.

If the census does not satisfy that premise, do not force this prediction.

### P3 — SPARSE versus DENSE

If cache-line residency is a major contributor:
- DENSE should perturb target traffic/timing more than SPARSE.

If SPARSE is equally strong:
- page/translation or other memory-state effects remain plausible;
- do not claim L2-specific causality.

### P4 — M256 shape control

If within-call traffic dominates at M256:
- pre-target DENSE pressure should have a smaller relative impact than at M1.

---

## 11. Intervention evidence classification

No single threshold upgrades the result to universal cache causality.

For each point record continuous effects.

For the primary up_proj M1 AWQ test, define:

### MATERIAL_TIMING_PERTURBATION
- abs(DENSE/WARM - 1) >= 0.05
- and effect exceeds combined timing dispersion.

### MATERIAL_DRAM_PERTURBATION
- DENSE DRAM >= 2 × WARM DRAM
- and absolute increase >= 1 MiB.

### REVERSIBLE
- WARM_B returns within max(5%, combined WARM_A/WARM_B dispersion) of WARM_A.

### DENSE_SPECIFIC
- DENSE effect exceeds SPARSE effect materially in both DRAM and timing.

Final scientific label may be:

- `RESIDENCY_INTERVENTION_STRONGLY_SUPPORTED`
- `RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED`
- `RESIDENCY_INTERVENTION_NOT_SUPPORTED`

The label refers only to the tested cache/memory-state intervention, not universal cache causality.

---

## 12. Interpretation boundary

Allowed if supported:

> Controlled pre-target memory-state perturbation reversibly changes the same semantic module's timing and traffic in a manner consistent with cache-line residency contributing to the M1 AWQ advantage.

Stronger L2-specific wording requires:
- DENSE > SPARSE intervention evidence;
- capacity census consistency;
- recovery;
- operator/shape controls.

Even then, do not claim:
- TLB excluded completely;
- one specific cache mechanism will help;
- end-to-end model speedup.

---

## 13. 109 deliverables

Review pack:

`docs/vm_tlb/review_packs/C16_E1_RESIDENCY_INTERVENTION_109_V1/`

At minimum:

- `UPSTREAM_AUTHORITY.json`
- `CAPACITY_CENSUS.tsv`
- `PRESSURE_HARNESS_CONTRACT.json`
- `PRESSURE_QUALIFICATION.json`
- `TARGET_POINT_BINDINGS.tsv`
- `NATIVE_INTERVENTION_TIMING.tsv`
- `NATIVE_INTERVENTION_ANALYSIS.json`
- `NCU_PROFILE_INDEX.tsv`
- `NCU_RAW_PROVENANCE.json`
- `NCU_KERNEL_METRICS.tsv`
- `NCU_SEMANTIC_SUMS.tsv`
- `INTERVENTION_TRAFFIC_ANALYSIS.json`
- `PRESSURE_DOSE_TIMING.tsv`
- `PRESSURE_DOSE_ANALYSIS.json`
- `CODE_INTERVENTION.json`
- `HYPOTHESIS_EVALUATION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Update:
`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

---

## 14. 174-new parallel role

In parallel, 174-new should:

- audit the intervention contract;
- independently freeze prediction logic;
- extend hardened raw-NCU normalization for state labels;
- build timing/intervention comparator;
- independently compute capacity census from accepted module receipts where possible;
- synthetic-test WARM/SPARSE/DENSE/WARM_B and raw-NCU cases;
- fetch producer once after prep;
- if producer exists, consume raw evidence directly;
- otherwise stop at `READY_FOR_E1_RESIDENCY_INTERVENTION_109`.

No GPU work.

---

## 15. Final STOP

This entire package is one node109 Goal.

Do not stop after native timing or after the first operator if normal gates permit continuation.

Do not start:
- NVBit;
- full address trace;
- cache/TLB mechanism design/experiment.

Those decisions happen only after producer + independent consumer closure.
