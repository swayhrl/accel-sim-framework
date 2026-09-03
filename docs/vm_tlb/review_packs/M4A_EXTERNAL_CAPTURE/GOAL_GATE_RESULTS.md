# Goal gate results

| Gate | Status | Result |
| --- | --- | --- |
| G0 | PASS | Valid local-snapshot pilot admission; post-restart host recovery confirms four idle RTX 3080 Ti SM86 GPUs, retained work root, and 970 GiB free. |
| G1 | PASS | Locked Python/CUDA/PyTorch/NVBit stack, six-file local snapshot checksum, capture-ready preflight, and rank0-wrapper digests rechecked after restart. |
| G2 | PASS | Formal prefill `m4a-llama-prefill-20260902T182016Z` completed with 724 retained raw and 724 postprocessed rank0 traces. |
| G3 | PASS | Prefill archive source/destination SHA256 matched and integrity was independently rechecked on the main server. |
| G4 | RUNNING | New formal decode1 began 2026-09-03T00:41:36Z under the unchanged frozen contract. |
| G5–G8 | NOT_STARTED | Await decode1 completion, checksum-verified copy-back, validation, parser/simulator compatibility, and closeout. |

The historical missing-Hugging-Face-credential blocker is superseded for this
Goal by the verified local snapshot route. No model substitution was made.
