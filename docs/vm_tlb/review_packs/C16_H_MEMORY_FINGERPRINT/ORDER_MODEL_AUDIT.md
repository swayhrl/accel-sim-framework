# C16 Order-Model Audit

Default/order-safe state: `SET_ONLY`.

| Metric | Permitted model | Current implementation | Prohibited interpretation |
|---|---|---|---|
| Per-window unique 4KiB/64KiB VA buckets, 128B lines, sectors, modulo set projection | `SET_ONLY` | Yes | hardware TLB miss, actual page mapping, PA locality |
| Adjacent captured-window page/line set intersection and Jaccard overlap | `SET_ONLY` | Yes | global L2 MRC or shared-cache temporal reuse |
| Local revisits | Not admitted in current `c16-trace-manifest-v1` | Always `NA` | inferred from CTA-group file order or a manifest assertion |
| Synthetic interleaving sensitivity | `SYNTHETIC_INTERLEAVING_PROXY` with a declared interleaving ID | Not implemented in this round | actual global GPU arrival order |

`.traceg` post-processing groups records by CTA. That file order cannot be named global L2 order or local chronological order. The manifest loader accepts only `SET_ONLY` in this schema and explicitly rejects `TRACEG + LOCAL_STREAM_ORDER`, even with a forged `order_evidence_receipt`. A future local-order schema must define a supported producer format, an immutable evidence receipt plus SHA, and a separate admission test. `REUSE_AND_OVERLAP.tsv` records `SET_ONLY` even when its input rows happen to be adjacent in a file.
