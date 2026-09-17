# SG5.4 G6 observer receipts

`SG5_G6_OBSERVER.tsv` is the compact index for immutable, observer-enabled
G6 diagnostic attempts.  Unlike `SG5_EQUIVALENCE.tsv`, a SG5.4 row has no
OFF peer and must not be used as a primary performance result.

Every accepted row requires natural exit, the exact observer-Core397 identity,
the pinned ordered config-chain identity, `gpu_tot_sim_cycle` and
`gpu_tot_sim_insn`, and all nine source-defined `SG5_*` report fields.  The
strict check is `sg5_equivalence.py validate-run`; it does not infer any
unreported lower-traffic metric.

The current partial checkpoint indexes five GESUMMV variants: B16-S, TC80-S,
B16-N, TC80-N, and IO. They were launched only after all twelve SG5.3 OFF/ON
pairs passed, in distinct immutable UUID directories under
`/workspace/wave-a-sg5-runs`, and remain diagnostic-only.

For a diagnostic `validate-run`, the expected config identity is the ordered
`config_chain_sha256`, not the single-file `config_sha256`. B16-S preserves an
original FAIL caused by passing the latter as the former; its distinct named
revalidation receipt and both hashes are recorded in
`SG5_G6_VALIDATION_RECONCILIATION.tsv`. No simulator run was repeated.
