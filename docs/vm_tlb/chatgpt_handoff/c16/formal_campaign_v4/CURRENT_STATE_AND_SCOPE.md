# C16 V4 — Current state and scope

## Accepted producer evidence

Producer authority for Qwen0 Decode:

- branch: `hrl/c16-qwen0-decode-formal-109-v3`
- commit: `20ee2e015d3b3eb72b67d03657242887932a925d`
- decision: `QWEN0_DECODE_FORMAL_EXPANSION_PASS`

Accepted Decode targets:

1. `Q05_DECODE_EARLY_HEAVY`
2. `Q05_DECODE_EARLY_KV_ATTN`
3. `Q05_DECODE_LATE_KV_ATTN`

`Q05_DECODE_LATE_HEAVY` is `CONTROL_REDUNDANT` under the producer's frozen implementation/grid-family evidence.

All three accepted targets are Pipeline V1 ACKed and admitted on node164.

Static-set sizes:

- Early Heavy: 16 static GLOBAL-MREF rows
- Early KV/Attention: 41 rows
- Late KV/Attention: 41 rows

Producer quickcheck:

- Early Heavy: 3 executed / 13 zero; 33 active lane-address events; overflow 0
- Early KV/Attention: 3 executed / 38 zero; 4158 active lane-address events; overflow 0
- Late KV/Attention: 3 executed / 38 zero; 4158 active lane-address events; overflow 0

Early/late KV/Attention use the same static-map/static-set identity and the same function/grid family, at distinct function-local occurrences. They are separate replay/address-space contexts and must not be merged as one absolute-VA stream.

## Accepted analysis hardening

Analysis authority:

- branch: `hrl/c16-v2-analysis-hardening-174new-v1`
- commit: `670a681f96adc3be463b2f8d9bc4a8c1c08fe7b8`
- decision: `C16_V2_ANALYSIS_HARDENING_PASS`

Frozen rules:

- access kind comes only from the hash-bound static row (`is_load` / `is_store` / atomic evidence);
- width is exact only when a validated explicit width-bearing SASS mnemonic proves it;
- bare `LDG.E` / `STG.E` remain `WIDTH_UNKNOWN`;
- each MREF shard is a separate replay unless same-process evidence proves otherwise;
- cross-shard absolute-VA/page/line union is diagnostic only;
- cross-shard order and cross-shard reuse distance are unsupported;
- object attribution may be performed only against the object ranges captured in the same CUDA address-space context as that shard.

## Decode V3 improvement

Decode V3 adds one `C16_ADDRESS_CONTEXT_V1` per MREF replay. The context binds:

- target/static index/function occurrence;
- process PID and generated address-space ID;
- GPU UUID;
- exact trace SHA;
- exact static-map SHA;
- object-map SHA;
- same-process object ranges.

This permits per-shard object attribution and, where semantic object identity is independently matched, object-relative normalization. It does **not** make different MREF replays share an absolute CUDA VA space.

## Scientific scope correction

`MREF_SHARDED_COMPLETE_SET` means the complete set of **NVBit-recognized direct GLOBAL MREF static rows** for the selected exact function/occurrence. It must not silently be generalized to every possible physical global-memory path in the kernel.

Before wider cross-model use, audit full target SASS/instruction metadata for global-memory semantics that may bypass the current `GLOBAL + MREF` selector, including asynchronous/global-to-shared or other special memory paths if present on this code object. The audit must classify coverage, not assume it.

Existing V2/V3 evidence remains valid for its frozen direct-GLOBAL-MREF scope even if another path is later found.

## Nonblocking inline fixes

Do not open a dedicated repair round for these:

1. Generic C16WARP1 ingest must inherit the hardening rule: cross-replay VA union diagnostic only and no cross-process object join.
2. Derived receipts should be self-contained: bind output path, size, SHA256, parser commit/CLI/config and creation timestamp.
3. Decode producer `UNKNOWN_WIDTH` metadata is advisory only; 174-new must re-derive width using the accepted hardening decoder.

These are to be folded into the next substantive analysis work.

## Current priority

Remain on capture/characterization mainline.

1. Consolidate and independently analyze the three admitted Decode targets on 174-new.
2. Qualify direct-GLOBAL-MREF coverage against special memory paths before broad replication.
3. Expand useful scenario axes for Qwen0 only when census shows materially different implementation/memory behavior.
4. Recover true fused AWQ (`awq_ext`) and begin cross-model formal capture.
5. Give raw Qwen2.5-7B one final exact-configuration admission attempt only after non-scientific GPU memory consumers are removed; no CPU layer/KV offload and no scientific configuration substitution.
6. Qwen3-8B and DeepSeek-V2-Lite remain blocked on prospective input authority and are not part of this wave.
