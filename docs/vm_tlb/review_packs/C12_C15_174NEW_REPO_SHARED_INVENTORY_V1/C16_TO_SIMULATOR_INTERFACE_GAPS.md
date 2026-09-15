# C16 formal/derived data to historical simulator gap

## Inputs observed

Modern C16 storage currently exposes formal raw/capture material, parsed `memory_access.jsonl`, binary `mref_*.bin` shards, `STATIC_MREF_MAP.tsv`, `OBJECT_MAP.json`, fingerprints, and catalog/receipt metadata under `/root/share/mnt164/huangrulin/c16_ai_workload/`. Accepted C16 launch manifests bind semantic kernel counts, trace/list/archive hashes, object maps, and a 49-bit VM configuration.

## Historical simulator contract

The Accel-Sim trace-driven path consumes a `kernelslist.g` with names ending `.traceg.xz`; the decoder and launcher expect the traceg record grammar and derive coalesced memory transactions before VM/TLB processing. The launcher also requires Core SM86 base/trace configs, a simulator binary, and a profile overlay. C12 scripts additionally bind old framework/core/binary SHAs and hard-coded `/workspace` roots.

## Exact gap (current evidence)

1. **Container/identity gap:** C12 manifests point to `/workspace/...`, Framework anchor `d64408a...`, Core `57bb71...`, and binary SHA `2351f7...`; current accepted M1–M3/M4 code uses different anchors. No compatibility proof exists.
2. **Format gap:** C16 `memory_access.jsonl`/`mref_*.bin` are not a `kernelslist.g` + `.traceg.xz` set. No repository tool was found that losslessly converts these modern records into the simulator traceg grammar.
3. **Semantic gap:** C16 records preserve active-lane addresses, semantic/object labels, and capture metadata; Accel-Sim requires instruction/kernel ordering and simulator memory-operation fields sufficient for coalescing, cache, TLB/PTW, and timing. The mapping of lane-level records to instruction IDs, warp/coalescing boundaries, memory operation size/type, and synchronization is not proven.
4. **Address/model gap:** C16 formal address scans authorize 49-bit SimVA use for accepted traces, but historical Segment registrations use modeled PA/descriptor policies. A bridge must specify SimVA/SimPA, page size, ASID/epoch, object range and contiguous Weight assumptions without rewriting raw addresses.
5. **Telemetry gap:** modern fingerprints are offline locality/footprint data, not simulator TLB/PTW/cache timing counters. Direct comparison is limited to carefully aligned address/page/cache-line locality; miss rates, walker latency, queue stalls, replacement and cycles require a simulator replay.

## Preserved vs lost if bridged

Preservable: raw address values, operation byte width where present, kernel/phase identity, object-map labels, page/cache-line footprints, and SHA-bound provenance. Potentially lost or requiring modeling: original warp coalescing, instruction timing/order, memory hierarchy queueing, PTW/cache contention, residency state, and simulator-specific semantic events. Any synthetic reconstruction must be labeled `MODELING_DECISION` and cannot upgrade C16 evidence to historical `FORMAL`.

## Round-2 bridge gates

Produce a small, schema-documented converter or prove an existing producer; bind input/output hashes; run a tiny parser smoke only; compare decoded record counts/addresses and object/page footprints; then perform one bounded compatibility replay. Do not bulk-copy C16 raw or rerun long simulations.
