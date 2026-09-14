# Route A limitation audit

`LLAMA_S0_FORMAL_V1` formally admits one selected instruction per phase role.
Its selected-target facts are:

| Phase / selected function | Requests | Lane addresses | Unique GPU VAs | Unique 128B lines | 4KiB VA buckets | 2MiB VA buckets |
|---|---:|---:|---:|---:|---:|---:|
| Prefill `indexSelectLargeIndex` static index 101 | 8,192 | 262,144 | 71,680 | 1,120 | 35 | 19 |
| Decode2 `indexSelectSmallIndex` static index 17 | 64 | 2,048 | 1 | 1 | 1 | 1 |
| Decode3 `indexSelectSmallIndex` static index 17 | 64 | 2,048 | 1 | 1 | 1 | 1 |
| Decode4 `indexSelectSmallIndex` static index 17 | 64 | 2,048 | 1 | 1 | 1 | 1 |

The Decode SmallIndex selected PC is a warp-uniform repeated-address stream:
each selected request has 32 active lanes but its 2,048 lane-address rows
collapse to one exact observed VA per decode step. This is a selected-
instruction behavior. It cannot represent Decode's complete memory working
set, its other loads/stores/atomics, physical mappings, TLB behavior, cache
misses, or cache reuse.

Route A also omits the two other GLOBAL+MREF instructions in each already
mapped selected function and all memory instructions in every other kernel.
Its `SET_ONLY` ordering does not establish a global L2 timeline. Route B adds
complete GLOBAL+MREF static coverage **within** selected representative kernels;
Route C is needed to audit whether those kernels represent the whole phase.
