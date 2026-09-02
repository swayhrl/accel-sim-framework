# M4A-P local environment inventory

Observed on 2026-09-02 at Framework commit
`aa901732753c5ca0c66694932456720081e468cd`:

| Item | Observation | Classification |
|---|---|---|
| NVIDIA GPU | `nvidia-smi` unavailable; no local GPU capture route | `VERIFIED_RUN` |
| CUDA toolkit | `nvcc` CUDA 11.8.89 | `VERIFIED_RUN` |
| Python | 3.11.6 | `VERIFIED_RUN` |
| PyTorch / Transformers / vLLM | not installed | `VERIFIED_RUN` |
| Llama-3.2 1B weights | no matching local model/cache candidate found | `VERIFIED_RUN` |
| Free workspace disk | 231 GiB at inventory time | `VERIFIED_RUN`; below the prepared 500 GiB rental gate |
| Frozen tracer | NVBit 1.7.6 download is declared by `util/tracer_nvbit/install_nvbit.sh`; binaries are not built locally | `VERIFIED_CODE` |

Conclusion: `EXTERNAL_SM86_GPU_REQUIRED`.  No package installation or GPU
trace attempt was made on this development host.
