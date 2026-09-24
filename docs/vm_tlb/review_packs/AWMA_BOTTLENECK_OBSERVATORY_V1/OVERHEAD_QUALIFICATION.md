# Observatory overhead qualification

Status: `PASS_NO_ARBITRARY_THRESHOLD`

Each target/level uses the same final binary, RTX4080/V1 configuration, payload,
and 10/80 translation parameters.  Every point has one warmup followed by three
measured host executions.  `runtime overhead = measured-level mean wall time /
measured-OFF mean wall time - 1`.

`output_bytes` is `run.log + run.stderr + host_metrics.txt`.  Maximum RSS is the
Linux `RUSAGE_CHILDREN.ru_maxrss` value for the single simulator child.  Small
negative RSS deltas are measurement granularity/noise, not reclaimed simulator
state.

| target | level | mean wall s | runtime overhead | RSS delta KiB | output delta bytes |
|---|---:|---:|---:|---:|---:|
| splitkv-combine | 1 | 1.336 | +6.710% | -2731 | 3782 |
| splitkv-combine | 2 | 1.352 | +8.028% | -1365 | 47933 |
| splitkv-combine | 3 | 1.369 | +9.356% | +1365 | 48041 |
| T2 | 1 | 104.703 | +6.229% | 0 | 4022 |
| T2 | 2 | 104.414 | +5.935% | +4096 | 67328 |
| T2 | 3 | 102.753 | +4.250% | +5461 | 67448 |
| T1 | 1 | 783.140 | +1.031% | -2731 | 4064 |
| T1 | 2 | 794.448 | +2.490% | +9557 | 70270 |
| T1 | 3 | 795.753 | +2.658% | +12288 | 70396 |

The T2 levels are not monotonic because one Level-1 repetition was a host-time
outlier; all three raw repetitions are retained.  The short combine kernel also
amplifies fixed startup cost and timer noise.  No arbitrary pass percentage is
applied.

`RECOMMENDED_DAILY_LEVEL = 1 (TRIAGE)`

Level 1 supplies all-domain aggregate location with only +1.03% on the long T1
run and small output growth.  Level 2 is appropriate when true-cycle temporal
correlation and Top-K windows are needed.

`DEEP_DIAGNOSTIC_LEVEL = 3 (DEEP)`

Level 3 adds exact progress, READY-to-admission latency, and DRAM boundaries.  On
T1 it costs +2.66% wall time, +12 MiB maximum RSS, and about 70 KiB output over
OFF, making it suitable for selected diagnostic reruns rather than default use.
