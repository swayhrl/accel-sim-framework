# SG5.4 G6 observer receipts

`SG5_G6_OBSERVER.tsv` is the compact index for immutable, observer-enabled
G6 diagnostic attempts.  Unlike `SG5_EQUIVALENCE.tsv`, a SG5.4 row has no
OFF peer and must not be used as a primary performance result.

Every accepted row requires natural exit, the exact observer-Core397 identity,
the pinned ordered config-chain identity, `gpu_tot_sim_cycle` and
`gpu_tot_sim_insn`, and all nine source-defined `SG5_*` report fields.  The
strict check is `sg5_equivalence.py validate-run`; it does not infer any
unreported lower-traffic metric.

The first two rows are B16-S/GESUMMV and TC80-S/GESUMMV.  They were launched
only after all twelve SG5.3 OFF/ON pairs passed, in distinct immutable UUID
directories under `/workspace/wave-a-sg5-runs`, and remain diagnostic-only.
