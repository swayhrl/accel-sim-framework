# AWMA Discussion Reference — Q05 representativeness and translation behavior

Date: 2026-09-17

## Why this stage exists

The first TLB/PTW characterization round established strong fixed-window sensitivity to removing the functional translation path, but it did not yet establish the root cause. In particular, the current 10k baseline has 125 L1/L2 TLB miss requesters, but only 19 new translation allocations and 106 merges. The maximum waiter depth is 35, and most accumulated requester-level translation latency is recorded in MSHR wait.

Therefore the current evidence is more specific than “TLB hit rate is low”, but less specific than “PTW is the bottleneck”. The scientific question now is whether the observed behavior is mainly caused by cold first-touch, low-reuse streaming, outstanding-translation fanout, long completion latency, or a mixture.

## Terminology used in this handoff

### S2_TEXT

`S2_TEXT` is an AWMA-internal scenario label, not a standard LLM concept. In the current project it means the frozen text-inference configuration:

```text
batch = 1
Prefill = 2048 tokens
Decode = 32 tokens
input type = TEXT
dtype = FP16
backend = SDPA
```

### capture completion / terminal status

When historical notes say `terminal = COMPLETE`, the intended meaning is simply:

> the trace-collection run ended with the expected completion marker.

For this Q05 producer capture, `drop=0` and `overflow=0` additionally show that the producer did not report dropped trace records or buffer overflow.

### trace bundle

A “bundle” means one self-consistent trace input package: the trace data plus its kernel metadata, configuration, receipts, manifests and hashes. It is not a special execution concept.

### kernel census

A “kernel census” means a lightweight inventory of every CUDA kernel launch in one complete model run. It records launch metadata such as kernel name, phase, launch shape and duration. It is not a complete SASS trace of every kernel.

### VPN

VPN means virtual page number. For the current 64 KiB base-page experiment, addresses belonging to the same 64 KiB virtual page share the same VPN, subject to the simulator's actual translation key semantics such as ASID/epoch/page-size.

## What was actually captured

Do not describe the current simulator input as a complete Qwen2.5 inference trace.

