# C16 Order-Model Audit

Default/order-safe state: `SET_ONLY`.

| Metric | Permitted model | Current implementation | Prohibited interpretation |
|---|---|---|---|
| Per-window unique 4KiB/64KiB VA buckets, 128B lines, sectors, modulo set projection | `SET_ONLY` | Yes | hardware TLB miss, actual page mapping, PA locality |
| Adjacent captured-window page/line set intersection and Jaccard overlap | `SET_ONLY` | Yes | global L2 MRC or shared-cache temporal reuse |
| Local revisits | `LOCAL_STREAM_ORDER` only when manifest explicitly proves it | Guarded; otherwise `NA` | inferred from CTA-group file order |
| Synthetic interleaving sensitivity | `SYNTHETIC_INTERLEAVING_PROXY` with a declared interleaving ID | Not implemented in this round | actual global GPU arrival order |

`.traceg` post-processing groups records by CTA. That file order cannot be named global L2 order. The manifest loader rejects `CTA_GROUP_FILE_ORDER`; producers must declare `SET_ONLY` unless they supply a narrower verified local stream ordering. `REUSE_AND_OVERLAP.tsv` records `SET_ONLY` even when its input rows happen to be adjacent in a file.
