# C16 translation headroom status

Status: `TRANSLATION_TIME_HEADROOM_UNKNOWN`.

The existing C16WARP1 shards provide recorded lane addresses and same-process tensor address contexts. The producer source establishes a 40-byte `C16WARP1` header and 280-byte warp record. `c16_translation_proxy.py` checks magic, record count, static index, context mapping and source hashes, then computes virtual page IDs at 4 KB, 64 KB and 2 MB. The three MoE runs have mapped expert weight addresses. Qwen2.5 AWQ has nonzero recorded addresses, but none of its 43 shards maps those nonzero addresses into the accompanying object ranges; its row is `UNMAPPED_OBJECT_VA_PROXY`.

These are recorded numeric runtime VA/mref addresses, treated as a virtual-page proxy. The project SimVA contract does not prove the exact NVIDIA internal VA stage. Page IDs here are not physical frames. No page table, mapping-size, TLB, MSHR, page-walk, PTE or translation stall timing is observed in these captures. The selected files are single static-memory-instruction shards from one isolated projection invocation, not a whole decode. Their per-shard record order does not reconstruct interleaving with other static instructions, kernels, experts or tokens.

| Candidate oracle | Legitimate C16 input now | Result |
| --- | --- | --- |
| Translation-access fraction of elapsed time | No accepted C16 TLB/page-walk timing or translation-caused blocked time tied to this decode | `UNKNOWN` |
| Translation-zero whole-decode ceiling | Requires a paired, causally isolated timing authority for translation versus data service | `UNKNOWN` |
| Perfect weight segment | The Segmentation paper supplies a simulated LLM result, but current C16 physical contiguity and translation time are unknown | `UNKNOWN` |
| Perfect page-size/reach | The 4 KB/64 KB/2 MB rows only repartition the same VA stream; actual mappings, allocation cost and TLB response are unknown | `UNKNOWN` |
| Perfect page walk throughput | No C16 PTW queue/active-walker timeline | `UNKNOWN` |

No page count is multiplied by a constant page-walk latency. No literature IPC is inherited as a C16 speedup. Existing C16 NCU memory traffic and stalls cannot be attributed uniquely to translation. AWMA translation experiments are method references only and are excluded from this Goal's workload evidence.

The current mapped-weight shard shows a concrete line/page distinction. At 64 KB, Q30 has 48 unique pages and 86.67 warp-page touches per page; DeepSeek has 88 and 48.36; OLMOE has 64 and 16.00. At 128 B, the corresponding warp-line touches per line are 2, 2 and 1. This supports local page reuse even where line reuse is limited. It does not establish TLB hits, PTW pressure or elapsed-time benefit. The objects have different byte sizes and executed-shard coverage, so cross-model page counts are not locality rankings.

No optional 109 capture contract was issued. The candidate qualification gates fail before a time oracle: MoE inter-expert page-set transitions are not captured, and single-tensor weight streaming has no demonstrated translation-specific stall distinct from data service. A future separately authorized study could ask only for translation-caused blocked time and TLB/PTW service attribution on a frozen current C16 workload after a same-VA multi-expert or weight/KV phenomenon is established; this statement is not an execution request.
