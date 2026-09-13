# Reusable model capture S0-S6 template

Use this after Phase A has frozen an exact model identity and local asset.

## S0 — freeze

Create a model-specific campaign contract containing:

- exact identity/revision/content manifest;
- quantization/dtype;
- deterministic input;
- batch/input/decode shape;
- backend/device-map/offload;
- runtime lock hashes;
- dedicated deployment/budget namespace.

Do not share a model deployment ID with historical diagnostics.

## S1 — no-trace runtime

Run the full frozen workload with Lane G present but capture disabled/no-match.

PASS requires:

```text
model load complete
workload terminal evidence/checksum
all required phases executed
prewarm trace count = 0
normal exit
no residual GPU/diagnostic process
MEASUREMENT_ACTIVE absent
```

If the model does not fit under the frozen runtime, diagnose memory allocation/offload/backend facts without silently changing the scientific contract.

## S2 — phase-aware census and target manifest

Perform low-overhead census separately for prefill and decode.

Build:

```text
<MODEL>_PHASE_TARGET_MANIFEST.json
```

with arrays:

```text
prefill_targets[]
decode_targets[]
```

Each selected target must include:

```text
full_mangled_identity
kernel/function label
phase
launch_count
static_range
opcode
memory_space
address_bearing=true
selection_reason
```

### Target-selection policy

The scientific goal is representative/required memory traffic for TLB/cache study, not forcing a common operator across models.

Prefer targets that are:

- address-bearing global-memory operations;
- repeatedly exercised in the phase;
- semantically relevant to model state/weights/KV/indexing;
- stable across independent runs;
- tractable under storage/runtime limits.

If prefill and decode dispatch to different kernels, select separate phase targets.

If a prefill target is not launched during decode, report `STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED`; do not force it to generate records.

Before finalizing targets, inspect the downstream consumer contract. If the consumer requires ROI-wide memory streams, record `FINAL_CAPTURE_SCOPE=ROI_WIDE_GLOBAL_MEMORY`; otherwise record `FINAL_CAPTURE_SCOPE=PHASE_TARGETED_MEMORY`.

## S3 — narrow canary

For every target class that will enter S5:

```text
prewarm outside measurement
READY
assert trace=0
acquire new campaign lease
MEASUREMENT_ACTIVE
CAPTURE_BEGIN
one bounded occurrence/window
CAPTURE_END
measurement off
parse/validate
cleanup
```

Require nonzero records only when the target was proven launched in that phase.

## S4 — reproducibility

Repeat canary in an independent process. Validate:

- model identity;
- phase target identity;
- static range/opcode;
- schema;
- structural record-count relationship;
- checksum/terminal behavior.

Do not require raw address equality across processes.

## S5 — complete frozen workload capture

Use the scope chosen in S2.

For `PHASE_TARGETED_MEMORY`, capture every required occurrence of every selected phase target across the complete workload.

For `ROI_WIDE_GLOBAL_MEMORY`, capture all address-bearing global-memory records in the frozen ROI, only after canary-based storage sizing shows it is safe.

Always retain phase attribution:

```text
prefill
decode1
decode2
...
```

when the workload exposes discrete decode steps.

Before S5:

- estimate bytes from S3/S4;
- verify free space;
- require projected output plus margin to fit;
- plan staged copyback if large.

## S6 — closeout

Create a compact model pack containing:

```text
identity receipt
runtime/no-trace receipt
phase target manifest
S3 canary receipt
S4 reproducibility receipt
S5 phase summary
schema/address validation
raw artifact index
remote/local SHA closure
storage accounting
cleanup receipt
PUBLISH_MANIFEST.json
```

Raw traces remain outside Git.

Model terminal status:

```text
COMPLETE
```

only if the complete required capture scope is satisfied.
