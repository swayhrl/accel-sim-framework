# C16 Lane G run / receipt schema

Every runner, profiler, and capture receipt uses `C16_G_NATIVE_RECEIPT_V1`. Before any GPU operation, `identity` must close `model_id`, immutable model/tokenizer revisions, deployment/implementation, dtype/quantization, scenario/input hash, run ID, and code commit. Native receipts additionally record CUDA device/UUID, driver, CUDA/PyTorch, attention backend, compile state, and profiler mode.

`NATIVE_GPU` with `scientific_eligible=true` is the only scientific native mode. `DRY_RUN` and `MOCK` receipts are deliberately `scientific_eligible=false`; their placeholder output must never be imported into a native catalog. A CPU fallback, dtype change, backend change, or incomplete identity invalidates the run rather than silently creating a result.

Kernel/counter/trace target receipts additionally bind phase, decode-step bin, device/context/stream/correlation, kernel name, implementation, grid/block, semantic evidence, and the revalidated run ID. A naked launch ordinal is never a capture key.
