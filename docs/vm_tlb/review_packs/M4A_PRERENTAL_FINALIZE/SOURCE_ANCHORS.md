# Source anchors

| PR gate | Evidence / source anchor |
|---|---|
| PR0 | Track-B `HEAD` began at `51a36b376a8c6a59c02c181b26233bd0c4c3322f`; Route-E package commit `4c4c083bac8d17f9a6901fc7132c273ade2d6849`; `util/tracer_nvbit/install_nvbit.sh`; `tracer_tool.cu:250-252,830-838` |
| PR1 | `run_m4a_c.sh`, `run_llama_tp4_rank0.sh`, `rank0_nvbit_exec.sh`, `test_rank0_nvbit_mock.sh` |
| PR2 | `ROI_TRACE_POLICY.md`; `llama_tp_workload.py:profiler_region`; `tracer_tool.cu` profiler callback above |
| PR3 | `CAPTURE_ENV_LOCK.md`; PyTorch 2.6.0 official wheel instructions; Hugging Face TP guide; pinned Transformers `v4.51.3` Llama configuration `base_model_tp_plan` and `modeling_utils.py` `tp_plan="auto"` source inspection; metadata API revision `4e20de362430cd3b72f300e6b0f18e50e7166e08` |
| PR4 | `bootstrap_route_e_nvbit.sh`, `run_generic_nvbit_smoke.sh`, NVBit asset SHA-256 `dba617…5467f` |
| PR5 | `host_preflight.py`, `capture_ready_preflight.py` |
| PR6 | `observe_kv_cache` and `validate_metadata.py` fake-tensor test |
| PR7 | `classify_kernels.py`, `NCCL_KERNEL_POLICY.md` |
| PR8/PR9 | `TRACE_ACQUISITION.md`, `AUTODL_RENTAL_CHECKLIST.md` |
| PR10 | `VALIDATION_SUMMARY.md` |

No Core VM/TLB semantic source or `gpu-simulator/` file changed.
