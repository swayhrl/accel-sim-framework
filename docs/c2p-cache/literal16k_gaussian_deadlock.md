# Literal-16KiB Gaussian geometry limitation

## Finding

The `4 sets x 32 ways x 128 B = 16 KiB` private-L1 sensitivity point does
not complete the `gaussian s=256` trace.  This is **not** caused by the
peer-locality observer or any C2P sharing state:

| replay | locality observer | C2P scheme at failure | result |
| --- | ---: | ---: | --- |
| `literal16k/gaussian/oracle` | enabled | `scheme=0` | deadlock |
| `literal16k-gaussian-baseline-r2` | disabled | disabled | deadlock |
| `literal16k-gaussian-oracle-no-observer-r3` | disabled | `scheme=0` | deadlock |

All three reports have the same signature:

```
last writeback core 43 @ gpu_sim_cycle 8082 (+ gpu_tot_sim_cycle 228901)
(91918 cycles ago)
shader core 24: 960 threads still running
C2P deadlock state: scheme=0 transactions=0 ... fallback=0
```

The latter two controls use the same trace and literal geometry as the
diagnostic run.  The baseline excludes C2P entirely; the oracle control keeps
the oracle-mode configuration but excludes
`-c2p_cache_peer_locality_diagnostic 1`.  Therefore this is a trace/scheduler
or baseline cache-geometry limitation, not an observation perturbation.

## Provenance

| run | output |
| --- | --- |
| observer run | `hw_run/c2p-peer-locality-final-20260828/literal16k/gaussian/oracle/run.out` |
| baseline control | `hw_run/c2p-peer-locality-control-20260828/literal16k-gaussian-baseline-r2/gaussian/baseline/run.out` |
| oracle, no observer | `hw_run/c2p-peer-locality-control-20260828/literal16k-gaussian-oracle-no-observer-r3/gaussian/oracle/run.out` |

The literal geometry is pinned in
`configs/c2p-cache/paper-table-l1-16k-literal.config`.  The canonical 64KiB
and the 4-set/64KiB geometry both complete Gaussian, so no R value from this
failed literal-16KiB point may be included in an aggregate geometry result.

## Consequence for the diagnostic

This failure is itself part of the configuration evidence.  The geometry
table must show Gaussian/literal16k as `invalid: baseline deadlock`, rather
than silently omitting it or attributing it to C2P.  The other five literal
16KiB workloads remain independently auditable.
