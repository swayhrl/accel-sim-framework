# C16 H Retry570 NVBit 1.8 local readiness

Status: `C16_H_RETRY570_NVBIT18_LOCAL_READINESS_READY`.

Consumed G publication: `99c868ddbfcd90559129fc00f7d02e00df537e51`
(`C16-G: qualify Retry570 NVBit 1.8 path`).  Its published transfer receipt
is `PASS_REMOTE_TO_LOCAL_TREE_SHA256_CLOSED`, with matching remote/local tree
SHA-256 `afb7fcb2145029d16abaca29104207b5a4545a74908682fb8040fdd6a79fd0ef`.

## NVBit 1.8 parser qualification

Every value in `NVBIT18_PARSER_QUALIFICATION_RESULT.json` is labelled
`NVBIT18_PARSER_QUALIFICATION_FIXTURE_ONLY` and has
`scientific_model_evidence=false`.  It consumes the remote/local SHA-closed
elementwise (2) and GEMM (3) C16 tracer `.trace.xz` files, their
`kernelslist`/`stats` catalogs, and the published NVBit/tool identity.  It
passes all 499,488 catalog-reported instruction records.

The parser now has an explicit `RAW_CTA_NVBIT18` format gate: the CTA-prefixed
record layout is decoded only after a trace header attests `nvbit version =
1.8` and an Accel-Sim tracer version.  Historical `RAW_CTA` and existing
TRACEG behavior remain unchanged and are regression-tested.

The qualification covers active masks, 4/8/16-byte accesses, read/write and
atomic classification, GLOBAL/LOCAL/SHARED/UNKNOWN_SPACE semantics, structural
4 KiB/64 KiB/128 B buckets, and CTA coordinates.  The physical Retry570
fixture contains GLOBAL and SHARED events; compact semantic parser fixtures
exercise LOCAL, UNKNOWN_SPACE, and atomic paths.  TRACEG remains
`SET_ONLY`, and every modulo line-set projection is explicitly `PROXY`, never
a measured hardware set mapping.

## Future real-model staging

`c16_nvbit_raw_ingest.py` implements the raw lifecycle outside Git:

```text
remote size/SHA -> rsync .partial -> local size/SHA -> immutable receipt
-> optional zstd/xz SHA closure -> parser scratch -> compact-derived receipt
```

It has no remote delete operation, retains verified local raw even after
compression, quarantines failed/partial material, and records only identity,
paths, sizes, hashes, tool/run/target identity in receipts.

`c16_nvbit_storage_estimate.py` emits `NVBIT_STORAGE_ESTIMATE.json` only for
an admitted real-model canary.  It includes raw/compressed bytes, ratio,
counts, duration, bytes/record, local free space before/after, B4/B8/B12/B24/
B48 storage-only projections, and a raw+compressed+scratch-aware safe budget.
Fixture schema tests are allowed but have null campaign projections and cannot
estimate an LLM campaign.

`REAL_MODEL_TRACE_INPUT_CONTRACT.md` and `real_model_trace_contract.py` reject
anything missing exact G commit, exact model/package/scenario identity, NVBit
1.8 tool SHA, C16 tracer SHA, raw path/size/SHA, terminal `COMPLETE`,
remote/local SHA closure, or a non-fixture real-model declaration.  The first
accepted Llama trace creates only `REAL_TRACE_PIPELINE_CANARY`; cross-model
scientific conclusions are explicitly forbidden.

Remaining blocker: `REAL_MODEL_TRACE`.
