# Qwen BF16 Decode weight supply and batch reuse probe, node109 V1

Final execution status: **NUMERIC_OR_RUNTIME_NO_GO**.
Scientific outcome: **INCONCLUSIVE**, H1/H2 untested. Model initialization=0, warmup=0, formal samples=0.
This is a new independent experiment, not A79 continuation or C16 Stage A recovery.

## Decisive result and STOP

G0 successfully requalified all12 model files by complete streaming SHA256 against the A79 frozen manifest, including both BF16 shards. Original A00/A01 source and512-token file/canonical IDs were checked and reproduced with the fixed local tokenizer and chat template. The historical MP02_A output reference SHA also matched. Actual installed versions remain vLLM0.30.0, torch2.13.0, transformers5.18.0, tokenizers0.23.2 and nvidia-ml-py13.615.71; fixed compilation/Qwen source hashes and cache-isolation interfaces matched the historical authority.

The supervisor made exactly one nonblocking campaign-lock attempt. It **acquired** the lock at epoch1793775525.2921214, initialized NVML and identified the expected RTX4080 UUID. Before starting any model/worker, its first snapshot referenced the nonexistent Python attribute NVML_VALUE_NOT_AVAILABLE. The installed binding instead exposes NVML_VALUE_NOT_AVAILABLE_ulonglong and maps unavailable process memory to None. The supervisor exited through finally and released the lock after0.01434885seconds.

This was an avoidable supervisor API qualification defect inherited from the historical template. CPU syntax and timing-order checks had passed but did not test this binding-symbol path. The original receipt, traceback and executed supervisor are preserved in raw/. A minimal CPU-only normalization fix now handles None, uint64 unavailable, ctypes and ordinary values; seven fixtures and installed-binding symbol shape pass without NVML/CUDA initialization. ENGINEERING_REPAIR.json distinguishes executed and repaired source hashes; SCIENCE_CONTRACT.json retains the pre-admission hashes.

**No second lock acquisition was attempted.** Engineering autonomy permits the CPU correction, but once the sole lock was released, a GPU revalidation would exceed this single-attempt contract. The repaired supervisor was not run. No formal samples are manufactured. The result is neither a lock conflict nor a model numeric failure.

Final cleanup observation listed three GPU PIDs outside this supervisor's own process set; own contexts were clear. Their ownership and scientific activity were not inspected. The failed initial snapshot means full exclusivity was not established. Do not assert an uncontended GPU window, that those PIDs owned the lock, or that the API fix alone would have admitted model execution. No other processes were signaled.

## Frozen scientific experiment

H1: incremental generation is compatible with streaming one dense BF16 weight pass per step; two simultaneous natural requests may share that pass.
H2: compute/GEMM utilization, launch/scheduling, padding, CUDA Graph dispatch, KV and logprob work can create the same batch response.
H3: input/model/dtype/backend/actual execution mismatches invalidate the comparison. These were frozen before admission.

One engine was prepared for max_model_len544, max_num_batched_tokens1088, max_num_seqs2; BF16, TP1, no quantization/offload/prefix caching, VLLM_COMPILE/inductor/FULL_AND_PIECEWISE, FlashAttention and unquantized linear required, no eager fallback. The512*2 prompt budget fits1088 and CPU source exposes the required scheduler fields. **Live support was not verified** because engine construction was never reached.

Six points are P1 A00x1/output1, P2 A01x1/output1, P3 A00+A01/output1each, P4 A00x1/output32, P5 A01x1/output32, P6 A00+A01/output32each. Each point has two pre-frozen interleaved warmup visits and five interleaved formal visits; all orders are in SCIENCE_CONTRACT.json. No tuning, extra point or input substitution occurred.

Required numeric rules remain exact per-source output length/token identity for repeats and B1/B2, all returned logprobs finite, sampled logprob abs(delta)<=0.05+0.01*abs(reference). A00/output32 additionally uses the pinned historical reference. A01 has no independent external numeric oracle. Nothing here receives Numeric PASS.

