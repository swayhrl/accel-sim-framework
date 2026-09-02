# Validation summary

Passed local/static checks after pilot fixes:

- `py_compile` for capture preflight, workload, and P4 diagnostic;
- `bash -n` for changed launch/bootstrap scripts;
- capture-ready toolchain provenance self-test;
- Llama wrapper/KV self-test;
- kernel classifier self-test.

Passed real-host checks:

- host-only preflight;
- selected CUDA 12.6 `nvcc`/`ptxas` identity;
- PyTorch sees four SM86 devices;
- checksum-verified NVBit bootstrap/build;
- capture-ready preflight;
- generic injection/postprocess/archive/integrity smoke;
- four-rank smoke and rank0-only trace-injection proof.

Additional repaired-route host validations:

- all six local-snapshot files rechecked against the immutable manifest;
- real NCCL TP=4 Llama no-trace run, B=8/S=64/G=3, finite logits and stable
  contiguous flat-weight binding;
- one rank0-only NVBit diagnostic `decode1` capture with raw trace retention,
  postprocessing, classification, Weight/KV validation, archive, and SHA256;
- remote-to-main-server archive digest equality;
- bounded frozen-parser smoke over 35 real SM86 trace kernels.

No synthetic KV object was introduced and no Segmentation implementation or
policy change was made.
