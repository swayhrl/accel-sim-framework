# Scientific interpretation

## Result boundary

The exact numerical results are in `FINAL_DECISION.json`, `ROLE_GEOMETRY.tsv`, and `PER_SHARD_GEOMETRY.tsv`. The analysis characterizes dynamic warp-request geometry inside each accepted shard only.

## Main result

The old active-lane event split remains about half weight and half input in all three anchors, but it does **not** imply the same request geometry.

| lineage / role | lane-event share | start or byte multiplicity | sector-proxy share | within-role sector fill |
|---|---:|---:|---:|---:|
| Q30 input | 49.9675% | 1.0 | 49.9675% | 6.25% |
| Q30 weight | 49.9675% | 1.0 | 49.9675% | 6.25% |
| DeepSeek input | 49.9823% | 2.0 | 33.2075% | 100% |
| DeepSeek weight | 49.9823% | 1.0 | 66.4151% | 100% |
| OLMoE input | 49.9756% | 2.0 | 33.1607% | 100% |
| OLMoE weight | 49.9756% | 1.0 | 66.3212% | 100% |

For Q30, each full-warp weight or input record has 32 distinct 2 B starts and covers 32 sectors: this is dispersed, one-small-access-per-sector geometry, not broadcast. Its overall `L/U` is 1.0 and `U/C32` is 0.0625. The 2,048 all-same-start records are single-active-lane output stores and are not multi-lane broadcasts.

For DeepSeek and OLMoE, each input record has 32 active lanes but only 16 distinct U16 starts (`L/U=2`), whose union fills one sector. Each weight record has 32 distinct U16 starts (`L/U=1`) and fills two sectors. Consequently, removing within-record duplicated bytes and counting covered sectors changes weight/input from about 50/50 lane events to about 66/33 sector proxy. Overall `L/U` is 1.33318 for DeepSeek and 1.33312 for OLMoE; overall `U/C32` is 0.99670 and 0.99547 respectively. No mixed-role records, shared-role sectors, or interval/object-boundary ambiguities were observed.

This supports `ROLE_EVENT_SHARE_DIFFERS_FROM_SECTOR_PROXY_SHARE` for DeepSeek and OLMoE, while Q30 materially differs. The repeated input addresses are a familiar two-lane broadcast/coalescing pattern, so the scoped closure is also `FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY`.

## Reading the metrics

Start-address multiplicity describes repeated-address structure. `L/U` distinguishes logical lane bytes from the within-record byte union. `U/C32` describes fill of the covered 32 B sectors. Neither `C32` nor record count is a measured cache request count or DRAM-byte total.

## Implementation and causality limits

All three anchors use the cuBLAS gemvx family; DeepSeek and OLMoE are bound to template parameter 6 while Q30 is template parameter 7. Therefore shared geometry is not implementation-independent MoE evidence. No cache hit rate, reuse distance, SM placement, bottleneck, or universal MoE behavior is inferred.

## Next experiment

No native experiment is warranted by this screen, and no follow-up question is retained. The observed duplication/coalescing is familiar and does not itself justify a new cache or broadcast mechanism.
