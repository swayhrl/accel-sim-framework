# M4 workload manifest

Status: **FINAL -- provenance resolved and accepted M4 triplets completed**.

All accepted triplets use an isolated copy of the named source directory, the
same extracted PTX/input/binary for Base/IO/OO, the Core runtime built from
`cdeec769fd0c1be12b45d58536ecb81074d4b415`, and differ only in
`-gpgpu_dtc_l1_mode` (`1`, `2`, or `3`).  No workload is silently renamed or
substituted.  Each accepted triplet must report matching dynamic
Load/Store/Atomic/source-reachable-FENCE_OP counts, with FENCE_OP zero under
the frozen frontend.

| ID | Source workload / invocation | Mapping status | Behavior | M4 disposition |
| --- | --- | --- | --- | --- |
| PB_ATAX | `polybench-gpu-wrapper/pb_atax`, `./pb_atax` | EXACT_MATCH | streaming matrix-vector | accepted Base/IO/OO triplet |
| PB_GEMM | `polybench-gpu-wrapper/pb_gemm`, `./pb_gemm` | EXACT_MATCH | dense matrix multiply | accepted Base/IO/OO triplet |
| PB_FDTD2D | `polybench-gpu-wrapper/pb_fdtd2d`, `./pb_fdtd2d` | SOURCE_EQUIVALENT_CONFIRMED | 2D stencil | accepted Base/IO/OO triplet |
| PB_2DCONV | `polybench-gpu-wrapper/pb_2dconv`, `./pb_2dconv` | SOURCE_EQUIVALENT_CONFIRMED | 2D convolution | recovery diagnostic only; IO/OO passed, Base is SLOW_BUT_PROGRESSING and is not an accepted final triplet |
| PARBOIL_SPMV | `parboil-wrapper/spmv`, `./spmv -i data/fidapm05.mtx,data/tiny_vec.bin` | EXACT_MATCH | sparse irregular SpMV | accepted Base/IO/OO triplet |
| PARBOIL_SGEMM | `parboil-wrapper/sgemm` driver/input as supplied by its wrapper | SOURCE_EQUIVALENT_CONFIRMED | dense SGEMM | accepted Base/IO/OO triplet |
| VECADD | existing extracted `vecadd` micro-workload | APPROXIMATE_PROXY | directed load/store completion smoke | R4C.6 regression only; not counted as a Chapter-4 workload substitute |
| M4_MIXED_CG | isolated temporary CUDA source, normal load + `ld.global.cg` + store + same-address atomic | DIRECTED_GATE | source-reachable lifecycle sequence | MIX01/BP01/BP02 only; not counted as a Chapter-4 workload substitute |
| bicg/mvt/syrk/syr2k/2mm/gesummv/gemv | no matching ready binary/input was found in the active workload checkout | UNRESOLVED | -- | not substituted or counted |

Historical `runs/*/provenance.txt` files establish the ready source roots for
PB_ATAX, PB_GEMM, PB_FDTD2D, and PARBOIL_SPMV.  Every new M4 result records its
source/config/log SHA-256 and is parsed by
`util/dtc_l1/parse_dtc_l1_summary.py --strict` before it can be accepted.
