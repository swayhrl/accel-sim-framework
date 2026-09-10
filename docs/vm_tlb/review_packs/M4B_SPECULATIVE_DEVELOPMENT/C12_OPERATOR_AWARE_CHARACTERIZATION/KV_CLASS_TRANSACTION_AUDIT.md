# FFN / Embedding KV-class transaction audit

## Question and scope

This read-only audit addresses an apparent conjunction in Decode1 F0:
operator classes determined by direct `weight_layout` parameter-range evidence
also have `DATA_KV_CACHE` cache transactions. It does **not** assume that the
operator class semantically consumes KV Cache.

`KV_CLASS_TRANSACTION_AUDIT.tsv` is the audit record. Its trace fields are
exact all-lane references from the same compute trace. Its cache fields are
exact `m4c_telemetry*` rows with `KERNEL` scope from the same raw-log marker.
`FIXED_WINDOW_PARTIAL` rows are excluded.

## Observed same-kernel conjunctions

| ROI / direct class | Same kernels with direct Weight + KV runtime-range trace refs | Trace Weight / KV lane refs | KERNEL L2 KV transactions |
| --- | ---: | ---: | ---: |
| Prefill FFN / Embedding-Output | 0 / 0 | 0 / 0 | 0 / 0 |
| Decode1 FFN | 21 of 48 | 11,010,048 / 1,896,448 | 142,902 (120,817 HIT, 19,913 MISS, 2,172 reservation fail) |
| Decode1 Embedding-Output | 1 of 2 | 32,833,536 / 7,695,360 | 1,057,895 (933,824 HIT, 67,068 MISS, 57,003 reservation fail) |

For Decode1, the class-level and same-kernel L1D/L2 KV-transaction totals are
equal in the TSV. Thus the reported KV-class transactions occur in markers
whose **same trace** also intersects the direct Weight range used for the
FFN/Embedding classification. The 21 FFN markers have generic
`CUTLASS_GEMM` symbols; the Embedding/Output marker has a generic
`AMPERE_GEMM` symbol. Neither embedded symbol gives direct fusion evidence.

## Runtime-range/lifetime boundary

Decode1's frozen object contract retains 64 KV events: 32 Prefill step-0
`CREATED` intervals and 32 Decode step-1 `REPLACED` intervals. Their event
bytes sum to 8,454,144, but their union is 5,259,264 bytes in five spans;
3,194,880 bytes overlap. All selected events have `end_phase=UNKNOWN_ACTIVE`.
Consequently, the exact classification is a match to the selected **union of
runtime ranges**, not a per-memory-instruction tensor-lifetime or logical
model-tensor proof.

## Allowed conclusion

It is correct to report: “KV-class cache transactions and KV-runtime-range
trace references were observed in kernels classified by direct FFN or
Embedding/Output Weight access.” It is not supported to report: “FFN directly
uses KV Cache,” “Embedding/Output directly uses KV Cache,” or “these kernels
are fused with attention.” The current evidence cannot distinguish logical
cross-object computation from the retained KV range/lifetime accounting; that
semantic causal question remains unresolved.
