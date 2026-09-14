# C16 Formal Campaign — Readiness Recovery Playbook V1

This document defines how Goal-mode Codex should solve the known pre-capture gaps **without weakening scientific quality**.

## A. Object-map closure

Current pre-capture blocking condition includes missing object maps. Build the object map during the same formal campaign.

### A1. Required classes

At minimum preserve:

- `WEIGHT`
- `QUANT_METADATA`
- `KV_CACHE`
- `UNKNOWN_RUNTIME`

`ACTIVATION` may be added when evidenced reliably, but lack of complete activation attribution is not a blocker.

### A2. Dense/Qwen/Llama weight ranges

After model load, enumerate parameter/buffer storage ranges in the actual runtime process.

For every unique storage record:

- device pointer/range;
- storage bytes;
- tensor/module name(s);
- dtype;
- model/layer ownership;
- alias group if multiple tensors share storage.

Treat ordinary model parameter payload as `WEIGHT`.

### A3. AWQ classification

For AutoAWQ quantized linear modules:

- packed quantized weight payload (`qweight` or runtime-equivalent packed weight tensor) -> `WEIGHT`;
- scales / zero-point / qzeros / g_idx / other quantization metadata -> `QUANT_METADATA`;
- do not call the observed unfused backend fused.

If names differ in the installed AutoAWQ implementation, derive the classification from module/tensor role and preserve the exact runtime name in provenance.

### A4. KV cache ranges

At prefill completion and selected decode steps, enumerate tensor storages that implement `past_key_values` / cache objects or the runtime-equivalent KV cache.

Record per layer when possible:

- address range;
- tensor shape/dtype;
- decode step;
- logical layer;
- whether a storage is reallocated or grows in place.

If the framework hides some temporary KV-like buffers, classify only evidenced cache tensors and leave others `UNKNOWN_RUNTIME`.

### A5. Coverage rule

Formal capture does **not** require 100% object attribution.

It does require:

- known model weights are range-bound;
- known AWQ metadata is range-bound for AWQ;
- known framework KV cache is range-bound for decode targets;
- unmatched addresses remain explicitly UNKNOWN.

The object map must be hash-closed and bound to the same process/run configuration as the trace.

---

## B. Heavy GEMM semantics unresolved

Current pre-capture data contains exact CUTLASS functions whose semantic role is not yet proven to be FFN/projection/etc.

Do not block a strong target solely on this.

Use the label:

`GEMM_HEAVY_UNRESOLVED_SEMANTIC`

while preserving:

- exact full/mangled function;
- code-object identity;
- grid/block;
- phase and launch ordinal;
- duration/population evidence;
- static GLOBAL MREF set;
- NCU/canary evidence.

Attempt cheap semantic refinement using module NVTX/callsite/shape evidence when available, but never invent FFN/attention projection labels.

---

## C. Missing exact static MREF map

A representative target needs an RTX4080-local static map of the selected exact function.

Recovery order:

1. revalidate the dynamic launch identity in the current process;
2. bind the loaded code object / binary identity;
3. disassemble/map that exact function;
4. enumerate all `GLOBAL` memory references and classify load/store/opcode/offset/index;
5. hash-close the static map.

If symbol names are unstable, use exact code-object identity + function handle/mangled name/offset evidence from the launch-identity diagnostic.

Do not substitute a neighboring function merely because it maps more easily.

If a target's exact function cannot be mapped after local identity recovery, rank a fallback from the same semantic stratum and repeat.

---

## D. NCU missing or incomplete

NCU is a ranking/characterization aid, not a universal formal-trace gate.

Preferred:

- at least one bounded NCU characterization for the highest-value target in each deployment/major stratum when practical.

If NCU cannot profile an otherwise exact target because of replay/permission/tool-specific limitations:

- retain the NCU failure receipt;
- use NSYS duration/population + static MREF + address-bearing canary footprint for readiness;
- do not fabricate NCU metrics;
- formal capture may continue if the target remains clearly representative and exact.

---

## E. Address-bearing canary quality

Before a large formal trace, perform a small address-bearing canary on the exact target.

Required observations:

- target launch is found by the exact selector;
- nonzero executing memory records;
- correct phase/decode-step binding;
- no silent selector drift;
- callback/drop/overflow status recorded;
- unique address/page/line footprint measured;
- object-map join attempted.

### Weak-target handling

A representative target that collapses to an obviously trivial footprint (for example one line/page when the stratum is expected to represent broad model memory movement) must not be promoted merely because instrumentation succeeded.

