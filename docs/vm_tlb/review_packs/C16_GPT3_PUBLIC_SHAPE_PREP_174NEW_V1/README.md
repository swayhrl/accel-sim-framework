# C16 GPT-3 public-shape CPU preparation V1

This pack freezes a two-track native screen using only the public GPT-3-175B FFN dimensions `H=12288` and `4H=49152`.

- `GPT3_PUBLIC_DIMENSION_FP16_DENSE_SHAPE_ANCHOR` is a real FP16 Dense operator at the public expand/contract dimensions, using deterministic synthetic finite values. It is not an original GPT-3 checkpoint or natural activation workload.
- `GPT3_PUBLIC_DIMENSION_AUTOAWQ_W4_MECHANISM_PROXY` maps the same dimensions to the accepted AutoAWQ split8/split1 kernel family. It is not a GPT-3 quantized model.

The independently recomputed maximum conservative peak bound is 5,534,384,128 bytes, including a 4 GiB runtime/workspace reserve. This is below the 16 GiB gate by 11,645,485,056 bytes. Only one operator is resident at a time; Dense and W4 assets are never co-resident, and the conditioner is allocated once for the W4 phase.

`PRE_GPU_CONTRACT_FROZEN.json` authorized Lane 7 CPU-only bootstrap at commit `deb0873240557937ce7ab6b83ecabbc0328754c4`. CUDA import/initialization, GPU lock acquisition, and GPU execution remain forbidden until a later `PRE_GPU_READY.json` is published and its validated commit/tree and hashes match.
