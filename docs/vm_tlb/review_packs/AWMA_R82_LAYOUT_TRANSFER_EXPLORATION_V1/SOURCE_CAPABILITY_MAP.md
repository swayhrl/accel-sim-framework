# Source capability map

| Capability | Pinned current Triton source | Installed B0 evidence | R82 treatment |
|---|---|---|---|
| Equivalent/no-op conversion | `minimalCvtLayout`; zero input dimensions replace the op | Triton 3.8.0 binary hash bound; optimized IR inspected | Mandatory baseline; never manufactured as candidate |
| Register-only permutation | one conversion input dimension named `register` | capability matches current lowering family | Mandatory baseline |
| Intra-warp exchange | `cvtNeedsWarpShuffle`, packed shuffle/permutation lowering | FLA selected SASS contains 232 `SHFL`; P1 B0 contains 74/20 | Mandatory baseline; not called free |
| Inter-warp exchange | optimal swizzled shared store/load plus warp/CTA/cluster synchronization | P1 B0 stage1/stage2 allocate 1024 dynamic shared bytes and emit shared operations plus `BAR`; FLA selected variant allocates 10240 bytes | Real finite-resource transfer |
| Source provenance | commit `eb93a9a97e5dfc6a20c29da0096c047dbabd514c`, file blob `f5c1b400...` | package version 3.8.0; exact package source commit is `UNKNOWN`; `libtriton.so` SHA256 `c3306b024133cf76abba389ac00c6dc9cb9127be6a0796aef2acf2134e5f082f` | Binary/hash plus observed relevant codegen qualifies the software control; no stronger commit claim |

## Ordered source paths

1. `QWEN35_0P8B_FLA_GDN_PREFILL64`: Hub FLA `6d22ed1d2bb627375b6ca8fc135f7f417863e639`, `chunk_fwd.py` SHA256 `34230aab3bbdb8cdb200686f56a10d46da152f0a31568fca6950a192f2092031`. Actual accepted prefill cache is inspected. Audit-only because inherited full-model semantics and exact per-binary call attribution are not qualified.
2. `QWEN25_S2_TEXT_D16_L12_FIXED_SPLIT_256`: accepted payload SHA256 `1ceed1e94363d8f459fb19f9e7b0a1196d59702ce43c4a7dcd20203fab38e939`; exact Q/K/V hashes are in the preregistration. This is the sole advanced real target.
3. Not opened: two real paths already exposed nontrivial conversions; no quota-filling third model/kernel.

## Literature boundary

Linear Layouts v5 is the relevant software baseline: it formalizes register/thread/warp mappings, selects no-op/register/shuffle/shared implementations, and evaluates real kernels including RTX4090. Its results are not silently transferred to RTX4080. Tensor Seeks Layout is broader global selection/cost modeling. FIBER is broader shared-register/decoupled execution. No novelty claim is made, so no architecture proposal depends on extending the Round08 abstract audit.
