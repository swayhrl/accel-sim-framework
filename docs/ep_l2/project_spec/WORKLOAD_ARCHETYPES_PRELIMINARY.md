# EP-L2 Preliminary Workload Archetypes

Status: **preliminary design-use map; Lane-D final convergence must validate/update it from the full promoted matrices.**

This file is intentionally conservative. It records only conclusions already supported by reviewed formal/calibration evidence and marks mechanism-specific gaps explicitly.

## Archetype A — sustained descriptor + lower-memory pressure

### `scan`

Measured characteristics:

- D256 descriptor-full pressure is extreme and sustained; D512 removes descriptor-full blocking but does not materially improve cycles.
- D512 reaches Line-MSHR max 128 but only a tiny exact Line-MSHR-full count compared with convolution.
- L2->DRAM / scheduler pressure is very high.
- Native DRAM physical utilization is high (~0.82 in the formal base).
- WAD and tag-way pressure are also measurable.
- Broad L1 META/BANK headroom has small performance sensitivity.

Working classification:

```text
SUSTAINED_DESCRIPTOR + LOWER/SCHEDULER + HIGH_BW
```

Best uses:

```text
baseline calibration
headroom experiments
structural-blocking / useful-throughput evaluation
```

Unified-payload temporal complementarity and RO eligibility: `UNKNOWN_NEEDS_TELEMETRY`.

### `vectorAdd_4M`

Measured characteristics:

- sustained descriptor pressure at D256; descriptor blocking disappears at D512 without speedup;
- persistent L2->DRAM/scheduler pressure;
- high native DRAM physical utilization (~0.80);
- Line-MSHR occupancy rises under D512 but does not exact-full block;
- weak L1 causal response.

Working classification:

```text
SUSTAINED_DESCRIPTOR + LOWER/SCHEDULER + HIGH_BW
```

Useful as a clean high-throughput headroom case.

## Archetype B — controlled bottleneck substitution

### `convolutionSeparable`

Measured controlled chain:

```text
D256 Descriptor-full
    -> D512 removes descriptor-full
    -> Line-MSHR128 exact-full = 931,416
    -> MSHR256 removes exact-full
    -> only ~0.38% cycle improvement
    -> pressure redistributes toward MissQ/WAD/lower path
```

Working classification:

```text
DESCRIPTOR -> LINE-MSHR -> DOWNSTREAM
```

This is currently the strongest workload for demonstrating that an L2 structural ceiling can be real without being the final end-to-end performance ceiling.

Best uses:

```text
resource-decoupling causal probes
admission-blocked-cycle metrics
lifetime/service-throughput analysis
headroom sensitivity
```

Do not use it to claim that MSHR capacity alone determines performance.

## Archetype C — descriptor relief exposes per-address / near-MSHR pressure

### `spmv`

Measured characteristics:

- D256 descriptor-full blocking is removed by D512;
- Line-MSHR max rises near capacity (125) without exact-full blocking;
- per-address-cap block rises under D512;
- MSHR128->256 negative control is cycle/counter identical because the exact MSHR-full condition is absent;
- lower path and DRAM are materially active;
- L1 headroom has small performance response.

Working classification:

```text
DESCRIPTOR -> PER-ADDRESS / NEAR-MSHR + LOWER PATH
```

Best uses:

```text
address-local pending-state policy
negative control for Line-MSHR mechanisms
```

## Archetype D — bursty descriptor / lower-path pressure

### `FWT_7_21`

Measured characteristics:

- large D256 descriptor-full event count;
- D512 removes descriptor-full but gives near-tie/slight slowdown;
- Line-MSHR rises but does not full-block;
- WAD hazard and lower/scheduler pressure are measurable;
- temporal averages indicate phase/burst behavior rather than whole-application saturation.

Working classification:

```text
BURSTY_DESCRIPTOR + WAD + LOWER PATH
```

Useful for testing whether elasticity tracks phase-local demand.

### `FWT_11_19`

Measured characteristics:

