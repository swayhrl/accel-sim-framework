# Engineering repair ledger

- The first generic compiled A0 package produced nonfinite output; its partial output is preserved as `A0_RUN_0_PARTIAL.npz` and `A0_COMPILED_FIRST_FAILURE_AUDIT.json`. The bounded repair used NequIP's exact discovery-shaped `--data-path` AOT interface; five reference and five A0 outputs then qualified.
- The first deterministic natural-order eager probe preserved receiver-major order but produced a force mismatch at `[0,0]` (reference about -0.144125, observed about -0.228056); the output is preserved. The source-backed `SortedNeighborListTransform` composite receiver/sender order plus its transpose permutation was required for correct deterministic forces. Edge/periodic-shift multiset remained exact and preparation occurs once per rebuilt graph, shared by both layers.
- The first AOT candidate compile failed because `edge_transpose_perm` was not registered. The bounded repair registered it as an edge-aligned int64 field before compile.
