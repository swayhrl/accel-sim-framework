# R22F final scientific decision

`R22F_R21A_FAMILY_RESULT_MIXED`. R21A remains `R21A_RESULT_MIXED_NEEDS_REVIEW`.

The source-backed profiled TP forward and force-backward families improved against sorted-graph atomic Aorder by 1.792 and 1.616 µs; gross TP path saved 3.392 µs. The direct JIT TP main kernels alone saved only 0.529 µs; about 2.848 µs of the gross path change is removal of atomic empty fixup launches. Deterministic mandatory real fixups added 30.160 µs (forward 10.368, backward 19.776), so the resolved *profiled* net target family became 26.752 µs more expensive. Even assigning all unresolved mixed-family advantage to target leaves 19.792 µs extra profiled cost. Non-target changed by 0.415 µs median benefit (0.198%), worst block 0.385 µs benefit; no stable non-target regression was observed.

The independently uninstrumented complete region conflicts in sign with the profiled GPU duration sum: Aorder→Dready wall was 13.955 µs / 2.878% faster and CLEAR; official A0→Dready was 14.845 µs / 3.065% faster by median but MIXED under 3×MAD. Ordering-only A0→Aorder was MIXED and near zero. Profiled duration sums (19.409 µs additional GPU service for Dready) cannot be subtracted from uninstrumented wall to explain the discrepancy.

Thus gross TP response exists, but no stable positive *net target-family* response has been established after mandatory deterministic auxiliary work; the complete official-baseline wall response also remains mixed. This is a bounded Native family localization, not an online graph-preparation payoff, cross-frame/model result, deployment or hardware claim. No new samples are added after this decision.
