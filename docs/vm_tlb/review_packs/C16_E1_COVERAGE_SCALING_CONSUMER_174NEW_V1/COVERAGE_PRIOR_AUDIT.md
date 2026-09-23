# Coverage prior audit

Sources are accepted historical C12 read-only analyses, not new qweight-residency evidence:

- `C12_OPERATOR_AWARE_CHARACTERIZATION/FINAL_REPORT.md` at commit `23bb01dd5681b94eb0d89b4660fca78f1177b6f5`;
- `C12_OPERATOR_AWARE_MECHANISM_DEEP_DIVE/FINAL_REPORT.md`, `LAYER_ROBUSTNESS_FINDINGS.md`, and `KERNEL_CRITICALITY_FINDINGS.md` at commit `484663a46b3810df24b31d8f97cd9cdb671ed91b`.

Those reports establish only the following qualitative motivation:

- Direct FFN and Attention Projection responses were broadly repeated across the 16 directly attributable layers in the tested operator-aware experiments.
- Their largest single-layer absolute shares were below 11.5%, with Top-4 shares at most 42.7%; this rejected a one/few-layer hotspot explanation for those direct classes.
- Several Decode comparisons were distributed across hundreds of changed kernels (for example 567/740 or 587/740 in the cited Segment comparisons), rather than being dominated by a single kernel.
- Separate Embedding/Output hotspots existed in some Prefill comparisons and must not be folded into the cross-layer FFN/Attention statement.

Boundary: C12 studied translation/Segment/operator-aware behavior, not AWQ qweight persistence. It neither measures nor predicts the quantitative benefit of the fixed-budget coverage experiment. No C12 cycle percentage, layer share, break-even, or speedup is transferred into a coverage-scaling prediction. It motivates measuring broad layer coverage and nothing more.

Explicitly: C12 does not provide direct evidence for AWQ qweight residency, and it does not quantify the expected benefit of the new persistence policy.
