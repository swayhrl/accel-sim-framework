# Corrected baseline v1 postchecks

Date: 2026-08-28

## Build

- Core: `source setup_environment && make -j8`
- Framework frontend: `source gpu-simulator/setup_environment.sh release && make -C gpu-simulator -j8`
- Compiler: g++ 11.4.0; CUDA 11.8.
- Result: PASS.  The existing upstream warning set remains; no new build error.

## Deterministic synthetic contract

```text
tests/l2_char/run_synthetic.sh
corrected L2 admission rule regressions: PASS (T1-T15 contract)
```

## Official low-pressure equivalence

Trace: `tests/l2_latebind/traces/kernelslist.g` from the local directed trace
fixture; QV100 core and trace configurations in this repository.

| Metric | Official `03c1fe44` | Corrected `4628b5c7` |
|---|---:|---:|
| `gpu_tot_sim_cycle` | 5526 | 5526 |
| `gpu_tot_sim_insn` | 256 | 256 |
| L2 accesses | 4 | 4 |
| L2 misses | 4 | 4 |
| L2 pending hits | 0 | 0 |
| L2 reservation failures | 0 | 0 |
| corrected-path activations | n/a | 0 |

This is deliberately a low-pressure equivalence smoke, not a characterization
campaign.  The result is exact as required when the corrected path is inactive.
