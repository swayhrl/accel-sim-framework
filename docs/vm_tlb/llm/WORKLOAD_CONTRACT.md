# M4A LLM workload contract

Status: formal Route-E capture complete and immutable; offline M4A merge-prep
semantic audit is in progress. This remains `PAPER_COMPATIBLE_SELF_CAPTURE`,
not author-exact.

## Frozen paper workload

| Field | Value | Evidence |
|---|---|---|
| Model | Llama-3.2 1B | `PAPER_SPEC` |
| Parallelism | tensor-parallel scale factor 4; simulate one partition | `PAPER_SPEC` |
| Batch size | 8 | `PAPER_SPEC` |
| Input length | 64 tokens | `PAPER_SPEC` |
| Generation | 3 tokens | `PAPER_SPEC` |
| Primary regions | prefill and first decode | `PAPER_SPEC` |
| Long context | no full 12K instruction trace; later synthetic-KV work only | `PAPER_SPEC` |

## Formal-route decision

Route E is the preferred formal candidate: one node with **4 x SM86**, actual
framework TP=4, and NVBit injection limited to rank 0. It is
`PAPER_COMPATIBLE_SELF_CAPTURE`, not `PAPER_EXACT`, because the authors' TP
method is unavailable. Rank-0 NCCL/collective activity is retained and
labelled; it must not be silently removed before later compatibility review.

Rank-selective instruction tracing intentionally makes rank 0 much slower than
its peers while the real TP=4 collectives remain live. The workload therefore
uses a recorded `M4A_DIST_TIMEOUT_SECONDS` process-group timeout (default
3600 seconds; values below 600 are rejected). This is a liveness guard only: it
does not change TP topology, workload shape, ROI placement, collectives, or the
raw trace-retention policy.

The frozen formal evidence consists of separate rank-0 ROIs for prefill and
decode1. Both used Llama-3.2-1B revision
`4e20de362430cd3b72f300e6b0f18e50e7166e08`, TP=4, BF16, B=8, S=64, and G=3.
Their capture executable is Framework
`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`; later audit/documentation commits
are not capture executables. Raw rank-0 trace files, raw `kernelslist.g`, and
runtime Weight/KV sidecars are immutable evidence. Semantic classification is
performed from each trace's embedded `-kernel name` header, not its opaque
`kernel-*.traceg.xz` filename.

Route A is a future single-GPU one-rank local-shape/weight-shard emulation
candidate, not the formal default. It needs local Q/K/V and MLP shards plus
explicit row-parallel peer placeholders, and is `DOCUMENTED_APPROX` only after
approval. A full Llama-3.2 1B single-GPU trace is diagnostic-only and rejected
as the formal paper workload.

For TP size 4, Route A would use local column-parallel Q output `H/4`, K/V
output `(N_kv_heads/4)*head_dim`, and gate/up MLP output `I/4`. The local
attention output projection (`H/4 -> H`) and MLP down projection (`I/4 -> H`)
produce only a partial result and require an explicit peer-sum/all-reduce
placeholder. No wrapper may replace those operations with a full `H -> H` or
`I -> H` full-model layer and still call the result a paper partition.

## Pinned executable Route-E wrapper

`util/llm_trace_capture/run_llama_tp4_rank0.sh` launches four ranks with
`torchrun`, requires the immutable Llama model ID and a 40-hex model revision,
an explicit `prefill`, `decode1`, or diagnostic `decode_reuse` ROI, and
enforces B8/S64/G3/TP4. Runtime package pins are in
`util/llm_trace_capture/requirements-llama-tp4.txt`. Inputs are deterministic
token IDs, so no prompt/tokenizer fallback exists; the model revision is also
recorded as tokenizer revision.

## Required command-file contract

The M4A-C entry point receives `--workload-command-file FILE`.  The executable
file is invoked twice, first with `M4A_PHASE=smoke` and then with
`M4A_PHASE=trace`.  It must honor:

```text
M4A_RUN_DIR        per-run output directory
M4A_METADATA_PATH  required allocation sidecar output
M4A_PHASE          smoke | trace
M4A_TRACE_REGION   prefill | decode1 | decode_reuse
```

The Route-E parent explicitly unsets inherited `CUDA_INJECTION64_PATH` before
`torchrun`. The rank wrapper then sets it only for `trace` rank 0; smoke has it
absent at all ranks. The command must use deterministic prompt/token input,
emit a metadata sidecar in `m4a-allocation-sidecar-v1`, and fail rather than
silently changing batch, length, generation count, model revision, ROI, or TP
setup.
