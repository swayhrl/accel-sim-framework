# Host and locked environment

Remote host: `autodl-container-y3dnxs4rbm-7ddc7538`.

- GPUs: four `NVIDIA GeForce RTX 3080 Ti`, 12,288 MiB each, compute capability
  8.6, driver `595.71.05`.
- CPU/RAM: 80 CPUs; 251 GiB installed memory (235 GiB available at P1).
- Large writable work root: `/root/autodl-tmp/m4a-llama` on `/dev/nvme0n1`;
  999 GiB free at P1 and 981 GiB at capture-ready preflight.
- Python: 3.10.12.
- PyTorch: `2.6.0+cu126`; `torch.version.cuda` is `12.6`.
- Packages: Transformers 4.51.3, Accelerate 1.6.0, Safetensors 0.5.3,
  huggingface_hub 0.30.2.
- Selected toolkit: `/root/autodl-tmp/m4a-llama/cuda-12.6`; both `nvcc` and
  `ptxas` report CUDA 12.6.85. The driver was not changed.
- Tracer: NVBit 1.7.6 with the locked SHA256 above; tracer and postprocessor
  were built using the selected toolkit, not the host PATH.

Machine-readable evidence is copy-backed as `host-preflight.json` and
`capture-ready-preflight.json` in the persistent root.
