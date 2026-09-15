# AWMA Identity and Evidence Contract

## 1. Design goals

The identity system must let Native and Simulation evidence refer to the same scientific workload without pretending that they are the same capture or the same evidence source.

All IDs have two parts:

1. human-readable prefix/fields for debugging;
2. a canonical full SHA256 stored in metadata.

When a shortened ID is shown, use at least the first 20 hex characters of the canonical SHA256 and retain the full hash beside it.

Canonical hashing must use UTF-8 JSON with:

- sorted keys;
- compact separators;
- no timestamps in workload-semantic identities;
- explicit null/UNKNOWN rather than omitted guessed values;
- stable schema version.

## 2. `WORKLOAD_ID`

Identifies the scientific workload/configuration independent of profiling tool.

Minimum identity fields:

```text
schema_version
model_id
model_revision / model_binding_sha256
input_binding_sha256
scenario_id
batch
prefill/context token count
decode token count
input class
dtype
attention/backend identity
quantization/deployment identity
framework/model-runtime identity when it changes execution semantics
```

Do not include:

- capture timestamp;
- producer hostname;
- profiling tool version;
- simulator config.

If a framework/backend change can change kernels or memory semantics, it belongs in `WORKLOAD_ID`, not merely environment metadata.

## 3. `TARGET_ID`

Identifies a scoped execution target inside one workload.

Minimum fields as applicable:

```text
WORKLOAD_ID
phase
semantic stratum
operator/implementation identity
decode step/window
function/code object
launch selector
static-MREF-set identity
```

Not every Native capture must have a narrow target; whole-phase/whole-run targets are allowed if the source supports them.

## 4. `CAPTURE_ID`

Identifies one real-GPU evidence acquisition.

It must bind:

```text
WORKLOAD_ID
TARGET_ID or whole-run scope
capture method
producer host
GPU UUID/model
CUDA/driver
capture tool + build/source SHA
capture configuration
attempt identity/time
artifact manifest SHA
```

Examples of capture method:

```text
NATIVE_TIMING
NSYS
NCU
C16WARP1_MREF_SHARDED
ROUTE_B_LANE_EVENT
SIM_COMPAT_CAPTURE_V1
```

Two captures of the same workload are different `CAPTURE_ID`s.

## 5. `SIM_INPUT_ID`

Created only from an input set that passes simulator-input acceptance.

Required state machine:

```text
CAPTURED
  -> VALIDATED_SIM_INPUT
  -> SIM_INPUT_ID issued
```

or

```text
CAPTURED
  -> NOT_SIM_INPUT_ELIGIBLE
  -> no SIM_INPUT_ID
```

Current accepted C16WARP1/MREF-sharded captures default to:

```text
sim_input_status = NOT_PROVEN_LOSSLESS
SIM_INPUT_ID = NONE
```

unless a future formally validated lossless path is proven.

A `SIM_INPUT_ID` must bind:

- source `CAPTURE_ID`(s);
- exact trace/list payload hashes;
- schema/grammar version;
- converter binary/source/config SHA if conversion is involved;
- validation receipt;
- ordering/coalescing/control semantics statement;
- address-space/page-policy sidecars.

## 6. `SIM_BASELINE_ID`

Identifies a maintainable simulator runtime/platform baseline.

Bind at minimum:

```text
framework commit
core/simulator commit
binary SHA256
build/toolchain identity
base architecture config
trace-mode config
VM/TLB/cache baseline overlays
telemetry schema/version
```

A historical binary identity without an available executable may remain a historical baseline reference but cannot be a runnable current `SIM_BASELINE_ID`.

## 7. `SIM_RUN_ID`

Identifies one simulator execution:

```text
SIM_INPUT_ID
+ SIM_BASELINE_ID
+ mechanism/arm config identity
+ run-control identity
```

One `SIM_INPUT_ID` may feed many `SIM_RUN_ID`s.

## 8. `evidence_origin`

Every normalized metric/result row must carry exactly one primary origin:

```text
REAL_GPU
SIMULATOR
CROSSVIEW_DERIVED
HISTORICAL_RECORD
```

`HISTORICAL_RECORD` is for retained evidence whose exact modern execution path is not being re-run. It must additionally keep its historical scientific status.

## 9. Scientific status and execution status are separate

Recommended scientific status:

```text
FORMAL
DIAGNOSTIC
PRE_FIX
OBSOLETE
UNKNOWN
```

Recommended execution/availability status:

```text
PASS
CONDITIONAL_PASS
FAIL
BLOCKED_ENVIRONMENT
NOT_SELECTED
NOT_APPLICABLE
NOT_PROVEN_LOSSLESS
PENDING_INGEST
```

Do not encode both meanings in a single overloaded string.

## 10. Metric provenance

Every normalized metric should be traceable to:

```text
metric_name
metric_value/unit
origin
WORKLOAD_ID
TARGET_ID
CAPTURE_ID or SIM_RUN_ID
source artifact SHA
producer/parser/analyzer SHA
scope/claim boundary
```

## 11. Cross-view join contract

A cross-view row must bind the Native side and Simulation side independently and then state `join_relation`.

Required join labels:

```text
EXACT_WORKLOAD_TARGET
SAME_WORKLOAD_DIFFERENT_CAPTURE
SAME_WORKLOAD_DIFFERENT_TARGET
HISTORICAL_REFERENCE
UNALIGNED
```

Only `EXACT_WORKLOAD_TARGET` and explicitly justified `SAME_WORKLOAD_DIFFERENT_CAPTURE` may be used for direct quantitative native-vs-simulator calibration.

## 12. Unknown policy

Unknown information remains explicitly UNKNOWN/null.

Forbidden examples:

- infer WRITE because width/access-kind is absent;
- infer object class from a kernel name alone;
- infer temporal order across independent MREF replays;
- infer simulator input eligibility because addresses exist;
- infer exact target alignment because model/scenario names look similar.