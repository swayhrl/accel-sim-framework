# Pilot commit history

- `c0bd9ed431173dfce7511dc1d2cfc0c353a2306c`: P4 project-local rank0 CUDA
  diagnostic.
- `d0ec8a7cd8413a69fb1d1c70b0bb8b2cd7bf37c9`: reuse only a SHA-verified
  staged NVBit archive when the rental image cannot reach GitHub.
- `caaaf5079f9c6b9e7301a07e585db728c20e2247`: accept PyTorch's locked
  `2.6.0+cu126` metadata and put selected CUDA tools on runtime PATH.
- `ac9f42f824abb325acec0846b0da6cce78849d56`: make the P4-only rank proof
  use Gloo for its process barrier so NVBit first-use latency cannot trip a
  NCCL watchdog; real TP4/NCCL remains P5.

These commits are descendants of the required `d22dae…` pilot handoff.
