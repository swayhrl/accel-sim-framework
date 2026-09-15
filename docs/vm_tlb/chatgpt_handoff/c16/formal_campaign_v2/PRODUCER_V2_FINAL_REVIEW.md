# C16 Producer V2 Final Review

## Decision

`FORMAL_CAMPAIGN_V2_PASS_WITH_SCOPED_EVIDENCE` is accepted for downstream analysis.

Authoritative producer commit:

`fd2cb24a73d5bb0d5bfadde19438db9ebc2552df`

Accepted formal runs:

1. `C16R_qwen25-05b_s2-text_prefill_nvbit-warp-mref-shard_attention-core-v2_20260915T013537Z_820eda91c057`
   - target: Q05_ATTN
   - evidence: `MREF_SHARDED_COMPLETE_SET`
   - raw manifest SHA256: `40d80a3b7fb46d398e4b3ff34878d813ea66a1830ffa9e1c95b5c805b516cbf3`
   - ACK SHA256: `63a223568a6a7de70cafab33ce49a2ab886f2c858c515f721d7899f0f8461a6b`
   - static MREF set SHA256: `9f82df6f77893a4f9c5e3c8d1d1ee44a63c1421d5676cef7dab21f562eff7857`
   - static MREF count: 29
   - final producer summary: 12 executed shards, 17 `ZERO_EXECUTION_PROVEN` shards, 10,752 warp records, overflow total 0.

2. `C16R_qwen25-05b_s2-text_prefill_nvbit-warp-mref-shard_gemm-heavy-v2_20260915T015202Z_1bf75d41aa29`
   - target: Q05_GEMM
   - evidence: `MREF_SHARDED_COMPLETE_SET`
   - raw manifest SHA256: `8b853b8633d0bfcd086c490572386bca6af5e6b3a7c7466050fbeed44f5889ba`
   - ACK SHA256: `18efd3346c9dfc879da673a9cdf8ac5943cd25f382e2b335309ce687a4d442cc`
   - static MREF set SHA256: `5a3958e94b8161b4ec67a406baf60641e8284664cdb9a6cb930ed4ed4fe93264`
   - static MREF count: 141
   - final producer summary: 16 executed shards, 125 `ZERO_EXECUTION_PROVEN` shards, 38,912 warp records, overflow total 0.

The final committed review pack is authoritative over intermediate console/log observations. In particular, an earlier in-progress attention count of `13 x 896` must not override the final pack; downstream analysis must independently recompute the admitted raw and use the final hash-bound manifests as authority.

## Binary format

Frozen producer format: `C16WARP1`.

- Header: `<8sIIQQQ>`
- Record: fixed 280-byte `<6I32Q>`
- Fields: static index, active mask, CTA x/y/z, warp, 32 absolute lane addresses.
- Producer decoder path: `util/vm_tlb/c16/formal_campaign/v2nvbit/decode_warp_shard.py`
- Producer decoder SHA256: `d0bfbbba43358ee92231d039fd64bda341a92ff699866afec8a006947e936185`

Downstream must implement/verify this format independently and fail closed on magic/version/length/header inconsistencies.

## Scientific scope

Accepted analyses:

- per-MREF footprint;
- union unique addresses/pages/cache lines;
- read/write/width facts when supported by static map;
- object attribution;
- set-based footprint comparisons between accepted logical targets.

Explicitly unsupported:

- cross-MREF-group temporal order;
- concatenated global stream claims;
- whole-kernel/global reuse distance;
- global hardware execution order.

`ZERO_EXECUTION_PROVEN` is valid only when the shard belongs to the frozen static MREF set and has exact-replay identity plus terminal complete plus zero callback/records plus zero overflow/drop. It is not equivalent to a missing shard.

## Deferred controls

- AWQ fused extension: source acquisition was blocked by network/TLS; current unfused AutoAWQ remains control-only.
- raw Qwen2.5-7B S2: allocator/lazy/last-logit recovery still results in true-capacity OOM. No CPU offload/configuration relaxation was used.

Neither defer invalidates the two accepted Qwen0 formal runs.
