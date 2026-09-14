# C16 RTX4080 U4-U9 R3 execution report

Status: `STOP_U5_MISSING_FROZEN_INPUT_BINDING`.

- Execution branch: `hrl/c16-4080-u4-u9-r3` from R2 `57b42ebbf54e0750aed96aea06ab42e6c63507ae`.
- U4: `U4_LOCAL_ASSET_EXACT_CLOSURE_PASS`; importer receipt `/data/c16/results/C16_U4_IMPORT_RETRY_20260914T123950Z.json`, SHA256 `5b1aed870cd03d50a0da5f6721ab639d56ca0f3a1c3782a9fed9cf8e3dc84a3b`.
- Promotion: `/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08` with six exact payloads.
- U5: blocked. The required frozen S0/B1/T128/Decode4/TEXT input/token receipt and derived token IDs are absent locally; their historical hashes are known but payloads are unavailable.
- U6/U7/U9: not executed because U5 cannot run without substituting/re-tokenizing the frozen input.
- U8.5: remains PASS from reviewed R1 evidence.
- Root required: `NO`.

Required external artifact: the small frozen input/token binding package containing the payload whose SHA256 values are `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208`, `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd`, `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7`, and `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`.

Review entry: `docs/vm_tlb/review_packs/C16_4080_U4_U9_R3/README.md`.

`NOT_READY`.
