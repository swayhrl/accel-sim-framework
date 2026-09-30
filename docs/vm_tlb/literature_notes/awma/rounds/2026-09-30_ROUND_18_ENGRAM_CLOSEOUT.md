# Round18 | Engram serving source closeout

Date: 2026-09-30

Final state: `R18_ENGRAM_DIRECT_SOFTWARE_COVERAGE_CLOSES_QUESTION`

This is a **source/literature closeout**, not a Native negative. No node109 CUDA experiment, profiler run, trace capture, or simulator run was performed.

## Authorities re-read

Parent project authorities:
- literature baseline: `5ff0287ce45c3909d53ac44975f6fa488664b085`
- Round16 final closeout: `31d585dc44f90eb70f83603c8b87a2d06efff01a`
- Round17 FlowANN closeout: `8462768f6baf8d4130ee0076c4aee5ff7fd9d6c1`
- Round18 preparation parent: `91df4cd47411e85302c2da37baf3e6969739e553`

Fresh direct-source pins:
- `deepseek-ai/Engram@fb7f84a21f91223715394a33a1dc24bbfb7f788e`
- `vllm-project/vllm@02a3c6dfc56c8776179a2e1c4fe01df270188f71`
- `sgl-project/sglang@bd66ce343e4f6e2f2b75d7e820fe4d0718a8d824`

The official DeepSeek-V4.1-Flash configuration confirms two Engram layers (1 and 14), roughly 384M rows per table, 8 heads, head dimension 256, and the production compressed-vocabulary/hash configuration. This is sufficient to bind the production shape even though the exact official checkpoint-file mapping was not needed for the closeout below.

## Why the candidate is now closed

The preparation card originally left one possible question:

> after mature host placement and overlap, does a real Engram lookup retain a material lookup-path residual on the discrete platform?

Current upstream software and its real-model evidence now directly cover essentially every causal subline that made this question interesting.

### 1. Host placement and UVA are already first-class production paths

Current vLLM defaults Engram to CPU offload: pinned host tables are directly addressable by the GPU through UVA. The model implementation keeps device staging rows and exposes a GPU-side lookup path rather than treating host placement as an external prototype.

SGLang independently implements host-resident Engram tables and a dedicated Engram gather path.

Therefore neither “move Engram tables to host memory” nor “direct GPU access to host-resident rows” is an open AWMA problem.

### 2. Lookup/compute overlap is already implemented and measured on the real model

vLLM PR #56512, merged as `d2d649e674c75425d2d6975c87eb89fd4d55fff8`, starts Engram lookup on a side CUDA stream before the corresponding layer consumes the rows. The current implementation retains:
- a model/layer prefetch stream,
- persistent staging rows,
- per-layer completion events,
- wait-on-consumption semantics.

The PR reports real DeepSeek V4.1 on 4xGB200. Against synchronous lookup, asynchronous prefetch changed TTFT by approximately 0 to -0.9% over the reported 512--16K-input points and was essentially neutral in decode. The PR explicitly reports that lookup bytes / host-link time can be removed from the critical path and that decode-sized lookups are already microsecond-scale.

Thus a generic “overlap host lookup with preceding compute” idea is directly implemented and its headroom is already bounded on the real workload.

### 3. Page size / GPU-MMU translation pressure is already a direct software optimization

vLLM PR #56926, merged as `6936e77ba451725e6482eee229839e10ab2bf48c`, does two things directly relevant to an AWMA memory-system hypothesis:
- serializes offloaded Engram lookups on one model-owned stream so concurrent background lookups do not starve decoder compute;
- packs private host tables into transparent huge pages, prefaults them, registers them with CUDA, and attempts post-load page collapse.

Its real-model kernel study uses one TP4 Engram shard of about 96M rows / 24.8 GiB. Reported lookup times for THP versus small-page pinned memory are:
- 1 token: 2.68 vs 2.69 us
- 32 tokens: 3.28 vs 3.35 us
- 512 tokens: 8.56 vs 11.24 us
- 8192 tokens: 102.32 vs 264.58 us
- 32768 tokens: 392.51 vs 3947.99 us

The PR directly attributes the large-prompt collapse of the small-page path to GPU-MMU TLB thrash. In other words, even the most architecture-adjacent Engram symptom discovered in source review -- translation/page pressure while reading host tables -- already has a mature upstream software counterfactual and quantitative real-model evidence.

The corresponding end-to-end TTFT improvements are modest (up to 2.84% in the reported matrix), which further weakens the case for admitting a new architecture line from this symptom alone.

### 4. Projection compute is already separately optimized

vLLM PR #58678, merged as `4bb804cc5bf0de81ce8344238b5b4522630874fd`, identifies the Engram `wkv` projection as repeated work across TP ranks and changes it from replicated execution to column-parallel execution plus all-gather.

The PR reports roughly 3--4% TTFT/throughput gains on several real DeepSeek-V4.1 serving points and similar gains with the default CPU-offloaded Engram placement.

Therefore a residual observed around an Engram layer cannot be attributed to “lookup memory” without first separating this already-optimized projection cost.

### 5. Cache-style directions are already explicit nearest neighbors

Current SGLang has a production host-table path and a dedicated gather implementation. Its active design discussion also contains rows-only overlap and a hot-row cache proposal. These are baselines/nearest neighbors, not unclaimed AWMA mechanisms.

## Scientific interpretation

A future isolated Engram microbenchmark on node109 could still characterize:
- UVA lookup latency on Ada,
- host-page-size sensitivity,
- overlap behavior,
- request-size scaling.

But after the direct upstream evidence above, such measurements would answer **platform characterization**, not establish a new problem whose causal core is absent from strong software.

The line is therefore closed before Native execution under the AWMA exploration rule:

```
real phenomenon
-> direct nearest-neighbor check
-> strong software counterfactual already exists
-> no new architecture problem admitted
```

No full checkpoint/table download is required merely to reconfirm an already-covered causal story.

## Final decision

`R18_ENGRAM_DIRECT_SOFTWARE_COVERAGE_CLOSES_QUESTION`

Do not:
- run a reduced/synthetic Engram table and promote it as scientific input;
- start node109 CUDA/NSYS/NCU to rescue the candidate;
- design a TLB/cache/prefetch mechanism from the THP result;
- start node174/Accel-Sim or tracing for this line.

Reopen only if a **different** real workload exposes a residual after the current mature host-UVA, overlap, page-size, stream-serialization, and projection baselines.
