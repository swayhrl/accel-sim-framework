# Bounded parser compatibility

The parser compatibility anchor is Core
`73774727e25fadf89df6f30ef5cf014091115db7` with the retained SM86 RTX 3070
`gpgpusim.config` and Accel-Sim SM86 `trace.config`. This is an offline format
and startup check only.

For each ROI, a separate one-entry list was constructed as a symlink-only
scratch fixture and run with a 15-second bound. Every sample read its specified
trace and reached `bind to kernel 1`; a timeout status `124` means the bounded
smoke was intentionally stopped after successful bind, while `0` means that
small sample completed within the bound.

| ROI | Semantic samples | Outcome |
|---|---|---|
| prefill | early `indexSelectLargeIndex`, middle vectorized add, late BF16 GEMM, NCCL AllReduce | all bound (bounded timeout) |
| decode1 | early `indexSelectSmallIndex`, middle vectorized add, late BF16 GEMM, NCCL AllReduce | all bound (completed or bounded timeout) |
| prefill/decode1 | corrected compute-only derivative startup | both bound |

There is one observed NCCL semantic family in each ROI,
`_Z40ncclDevKernel_AllReduce_Sum_bf16_TREE_LLP11ncclDevCommmP8ncclWork`; it
also bound. This does not decide whether later integration simulates the full
rank-0 order or its compute-only derivative. That policy is
`DEFER_TO_M4B_INTEGRATION`.
