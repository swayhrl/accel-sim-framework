# AWMA Unified Analysis Architecture

## Decision

Use **one AWMA project**, **one shared identity/catalog plane**, and **one durable node164 root**, with two scientifically separate evidence backends and one explicit cross-view layer.

Do not create two disconnected projects such as “NVBit project” and “Accel-Sim project”.

Do not collapse real-GPU measurements and modeled simulator results into a single metric namespace.

## Architecture

```text
                         AWMA
                          |
                  Common Identity Plane
                          |
       +------------------+------------------+
       |                                     |
Native Evidence Plane                Simulation Evidence Plane
REAL_GPU                              SIMULATOR
       |                                     |
NSYS / NCU / NVBit                   Sim-compatible trace
C16WARP1 / object maps               + validated SIM_INPUT
       |                                     |
page/line/object/native metrics       Accel-Sim/GPGPU-Sim
       |                                     |
       |                              TLB/PTW/cache/IPC metrics
       |                                     |
       +------------------+------------------+
                          |
                    Cross-view Plane
                          |
              calibration / correlation /
             representative selection /
             mechanism applicability
```

## 1. Native Evidence Plane

### Inputs

Potential sources include:

- native timing/output receipts;
- NSYS launch census;
- NCU reports/counters;
- NVBit Route-B records;
- C16WARP1 MREF-sharded records;
- static MREF maps;
- same-process address context/object maps;
- capture manifests and Pipeline-V1 receipts.

### Allowed evidence examples

- observed kernel identity/duration;
- observed GPU VA values;
- static-MREF executed/zero classification;
- page/cache-line footprint within the accepted capture scope;
- hardware counter values when metric provenance is exact;
- object attribution when address-space identity is proven;
- context/batch/prefill/decode trends from matched workload identities.

### Forbidden automatic upgrades

Native capture alone does not establish:

- alternate-architecture speedup;
- modeled TLB/PTW latency;
- cache-policy counterfactual behavior;
- whole-kernel temporal order when source sharding does not preserve it.

## 2. Simulation Evidence Plane

### Inputs

A Simulation run may only consume a `SIM_INPUT_ID` that passed simulator-input validation. The input may be native traceg or another formally specified format only if a validated lossless converter produces the simulator grammar.

Current MREF-sharded C16WARP1 is **not** simulator-input eligible by default.

### Evidence examples

- TLB hit/miss;
- PTW requests/latency/walker occupancy;
- PWC behavior;
- modeled L1/L2/cache behavior;
- queue stalls;
- cycles/IPC;
- controlled mechanism deltas/speedups.

Every Simulation result must bind:

```text
SIM_INPUT_ID
SIM_BASELINE_ID
SIM_RUN_ID
config/arm identity
simulator source/binary identity
```

## 3. Cross-view Plane

Cross-view does not create new raw truth. It joins already qualified evidence.

### Valid uses

- compare native hardware counter vs simulator baseline metric;
- correlate native page/KV/Weight footprints with simulated TLB/PTW pressure;
- choose expensive simulator targets from the broader Native corpus;
- evaluate whether a mechanism helps the workload classes suggested by native characterization.

### Required relation labels

Every join must state a relation such as:

```text
EXACT_WORKLOAD_TARGET
SAME_WORKLOAD_DIFFERENT_CAPTURE
SAME_WORKLOAD_DIFFERENT_TARGET
HISTORICAL_REFERENCE
UNALIGNED
```

`UNALIGNED` rows must not produce quantitative cross-view conclusions.

## 4. One library, three logical datasets

Long-term logical outputs:

```text
AWMA Native Evidence Library
AWMA Simulation Evidence Library
AWMA Cross-view Dataset
```

These are logical domains inside one project/catalog/storage root.

## 5. Sampling relationship

Native coverage is expected to be broader than Simulation coverage.

Example:

```text
20 model/scenario workloads
        |
        +--> all or many get Native characterization
        |
        +--> representative subset gets simulator-compatible capture
                 |
                 +--> multiple simulator mechanism runs per SIM_INPUT
```

Therefore lack of Simulation evidence is not automatically a missing-data bug. `NOT_SELECTED` is a valid state.

## 6. Calibration rule

Simulator results never overwrite real-GPU results.

Store, for example:

```text
native.metric
simulation.baseline.metric
crossview.delta
```

If they disagree, preserve both and analyze the fidelity gap.

## 7. Implementation strategy

Do not rewrite the repository around this architecture in one step.

Preferred sequence:

1. add common AWMA identity/schema/catalog layer;
2. wrap/adapt existing `util/vm_tlb/c16/analysis` and historical simulator tools;
3. produce normalized Native and Simulation dataset schemas;
4. add Cross-view joins;
5. only later move stable code into cleaner subdirectories if beneficial.

Existing proven tools remain usable until replacements pass regression.