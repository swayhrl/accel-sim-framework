# Final decision

Decision:

`R101R3_S1_BELOW_5_PERCENT_H1_NOT_TRIGGERED`

## Stage A

The accepted O2 raw records maximum unbounded-oracle scheduled/ready depths of
1/16. Exact B0 and O2 kernel4/5/6 boundaries were recoverable; no missing field
was fabricated.

Offline arch-89 sector coalescing exactly reproduces all accepted O2
per-kernel LDG/LDGSTS/WRITE and byte totals:

- 29,937,568 measured transactions;
- 958,002,176 request bytes;
- 958,002,176 active bytes.

The line/sector producer ledger finds byte-complete earlier-kernel producers
for 27,594,584 of 27,594,656 measured reads. The remaining 72 B2 reads share
the producer kernel and are not upgraded from serialized trace order to runtime
chronology. Initial X0 has no producer in the six-member view and is not
preloaded.

This establishes a strong data-availability opportunity but not cache
residency.

## S1 qualification

`S1_PARTITION_HIT_SERVICE` preserves normal VM translation, L1, request ICNT,
the existing L2-subpartition ingress/data port, existing return queue/ICNT and
normal LDGSTS/LDG/store completion paths. It adds no request/ready queue,
response port, ordinary L2 allocation or data capacity.

Qualification completed:

- default-absent and explicit-none exact accepted T2 equivalence;
- 24 directed policy/resource assertions;
- 18 source-placement/resource checks;
- three accepted VM regressions;
- accepted transient-region and O2 helper regressions;
- positive 6-kernel integrated S1 read/write test;
- exact context timing in the formal run;
- 56/56 formal correctness, coverage, exactly-once and full-drain gates.

## S1 CONTEXT2 result

The context boundary is exactly the accepted comparator:

- 2,976,829 cycles;
- 1,217,463,296 instructions;
- 7,040 CTAs;
- identical registered L1D/L2/DRAM counters;
- lifecycle hash `c11eff45e7bbc37f`;
- zero S1 service in kernels1-3.

Measured ROI:

| Arm | ROI cycles | Improvement vs B0 |
| --- | ---: | ---: |
| accepted B0 | 2,985,319 | 0% |
| accepted O2 | 1,130,670 | 62.1256555832% |
| S1 | 2,963,656 | 0.7256510946% |

S1 therefore saves 21,663 cycles versus B0, below the preregistered 5% gate.

S1 serves:

- 27,594,656 reads;
- 1,126,400 LDG reads;
- 26,468,256 LDGSTS reads;
- 2,342,912 writes;
- 958,002,176 request/active bytes;
- all 16 subpartitions;
- zero fallback, semantic violation, duplicate or context service.

Measured-ROI hierarchy deltas are:

- L1D accesses/misses: 3,469,312 / 3,349,078;
- L2 accesses/misses: 29,964,036 / 3,209;
- DRAM reads/writes/writebacks: 3,209 / 0 / 1,031.

Thus S1 retains essentially the O2 traffic-suppression direction after normal
L1/request delivery, but the cycle response is not material. Existing bounded
path observations include maximum ingress/return occupancies 61/64,
365,356 return-queue-full qualified-head cycles, and 1,017 data-port-busy
cycles.

These counters describe finite-path pressure. They do not prove that one
counter is a causal runtime fraction.

## Gate consequence

Because S1 improvement is below 5%:

- `H1_PRODUCER_BACKED_HANDOFF_4M`: not implemented or run;
- H1 capacity/latency variants: not run;
- L3/FULL5 and capacity-matched control: not triggered;
- no new 109 capture, sweep, scratchpad/DSMEM or cluster mechanism was run.

The required interpretation is:

> The large pre-L1 O2 headroom does not survive bounded partition-side hit
> placement strongly enough in the accepted CONTEXT2 screen.

The Stage-A producer ledger does not overturn this gate and does not imply that
all producer-consumer handoff is impossible. It only shows that data
availability was not the reason to bypass the S1 placement test.

## Postprocessing recovery

The completed S1 simulator process was rc=0 with empty stderr and immutable
6/6 raw evidence. Its formal-at-run summarizer contained two
non-preregistered assumptions:

1. it treated an inherited combined service-mode print label as R2-only; and
2. it assumed queue observations must be at most 8 instead of recording the
   existing finite queue values.

A hash-bound postprocess-only recovery removed those assumptions, changed no
simulator bytes, produced 56/56 passing gates and promoted the original run.
No simulator rerun occurred.

An earlier attempt was manually stopped after about three minutes when the
extra assumed-depth gate was found before useful completion. Its raw is
retained as engineering evidence and is not used scientifically.

## Claim boundary

S1 is still an oracle for data availability at the partition; it is not a
realizable storage structure. This result does not establish hardware cost,
energy, RTX4080 speedup, Native causality, novelty or generalization.

O2/S1/B0 percentage differences are matched responses, not additive
measurements of L1 time, interconnect time or cache time.
