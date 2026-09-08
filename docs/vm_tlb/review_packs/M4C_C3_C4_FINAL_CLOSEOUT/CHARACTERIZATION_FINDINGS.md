# Baseline characterization findings

## Measured facts

The table below is a direct rendering of `PERFORMANCE_SUMMARY.tsv`; all other
measured hierarchy data are retained in the named TSVs in this package.

| ROI | Profile | Cycles | Instructions | IPC | Slowdown vs ideal identity | Slowdown vs VM-disabled |
| --- | --- | ---: | ---: | ---: | ---: |
| decode1 | disabled | 10938651 | 4128551787 | 377.4279 | 1.000000000 | 1.000000000 |
| decode1 | ideal | 10938651 | 4128551787 | 377.4279 | 1.000000000 | 1.000000000 |
| decode1 | generic | 32812575 | 4128551787 | 125.8222 | 2.999691187 | 2.999691187 |
| decode1 | paper | 34438514 | 4128551787 | 119.8818 | 3.148332825 | 3.148332825 |
| prefill | disabled | 36328725 | 18452620427 | 507.9348 | 1.000000000 | 1.000000000 |
| prefill | ideal | 36328725 | 18452620427 | 507.9348 | 1.000000000 | 1.000000000 |
| prefill | generic | 45976701 | 18452620427 | 401.3472 | 1.265574308 | 1.265574308 |
| prefill | paper | 62173001 | 18452620427 | 296.7948 | 1.711400579 | 1.711400579 |

Measured translation facts are in `TRANSLATION_TOTALS.tsv`, `OBJECT_VM_STATS.tsv`,
`L2_TLB_REPLACEMENT_MATRIX.tsv`, and `LATENCY_SUMMARY.tsv`.  Measured cache and
memory context is in `L1D_L2_OBJECT_SUMMARY.tsv`,
`DATA_L2_REPLACEMENT_MATRIX.tsv`, `L2_QUEUE_PRESSURE_SUMMARY.tsv`,
`DRAM_CLASS_SUMMARY.tsv`, `NATIVE_DRAM_MEMORY_SYSTEM_STATS.tsv`, and
`CROSS_LAYER_TRANSLATION_L1D_L2.tsv`.  Offline exact trace locality is in
`TRACE_LOCALITY_OFFLINE.tsv`.

## Supported inference

No causal conclusion is inferred from a single counter.  Any claim about
translation-versus-cache/DRAM bottlenecks, object interference, or prefill
versus decode differences must be checked against the corresponding structured
tables above during review.

## Paper comparison

`generic` and `paper` are reported as separate measured platform profiles.  No
paper-mechanism approximation or Window-B/C result is imported into this
authoritative package.

## Unknown / unavailable

Object-specific Weight/KV/PTE attribution by DRAM channel, bank, or row remains
unavailable.  Native global channel/bank/read/write/latency/row-locality data
are existing GPGPU-Sim statistics.  `L1D_ACCESS_ATTEMPT_WINDOW` is not an exact
unique-coalesced-transaction window and must not be used to derive exact
transactions per memory instruction.
