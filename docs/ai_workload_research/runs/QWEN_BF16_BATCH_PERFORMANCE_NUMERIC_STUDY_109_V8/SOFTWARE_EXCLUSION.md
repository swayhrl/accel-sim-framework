# V8 strong-software exclusion and measured controls

Historical paper capabilities and exclusions remain in INHERITED_SOFTWARE_EXCLUSION.md. Its old 'never initialized/NOT_MEASURED' row describes historical provenance, not V8.

| Existing mechanism | V8 direct evidence | Consequence for hardware claims |
|---|---|---|
| Strong compiled BF16 plus FULL_AND_PIECEWISE and FlashAttention | All five configurations complete six points; formal active compiled model and31 fullgraph replays for output32, no formal compilation/capture | Generic compile/Graph/Batch reuse is already software; these controls do not expose DRAM/compute causality. |
| Two-request natural batching | MAIN R1.031484 and same32-token sequences, fixed natural512-token inputs | Large observed amortization is native Batch reuse, not a new hardware idea. |
| Optional top20 logprobs | Time-interleaved LP20_CONTROL versus official LP_NONE; about4.2-4.5ms difference in32-minus1 contrasts;R remains about1.033 | Return/normalization overhead is an existing software knob. It does not explain away the Batch response and is not an isolated kernel measurement. |
| Automatic prefix caching | Reset cold and reset+output1-prime warm;actualcachedtokens0 inB1cold,0/16 inB2reset,496/requestinwarm | Strong software materially reduces repeated-prompt prefill. Do not call this weight sharing; hot-cache A01 has sequence divergence and separate descriptive statistics. |
| Actual new GPU sampler | Runtime-bound class vllm.v1.worker.gpu.sample.sampler.Sampler;Triton topk log-softmax;FP32 normalization source and captured logits | Older generic v1.sample.sampler source is not the operative sampler identity. Captured pre-sampler differences already explain returned scores. |
| Lossless BF16 compression and scheduling prior art | Historical NanoFlow,LLMCompass,DFloat11,ZipServ,Unweight,muShare table retained with frozen source links;noneinstalledorbenchmarkedhere | Compression,sharedweights and colocation are not novel by themselves. No exact-checkpoint speedup or hardware/PPA improvement is claimed. |

Unresolved measured cost is roughly318ms/31 extra B1 steps with strong software. Native timings and software controls cannot partition it into DRAM,TensorCore execution,launch/control or scheduler components. NEXT_QUESTIONS.md defines falsifiable future axes; no new mechanism,RTL or independent Goal is started.
