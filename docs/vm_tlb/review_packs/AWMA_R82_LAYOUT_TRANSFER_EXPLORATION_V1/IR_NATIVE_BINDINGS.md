# IR to native bindings

## P1 qualified target

| Config | TTGIR SHA256 | PTX SHA256 | cubin SHA256 | warps | dynamic shared B | regs/thread | SASS SHFL | SASS LDS | SASS STS | SASS BAR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| r82_b0_stage1 | 32b5052eac182c2d53e8aa2845dac1831b8a32f3e2b069d87660957bc776fe7b | ac5f9c5e933439ce0fb3b20f7566c4b025288d0378534cbc9a0945857d652f1e | ca6289cd31f9905812ecb7a5d1b05923b834a7491389f243f6f2fa9c08e4a2c8 | 8 | 1024 | 58 | 74 | 7 | 8 | 13 |
| r82_b0_stage2 | 57372eeef018d8aec522777bbe541cc9f6369ae1fa7ce6e7e3318e10df212bc0 | f0813403c6f77d7471517800b957506b577a1c76984b199333f497b303720319 | 68c9cb905767f1f63083c99be1499554700ef7f7acb57e8b7081737b032fbb6a | 4 | 1024 | 26 | 20 | 3 | 6 | 5 |
| r82_c1_stage1 | b95092ca6cf4db84076f016a59b41f63246d48388da2642ba5f3582737cf70ad | 5310595b16b6a46c67dd65ac3276b8ce843d9176a9fa03471548049b687b4efd | 675a858dc12a7a7fa0330d053f6765188fb620a2ff0d541d4a55f2b0915c38b8 | 8 | 1024 | 58 | 74 | 7 | 8 | 13 |
| r82_c1_stage2 | 032f0f7aa4607af0c43baafcae6cbe2fc0d59ff78b5e32af1cf5d3b21e976bdb | 4749004efb2fe389d2af716d6049b6e92c7f322a31a3155d674a9cfde59e2139 | 864e2abf7f54d3c654bba74fd76810d72de4fd4d8803fd775e06867dee44f851 | 4 | 1024 | 26 | 20 | 3 | 3 | 5 |

B0 and C1 each retain exactly one `ttg.convert_layout` in stage1 and one in stage2. B0 stage1 maps `slice<blocked>` to a 1-D blocked store layout; B0 stage2 maps the combined 64-element result similarly. Their source-line PTX ranges contain shared staging and CTA barriers, and their layouts distribute ownership over 8 and 4 warps respectively. They are `INTER_WARP_SHARED`, not legal warp-shuffle-only cases.

C1 preserves the singleton reduction dimension. The resulting destination is a sliced blocked layout, but the compiler still requires inter-warp redistribution. Stage1 native counts are identical to B0. Stage2 reduces SASS `STS` from 6 to 3, with registers 26, dynamic shared 1024 B, `SHFL` 20, `LDS` 3, and `BAR` 5 unchanged.

## FLA audit-only path

Selected accepted cache ID `GCQQ6DY2Q5CTNDQ4X5NOST7AUHLNZK6MMXDIKNKXLU5G5Y4JX24Q` binds a real Qwen3.5 prefill `chunk_gated_delta_rule_fwd_kkt_solve_kernel`: 55 optimized-IR conversions, 4 warps, 10240 B dynamic shared, 228 registers/thread, 232 SASS shuffles, 111 LDS, 57 STS, and 50 BAR instructions. The accepted NSYS table aggregates 601 launches for the 128-thread kernel family but does not bind each launch to this exact cubin; exact dynamic multiplicity is therefore `UNKNOWN`.

`CONVERSION_LEDGER.tsv` contains 59 rows: {'INTER_WARP_SHARED': 29, 'INTRA_WARP_SHUFFLE': 25, 'OTHER_UNKNOWN': 5}. Source-line attribution is useful for IR/native correspondence but is not an exclusive time decomposition; shared or barrier instructions on the same source line may also serve reductions/MMA pipelines.