Primary timing would be pre-sync, CUDA-event start, complete single generate, event stop, post-sync and elapsed. Host call wall and synchronized host request wall are separate. Manager-level graph descriptors would report padded graph shapes, not actual kernel/DRAM counts or semantic timing. No replay, backend or graph identity was observed this round.

## Conditional structural bound

Safetensors headers contain3,085,938,688 stored BF16 parameters,6,171,877,376 tensor-payload bytes. Dense matrices account for6,171,394,048bytes. The tied embedding is counted once as a full dense LM head; token embedding lookup is not another full scan. All per-tensor identities and arithmetic are in MODEL_AND_BANDWIDTH_BOUND.json.

The [manufacturer specification](https://www.msi.com/Graphics-Card/GeForce-RTX-4080-16GB-SUPRIM/Specification) lists22.4Gbps memory data rate and256-bit bus: nominal716.8GB/s (decimal). This is rated bandwidth, not achieved service measured here.

Under dense BF16, full-vocabulary head, no compression/skipping/speculation/offload, one ideal shared read per dense matrix per step and no persistent weight retention,31 incremental passes imply191,313,215,488bytes and an optimistic streaming time266.899ms. An optional64MiB L2-only persistence credit is separately calculated. The latter assumes no additional persistent L1/register weight residency; neither residency nor achieved clocks were measured. Norm/activation/KV/output/logprob traffic, contention, launch overhead and overlap are omitted.

These are **conditional traffic/bandwidth models**, not measured DRAM bytes or an unconditional bound on a signed request difference. Output32 minus output1 includes graph/planning/prefill differences. Ideal B2 shared weight supply would make its increment similar to the mean single-request increment, but H2 may do so as well. There is no current timing to compare. The historical354.598ms32-token request total has a different capacity configuration and cannot substitute for the missing current delta.

## Strong-software exclusion and hardware decision

See SOFTWARE_EXCLUSION.md for focused primary-source checks of NanoFlow, LLMCompass, DFloat11, ZipServ, Unweight and muShare. Generic batch weight reuse is already software functionality; generic lossless BF16 compression, fused decode/GEMM, per-batch selection and scheduling also have concrete precedents. Unweight supplies an explicit negative throughput example despite compressed bytes, reinforcing conversion/pipeline cost accounting.

Ordinary batch-amortization novelty is SOFTWARE_ABSORBED. This does not claim that every latency source in this exact configuration is solved; no current performance sample exists. No candidate-specific remaining cost or independently falsifiable hardware variable was established, so **no hardware idea card is generated**. Do not label this MEMORY_SUPPLY_CONSISTENT_NOT_CAUSALLY_PROVEN, NATIVE_BATCH_SENSITIVITY_COMPLETE or a measured scheduling confound.

## Sources, resources and handoff

Latest fetched coordination base: ed365741b230718f6ffc1ccbed125fc2566aac15, tree e2f3c9d2d4485b0d41db6c6ceec33af0d8e35304. A79 final1ad28dbe, Stage A terminal ccd6928b and A81492c7c79 were read-only history. A81's missing AWQ path was excluded; it says nothing about this readable BF16 model.

Private inputs/cache roots are isolated under this new output .private directory and ignored by Git. No old model, environment, runtime, source, compiled cache, raw, coordination branch or shared manifest was modified. Weight/data downloads, installs,164 access, profiler/simulator runs and old-Goal resumes are0.

CPU G0 sampled tree peak was732,073,984bytes at1-second resolution. Brief admission and the whole Goal were not continuously RSS-sampled; no full-Goal measured-RSS PASS is claimed. The GPU phase has no successful resource samples because the first snapshot failed; the0.01435seconds is lock-held wall, not model compute time. New disk and final publication are recorded in receipts. Source browsing was read-only on the controller; no model/data transfer occurred.

The next useful work, if separately authorized, is a single bounded admission attempt using the CPU-verified repaired observer, the same frozen scientific points/inputs/precision/backend/numeric gates and explicit one-attempt resource budget. That is a proposal, not a background retry or new Goal. No GPU, RTL, profiler or other task continues after publication.