Instead:

1. confirm selector/MREF logic;
2. try another launch occurrence if shape/role differs;
3. move to the next evidence-ranked fallback in the same stratum.

A genuinely small-footprint special/control kernel may still be kept as `CONTROL_ONLY`, not as a phase representative.

---

## F. NVBit produces zero addresses

Recovery order:

1. rerun exact selector once in a fresh process;
2. verify function/launch identity did not drift;
3. verify selected static GLOBAL MREFs actually execute;
4. run the known-good NVBit 1.7.5 tool regression/canary;
5. rebuild the tool from the pinned source/tool identity if the tool itself is suspect;
6. if the target remains zero, use a same-stratum fallback.

Do not switch NVBit versions silently.

---

## G. Trace too large / slow / overflow

Use bounded capture, but preserve complete scientific windows.

Preferred recovery:

- reduce number of selected launch instances;
- capture one exact representative launch instead of many repeats;
- narrow to a precise phase/decode-step window;
- keep all relevant GLOBAL MREFs within the selected launch.

Do **not** solve size by falling back to one arbitrary PC.

Default per-target planning bounds remain approximately:

- `<= 4 GiB` raw target bundle;
- `<= 20 min` target runtime;

These are operational bounds, not reasons to accept a mid-launch truncated file as formal.

If the bound is hit mid-window:

- preserve it as `BOUNDED_DIAGNOSTIC`;
- rerun with a smaller complete launch/window selector;
- promote only the complete bounded rerun to formal.

---

## H. Qwen2.5-7B raw S2 OOM

The prior failure was near the 16-GB device boundary. Perform a clean exact retry only after the GPU is otherwise idle.

Allowed:

- fresh process;
- no unrelated GPU process;
- previous model processes exited;
- exact same frozen input/model/dtype/backend/scenario.

Not allowed for the same formal deployment:

- smaller context/batch/decode;
- lower precision;
- different attention backend;
- CPU offload;
- unrecorded allocator/runtime changes that alter memory-layout behavior.

Two clean-process failures are sufficient to classify the exact S2 deployment as `NOT_ADMITTED_MEMORY_CONFIRMED`; continue the rest of the campaign.

---

## I. AWQ backend is unfused

The observed environment lacks `awq_ext`; the current admitted deployment is unfused AutoAWQ.

For this campaign:

- capture the actual unfused deployment as its own exact implementation;
- do not call it fused or compare it as if it were fused;
- do not install/build a new fused extension in-place during the formal campaign.

A fused AWQ backend can be a later separately qualified deployment if desired.

---

## J. Decode early/late selection

For S2 Decode32, prefer to compare an early and late decode step for memory/KV-sensitive targets, e.g. near step 1 and near the final admitted step, when the exact runtime makes both identifiable.

For S3 Decode16, use the analogous early/late concept if S3 becomes a selected control.

If the target kernel population/shape is identical and the observed object/KV footprint does not materially change, one may be retained as the representative and the other as a bounded control; record the evidence rather than forcing duplicate traces.

---

## K. Scenario content/context/batch expansion

Do not collect all seven frozen scenarios automatically.

Use lightweight native/NSYS comparison first.

Promote a scenario to formal control capture when it exposes meaningful new evidence such as:

- new memory-relevant kernel class;
- changed target function/launch shape;
- long-context attention/KV behavior;
- materially different memory-heavy population;
- batch-induced implementation change.

Otherwise record `CONTROL_ONLY / NO_MATERIAL_KERNEL_CHANGE` and continue.

---

## L. Pipeline transfer/ACK failure

If capture is locally closed but remote publication fails:

- keep the local `ready/<RUN_ID>` bundle;
- retry transfer only;
- do not rerun the GPU workload;
- never delete the source because rsync returned success;
- accept completion only after destination rehash/catalog/ACK and node109 ACK verification.

If node164 is temporarily unavailable, continue new bounded captures only if node109 has safe free space; otherwise stop starting new large captures and preserve completed local bundles.

---

## M. Analysis parser failure after valid capture

Analysis prep at `d07b7eb5...` already passed exact RTX3090 Q2 regression.

If a newly admitted formal trace fails parsing:

- preserve raw/ACK as valid capture evidence;
- attempt parser adaptation on 174-new without mutating raw;
- do not invalidate/re-run the GPU trace merely because derived analysis failed;
- final campaign may classify `CAPTURE_PASS_ANALYSIS_PENDING` for that run if parser repair cannot finish within the capture session.
