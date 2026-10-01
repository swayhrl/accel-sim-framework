# Runtime qualification gaps

- The isolated vLLM 0.30.0 wheel is source-anchor matched and dependency-closed, but has not been imported against a live CUDA device or accepted as the campaign runtime.
- Actual Qwen attention/projection kernels, AWQ-Marlin selection/repack output, and OLMoE expert backend remain unknown until an approved GPU canary.
- No model load, VRAM feasibility, tokenization receipt, token correctness, routing correctness, graph OFF/ON identity, or instrumentation neutrality has been executed.
- OLMoE graph ON remains `STRONG_RUNTIME_VRAM_RISK`; static estimates cannot declare success or failure.
- NCU exact metrics are deliberately not frozen. The AD103 catalog exposes no directly named TLB/PTW/translation blocked-time observable; `TRANSLATION_OBSERVABLE_UNQUALIFIED` remains.
- Direct GitHub fetch of the pinned commit timed out. Official v0.30.0 sdist/wheel hashes are frozen and every preflight-pinned runtime source anchor matches exactly; the full Git object/tree was not locally fetched.
- Existing installed runtimes are inventory only and are not accepted substitutes.
