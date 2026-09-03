# Goal gate results

| Gate | Status | Result |
| --- | --- | --- |
| G0 | PASS | Valid local-snapshot pilot admission; post-restart host recovery confirms four idle RTX 3080 Ti SM86 GPUs, retained work root, and 970 GiB free. |
| G1 | PASS | Locked Python/CUDA/PyTorch/NVBit stack, six-file local snapshot checksum, capture-ready preflight, and rank0-wrapper digests rechecked after restart. |
| G2 | PASS | Formal prefill `m4a-llama-prefill-20260902T182016Z` completed with 724 retained raw and 724 postprocessed rank0 traces. |
| G3 | PASS | Prefill archive source/destination SHA256 matched and integrity was independently rechecked on the main server. |
| G4 | PASS | Fresh formal decode1 produced 772 raw and 772 postprocessed traces. |
| G5 | PASS | Decode1 archive copied back with matching SHA256. |
| G6 | PASS | Formal metadata/kernel validation completed. |
| G7 | PASS | Bounded frozen-parser compatibility audit completed. |
| G8 | PASS | Review evidence and closeout complete. |

The historical missing-Hugging-Face-credential blocker is superseded for this
Goal by the verified local snapshot route. No model substitution was made.
