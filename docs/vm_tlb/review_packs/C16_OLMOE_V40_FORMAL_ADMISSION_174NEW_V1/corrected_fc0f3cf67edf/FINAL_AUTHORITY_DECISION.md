# OLMoE V40 node164 authority decision

`PASS ¡ª IMMUTABLY_ADMITTED_AND_ACKED`

- RUN_ID: `C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf`
- manifest SHA256: `8f3e5e338166a2ebc4da6b9a55986980d31227f3d0e383ca5a1f24d0d924f31b`
- transport receipt SHA256: `0b4a21b81c157d3b034d688b6f1eda7af39de25be1e285d4aba04b5ad752d2c0`
- raw selector SHA256: `d70035debd62f0821f7b4b0c802ecdd3ca101b7213eafb591b3cc56438a271eb`
- receiver/producer canonical V1 SHA256: `cb20c01619acf563de69776a7a098b21c31c6ce6d836ea0bc0beab9fe42c979b`
- independent recompute/delta: PASS; 243 = 129 executed + 114 proven-zero + 0 failed;
  132096 C16WARP1 warp records; 4196352 active-lane events.
- immutable raw: `/root/share/mnt164/huangrulin/c16_ai_workload/raw/<RUN_ID>`
- catalog entry SHA256: `676422708f865c6b3287998dcde3dd126a469e83d3245bcf00fe11d07b9c1637`
- admission receipt SHA256: `33646fd106ea3773aca68d62d3fb0d24f32f3598aa711722e38e5b54cd9f5c81`
- positive ACK SHA256: `9c4d08a960f53acece00dbb3143cba460c22bc638ff4a879833c0e4460b98e39`

Scientific scope is **natural expert58 `down_proj`, actual-JIT variant A
conditioned**. Variant B remains unformalized. This does not claim OLMoE
implementation-variant invariance.

## Third-lineage handoff

The descriptive next consumer set is:

1. Qwen3-30B natural expert21 `down_proj`.
2. DeepSeek-V2-Lite natural expert4 `down_proj`.
3. OLMoE natural expert58 `down_proj`, actual-JIT variant A conditioned.

The permitted conclusion language is `three-independent-lineage MoE-family
pattern`. It is not a matched-input causal study and must not be described as a
`universal MoE law`.
