# C16 First V2 Formal Ingest Review

## Decision

Accepted:

- `FIRST_V2_FORMAL_INGEST_PASS`
- producer authority: `fd2cb24a73d5bb0d5bfadde19438db9ebc2552df`
- consumer authority: `39c23ed4a2b2fde61b762aac6362c4ede7ab9879`
- two Pipeline-ACKed Qwen2.5-0.5B S2_TEXT Prefill formal runs are valid `MREF_SHARDED_COMPLETE_SET` evidence.

Independent consumer recomputation exactly matches the producer for the presently asserted closure quantities:

- Q05_ATTN: 12 executed / 17 zero, 10,752 warp records, 258,048 active address events, 1,008 4KiB buckets, 30,464 128B start-address buckets.
- Q05_GEMM: 16 executed / 125 zero, 38,912 warp records, 1,245,184 active address events, 9,728 4KiB buckets, 155,648 128B start-address buckets.

No cross-MREF temporal/global ordering or cross-shard reuse-distance claim is authorized.

## Important scope hardening before scaling

The ingest PASS closes transport, binary decoding, exact static-MREF-set coverage, executed-vs-zero classification, terminal/overflow closure and reproducibility. It does **not** yet justify every semantic field currently printed by the derived fingerprint.

### A. Access-kind audit required

The current aggregate review output reports every event as `WRITE`. This is not accepted as a scientific conclusion until it is independently joined against the hash-bound `STATIC_MREF_MAP.tsv` and the exact static instruction metadata.

Policy:

- never default an unknown access to READ or WRITE;
- derive READ / WRITE / ATOMIC only from exact static instruction evidence;
- if unresolved, emit `UNKNOWN_ACCESS_KIND`;
- add a regression ensuring known LDG and STG static rows do not collapse to the same access kind.

### B. Byte width is not represented by C16WARP1

C16WARP1 contains static index, active mask, CTA, warp and lane addresses, but not memory access width. Existing output correctly says `UNKNOWN_NOT_REPRESENTED`.

Before line/page crossing-sensitive claims are expanded, recover width from hash-bound static metadata where exact. If the static tool cannot prove width, preserve `UNKNOWN_WIDTH`; do not guess from a friendly opcode spelling without a validated parser.

Metrics based only on starting addresses must be labeled as such when width is unresolved.

### C. Object attribution currently has zero useful coverage

Both accepted targets currently classify every active address as `UNKNOWN_RUNTIME`.

This is conservative and valid, but it means the current object map is not yet useful for Weight/KV/Activation attribution.

The current object-map helper records CUDA storage addresses in its own runtime process. MREF-sharded captures are deterministic replay executions and may use a distinct CUDA virtual-address space. Therefore a process-external absolute-VA object map must not be assumed to match another replay.

For future formal shards, object/allocation metadata must be captured in the **same CUDA process / address space** as the shard or normalized to a proven stable object-relative identity.

### D. Cross-replay absolute-VA union requires proof

`MREF_SHARDED_COMPLETE_SET` replays the same exact target for different static MREFs. Unless all shards are proven to share one CUDA address space, absolute virtual addresses from different replay processes are not automatically in a common coordinate system.

Therefore, until address-space equivalence or normalization is proven:

- per-shard address/page/line footprints are FORMAL;
- exact static-MREF completeness is FORMAL;
- executed/zero classification is FORMAL;
- cross-shard absolute-VA/page/line set union is `REPLAY_UNION_DIAGNOSTIC`, not a universal whole-launch footprint claim;
- cross-shard object union is unsupported when object-relative identity is unavailable.

A future logical target may promote cross-shard union to FORMAL only through one of:

1. all shards captured inside one proven shared CUDA address space; or
2. per-shard same-process allocation/object maps plus lossless normalization to stable object/allocation-relative coordinates with recorded base alignment; or
3. an explicit repeatability experiment proving address-space layout identity for the relevant allocations and scenario, with a hash-bound contract.

## Next scientific priority

Do not return to infrastructure work. The next target is Qwen2.5-0.5B S2_TEXT Decode coverage:

- early Decode heavy-compute target;
- early Decode KV/attention-memory target;
- late Decode KV/attention-memory target;
- late heavy-compute only if runtime census shows a meaningful implementation/shape change.

The V2 MREF-sharded capture method remains the baseline. First harden address/access metadata, then expand coverage.
