# C12 operator-aware conservation audit

Scope: read-only analysis of formal C12 source commit
`a268aba0d01310294074ded5bb8017e2092394c0`
(`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`). All 22 arms are terminal
`PASS` in both final formal C12 tables and are admitted to arm-dependent
summaries.

## Continuation identity

Before consuming the final two Prefill arms, the immutable trace/sidecar
inputs were revalidated. The compute-list SHA-256 values remain
`a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
(Prefill) and
`b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
(Decode1). The formal C12 registration digests remain
`6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0`
and `3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48`.

The canonical trace-scan, parameter-range, and object-range derived tables
were regenerated from those inputs; their SHA-256 values are unchanged from
the previously reviewed 20-arm window. `PROVENANCE.md` records the final
sidecar SHA-256 values and frozen framework/Core/binary identity.

## Alignment and classification closure

| ROI | compute entries | aligned `Processing kernel` markers | map rows | status |
| --- | ---: | ---: | ---: | --- |
| Prefill | 692 | 692 | 692 | PASS |
| Decode1 | 740 | 740 | 740 | PASS |

Every aligned trace has exactly one embedded semantic header. The raw
semantic manifests reproduce the compute-only lists after exactly 32 NCCL
entries are removed, so there is no index shift.

## F0 additive closure

The sums below include direct, semantic-direct, and `UNRESOLVED` rows. No
heuristic rows exist in this pack.

| ROI | operator-cycle sum | C12 F0 `gpu_tot_sim_cycle` | trace Weight refs | KV refs | UNKNOWN refs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prefill | 62,490,238 | 62,490,238 | 410,255,360 | 54,935,552 | 2,102,553,796 |
| Decode1 | 34,564,626 | 34,564,626 | 63,799,296 | 25,915,264 | 721,919,901 |

For each ROI, the object-reference totals exactly equal the independent sum
of `TRACE_SCAN_<roi>.tsv`; they are lane references, not cache requests. The
operator instruction sums also equal the C12 F0 totals: 18,452,620,427
(Prefill) and 4,128,551,787 (Decode1).

## F0 translation closure

The selected cumulative raw-log counters were differenced between adjacent
kernel snapshots, then summed. They match the immutable F0 validation
sidecars exactly.

| ROI | L1 TLB misses | L2 TLB misses | translation walks | PTE requests |
| --- | ---: | ---: | ---: | ---: |
| Prefill | 1,119,527 | 45,227 | 20,816 | 20,899 |
| Decode1 | 57,947 | 22,220 | 15,691 | 15,796 |

The checks intentionally exclude non-monotonic gauge fields and
`FIXED_WINDOW_PARTIAL` telemetry. Thus no gauge is mistakenly differenced
and no partial-window cache observation is attributed to an operator.

## Final-arm admission

The final source additionally contributes Prefill F1 and Prefill F8-Lseg20.
Their raw-log SHA-256, frozen framework/Core/binary identity, compute-list
SHA-256, and registration SHA-256 all pass the same parser gates as the
earlier arms. `ARM_OPERATOR_CHARACTERIZATION.tsv`,
`OPERATOR_ARM_DELTAS.tsv`, and `LSEG_OPERATOR_SENSITIVITY.tsv` therefore use
the complete 22-arm formal set. This admission changes no F0 alignment,
parameter-range, or trace-scan evidence.

## Reproduction command

The generated tables can be reproduced read-only from this worktree with:

```bash
g++ -O3 -std=c++17 util/vm_tlb/c12_operator_trace_scan.cc -o /tmp/c12_operator_trace_scan
python3 util/vm_tlb/analyze_c12_operator_aware.py \
  --scanner /tmp/c12_operator_trace_scan --resume \
  --source-commit a268aba0d01310294074ded5bb8017e2092394c0 \
  --arm-status /workspace/worktrees/accel-sim-vm-m4b-speculative/docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/ARM_STATUS.tsv \
  --arm-results /workspace/worktrees/accel-sim-vm-m4b-speculative/docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/ARM_RESULTS.tsv
```

This command only reads frozen trace, sidecar, raw-log, and formal-C12
inputs; it does not invoke `accel-sim.out`.
