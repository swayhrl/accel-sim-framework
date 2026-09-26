# Source and asset audit

Status: `PASS`.

- Accepted execution base: `9098443082d8edd4f0efa2fa8922969c0559254a`.
- Goal handoff: `aea9cc79186c23fa163b3c215d1b43eac7c6b174`; literature boundary: `082dd8b36b199e135585c0ba61cab587d6814e60`.
- Model: `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`; config SHA `18e18afcaccafade98daf13a54092927904649e1dd4eba8299ab717d5d94ff45`; safetensors SHA `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`.
- P1 target input is accepted S2 TEXT T2048 (`0ab5bfe...`); companions are accepted S2 CODE (`7acdc48f...`), accepted S2 STRUCTURED (`890eea66...`), and the explicitly labeled deterministic CODE-roll control. Target and companions were executed through decode step 16 and layer-12 Q/K/V were frozen.
- P2 input is accepted S3 TEXT T8192 (`9e127ae9...`); layer-12 decode-step1 Q and 8,192-token historical K/V were frozen. Exact tensor hashes are in `P2_INPUT_RECEIPT.json`.
- Historical P1 SplitKV/Combine anchors are Lane D V3 (`ba1b4bdb...`) and the Lane A inventory; this round's functional Q/K/V/output receipts supersede filename-only inference.
- Runtime: PyTorch 2.5.1+cu124, Transformers 4.46.3, Triton 3.1.0, driver 580.178.04, RTX4080/SM89. FlashInfer, flash-attn package, xFormers, and local Quest checkout were absent.
- `PREREGISTRATION_AMENDMENT_3.json` closes a clerical bootstrap-filename mismatch: the executed Qwen extractor is hash-bound by `INPUT_SOURCE_CLOSURE.json`; the unused Llama draft is preserved only in raw `superseded_sources/`.
- GPU work was serialized with `/data/c16/locks/c16_gpu_campaign.lock`. No model was downloaded; no Accel-Sim or NVBit full trace ran.
