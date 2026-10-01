# Three-object numerical decomposition

All three objects use the same frozen real Qwen2.5 layer0 `mlp.up_proj` input and weight, M/N/K `256/4864/896`, parent payload SHA256 `5ac9e6eb35ec2676926481d563628b80d528dac3dbdbe87bece26d21f4c54b48`. Source/runtime: TE v2.19.0 at `5e52befd5262c06289106338c308079d6adb391f`, RTX4080/SM89, PyTorch `2.6.0+cu124`, `Float8CurrentScaling(E4M3)`.

- `B0_ORIGINAL`: BF16 `torch.nn.functional.linear` on original BF16 values. Output `[1,256,4864]`, SHA256 `95e991b844cc2a1df46975e0b0ab7d996fb02a8e5e8a9688b8bb2deaeeb436f5`.
- `R0_REP_MATCHED`: TE's **actual** online FP8 input representation and cached FP8 weight representation, dequantized to FP32, then non-FP8 `torch.nn.functional.linear` with TF32 disabled. Output `[256,4864]`, SHA256 `a66d1388ba6440473d27301adcccef5cf24434eecfc2562d4038a4b8d05b6bc8`.
- `F0_TE_FP8`: TE native FP8 consumer on a public FP8 input tensor verified bit-and-scale identical to TE's online representation, using the same cached FP8 weight. BF16 output `[1,256,4864]`, SHA256 `f0d76722af0d3f67e08ea67b2abf20217035fccadbf6014c90eb5f6847878e10`. Normal online and F0 outputs are bitwise equal.

TE current-scaling input FP8 data SHA256 is `79c754c1ec58ac3e5338e3bab28887a56803d0139394fe5a93c35df74e33ee15` (229,376 bytes), inverse-scale SHA256 `e40242473eecf057b7426f890b25b6645e7c8d6f570596591ec2b150598c8734` (value ≈0.0273437481). Cached FP8 weight data SHA256 is `bac0aac613572052c949f3ec9719ce95520185233c0c2253a82af0181a8457dd` (4,358,144 bytes), inverse-scale SHA256 `a25c716f62dc84bdbc084a46fe4c52fe1e91ef94a69bb251850776e9d2ba66ed` (value ≈0.000623430533). Public prequantization reproduces TE's online input bytes and scale exactly. The weight workspace bytes, scale and device pointer remain unchanged across the canary.

| Comparison | Purpose | Max abs | Mean abs | RMSE | Cosine | p99 abs | E4M3 allclose |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| F0 vs R0 | FP8 consumer-compute gate | 0.01669884 | 0.00030984 | 0.00049033 | 0.99999845 | 0.00179137 | **pass** |
| R0 vs B0 | Representation distortion diagnostic | 0.11851597 | 0.00874763 | 0.01114098 | 0.99920928 | 0.03007996 | fail (not a gate) |
| F0 vs B0 | Historical V1-style diagnostic | 0.1171875 | 0.00873995 | 0.01115072 | 0.99920779 | 0.03027344 | **fail; V1 preserved** |

All values are finite. The only R19F1 pass/fail numerical gate is F0 versus R0 using TE v2.19 E4M3 `atol=0.0675, rtol=0.125`. TE's quantized-GEMM tests in `tests/pytorch/test_fusible_ops.py::make_reference_and_test_tensors` copy represented/dequantized test values to the reference before comparing. These are engineering numerical checks of one linear layer, not deployment accuracy. Full unrounded values are in the two TSVs and `REPRESENTATION_RECEIPT.json`; complete tensors and quantized data are frozen in node164 `raw/NUMERICAL_OBJECTS.pt`.