The accepted simulator-native input is the complete selected Q05 CUDA kernel:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
pytorch_flash::flash_fwd_kernel<...>
```

The 10k and 50k experiments are cycle-limited replays of that complete selected-kernel input.

Other Native traces and full-run metadata exist under the broader AWMA/C16 workflow, but Native C16WARP1/MREF evidence must not be post-hoc converted and claimed as a lossless Accel-Sim trace.

The simulator-compatible producer pipeline is now operational, so additional selected kernels can later be captured by reusing the qualified path. This stage deliberately does not authorize new selected-kernel capture because target selection should first be informed by the full workload kernel inventory.

## Why the current L2-TLB 0-hit observation is not enough

In the 10k R0 window:

```text
L1 misses               = 125
L2 accesses             = 125
L2 hits                 = 0
L2 misses               = 125
translation allocations = 19
translation merges      = 106
```

The identity

```text
125 = 19 + 106
```

shows that many miss requesters are joining an already-outstanding translation instead of starting independent walks.

Consequently, an L2 lookup can miss because the corresponding translation has not yet completed/fill occurred, even when many requesters are asking for the same page. This is different from capacity thrashing and different from a purely streaming workload.

The current L2 TLB also has 768 entries, while the offline full-trace footprint is on the order of only a few hundred 64 KiB pages. That makes a simple “capacity is obviously too small” narrative especially inappropriate without further evidence.

## Why P2 does not establish that L2 lookup is irrelevant

P2 changes L2-TLB port count from 1 to 2. It strongly reduces port-denial/retry events but produces essentially no 10k progress improvement.

This causally downgrades **L2-TLB port throughput/queueing** as the dominant single bottleneck.

It does not change the configured L2-TLB lookup service latency. Therefore it does not establish that L2 lookup latency itself is irrelevant.

## Why I0 is not “100% L1 hit”

I0 uses ideal identity translation. It bypasses the functional translation path rather than simulating a 100%-hit 10-cycle L1 TLB. It therefore removes more than TLB misses: it also removes TLB lookup delays, translation-MSHR/walker/PTW behavior and PTE memory traffic.

Thus the +56.55% (10k) and +76.55% (50k) values are aggregate translation-path fixed-window progress sensitivity, not the speedup of a realizable perfect-L1-TLB mechanism and not full-kernel speedup.

## Why full-Q05 VPN analysis is required

The next analysis must distinguish at least four behaviors.

### Cold first-touch

A page misses on its first access, fills, and subsequent accesses mostly hit.

### Streaming / low reuse

New pages continue to appear throughout execution and many are rarely revisited.

### Burst fanout before fill

A page first misses, one translation becomes outstanding, and many requesters arrive before that translation completes. These requesters can repeatedly traverse part of the lookup path and then merge.

### Persistent post-fill reuse

A page continues to receive meaningful traffic after translation fill and later benefits from TLB residency.

The real workload may be `MIXED`; the analysis must not force one label.

## Why the analysis must cover the complete Q05 kernel

The present 10k and 50k values are cycle windows. To interpret them, establish where they sit in the complete selected kernel using comparable coverage measures rather than dividing unlike counters.

Required coverage axes:

1. CTA issued and CTA completed;
2. warp-instruction trace progress using a proven same-unit numerator/denominator;
3. memory-reference trace progress using a proven same-unit numerator/denominator;
4. unique 64 KiB page coverage.

The page-coverage metric is particularly important. If most full-kernel pages have already first-touched by 10k, the observed translation pressure can be front-loaded cold behavior. If unique pages continue to grow throughout the kernel, a streaming interpretation becomes more plausible.

## Why the full workload kernel inventory is required

Q05 is scientifically useful only if its representativeness is understood.

The full B1/T2048/Decode32 run should therefore be inventoried at lightweight kernel-launch level. For each semantic/exact family, report both:

- launch-count share;
- accumulated GPU-time share.

These are different notions of frequency/importance. A tiny kernel may launch many times yet consume little GPU time; a large GEMM or attention kernel may launch fewer times but dominate runtime.

Attention should be analyzed at two levels:

1. semantic family such as projection, attention core, output projection, RoPE/layout/auxiliary work;
2. exact CUDA implementation and launch shape.

Do not infer Q/K/V identity or Transformer layer purely from mangled kernel names or launch order. Use reliable NVTX/runtime/operator evidence if available; otherwise mark fields `UNKNOWN`.

## Why the two tracks run on different nodes

### 174-new

The complete accepted Q05 simulator-native trace and accepted simulator characterization live on the Simulation plane. 174-new is therefore the correct owner for full-Q05 VPN/translation analysis and any diagnostic-only simulator instrumentation.

### 109 / RTX4080

The full-model kernel inventory is a Native execution question. Existing accepted NSYS/catalog data should be reused first; only if they are insufficient should 109 run one lightweight NSYS capture of the frozen scenario.

No NCU, NVBit memory trace or simulator-native detailed capture is required for this inventory.

## Rejected next steps for now

Do not yet start:

- L2-TLB latency sweep;
- PTW fixed-latency mode;
- walker-count sweep;
- translation-MSHR capacity sweep;
- TLB-capacity sweep;
- page-size sweep;
- Segment experiments;
- early-outstanding-translation detection mechanism;
- broad capture of additional kernels.

Those may become appropriate after the current stage clarifies whether Q05 pressure is cold, streaming, fanout-dominated or mixed, and whether Q05 is representative enough to justify mechanism work.

## Expected decision after both tracks

After the two Codex tracks complete, ChatGPT should review both reports and decide among paths such as:

- if Q05 is cold/front-loaded and post-fill reuse is strong: investigate cold-translation completion/fanout mitigation rather than TLB capacity;
- if unique pages continue to stream and reuse is weak: investigate translation reach/page-size/streaming behavior;
- if post-fill reuse is high but latency remains exposed: decompose lookup service latency versus PTW/PTE completion latency;
- if Q05 is not representative: select a small set of additional high-value kernels using launch count, GPU-time share and address-translation characteristics before mechanism design.

No mechanism conclusion is predetermined by this handoff.
