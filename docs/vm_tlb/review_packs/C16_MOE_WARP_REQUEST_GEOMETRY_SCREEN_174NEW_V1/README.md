# C16 MoE warp request geometry screen / Lane 8

Status: `WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED`. CPU-only consumer; no GPU and no GPU lock.

## Contract and authority

The consumer starts from accepted three-lineage commit `08536be9940590be101c7f5bac2117ba82056db5` and coordination commit `17dd9482245d8bdac8e89ff53be5a567048016f1`. It verifies the exact Q30, DeepSeek, and OLMoE RUN_IDs, immutable run manifest, positive transfer ACK, catalog binding, per-shard trace hashes, C16WARP1 header/count closure, and historical selected/executed/zero/record/lane totals.

All 243 selected paths per lineage are ordinary global loads/stores. Static SASS provides widths for the full scoped set: U16 paths are 2 B and scalar `LDG.E` paths are 4 B. There are no atomic, reduction, or LDGSTS paths in the selected set. Full access intervals, not only starting addresses, determine G1 roles.

## Method

Each shard is opened once and streamed record-by-record. G0 counts active lanes and distinct starting addresses. G1 computes logical lane bytes, the within-record interval union, distinct covered 32 B sectors, and a 32 B sector-coverage proxy. `C32` is not an observed L1/L2 request count or DRAM traffic. Quantiles use nearest-rank: sorted_values[ceil(p*n)-1]; min/max exact.

`ROLE_GEOMETRY.tsv` gives lineage/role totals and old event shares beside qualified logical/unique/sector-proxy shares. `PER_SHARD_GEOMETRY.tsv` gives path/role totals plus per-record distributions. Role sector values are non-additive when roles share a sector.

## Result

Q30 weight and input each retain 49.9675% of the sector proxy: their full-warp records have 32 distinct U16 starts dispersed over 32 sectors (`L/U=1`, `U/C32=0.0625`). DeepSeek and OLMoE input records instead duplicate 16 starts across 32 lanes and fill one sector (`L/U=2`), while weight records have 32 distinct starts and fill two sectors (`L/U=1`). Their sector-proxy shares therefore change from about 50/50 lane events to 66.4151%/33.2075% and 66.3212%/33.1607% weight/input respectively (small output remainder).

Decision labels: `WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED`, `ROLE_EVENT_SHARE_DIFFERS_FROM_SECTOR_PROXY_SHARE`, and `FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY`. This is a negative closure for a new native experiment or mechanism.

## Scope limits

No cross-shard chronology or VA union is formed. G2 is omitted as `G2_NOT_AUTHORIZED_BY_AVAILABLE_SCOPE` because the payload does not carry explicit process/launch identity. These three independent model lineages remain coupled to the cuBLAS gemvx implementation family. High lane-byte multiplicity or low sector fill alone does not establish avoidable DRAM traffic or authorize a cache/broadcast mechanism.
