# Lane-C Config-Delta Evidence

All four contracts bind a SHA-256 over the canonical sorted map of the four
config files actually passed to the simulator: core `gpgpusim.config`,
Framework `trace.config`, B0-Banked payload overlay, and one Lane-C L1
overlay. This keeps configuration identity independent of worktree paths.

| Contract | Runtime composite SHA-256 | Permitted changed fields | Status |
|---|---|---|---|
| D256_META_HR | `3a5573ccac1e02e06d338e8d78e13a21676a1087ac24d94add9c7944e8b42112` | `l1_mshr_entries`, `l1_merge_cap`, `l1_missq_entries` | PASS |
| D256_BANK_HR | `304c7b50822bdbb57189c94af50b16d17d03913c033798e8489b9189cc170810` | `l1_bank_count` | PASS |
| D512_META_HR | `6fd73e4a6e322ba94a5aca2b242da448ac3593d995f7b2e3735a11c307c3c2c2` | `descriptor_pool_size`, `l1_mshr_entries`, `l1_merge_cap`, `l1_missq_entries` | PASS |
| D512_BANK_HR | `b4e08481e333ae8f469cc486d530e945697d6ed200a1910ff4151cc8a8e36fc2` | `descriptor_pool_size`, `l1_bank_count` | PASS |

The D256 effective configurations are read from each local `effective_config.json`;
the D512 effective configurations additionally record the exact promoted Lane-B
parent Core `878f80869ce212e779df20b6421e4dc7f987825d` and Framework
`aae62b66685f15437cecf0193934f628e6fac6ae`. All source/config checks and
required parser/invariant checks passed for 7/7 rows in each cell.
