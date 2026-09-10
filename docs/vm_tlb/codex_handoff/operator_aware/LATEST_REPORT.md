# C12 operator-aware Codex handoff

## Final state for this publication

`C12_OPERATOR_AWARE_INTERIM_READY_WAITING_C12_FINAL`

The review pack is committed in Framework commit
`27ade79ca3e2041a96b4e49bdc2c9c2ae4a23eef` on
`hrl/vm-m4b-operator-aware-v0`.

## C12 source cutoff

- Read-only source branch: `origin/hrl/vm-m4b-speculative-v0`
- Fetched source commit: `269c274712f4eeaee15d304033a9e6d61b5b3206`
- Formal status at publication: 20 `PASS`, 2 `PENDING`
- Excluded pending arms: `Prefill F1`, `Prefill F8-Lseg20`
- Decode1: 11/11 terminal-PASS arms analyzed.

## Delivered

- Review pack: `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION/`
- Exact 692/692 Prefill and 740/740 Decode1 list/header/marker alignment.
- Direct parameter-range and direct-semantic mapping, with no heuristic
  assignments and one retained `UNRESOLVED` kernel per ROI.
- F0 Weight/KV/UNKNOWN trace characterization, exact per-kernel translation
  and KERNEL cache attribution, and terminal-arm mechanism deltas.
- Conservation audit: F0 operator cycles, instructions, selected translation
  counters, and trace refs each exactly close against same-source totals.
- Exact changed-path inventory: `CHANGED_FILES.md` in the review pack.

## Review entry points

1. `INTERIM_REPORT.md` — scope, OA0--OA5 status, and final-attach condition.
2. `PAPER_FACING_FINDINGS.md` — measured facts, supported signals, and
   explicit unresolved boundaries.
3. `CONSERVATION_AUDIT.md` — numerical closure and read-only reproduction.
4. `KERNEL_OPERATOR_MAP.tsv` / `OPERATOR_ARM_DELTAS.tsv` — row-level evidence.

No C12 simulator replay was launched and no live-C12 asset was changed.  The
only remaining action is a read-only regeneration after official C12 publishes
its final 22/22 terminal-PASS state.

## Worktree state at handoff

Tracked worktree: clean after committing this handoff.  Local ignored scanner
resume/input shards and Python bytecode are not part of the review pack or any
commit; they neither modify nor duplicate C12 evidence.
