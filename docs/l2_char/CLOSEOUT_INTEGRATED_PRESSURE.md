# Corrected L2 baseline closeout: integrated pressure

This is closeout evidence for the conventional corrected sector-L2 baseline.
It does not enable LateBind, Decoupled-L2, FRC, or a full workload
characterization campaign.

## Production path

T1--T15 call the production inline predicates in
`src/gpgpu-sim/l2_admission_rules.h`; that header is included by the cache
preview and controller implementation.  They do not reimplement admission
rules in test code.  In every build, the controller also counts any mismatch
between the previewed lower-read/lower-write/writeback/MissQ effects and the
subsequent `access()` commit; debug builds assert the same condition.

## Terminal integrity

The framework now keeps cycling after a kernel's CTAs retire when a memory
partition is still active.  A memory partition remains active for every
borrowed DRAM credit and latency-queue entry, including no-return L2
writebacks.  The framework emits a final statistics snapshot only after that
drain; the pressure harness uses that snapshot for integrity checks.

## Executed evidence

The legacy compact P1/P2 evidence was run with:

```bash
tests/l2_char/run_integrated_pressure.sh --out /tmp/l2-char-pressure-final12
```

Its result (`summary.tsv`) was:

| case | cycles | instructions | corrected activation | required evidence |
|---|---:|---:|---:|---|
| P1 LowerQ | 6527 | 13568 | 193 | lowerq activation 193 |
| P2 RespQ | 6226 | 13568 | 123 | respq activation 123 |
| P3 DataPort | directed | directed | 1 | busy + clean-miss admit=1; busy + hit block=217 |
| P4 MSHR/MissQ | 5959 | 704 | n/a | dirty one-slot blocks=132; no partial mutation=132; later two-slot admit=1 |

P5 and P6 use the stronger closeout fixtures below rather than attempting to
force a timing relation through warp/trace text order.

| case | command | final evidence |
|---|---|---|
| P5A ReturnQ/FIFO | core `tests/l2_char/run_memory_partition_returnq.sh` | actual R0 fills ReturnQ; FIFO-head W0 issues (`wb_head=1`, `wb_issued=1`); next FIFO-head R1 is blocked (`read_head=1`, `read_blocked=1`); no reorder/leak |
| P5B progress credit | `tests/l2_char/run_p5_progress_credit.sh` | real integrated use=4, maximum=1/limit=1, final current=0, no credit/resource leak |
| P6 Official vs Corrected | `tests/l2_char/run_p6_official_vs_corrected.sh` | same trace: 13,568 instructions and 513 injection requests on both paths; Official=6,902 cycles, Corrected=6,895 cycles, corrected activation=242 |
| hook equivalence | `tests/l2_char/run_hook_off_equivalence.sh` | hook omitted versus explicit zero: identical cycles and 1,594 normal-stat rows |

For every corrected integrated case, the final production snapshot reports
`L2_char_preview_commit_mismatch = 0`,
`L2_char_resource_leak_free = 1`, and
`L2_char_credit_leak_free = 1` for every subpartition/partition.  All blocker
classes meet `block_cycles >= block_episodes >= block_requests`.

`tests/l2_char/run_synthetic.sh` passes T1--T15 against the same core
header and reports `corrected L2 admission rule regressions: PASS (T1-T15
contract)`.

## Remaining limitation

The exact preview currently covers the audited QV100 conventional
write-back/lazy-fetch-on-read sector L2 policy.  Other cache policy
combinations intentionally retain the historical coarse controller gate until
they receive their own reviewed preview contract.
