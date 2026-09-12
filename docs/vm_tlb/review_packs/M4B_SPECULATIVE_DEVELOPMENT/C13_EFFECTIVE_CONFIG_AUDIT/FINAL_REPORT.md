# C13 effective-config audit — Path A final report

Status: `C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`

## Root cause and supersession

C13 MANUAL config synthesis inherited `gpgpu_vm_l2_tlb_mode=1`; MANUAL does not apply F7's internal exact-mode override.  Independent last-option folding and raw final telemetry confirm mode 1 for all original nine C13 rows.  They remain immutable engineering evidence but are `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16` for H1/H2/H3.
All repaired configs explicitly end in `gpgpu_vm_l2_tlb_mode 0`; their receipts prove intended entries, associativity/sets, Segment state, binary/Core, frozen trace/registration and exclusion-map provenance.  EQ1 reproduces C12 F7-L10 under C12 binary MANUAL exact mode; EQ2 reproduces EQ1 under new binary empty exclusion.  Equivalence is exact for kernel markers/cycles and modeled `gpu_*`/`vm_*` counters; only `gpu_total_sim_rate` is excluded because it is derived from host wall-clock time rather than simulated state.  Only then were repaired results promoted.

## MEASURED_C13_DIAGNOSTIC_FACT

- Prefill repaired L8 delta vs F0: `-1189116` cycles; L9: `-206118` cycles.  Measured bracket: `9 < Lseg* < 10 (MEASURED_BRACKET_ONLY)`.
- Decode repaired L11 delta vs F0: `-24692` cycles.  Measured bracket: `11 < Lseg* < 20 (MEASURED_BRACKET_ONLY)`.
- Corrected capacity cycle contrasts: B-A `1402804`, C-A `-423264`, D-B `-522154`, D-C `1303914`; interaction `-98890` (`DIAGNOSTIC_INTERACTION_ONLY`).
- Corrected selective candidate-control cycle deltas: Prefill `186775`, Decode `51581`; Prefill kernel 691 delta versus same-new-binary control `166235`.

## SUPPORTED_C13_MECHANISM_SIGNAL

- Operator deltas are reported only as observed associations between exact-mode policy/configuration and cycles/translation counters.  They do not identify a unique critical path.
- The tied Embedding/Output exclusion is whole-range policy, not a final-kernel special case.  H1 comparisons use same-new-binary controls only.

## DIAGNOSTIC_INTERACTION_ONLY

- The repaired 2×2 is non-equal-budget and local to Prefill.  Its interaction is a decomposition, not a general causal law.

## UNRESOLVED

- Translation/cache associations do not by themselves prove queue, DRAM, or critical-path causality.
- No execution-order inference upgrades direct/semantic/heuristic/unresolved operator evidence tiers.
