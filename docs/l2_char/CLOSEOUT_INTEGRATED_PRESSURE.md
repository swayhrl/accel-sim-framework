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

Command:

```bash
tests/l2_char/run_integrated_pressure.sh --out /tmp/l2-char-pressure-final12
```

Result (`summary.tsv`):

| case | cycles | instructions | corrected activation | required evidence |
|---|---:|---:|---:|---|
| P1 LowerQ | 6527 | 13568 | 193 | lowerq activation 193 |
| P2 RespQ | 6226 | 13568 | 123 | respq activation 123 |
| P3 DataPort | 204016 | 2261 | 0 | 28,704 data-port-busy cycles under integrated traffic |
| P4 MSHR/MissQ | 5335 | 256 | 0 | one-entry MSHR and MissQ reached capacity |
| P5 WB/ReturnQ | 6123 | 64 | 7 | WB progress credit used 4 times |
| P6 end-to-end | 6895 | 13568 | 242 | lowerq 17 and respq 225 activations |

For every P case, the final production snapshot reports
`L2_char_preview_commit_mismatch = 0`,
`L2_char_resource_leak_free = 1`, and
`L2_char_credit_leak_free = 1` for every subpartition/partition.  All blocker
classes meet `block_cycles >= block_episodes >= block_requests`.

`tests/l2_char/run_synthetic.sh` also passes T1--T15 against the same core
header and reports `corrected L2 admission rule regressions: PASS (T1-T15
contract)`.

## Remaining limitation

The exact preview currently covers the audited QV100 conventional
write-back/lazy-fetch-on-read sector L2 policy.  Other cache policy
combinations intentionally retain the historical coarse controller gate until
they receive their own reviewed preview contract.
