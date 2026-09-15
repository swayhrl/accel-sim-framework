# Simulation Analysis Architecture

## Goal

Build one maintainable simulator research path that can consume formally admitted simulator inputs, produce reproducible TLB/PTW/Cache evidence, and join with Native Evidence only through explicit AWMA identity.

## Logical architecture

```text
Producer side (later, 109 / RTX4080)

exact workload/scenario/target
        ↓
SIM_COMPAT_CAPTURE_V1
        ↓
SIM_INPUT bundle
        ↓ transfer / hash closure

Consumer side (174-new)

SIM_INPUT admission
        ↓
NEW_SIM_BASELINE_V1 runtime
        ↓
Baseline characterization
        ↓
Mechanism variants
        ↓
Simulation telemetry normalization
        ↓
Simulation Evidence Library
        ↓
AWMA Cross-view joins
```

## Four independently versioned contracts

### 1. Simulation input contract

Defines what one replayable input bundle means.

Required authority must include at least:

```text
WORKLOAD_ID
TARGET_ID
capture/producer identity
kernel/launch ordering
trace payload/list hashes
trace schema
object/address-context sidecars
terminal completeness/drop/overflow state
```

A bundle that does not satisfy the simulation-input contract gets no `SIM_INPUT_ID`.

### 2. Simulator baseline contract

Defines one qualified runtime:

```text
SIM_BASELINE_ID
framework commit
core commit
build/toolchain identity
binary SHA256
base config identity
trace config identity
VM/TLB/cache policy identity
telemetry schema
```

Never describe a baseline only as “current accel-sim”.

### 3. Simulation run contract

One run is immutable by:

```text
SIM_INPUT_ID
+
SIM_BASELINE_ID
+
mechanism/config overlay
+
execution controls
=
SIM_RUN_ID
```

The same input may legitimately have many simulation runs.

### 4. Evidence contract

Every normalized metric records:

```text
SIM_RUN_ID or historical lineage
metric name/value/unit
raw log SHA256
analyzer identity
scientific status
claim scope
```

## Separation of baseline and mechanism evaluation

The simulation project must proceed in this order:

```text
input fidelity
    ↓
runtime qualification
    ↓
baseline calibration
    ↓
baseline workload characterization
    ↓
mechanism experiments
```

Do not start a broad Segment/Selective/Cache mechanism sweep while baseline fidelity is unresolved.

## Historical data role

Historical C12–C15 assets serve three purposes:

1. parser and telemetry regression;
2. known input/config/provenance anchors;
3. expected qualitative/numerical reference ranges.

They are not automatically reclassified as results of the new baseline.

Use explicit labels:

```text
HISTORICAL_EXACT_RECORD
NEW_BASELINE_REPLAY
CALIBRATION_COMPARISON
CURRENT_MODEL_SIMULATION
```

## Current-model simulation role

Once true simulator-compatible traces exist, initial current-model targets should mirror Native Characterization semantic strata rather than trying to simulate the whole model indiscriminately.

Initial priority:

```text
Qwen2.5-0.5B S2_TEXT
  Prefill Attention
  Prefill heavy GEMM
  Decode early attention/KV-memory
  Decode late attention/KV-memory
```

Additional targets are admitted only when Native Characterization shows a materially distinct behavior or implementation.

## Storage architecture

Keep one physical project root:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

`c16_ai_workload` remains a legacy storage name; do not rename it for cosmetics.

Simulation-oriented additions should be logically isolated, for example:

```text
derived/awma/simulation/
├── inputs/
├── runs/
├── telemetry/
└── datasets/

catalog/awma/
├── entries/
└── snapshots/
```

Large raw traces/runs stay out of Git. Git stores source, config, manifests, receipts, normalized summaries and review packs.

## Code architecture

Prefer thin new AWMA wrappers around already validated historical tools rather than rewriting everything:

```text
util/vm_tlb/awma/simulation/
├── sim_input.py
├── admit.py
├── baseline.py
├── run.py
├── telemetry.py
├── catalog.py
└── calibration.py
```

Existing tools may remain where they are and be called through explicit adapters.

## Failure policy

Unknown must remain unknown.

Examples that must fail closed:

- incomplete trace ordering;
- absent access width/type required for replay;
- config hash mismatch;
- binary hash mismatch;
- unclosed run log;
- simulator output from a different baseline;
- filename-only mapping between Native and Simulation targets.
