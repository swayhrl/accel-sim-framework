# Source and runtime authority

## Transformer Engine

Source checkout: `/data/c16/awma/r19_fp8_readiness_20261001/source/TransformerEngine_v2_19` on node109. `git rev-parse HEAD` = `5e52befd5262c06289106338c308079d6adb391f`; stable `v2.19.0` tag. No TE source modifications. Installed into isolated `/data/c16/awma/r19_fp8_readiness_20261001/env` copied from the accepted R101 environment; accepted R101 environment and system CUDA/driver were not edited. Local TE Torch wheel build used CUDA 12.8 toolkit, `NVTE_CUDA_ARCHS=89`, `NVTE_WITH_NCCL_EP=0` and resolved isolated include/library paths; the runtime environment is PyTorch `2.6.0+cu124`, CUDA runtime `12.4`. Build/install logs remain in node164 raw.

| Materialized artifact | SHA256 |
| --- | --- |
| `transformer_engine-2.19.0-py3-none-any.whl` | `965d78429d287f7db6978bf299cfcecf68c730247f05cc830ecc6983a123bbc7` |
| `transformer_engine_cu12-2.19.0-py3-none-manylinux_2_28_x86_64.whl` | `a7e098a09042c2451452d6cd2a268d2714b3e66ace5f713991ac1bcfc2409393` |
| `transformer_engine_torch-2.19.0.tar.gz` | `ef268cdd1296bd0ee9e563e18df96c992c347d2f5cb9b48335540e5498043635` |
| Locally built `transformer_engine_torch-2.19.0-cp312-cp312-linux_x86_64.whl` | `8d0e10aada52460cc71a1c8e2c69834ea473a081e5dab2a566912d48ec38d559` |

Runtime receipt in both canaries: RTX 4080 SM89; `te.is_fp8_available() = true`; cuBLASLt `120405`; `layer.fp8 = true`; TE `Float8TensorStorage` quantized input and TE `Float8Tensor` weight workspace. This establishes runtime and representation-path admission, not independently profiled FP8 GEMM SASS identity. No formal operator timing or profiler was run after the numerical gate failed.

TE source numeric-rule location: `tests/pytorch/utils.py::dtype_tols(torch.float8_e4m3fn)` and `quantization_tols("fp8_current_scaling")` yield `rtol=0.125`, `atol=0.0675`. The source lists both delayed and current E4M3 recipes. The numeric criterion was frozen before any formal timing and retained through the excluded delayed canary and final current canary.

## Accepted Qwen input authority

Reused, not redownloaded: `Qwen/Qwen2.5-0.5B-Instruct` revision `7ae557604adf67be50417f59c2c2f167def9a775`; `model.safetensors` SHA256 `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`. Accepted R101 256-token raw JSON file SHA256 `000404d45d04a183379bd7ffa27efdfc196a08f4f97f2003cabad705ab8e2e6d`, canonical token-ID JSON SHA256 `179439d64cb3ba775457854c336633a21d066eceb67a8ad8bfeb99ca78f5208d`. Full hook/tensor/payload identity is in `REAL_INPUT_RECEIPT.json`.
