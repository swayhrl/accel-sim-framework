# AWMA R19 Lane F — native Ada FP8 readiness qualification

Stage: `AWMA_R19_FP8_READINESS_109_V1`

Execution branch: `hrl/awma-r19-fp8-readiness-109-v1`

Starting commit: `c618f9f7bb2172908adb0e26bd60f04acc72cacb`
Final classification: `R19_FP8_RESULT_MIXED_NEEDS_REVIEW`

The real-input and Transformer Engine runtime admission gates passed, but the predeclared elementwise FP8-versus-BF16 numerical gate did not. This is a scientific stop before formal timing. There are **no** A0/A1/D0 paired timing samples, median/MAD, NSYS or NCU measurements, and no quantified representation-readiness residual. In particular, this result is neither evidence that TE software is sufficient nor evidence that a hardware opportunity remains.

## Frozen identity and source

- Node: 109, NVIDIA GeForce RTX 4080, SM89. Every CUDA action used `/data/c16/locks/c16_gpu_campaign.lock`; the lock is not retained after the run.
- Source: NVIDIA Transformer Engine v2.19.0, exact source commit `5e52befd5262c06289106338c308079d6adb391f`. Isolated R19 environment: PyTorch `2.6.0+cu124`, CUDA runtime `12.4`, cuBLASLt `120405`. `te.is_fp8_available()` returned true. The source and installed wheel hashes are in `SOURCE_RUNTIME_AUTHORITY.md`.
- Input: accepted `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`, accepted R101 `TRAIN_DISCOVERY_256` token stream. A real evaluation forward-pre-hook captured the input to `model.layers.0.mlp.up_proj` and its actual BF16 weight. Input shape `[1,256,896]`, weight `[4864,896]`, GEMM M/N/K `256/4864/896`. Tensor and payload hashes are in `REAL_INPUT_RECEIPT.json`. The 9.18 MB frozen payload is on node164, not Git.

## Gate outcome

The engineering tolerance was frozen before formal operator timing from TE v2.19.0 `tests/pytorch/utils.py::quantization_tols`, E4M3: elementwise `atol=0.0675`, `rtol=0.125` relative to the same-input/weight BF16 `torch.nn.functional.linear` output. This tolerance is an engineering qualification rule, **not** an application-level quality claim and not a bound guaranteed by TE for a complete GEMM.

| Canary | Source-backed recipe | Native FP8 representation | Finite | Max absolute error | Mean absolute error | Cosine | Frozen allclose |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| Excluded initial | `DelayedScaling(E4M3, margin=0, history=8)` | yes | yes | 0.1171875 | 0.01124962 | 0.998715 | fail |
| Final bounded canary | `Float8CurrentScaling(E4M3)` | yes | yes | 0.1171875 | 0.008739947 | 0.999208 | fail |

The initial delayed-scaling canary retained forward scales of 1.0 without inference-only history advancement. It was preserved as an excluded attempt, not silently presented as a strong normal-path result. A source-supported current-scaling recipe was then frozen with the **same** numeric gate; that final bounded canary also failed. Both receipts report TE FP8 input and weight representations, including quantized input 229,376 bytes and cached weight 4,358,144 bytes, but no NSYS was run to independently identify the GEMM kernel. Do not promote the tensor metadata alone into a SASS/kernel identity claim.

Because the final numerical gate failed, D0 public-API equivalence was not admitted or timed; A0/A1 formal timing was not run. No threshold relaxation, third recipe, shape search, alternative model, custom FP8 kernel, or Blackwell FP4 proxy was attempted. The Qwen source forward emitted the existing Transformers sliding-window/SDPA warning, recorded in raw stderr; it does not alter the captured layer-0 projection identity.

## Evidence map

- `MEASUREMENT_CONTRACT.md`: final frozen current-scaling measurement contract.
- `EXCLUDED_DELAYED_SCALING_CONTRACT.md`: preserved initial source-backed recipe contract.
- `REAL_INPUT_RECEIPT.json`: model/input/hook/tensor/payload authority.
- `DELAYED_SCALING_CANARY.json` and `CURRENT_SCALING_CANARY.json`: complete numerical/native-path canary receipts.
- `SOURCE_RUNTIME_AUTHORITY.md`: source, environment, wheel and accepted-input identity.
- `RAW_INDEX.md` and `SHA256SUMS`: durable node164 raw paths and compact review-pack file hashes.
- `util/vm_tlb/awma/r19_fp8/`: executable payload capture and canary code. The canary requires an externally held GPU lock.

This review only concerns native Ada/SM89 FP8. It does not establish Blackwell FP4/TMEM behavior, a representation-readiness speedup, or a hardware mechanism.
