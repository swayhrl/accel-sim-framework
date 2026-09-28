# C16 low-bit dataflow hypothesis screen V1

Status: `ONE_BOUNDED_OPPORTUNITY`. This is a read-only screen. No GPU run, requantization, backend installation, simulator build, trace recapture, full timing, or Lane 4 result was used.

## Authority and execution identity

The clean timing authority is consumer `59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`, which resolves to producer `8988d6108ff8bdca180a14cec2fe769df45b099f1`. Semantic NCU V2 authority is consumer `cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`, which resolves to producer `8d1f62229cae15199793ba5569327cf1e83596f3`.

The executed AWQ path is `WQLinear_GEMM` in `/data/c16/env/c16-awq-v6`. V6/V7 receipts bind its `awq_ext` binary SHA to `AutoAWQ_kernels@c7b0e88c327694c715b0a758d9ce8fd414a1fa21`; this exact historical source is used below. No current upstream kernel was substituted. V2 preserved the same environment path but did not re-hash the `.so`, so source continuity after V7 is a bounded contractual inference, not a new binary-identity measurement.

## What the current path actually does

For the four clean points, the accepted path class is `GEMM_QUANTIZED`. The exact source implements a `16x128x32` CTA tile with two warps. It loads FP16 activation tiles global -> shared -> `ldmatrix` registers. Packed qweight and packed zero are unpacked in registers; affine scale/zero math is performed in half2 registers; the resulting FP16 weights are written to shared and loaded again with transposed `ldmatrix` before MMA.

For V2 up_proj M1 and M256, grid algebra and the source allocation prove `split_k_iters=8`. Eight FP16 partial planes are written to global scratch and a separate PyTorch `sum(0)` kernel produces the final output. The same split is dynamically observed for accepted ancestor down_proj M1 on the same runtime. Down_proj M256 has source/path support but no allowed dynamic launch row.

The source is single-buffered: there is one A shared tile and one B shared tile, with barriers around each K32 load/dequantize/consume step. No `cp.async`, double buffering, or source-level overlap is present. Static shared allocation is 9,984 B/CTA. Actual registers/thread, spills, occupancy, stall reasons, shared-bank conflicts, and kernel duration are absent.

## Candidate screen

| Candidate | Existing support | Screen result | Reason |
|---|---|---|---|
| Activation repeated supply | Exact source proves that each output-N CTA reloads A. Source-level requests are 1,060,864 B at M1 and 271,581,184 B at M256 for both transpose shapes. | `NOT_RETAINED_NEEDS_TENSOR_ATTRIBUTED_DIAGNOSTIC` | The V2 counters are whole-kernel totals and cannot assign L1/L2/DRAM bytes to A. Repeated source requests may hit cache, and no kernel-time or stall counter establishes criticality. MARLIN already treats this supply problem directly. |
| Dequantization/layout conversion | Exact source proves qweight unpack + affine math in registers, followed by dequantized-weight shared write and `ldmatrix` read. | `COVERED_BY_EXISTING_KERNEL_TECHNIQUE` | The current implementation has not eliminated the path, but QUICK already addresses this exact class with offline interleaving. C16 has no shared-bank/duration evidence and a re-layout implementation would be a larger, non-novel engineering port rather than the minimal next diagnostic. |
| Fixed split-K and global reduction | Dynamic launches prove split-K=8 and GEMM+reduction for up_proj M1/M256; source proves 8-plane FP16 scratch. At up_proj M256, the reduction kernel contributes 116,391,936 L1 bytes, 107,066,944 L2 bytes, and 76,003,328 DRAM bytes: 8.25%, 8.46%, and 42.65% of the semantic-range totals. | `RETAIN_H1_NEEDS_ONE_BOUNDED_NATIVE_AB` | This is independent of cross-token weight residence, has a clean control in the existing extension, scales sharply with M, and is not already avoided by the current implementation. It is still only a traffic/opportunity result because no per-kernel time is available. |

Only one hypothesis is retained.

## H1 — fixed split-K=8 is net-costly at M=256

> For the accepted up_proj/down_proj M256 shapes, the deployed fixed `split_k=8` policy loses more through 8-plane FP16 scratch, a separate global reduction, and extra synchronization/launch work than it gains from added K-parallel CTAs; a no-split native path will reduce module time while preserving AWQ numerical behavior. M1 may retain or reverse the tradeoff.

Support:

- The control is real: up_proj V2 grids are exactly the source formula multiplied by eight; down_proj M1 independently shows the same factor.
- Scratch grows from 303,104 B to 77,594,624 B for up_proj and from 57,344 B to a conditional 14,680,064 B for down_proj when M grows 1 -> 256.
- Up_proj M256 reduction has substantial dynamic fabric traffic, including 76,003,328 DRAM bytes under the accepted application-replay/cache-control-none contract.
- Both M256 AWQ clean timings are slower than RAW_FP16, while both M1 AWQ timings are faster. This motivates the shape question but does not identify its cause.

Still unknown:

- GEMM and reduction duration separately;
- whether fewer, longer no-split CTAs lose enough parallelism to outweigh removed scratch/reduction;
- down_proj M256 actual grid and traffic;
- register count, spills, occupancy, stalls, bank conflicts, and tensor-level traffic;
- whether activation or metadata supply dominates after the split policy changes.

## Why the other paths are not promoted

Activation repetition is a real source property, not a demonstrated bottleneck. Its 271.6 MB M256 value is a source-level per-thread request calculation, not an NCU tensor attribution. The total NCU bytes are compatible with multiple operands and output stores, so they cannot close the hypothesis.

The current qweight path does retain the shared-memory round trip highlighted by QUICK, so it is not “already solved” locally. However, the mechanism is already a direct published technique, and current accepted evidence lacks the shared-bank or kernel-time breakdown needed to show that porting it is valuable here. It is closed for this round as `COVERED_BY_EXISTING_KERNEL_TECHNIQUE`, not as “zero cost.” FLUTE is a useful dataflow neighbor but uses LUT quantization and cannot be treated as an equivalent AWQ backend.

MARLIN and FLUTE also contain partition/reduction techniques, so H1 is an implementation diagnostic, not a novelty claim. The value of the C16 question is that the accepted kernel still uses fixed split-K plus global reduction at the exact E1 shapes.

## Static, dynamic, and causal boundaries

- The accepted “43” AWQ direct-global inventory is a count of static sites. It is not a dynamic instruction or transaction count.
- V2 L1/L2/DRAM values are additive dynamic kernel totals. They are not qweight, activation, metadata, or scratch attribution.
- Source-level byte calculations are requested operand bytes before cache/coalescing/broadcast effects. They are not fabric traffic.
- Timing and traffic co-vary with operator, M, and implementation. They do not prove cache/TLB, split-K, activation, or layout causality.
- This screen does not claim the unique cause of E1 and does not reinterpret accepted E1 results.

## Closure

Result: retain H1 only and authorize nothing in this commit. The sole follow-up design is in `MINIMAL_NATIVE_AB_PLAN.md`. If that bounded A/B is not separately authorized or is numerically invalid, stop with `NO_NEW_OPPORTUNITY_FROM_EXISTING_EVIDENCE` rather than expanding to a new backend or framework.
