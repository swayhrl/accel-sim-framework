# Changed files

| Area | Purpose |
|---|---|
| `docs/vm_tlb/llm/` | explicit Route-E lock, ROI, rental, NCCL, metadata, and execution contracts |
| `util/llm_trace_capture/` | rank-clean injection, per-ROI workload, KV runtime events, bootstrap/smoke/preflight/classifier/test utilities |
| `docs/vm_tlb/codex_handoff/m4a/` | active Track-B closeout report |
| this review pack | auditable PR0–PR10 evidence |

The only selected formal candidate remains Route E: actual TP=4 on one
same-model 4xSM86 host, trace rank 0. Full-model one-GPU tracing remains
rejected as a paper workload.
