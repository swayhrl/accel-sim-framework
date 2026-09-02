# M4A LLM workload contract

Status: `M4A-P_PREPARED`; no LLM trace has been collected.

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

The capture package requires the runtime command to record its exact framework,
model revision, tokenizer revision, dtype/quantization, and TP method.  Those
four fields remain `UNKNOWN`/`PAPER_DETAIL_UNAVAILABLE`; a full-model,
single-GPU trace must never be relabelled as the paper's TP=4 partition.

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
