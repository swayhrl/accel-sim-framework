# Retry570 microreproducer discriminator closeout

Status: `NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED`.

This bounded diagnostic did not use a full Llama model for static-map discovery. It used a small `torch.index_select` workload under the same observed RTX3090/driver570.124.04/PyTorch2.5.1+cu124/libtorch CUDA SHA identity as the Llama candidate. Exact equivalence required the complete mangled `indexSelectLargeIndex<Half, long, unsigned int, 2, 2, -2, true>` identity; no similar kernel was accepted.

The first finite candidate set failed closed to materialize the exact function. The `CUDA_INJECTION64_PATH` path was then used because NVBit documents that PyTorch can overwrite `LD_PRELOAD`. The richer fast-path mapper and a final map-only discriminator both bounded out before the first micro CUDA kernel. The latter has no context-init/tool-init hook, CUDA allocation, instrumentation, or target cache. This supports a narrow NVBit/PyTorch callback-path limitation for this setup, but it does not prove a causal driver failure or a model-level incompatibility.

No NVBit-native static map, authoritative instruction index, direct memory record, C16 tracer trace, Qwen run, or C frozen target was produced. `348` remains only a historical candidate ordinal and `34` only a SASS text-line counter. Both the P0 Llama deployment and the separate microreproducer deployment have their six bounded NVBit windows fully accounted, so no further diagnostic or model NVBit run is authorized on this node. Raw files are outside Git and are locally SHA-closed by the raw index and transfer receipt.
