# M4A LLM workload contract

Status: `M4A_PRECAPTURE_FIXUP_PREPARED`; no LLM trace has been collected.

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
and enforces B8/S64/G3/TP4. Runtime package pins are in
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
```

The command must use deterministic prompt/token input, emit a metadata sidecar
in `m4a-allocation-sidecar-v1`, and fail rather than silently changing batch,
length, generation count, model revision, or TP setup.
