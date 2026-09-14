# Llama trace-scope audit

The two analyzed rows are individual selected `LDG.E.U16` PCs in two old M4A
full-tracer files.  They are not C16 formal inputs.  The prefill input is
`B8/T64/TP4`; the decode input is `B8/T64/TP4` at Decode1.  C16's intended S0
is `B1/T128/Decode4`, so neither identity nor control is equivalent.

| Claim | Status | Reason |
|---|---|---|
| Parser/address-analysis validation | SUFFICIENT | Real compressed TRACEG records exercise active masks, base-stride address encoding, width, opcode-derived GLOBAL space, and headers. |
| `indexSelect` local-address case study | PARTIAL | Two real selected PCs are SHA-closed, but cover different phases, kernels, and an old B8/T64/TP4 execution. |
| Llama prefill-vs-decode behavior for these targets | PARTIAL | The selected streams can be compared structurally, but phases use different target kernels and only Decode1 exists. |
| Whole-Llama TLB characterization | INSUFFICIENT | One selected PC per phase is neither ROI-wide nor representative-kernel complete; observed VA buckets are not TLB misses. |
| Whole-Llama cache characterization | INSUFFICIENT | Scope excludes almost all memory instructions and TRACEG ordering does not establish global L2 order/reuse. |
| Formal Segmentation/TLB workload evidence | INSUFFICIENT | No C16 admission, no controlled C16 S0 row, no receipt-bound object map, and insufficient trace scope. |

Captured scope is exactly the selected static PCs `0x0660` in an
`indexSelectLargeIndex` prefill kernel and `0x2aa0` in an
`indexSelectSmallIndex` Decode1 kernel.  The raw containers have much wider
kernel traces, but no claim here consumes their other instructions.  Operators
outside those two PCs, the rest of the kernels, Decode2--4, C16 B1/T128, and
any formal runtime object attribution are not captured by this analysis.

The prefill/decode cross-capture overlap in `CROSS_CAPTURE_OVERLAP.tsv` is
zero at exact-address, 128B-line, 4KiB, 64KiB, and 2MiB VA buckets.  This is a
between-target comparison, not decode-step reuse; it must not be generalized
to Llama inference.
