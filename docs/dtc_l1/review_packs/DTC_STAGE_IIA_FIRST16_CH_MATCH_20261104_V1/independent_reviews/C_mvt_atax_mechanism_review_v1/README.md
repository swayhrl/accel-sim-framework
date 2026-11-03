# Independent interim MVT/ATAX mechanism review

Decision: **PASS_WITH_EXISTING_SOURCE_SCOPE_LIMITS**. This reviews the two frozen F128 four-source packages only; it is not the all-16 terminal review or execution authorization.

Reviewed package manifests:
- MVT: `062f7262459e8bac45adeee494038a85b63b73319fe19db7b1dbde3150a440ae`.
- ATAX: `af69366bb4fe44dd919518150f763a248451a4cdd67a4764c25b2494bec47158`.

All 14 MVT and 16 ATAX check groups passed. Eight closed raw/result/natural-exit identities, fixed input/Core/Framework/binary, exact kernel cycles, consumed additive counters and 20-controller traffic units were independently checked. Actual pure differencing helpers were extracted through AST without importing the producer scripts. Late or disappearing fields stay unavailable; decreased cumulative fields raise an error. No model or runtime action was performed.

| Program | CH total cycles P0 / F128 | DH total cycles P0 / F128 | CH self speedup | DH self speedup | Relative improvement I | CH_F128 / DH_F128 |
| --- | --- | --- | --- | --- | --- | --- |
| MVT | 26581175 / 25573002 | 34687540 / 35332620 | 1.039423 | 0.981743 | 0.944507 | 0.723779 |
| ATAX | 28428842 / 29882110 | 31880220 / 31894637 | 0.951367 | 0.999548 | 1.050644 | 0.936901 |

MVT K2 changes by +304 cycles for CH and -755 for DH; these are nonzero. K1 dominates the aggregate differences. ATAX DH increases by 14417 cycles (+0.0452%), including K2 +123: near zero response is not exact zero. ATAX I greater than one means CH regresses more; DH does not accelerate and remains 6.73% more cycles than matched CH. MVT DH remains 38.16% more cycles than matched CH.

Counters retain their units and active domains: CH mode1 common PIB256 and bounded Tag service are active; DH mode3 OO uses PIB128, not generic common PIB8. Retry events are not occupancy, unique requests or critical-path stall cycles. Reduced MISS_QUEUE_FULL does not establish that all bottlenecks disappeared. Aggregate request counters establish correlations, not complete performance causality. Missing metrics are not zero.

ATAX tmp dependency is supported only by the SHA-pinned candidate-source kernels and host synchronization. The candidate has not been bound to capture ELF or original numeric bytes. Excerpts using the report shorthand real tmp dependency must carry that candidate-source qualification. The approved 5001c3f frozen input identity remains unchanged: no numerical-validity upgrade, full-application claim or scientific-identity downgrade follows from candidate source. Source static reuse is not an observed cache hit, merge or runtime dependency measurement.

The detailed JSON records source paths, input digests, result/raw hashes, endpoint checks and exact per-kernel changes. The audit script is included for reproducibility. Existing history, running components, remaining48 planning and v0.23 were not changed.
