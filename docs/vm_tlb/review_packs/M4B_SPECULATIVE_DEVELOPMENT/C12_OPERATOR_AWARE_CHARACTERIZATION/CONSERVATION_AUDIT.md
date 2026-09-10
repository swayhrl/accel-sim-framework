# C12 Operator-aware conservation audit

Scope: read-only analysis of the C12 source commit
`269c274712f4eeaee15d304033a9e6d61b5b3206`.  Only the 20 arms that are
terminal `PASS` in both formal C12 tables are included.  The two pending
Prefill arms are not present in any aggregate.

## Alignment and classification closure

| ROI | compute entries | aligned `Processing kernel` markers | map rows | status |
| --- | ---: | ---: | ---: | --- |
| Prefill | 692 | 692 | 692 | PASS |
| Decode1 | 740 | 740 | 740 | PASS |

Every aligned trace has exactly one embedded semantic header.  The raw
semantic manifests reproduce the compute-only lists after exactly 32 NCCL
entries are removed, so there is no index shift.

## F0 additive closure

The sums below include direct, semantic-direct, and `UNRESOLVED` rows.  No
heuristic rows exist in this pack.

| ROI | operator-cycle sum | C12 F0 `gpu_tot_sim_cycle` | trace Weight refs | KV refs | UNKNOWN refs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prefill | 62,490,238 | 62,490,238 | 410,255,360 | 54,935,552 | 2,102,553,796 |
| Decode1 | 34,564,626 | 34,564,626 | 63,799,296 | 25,915,264 | 721,919,901 |

For each ROI, the object-reference totals above exactly equal the independent
sum of `TRACE_SCAN_<roi>.tsv`; they are lane references, not cache requests.
The operator instruction sums also equal the corresponding C12 F0 total:
18,452,620,427 (Prefill) and 4,128,551,787 (Decode1).

## F0 translation closure

The selected cumulative raw-log counters were differenced between adjacent
kernel snapshots, then summed.  They match the immutable F0 validation
sidecars exactly.

| ROI | L1 TLB misses | L2 TLB misses | translation walks | PTE requests |
| --- | ---: | ---: | ---: | ---: |
| Prefill | 1,119,527 | 45,227 | 20,816 | 20,899 |
| Decode1 | 57,947 | 22,220 | 15,691 | 15,796 |

The checks intentionally exclude non-monotonic gauge fields and
`FIXED_WINDOW_PARTIAL` telemetry.  Thus no gauge is mistakenly differenced
and no partial-window cache observation is attributed to an operator.

## Reproduction command

The generated tables can be reproduced read-only from this worktree with:

```bash
g++ -O3 -std=c++17 util/vm_tlb/c12_operator_trace_scan.cc -o /tmp/c12_operator_trace_scan
python3 util/vm_tlb/analyze_c12_operator_aware.py \
  --scanner /tmp/c12_operator_trace_scan --resume \
  --source-commit 269c274712f4eeaee15d304033a9e6d61b5b3206
```

This command only reads the frozen trace, sidecar, raw-log, and formal-C12
inputs; it does not invoke `accel-sim.out`.
