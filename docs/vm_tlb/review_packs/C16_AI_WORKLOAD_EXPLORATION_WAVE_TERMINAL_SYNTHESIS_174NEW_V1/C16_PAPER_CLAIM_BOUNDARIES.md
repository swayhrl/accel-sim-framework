# Paper claim boundaries

## Supported

- Compressed W4 execution has real shape/state sensitivity; capacity and access policy matter, but no single L2-only cause is established.
- Cross-M physical address sharing materially controls observed reuse, and grouped CTA scheduling is the decisive strong baseline for the frozen Split-K points.
- Legal FFN wall union is 28.4797% of the accepted timeline; additive module timing is not an admission weight.
- Correctness-passing two-stream execution activates overlap in 10/112 windows but slows full D0-D3 by 9.7257%; gate and up kernel durations inflate.
- Resource contention is directly observed through kernel-duration inflation. It is not proven to explain the entire whole-decode slowdown; stream/event coordination and limited realized overlap remain possible contributors.
- The exploration methodology—oracle-first, strong-software-first, and correctness-first—eliminated several attractive but nonviable mechanism stories.

## Not supported

- A new cache/replacement/dequant/split/concurrency mechanism ready for promotion.
- A hard 64 MiB threshold, all DRAM being qweight, or L2 as the unique cause.
- A performance ranking for the merged vLLM path, or bitwise equivalence across its different backend.
- Plain gate/up concurrency, merged gate/up, tile-ready triggering, generic Stream-K, or fused FFN as novel by itself.
- `resource contention explains all of the two-stream slowdown`.
- A legal cross-tile producer→down pipeline ceiling.
- Generalization from these frozen Qwen2.5/AWQ/RTX4080 points to all GEMMs, LLMs, GPUs or quantization formats.
