# Decision

`R82_CURRENT_SOFTWARE_SUFFICIENT_IN_SCOPE`

## Result

- `VERIFIED_CODE`: pinned Triton source `eb93a9a97e5dfc6a20c29da0096c047dbabd514c` has the expected minimal conversion sequence: no-op reuse, register permutation, warp shuffle, otherwise swizzled shared-memory exchange with required scope synchronization. The requested file blob is exactly `f5c1b400a8a45b579271696e73b9ebf9fb16e7f2`.
- `VERIFIED_RUN`: installed Triton 3.8.0 (`libtriton.so` SHA256 `c3306b024133cf76abba389ac00c6dc9cb9127be6a0796aef2acf2134e5f082f`) produces surviving IR conversions and real SM89 shuffle/shared/barrier instructions. This is a modern strong software baseline, not an obsolete compiler control.
- The first ordered path, Qwen3.5-0.8B FLA GDN prefill, contains 55 conversions in the selected real-prefill optimized IR and corresponding native movement. It is not advanced to candidate timing: accepted R54 V1R1 records `exact_top1_top2_ordering=false`, and exact binary-level dynamic multiplicity is not recoverable from the aggregated NSYS family. Those limitations are not hardware opportunity evidence.
- The second ordered path, accepted Qwen2.5-0.5B layer-12 fixed-split-256 attention, is qualified. B0 and C1 are bitwise identical with zero differing elements and zero max absolute difference. C1 keeps the reduction dimension through the final store but both stage1 and stage2 still contain one conversion.
- Seven preregistered paired measurements with 100 operator invocations per sample give B0 median `0.021401601` ms and C1 median `0.021452799` ms per complete two-kernel operator. C1/B0 is `0.239%`; B0 CV is `1.685%`, C1 CV `1.252%`.

## Interpretation boundary

The experiment identifies real layout-transfer execution, but no reproducible beneficial response to the single legal joint-layout change. Stage2 C1 emits fewer SASS shared stores (3 versus 6) while retaining identical registers, dynamic shared allocation, barriers, shuffles, and timing within noise. This is an informative compiler/codegen observation, not an application speedup and not a causal decomposition.

A warp shuffle cannot legally replace the remaining P1 conversions because producer and consumer ownership spans multiple warps. Reducing the CTA barrier scope or deleting the barrier would be incorrect. No C2 was therefore attempted. The reserved S2_CODE holdout was not used.

No architecture novelty is proposed. Linear Layouts already supplies the relevant strong lowering family; Tensor Seeks Layout addresses global layout choice; FIBER directly covers a much broader thread/register-decoupled machine. This Goal does not claim differentiation from them.
