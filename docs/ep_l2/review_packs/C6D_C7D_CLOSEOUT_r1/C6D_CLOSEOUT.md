# C6d bank-arbitration closeout

Status: **PASS as C6d diagnostic/correctness evidence.** These smoke results
use the corrected C6 source pair (`0cde3333` / `0a0c0fc3`) and are not formal
Target-Baseline characterization evidence after C7d changed the final Core.

## Correction outcome

The pre-fix Banked store staged every idle-bank logical operation for a retry
in the following cycle. C6d changes the idle-bank first ready operation to a
same-cycle grant, while retaining oldest-ready priority where a bank already
has pending work and one operation per bank per cycle.

The smoke data supports these bounded conclusions:

- The unconditional Banked +1-cycle staging is gone: `spmv`, `gemm`, and
  `FWT_7_21` have attempts = logical operations = grants and no retries.
- Zero-contention smoke workloads have no observed Banked cycle penalty:
  `spmv`, `gemm`, and `FWT_7_21` have equal Legacy and Banked cycles.
- `cfd_097k` retains a 2.37% Banked slowdown together with 16,166 true
  conflict operations/events and wait cycles. This is association, not a
  cycle-for-cycle causal decomposition because wait can overlap other stalls.
- All four pairs are `COMPLETE_VALID`, with payload consistency and terminal
  invariants asserted by their run status/summary records.

## Pre-fix comparison

| Workload | Pre-fix Legacy | Pre-fix Banked | Pre-fix Banked/Legacy | C6d Legacy | C6d Banked | C6d Banked/Legacy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| spmv | 23,453 | 23,719 | 1.0113 | 23,453 | 23,453 | 1.0000 |
| cfd_097k | 79,555 | 83,349 | 1.0477 | 79,555 | 81,443 | 1.0237 |
| gemm | 556,340 | 671,311 | 1.2067 | 556,340 | 556,340 | 1.0000 |
| FWT_7_21 | 493,466 | 564,982 | 1.1449 | 493,466 | 493,466 | 1.0000 |

Pre-fix values are retained only as obsolete diagnostic comparison. The
post-fix detail is in `C6D_SMOKE_COMPARISON.csv`.
