# M4 counter and invariant closeout

`parse_dtc_l1_summary.py --strict` preserves all `DTC_L1_m4_*` fields. Its committed JSON summaries cover five accepted Base/IO/OO triplets and directed store, atomic-pair, atomic-contention, and mixed-CG checks.

- Accepted triplets have identical dynamic source-domain counts across Base/IO/OO and zero source-reachable fence count.
- PAPER_IO and PAPER_OO strict summaries drain their current PIB/lower state.
- Source completions equal observation retires. Directed Store (2), Atomic pair (2), and mixed-CG (3) close that cardinality without weakening pending-write or scoreboard assertions.
- PAPER_BASE emits source-domain counters after `cdeec769`, enabling F00C while intentionally reporting no IO/OO sidecar admissions.
- Existing deterministic CTests retain stale-generation, dependency, no-allocation, and completion-accounting assertions.

`ld.global.nc` maps to `CACHE_L1`, not the source architectural bypass route, so it is excluded. `ld.global.cg` maps to `CACHE_GLOBAL` and is the BP01/BP02/MIX01 bypass evidence.
