# C16 V1 destination state

Observed `2026-09-14T14:43:07Z` on branch
`hrl/c16-ai-workload-2239-destination-acceptance-v1` at
`9add956570217abae55f75eda653e9cfeaa27bc3`. The worktree was clean before
creating this V1 result set; `git worktree list` showed this repository as the
sole listed worktree.

## Acceptance summary

| Gate | Result |
|---|---|
| External storage | `STORAGE_ADMISSION_PASS` — selected planned root `/root/share/mnt164/huangrulin/c16_ai_workload_2239`; scratch test passed and was removed |
| Exact Llama asset | `EXACT_ASSET_ADMISSION_PASS` — revision `4e20de362430cd3b72f300e6b0f18e50e7166e08`, six payload hashes matched its immutable local receipt |
| Frozen S0/T128/Decode4 input | `PARTIAL_PRESENT` — raw text hash is visible but the Llama token receipt, IDs, and binding receipts are absent, so the four-hash contract is not closed |
| Runtime | `NEW_DESTINATION_RUNTIME_NON_EQUIVALENT_TO_R5` — no visible GPU or CUDA/PyTorch/transformers closure |
| NVBit 1.7.5 | `REBUILD_OR_VERIFY_REQUIRED` |
| NCU | `REBUILD_OR_VERIFY_REQUIRED` |
| N1/U8 artifact reconciliation | three receipt-bound artifacts not visible in bounded C16 roots; R5 U5/U6/U9 remains `UNKNOWN_PROVENANCE` |

The selected external storage root is a plan only; its namespace was not
created, and no data was copied. The model was observed in the existing 3090
recovery root only for local asset-identity validation. That does not merge
RTX3090 and RTX4080 scientific authority.

## GPU non-interference

`nvidia-smi`, device nodes, CUDA tools, and GPU process telemetry are not
available to this container. Process-name inspection found no independent
Llama/Python/Torch/CUDA/VLLM process. No diagnostic was run and no process was
modified: `GPU_DIAGNOSTIC_NOT_RUN_GPU_NOT_VISIBLE`.

## Decision

`DESTINATION_BLOCKED_MODEL_OR_INPUT_IDENTITY`. Storage and model identity are
admitted, but the exact frozen input package cannot be proven without its
actual payloads and binding receipt. Toolchain rebuilding/verification is also
required before any future bounded canary, but it is not the strongest current
decision blocker.
