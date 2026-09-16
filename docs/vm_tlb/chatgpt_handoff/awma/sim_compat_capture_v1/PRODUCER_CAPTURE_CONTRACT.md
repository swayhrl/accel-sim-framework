# SIM_COMPAT_CAPTURE_V1 Producer Contract

## Producer intent

The producer creates a **new simulator-native trace bundle** on node109. It must not derive the bundle from C16WARP1 shards.

Preferred implementation strategy:

1. inspect the existing Accel-Sim/NVBit tracer already present in repository/history;
2. build/requalify it for RTX4080 / SM89 / the node109 CUDA environment;
3. make only compatibility changes needed to preserve simulator trace semantics;
4. emit the simulator's native `kernelslist.g + *.traceg.xz` grammar when possible.

A new intermediate format is allowed only if a formally specified and tested lossless converter produces the exact consumer grammar. Do not create such an intermediate merely for convenience if the native tracer can be made to work.

## Required identity binding

Before GPU capture, freeze a producer manifest containing at minimum:

```text
WORKLOAD_ID / exact legacy authority mapping
TARGET_ID / exact accepted target mapping
model repository + exact revision
input binding SHA256
scenario ID and all dimensions
phase / decode step
backend
dtype / quantization mode
launch selector / target function
producer Git commit
NVBit/tracer source SHA256
tracer binary SHA256
GPU UUID / CC / driver / CUDA identities
```

No retokenization or fallback input is allowed.

## Required trace semantics

The bundle must preserve or explicitly provide:

```text
kernel launch order
stream/context identity
grid/block geometry
static instruction identity / PC
opcode
access kind: READ / WRITE / ATOMIC
memory space
byte width
warp ID
CTA ID
active mask
per-lane addresses
instruction/event ordering
sync/control semantics
terminal completeness
```

Sidecars must include enough address context for the admitted simulation scope, including ASID/epoch/VA width/page policy and object/address context when available.

## Completeness and integrity

Formal capture requires:

```text
terminal_status = COMPLETE
drop_count = 0
overflow_count = 0
all kernelslist members exist
all payload/list/sidecar SHA256 values closed
deterministic decoder/parser record-count sanity
```

A capture with drops, overflow, truncated terminal state, unresolved identity, or missing simulator semantics is DIAGNOSTIC/REJECTED and cannot receive a formal `SIM_INPUT_ID`.

## Capture sequence

### P0 CPU-only preparation

Before taking the GPU lock:

- build tracer/tool;
- run static/source audits;
- prepare exact workload/target manifest;
- prepare output directory and disk-space estimate;
- prepare terminal/drop/overflow checks;
- prepare transfer manifest;
- prepare bounded run timeout/size guards.

### P1 micro-canary

Acquire the GPU lock. Run the smallest real CUDA canary required to prove:

- tracer loads on SM89;
- output grammar is generated;
- kernelslist and trace file(s) are readable;
- required semantics are present;
- no drop/overflow.

The micro-canary is qualification evidence only.

### P2 target canary

Run the exact Qwen target with a small/bounded capture selector if needed to validate launch matching and estimate data volume. This remains diagnostic until the formal target capture closes.

### P3 formal target capture

Capture the exact accepted Qwen2.5-0.5B S2_TEXT Prefill Attention target. Preserve the full execution semantics of the selected simulation target. Do not shard by MREF in a way that loses global warp/instruction order.

### P4 producer validation

Before publication:

- re-read/decompress all trace members;
- validate list closure;
- validate terminal/drop/overflow;
- run local parser/format smoke if available;
- hash all artifacts;
- create immutable READY manifest.

### P5 transfer

Use the accepted 109→174/node164 pipeline. Publish only READY/hash-closed content. Consumer independently rehashes/admission-checks before raw acceptance.

## Storage

Keep simulator capture logically separate from Native raw. Do not overwrite existing C16 capture directories. Suggested node164 logical destination after ingest:

```text
captures/raw/<capture_id>/simulation_trace/
derived/awma/simulation/inputs/<sim_input_id>/
```

Actual existing pipeline layout may be reused if identity/catalog relations are explicit.

## Size/resource rule

Trace size is a bounded engineering problem. Estimate and record output rate early. If a target is too large for a safe formal run, narrow the **scientific target/ROI explicitly**; do not silently truncate an otherwise full target and call it complete.
