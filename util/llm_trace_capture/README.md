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
python3 util/llm_trace_capture/llama_tp_workload.py --self-test
bash util/llm_trace_capture/test_rank0_nvbit_mock.sh
python3 util/llm_trace_capture/test_roi_contract.py
python3 util/llm_trace_capture/test_roi_memcpy_policy.py
python3 util/llm_trace_capture/classify_kernels.py --self-test
python3 util/llm_trace_capture/capture_ready_preflight.py --self-test
bash util/llm_trace_capture/test_bootstrap_toolchain_provenance.sh
bash util/llm_trace_capture/bootstrap_route_e_nvbit.sh --framework-root "$PWD" --work-root /tmp/m4a --cuda-home /opt/cuda-12.6 --dry-run
bash util/llm_trace_capture/run_m4a_c.sh --help
```

The concrete preferred wrapper is `run_llama_tp4_rank0.sh`: it uses four SM86
GPUs, real TP=4, rank-0-only NVBit injection, `llama_tp_workload.py`, and the
pinned requirements file. It has distinct `prefill`, `decode1`, and optional
`decode_reuse` runs with profiler-controlled ROI. Set an immutable
`M4A_MODEL_REVISION`; secrets stay external. See
`docs/vm_tlb/llm/WORKLOAD_CONTRACT.md`.
