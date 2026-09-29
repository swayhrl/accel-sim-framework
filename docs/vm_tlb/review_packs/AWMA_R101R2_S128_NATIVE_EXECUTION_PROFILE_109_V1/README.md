
# AWMA R101R2 S128 Native execution profile — node109

Final status: **`R101R2_NATIVE_PROFILE_PASS`**. Native-side diagnostic label: **`NATIVE_PROFILE_MIXED`**. This pack is for joint review with Lane E's independent O2 result; it does not itself set the final R101R2 research state.

The exact accepted R101 discovery S128 payload (581 BF16 128×128 tiles) and pinned HiMuon source were reused. F128 fused and K128 five-step three-kernel graph outputs matched accepted hashes exactly; a diagnostic NSYS canary matched accepted family/name/grid/block strata. Original R101 graph timing—F128 0.493408 ms versus K128 0.623488 ms, 20.863% improvement—remains the only primary timing authority.

Read `NATIVE_PROFILE_INTERPRETATION.md` first for counter ratios, family decomposition and limitations. `NCU_METRIC_PREREGISTRATION.md` plus `NCU_RAW_METRIC_BINDING.tsv` expose every supported/unsupported metric and its raw unit. `STATIC_SASS_SUMMARY.tsv` is per-binary static code, distinct from `NCU_FAMILY_SUMMARY.tsv` dynamic executed work. The final F128/K128 NCU reports are one bounded metric-engineering retry per arm; ATTEMPT0 is retained under node164 but never mixed into formal totals.

Node164 durable root: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101r2_s128_native_profile_20260929/`. `RAW_DATA_INDEX.tsv` and `SHA256SUMS` close the raw/report identity. No new model, gradient, holdout, mechanism, or Accel-Sim run was performed.
