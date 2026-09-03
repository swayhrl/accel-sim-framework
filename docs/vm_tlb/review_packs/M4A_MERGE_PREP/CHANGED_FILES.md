# Changed files

The merge-prep changes are limited to offline B-owned analysis utilities and
documentation. They do not alter frozen archives, Track-A/Core, capture
wrappers, or VM semantics.

- `util/llm_trace_capture/classify_kernels.py`: embedded-header semantic
  classification and non-destructive compute/NCCL derivatives.
- `util/llm_trace_capture/analyze_trace_address_coverage.py`: exact
  active-lane streaming decoder and conservative runtime-range coverage.
- `docs/vm_tlb/llm/WORKLOAD_CONTRACT.md` and `NCCL_KERNEL_POLICY.md`.
- `docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/*`: corrected semantic audit
  facts and decode1 evidence parity.
- `docs/vm_tlb/review_packs/M4A_MERGE_PREP/*` and M4A handoff closeout.
