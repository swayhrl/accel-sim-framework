# M4A-P review pack

Stage status: `CONDITIONAL_PASS`.

M4A-P has completed its authorized preparation scope.  The only remaining
execution blockers are deliberately deferred M4A-C work: access to a selected
SM86 rental GPU and the unavailable author artifact / TP-capture details.
No external GPU was rented, no NVBit trace was collected, and no Core VM/TLB
source was modified.

Review order:

1. `SOURCE_ANCHORS.md`
2. `CHANGED_FILES.md`
3. `VALIDATION_SUMMARY.md`
4. `OPEN_ISSUES.md`
5. `RAW_LOG_INDEX.tsv`

Stable deliverables are in `docs/vm_tlb/llm/` and
`util/llm_trace_capture/`.  The exact later capture entry is:

```bash
M4A_C_AUTHORIZED=1 bash util/llm_trace_capture/run_m4a_c.sh \
  --framework-root "$PWD" --work-root /mnt/nvme/m4a-llama \
  --workload-command-file /mnt/nvme/m4a-llama/llama_workload.sh \
  --minimum-free-gib 500
```

It is intentionally blocked until a later written M4A-C authorization.
