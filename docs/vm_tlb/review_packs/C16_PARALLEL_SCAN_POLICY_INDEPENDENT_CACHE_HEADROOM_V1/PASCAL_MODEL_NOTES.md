# PASCAL model notes and C16 mapping

## Literature authority

The formula authority is [PASCAL: A Phase-Aware Shared-Cache Model for Parallel Scans](https://arxiv.org/pdf/2609.10515v1), arXiv:2609.10515v1, PDF SHA-256 `e66e606470a841eae6495c6d0ddffbbb922d04a7ce6f4140a657850b7914db2e`. ArXiv v2 was revised on 2026-09-26 under a different title; this analysis does not mix v2 formulas into the named v1 contract.

## Author formulas (PASCAL v1)

- A fixed parallel scan has `M` workers over a cyclic address space of `N` blocks, phases `s_m`, distinct cyclic gaps `g_i`, and cache capacity `C` blocks.
- Cyclic-gap footprint: `U(t) = sum_i min(g_i, t)` and `K(t) = U(t+1)-U(t) = #{i: g_i > t}`.
- `T*` is the largest integer round window with `U(T*) <= C < U(T*+1)`.
- Exact slotted-TTL misses: `K_TTL = K(T*)` misses per round and `K_TTL/M` per request.
- Fully associative LRU certificate: `K(T*+1) <= K_LRU <= K(T*-1)`; equality follows when the interval collapses.
- Policy-independent residency bound: with inter-reference intervals `delta_m`, fractional residency `V(C)=max sum x_m` subject to `sum delta_m*x_m <= C`, `0<=x_m<=1`; every demand-paging policy satisfies `K_policy >= M-V(C)`. For an `H`-round finite trace with arbitrary initial state, the per-round correction is at most `N/H`. The fractional program is optimistic and need not be realizable.
- Progress divergence is the maximum historical worker request-count spread `sigma_E`. For fully associative LRU and no other accesses, `C >= 2*sigma_E-1` is sufficient to preserve all post-first sharing; final phase alignment cannot replace the historical maximum.
- Pipeline recurrence separates issue/wait/consume costs from memory latency. Theorem 6 shows cache hits cannot repair a persistent service-rate disadvantage, and its `G_d` term can be zero when misses already fit available overlap. Traffic and time must therefore be evaluated separately.

## C16 mapping (not an author claim)

- The selected AutoAWQ family has 16 M-tile macro-workers. Each macro-worker traverses the same combined weight-side 128-byte-line stream over 384 N tiles. `N` is 612,864 lines at K3072 and 817,152 at K4096; RTX4080 L2 gives `C=524,288` lines.
- `GROUP_M16_FULL_M` makes same-Ntile workers adjacent in logical block ID and supports an aligned best-case model. `ROW` separates consecutive M-tile reuse by 384 logical CTA IDs and 383 intervening CTAs/N tiles.
- CUDA logical ID order is not an actual issue/progress trace. No existing artifact contains per-CTA progress phases or `sigma_E`, so observed-phase `U(t)`, `T*`, TTL/LRU and residency bounds remain UNKNOWN. Numeric rows are aligned best cases only.
- Split8 is represented as a composite macro-worker stream over the union of eight split subpanels. This is a weight-side proxy; reduction traffic is kept separate.
- The kernel performs one finite scan. With `H=N`, PASCAL's finite correction is `N/H=1`, so the long-run fractional lower bound is not by itself discriminative for this run. The C16 one-unique-fill value is an aligned TTL/LRU reference, not a PASCAL policy-independent floor.
