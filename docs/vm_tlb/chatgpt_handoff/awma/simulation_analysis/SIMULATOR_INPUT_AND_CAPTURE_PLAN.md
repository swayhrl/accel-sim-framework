# Simulator Input and Capture Plan

## Core decision

Do **not** convert current C16WARP1/MREF-sharded data into simulator trace by guessing missing semantics.

Future simulator work gets a separate capture path:

```text
SIM_COMPAT_CAPTURE_V1
```

The preferred technical direction is to requalify the existing Accel-Sim/NVBit trace producer on RTX4080/SM89 if it can emit the native simulator grammar correctly. This avoids inventing an unnecessary second intermediate format. If the existing producer is incompatible, modify it minimally and validate the output contract; do not derive the missing information from C16WARP1.

## Producer-side scientific identity

A simulator capture must bind to the same AWMA workload/target semantics as Native Characterization:

```text
WORKLOAD_ID
TARGET_ID
model revision
input binding
scenario
phase
optional decode step
backend/dtype/quantization
launch selector
kernel/code-object identity
```

Native and simulation captures may use different `CAPTURE_ID`s while sharing a `WORKLOAD_ID`/`TARGET_ID`.

## Required trace semantics

For simulation eligibility, capture or formally derive without ambiguity:

```text
kernel launch sequence
grid/block
stream/context identity
static instruction identity / PC
opcode
memory space
read/write/atomic semantics
byte width
warp ID
CTA ID
active mask
per-lane addresses
instruction/event order
synchronization/control events required by trace grammar
trace schema/version
producer source/binary SHA
```

Additional sidecars:

```text
object/address-context map
ASID/epoch where modeled
VA width
page policy
semantic phase/operator binding
```

## Completeness

Every bundle must explicitly close:

```text
terminal status
expected/written records
drop count
overflow count
payload SHA256
list SHA256
sidecar SHA256
producer/config SHA256
```

No terminal closure → no `SIM_INPUT_ID`.

## Preferred output

Preferred if the existing Accel-Sim tracer is qualified:

```text
kernelslist.g
*.traceg.xz
SIM_INPUT_MANIFEST.json
OBJECT_ADDRESS_CONTEXT.*
SHA256SUMS
```

If a new intermediate format is unavoidable, it must have a formally proven lossless converter to traceg. The converter source/binary/config becomes part of the input identity.

## Target scope

Do not initially capture whole-model unbounded traces.

The first current-model simulation input campaign should mirror representative Native targets:

```text
Qwen2.5-0.5B S2_TEXT
  Prefill Attention
  Prefill heavy GEMM
  Decode early Attention/KV-memory
  Decode late Attention/KV-memory
```

Use exact launch/window selection and size/time guards. Add targets only when Native results demonstrate materially different memory behavior.

## Capture qualification sequence

### C0 — vector/synthetic tracer canary

Verify tracer loading, trace syntax and terminal closure.

### C1 — small model kernel canary

Use a deterministic small Qwen target and validate:

```text
kernel identity
instruction count
memory record count
opcode/width/access semantics
warp/CTA/mask
address stability within the run
```

### C2 — parser round trip

109 output → 174-new parser/admission → stable hashes and counts.

### C3 — simulator smoke

Admitted trace → `NEW_SIM_BASELINE_V1` → bounded completion/telemetry.

Only after C0–C3 may capture be used for formal current-model simulation.

## Relationship to current Native capture

Current Native capture is not replaced.

Long-term desired relationship:

```text
same workload/target
├── Native capture(s): real-GPU observation
└── Simulation trace capture: replay input
```

When practical, future producer implementation may share model runner, frozen input, launch selection, object mapping and provenance helpers with Native capture. Do not force one instrumentation format to serve both purposes if that compromises correctness.

## Storage lifecycle

Producer:

```text
109 staging → ready → publish
```

Consumer/node164:

```text
inbox.partial → verify → raw/admitted simulation input
```

Reuse the proven Pipeline-V1 transfer semantics: partial/resume, independent hash verification, ACK before producer state transition, no deletion on transfer success alone.

## Explicit prohibitions

- no synthetic ordering from MREF shards;
- no inferred width/opcode/access kind from nearby instructions;
- no filename-only target identity;
- no retokenization/reconfigured workload just to make capture easier;
- no CPU offload or dtype/context changes hidden inside simulator-capture qualification;
- no large-scale current-model capture until canary + bounded simulator smoke pass.
