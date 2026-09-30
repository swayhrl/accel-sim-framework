# C16 E1 Oracle-Elastic B16 Reuse Performance Canary Log

Stage `C16_E1_ORACLE_ELASTIC_B16_REUSE_CANARY_COMPLETE_V1` closed on 2026-09-30 from the qualified continuous D1 plus D2-prefix reuse window. The execution used Core `0271de82432db004beed43280ed01057246a0f2c`, binary SHA `6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186`, the frozen SM89 RTX4080 platform, and the accepted bounded-trace manifest `db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389` without trace filtering, reordering, or traffic removal.

R0 and M1 both naturally terminated after 1,565 kernels, 168,794,081,786 executed thread instructions, and 1,259,187 CTAs. Their complete kernel/stream sequence and every UID's cumulative instructions/CTA are exact. The independent primary responses, defined as `(R0-M1)/R0`, are:

- full window: `-0.20543388284633024%` (`134571764` versus `134848220` cycles);
- D2 prefix: `+0.4127619325619468%` (`3535452` versus `3520859` cycles);
- D2 L0 up_proj: `-0.2776667594555212%` (`1286074` versus `1289645` cycles).

The admitted diagnostic run is telemetry-neutral for cycles, instructions and CTA at every one of the 1,565 UIDs. Its 25,040 counter rows and 25,040 class-occupancy rows close exactly across 16 L2 instances with an 8,192-line per-instance quota and 131,072-line aggregate B16 quota. Target accesses and protected fills are nonzero (`57099207` and `7691289` at the final checkpoint), so the mechanism genuinely activated.

D1 layer-0 class-1 occupancy was 131,072 lines after its fill and zero immediately before D2 layer-0 reuse. The pre-D2 diagnostic contains no target-protection admission denial and no ordinary-to-protected fallback victim. Quota-full events correspond to protected-to-protected replacements; they are not relabeled as fallback and are not claimed as a unique cause of class-1 loss. The frozen qualitative Case-4 language has no numeric threshold, and its conservative exact-zero-retention-with-observed-constraint-events subset is not satisfied.

The signed classification is therefore `CASE_3_RESIDENCY_ACTIVITY_WITHOUT_TARGET_LOCAL_TIMING_BENEFIT`. This is a completed first real-trace B16 reuse-window canary, not a mechanism promotion, budget sweep, whole-model/system speedup claim, or authorization for another mechanism stage. Reproducibility is limited to `BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168`; no full 1,565-kernel repeat is claimed.
