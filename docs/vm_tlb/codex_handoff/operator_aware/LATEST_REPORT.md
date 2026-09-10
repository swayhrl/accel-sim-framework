# C12 operator-aware Codex handoff

## Final state

`C12_OPERATOR_AWARE_COMPLETE_READY_FOR_REVIEW`

The final review pack is committed in Framework commit
`2342614f60bb70e8b567309a4b4411e2de3cbbbf` on
`hrl/vm-m4b-operator-aware-v0`. This handoff records that completed pack.

## C12 source cutoff

- Read-only source branch: `origin/hrl/vm-m4b-speculative-v0`
- Verified source commit: `a268aba0d01310294074ded5bb8017e2092394c0`
- Formal status: `C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`; 22/22 terminal `PASS`
- Newly admitted final Prefill arms: `F1` and `F8-Lseg20`
- Decode1 remains complete at 11/11 terminal-PASS arms.

## Delivered

- Final review pack: `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION/`
- Exact 692/692 Prefill and 740/740 Decode1 trace-list, embedded semantic
  header, and simulator-marker alignment, revalidated without a trace or
  sidecar identity change.
- Complete 22-arm `ARM_OPERATOR_CHARACTERIZATION.tsv`,
  `OPERATOR_ARM_DELTAS.tsv`, and `LSEG_OPERATOR_SENSITIVITY.tsv`, including
  Prefill F1-vs-F2, F8-L20-vs-F7-L20, and F8 Lseg 5/10/20.
- Direct parameter-range/direct-semantic mapping only; no heuristic
  assignments; one deliberately retained `UNRESOLVED` kernel per ROI; and
  `UNKNOWN` remains an address class.
- `KV_CLASS_TRANSACTION_AUDIT.*`: same-marker FFN/Embedding direct-Weight plus
  KV-runtime-range/cache-transaction observations are documented, while
  semantic FFN/Embedding KV use and fusion remain explicitly unproven.
- Final conservation and provenance audits, including formal registration,
  trace, raw-log, framework/Core/binary, and final-arm admission gates.

## Review entry points

1. `FINAL_REPORT.md` — completion state and primary 22-arm findings.
2. `PAPER_FACING_FINDINGS.md` — measured facts, supported signals, evidence
   tiers, and unresolved limits.
3. `CONSERVATION_AUDIT.md` — identity checks, numerical closure, and read-only
   reproduction command.
4. `KV_CLASS_TRANSACTION_AUDIT.md` — limits of the FFN/Embedding KV-class
   observation.
5. `KERNEL_OPERATOR_MAP.tsv`, `ARM_OPERATOR_CHARACTERIZATION.tsv`, and
   `OPERATOR_ARM_DELTAS.tsv` — row-level evidence.

No C12 simulator replay was launched and no formal-C12 raw log, trace, config,
registration, binary, Core, scheduler, or finalizer was modified.

## Worktree state at handoff

Tracked worktree is clean after the final handoff commit. Local ignored scanner
resume/input shards and Python bytecode are not review-pack evidence and are
not committed.
