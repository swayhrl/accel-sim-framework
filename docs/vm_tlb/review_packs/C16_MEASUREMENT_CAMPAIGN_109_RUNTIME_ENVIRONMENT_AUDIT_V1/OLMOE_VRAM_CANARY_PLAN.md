# OLMoE VRAM qualification-canary plan

This is static planning only; no model was loaded. The pinned OLMoE weights total 13,838,721,960 bytes. Authority estimates place the graph-OFF lower envelope at 15,520,637,864 bytes and the conservative upper envelope at 19,278,734,248 bytes versus node109's 16376 MiB. vLLM defaults `gpu_memory_utilization=0.92`, profiles/reserves KV dynamically unless `kv_cache_memory_bytes` is explicit, and exposes `max_model_len`, `max_num_seqs`, `enforce_eager`, and CUDA-graph compilation controls. The built-in CuMemAllocator is available; sleep mode/custom allocation policy is not part of the canary.

`STRONG_RUNTIME_VRAM_RISK`: graph ON may require materially more memory and may not fit. This estimate is not a failure decision.

Future graph-OFF identity canary (project approval required): M=1, context=512 plus D0–D31, `max_model_len=544`, `max_num_seqs=1`, graph/compile OFF (`enforce_eager=True`), frozen BF16 checkpoint/input/tokenization receipt. Record load success, peak/steady VRAM, tokens, routing, kernel/backend identity, and unload closure.

Future graph-ON strong-baseline qualification: identical model/input/limits with the mature default compiled/CUDA-graph path. Require correctness, routing and kernel identity contract; record graph pool/reservation and peak VRAM. OOM is preserved as a qualification failure, not bypassed by offload or a weaker backend. Combined future GPU-active cap: <=4 minutes. This audit does not authorize it.
