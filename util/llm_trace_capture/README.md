# M4A prepared capture package

This package is a pre-capture deliverable.  `run_m4a_c.sh` is intentionally
blocked unless a later M4A-C authorization sets `M4A_C_AUTHORIZED=1`.

It adapts the safety properties of the audited V100 AutoDL campaign: explicit
host preflight, serial phases, a free-space guard, postprocessing checks,
SHA256 manifesting, and archive integrity.  It does not reuse V100 traces or
claim an exact TP=4 Llama implementation.

Commands safe during M4A-P:

```bash
python3 util/llm_trace_capture/plan_contiguous_weights.py --self-test
python3 util/llm_trace_capture/validate_metadata.py --self-test
bash util/llm_trace_capture/run_m4a_c.sh --help
```

The M4A-C workload command must be an executable, pinned runtime wrapper that
writes `$M4A_METADATA_PATH` and observes `M4A_PHASE`.  See
`docs/vm_tlb/llm/WORKLOAD_CONTRACT.md`.
