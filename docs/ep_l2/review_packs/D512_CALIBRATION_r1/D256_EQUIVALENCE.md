# D256 backward-equivalence (B3): PASS

The generalized D512 Core was configured back to the exact D256 formal
Framework/config. `vectorAdd_4M`, `spmv`, and long `scan` reproduce the formal
C7e output exactly: all seven required parsed artifacts (`summary`, `slice`,
`kernel`, `bank`, `window`, `l1`, `dram`) are byte-identical per workload.

`D256_EQUIVALENCE_STATUS.csv` records source/config identities, cycles,
instructions, selected L1/L2/DRAM counters, terminal invariants and artifact
SHA-256s. The completed machine-readable gate is `D256_EQ_SCAN_GATE.json`.