- descriptor-full events exist at D256 but temporal/application average occupancy is much lower than scan/vectorAdd;
- D512 removes the descriptor block with negligible performance response;
- DRAM utilization is low.

Working classification:

```text
BURSTY / SHORT-PHASE DESCRIPTOR PRESSURE, LOW GLOBAL BW
```

Useful to distinguish event count from sustained structural occupancy.

## Archetype E — payload-bank service contention

### `cfd_097k`

Measured characteristics:

- the only formal B0-Banked workload with material true payload-bank conflicts;
- Banked is ~2.37% slower than Legacy under measured true contention;
- descriptor pressure is not the dominant case;
- native DRAM utilization is relatively low;
- WAD hazard is present.

Working classification:

```text
BANK-SERVICE CONTENTION / LOW-MODERATE DOWNSTREAM BW
```

Best use:

```text
payload-bank arbitration/service control
```

Do not use cfd as evidence for payload-capacity borrowing unless new capacity/slack evidence supports it.

## Archetype F — WAD/victim pressure without descriptor dominance

### `dwt2d`

Measured characteristics:

- WAD full/hazard pressure is substantial;
- descriptor and Line-MSHR full blocking are not dominant;
- DRAM utilization is moderate;
- L1 MissQ/bank pressure exists but causal L1 screen is weak overall.

Working classification:

```text
WAD / VICTIM-LIFETIME CANDIDATE
```

Potentially useful for TVD investigation, but exact dirty-victim payload-lifetime opportunity remains `UNKNOWN_NEEDS_TELEMETRY`.

## Archetype G — local address/L1 pressure, weak broad L2 bottleneck

### `btree`

Measured characteristics:

- descriptor occupancy can approach the pool capacity but does not descriptor-full block;
- per-address cap blocking is nonzero;
- substantial native L1 merge-related pressure exists;
- L1 META/BANK headroom gives only a small ~2% class response, not a broad baseline-changing result;
- lower path is not dominant.

Working classification:

```text
ADDRESS-LOCAL / WEAK-L1-SENSITIVE CONTROL
```

### `sgemm`

Measured characteristics:

- little broad L2 structural blocking;
- small per-address-cap activity;
- low DRAM utilization;
- L1 pressure dominates the raw event picture without strong evidence for L2 structural opportunity.

Working classification:

```text
LOW-L2-PRESSURE / L1-HEAVY CONTROL
```

## Archetype H — low-L2-pressure controls

### `sad`

Very low downstream/DRAM pressure and little descriptor/MSHR structural pressure. Useful as a low-pressure negative control.

### `gemm`

No meaningful descriptor/MSHR/lower blocking in the final baseline, very low native DRAM utilization, substantial L1 event activity. Useful as a low-L2-pressure control.

### `3mm`

Similar to gemm: low L2/lower pressure, very low native DRAM utilization, high L1 event activity, and no residual B0-Banked conflict penalty. Useful as a low-L2-pressure/control workload.

## Preliminary fast-development set

Before Lane-D final convergence revises this map, a practical minimal development set is:

```text
convolutionSeparable  controlled bottleneck substitution
scan                  sustained descriptor/lower/high-BW
vectorAdd_4M          clean sustained throughput/high-BW
spmv                  per-address/near-MSHR case
FWT_7_21              bursty phase-local case
cfd_097k              true payload-bank contention
sad                    low-pressure control
```

Mechanism-specific subsets should be narrower when evidence permits.

## Current unknowns that matter for architecture implementation

Existing data do **not** yet establish:

```text
per-line/read-only eligibility for the proposed RO pending-tag path
time-aligned resident-vs-bypass payload slack/complementarity
counterfactual cache-miss reduction from unified payload borrowing
dirty-victim payload lifetime that TVD would shorten
useful L2 throughput gained when blockers disappear
cycle-based non-retry L2 admission-blocked time by reason
```

These gaps should drive the first mechanism-readiness instrumentation rather than be filled by assumption.
