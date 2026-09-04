# Extended-20 E1 legacy CUDA SDK 4.2 parameterized-source audit

Status: **SOURCE/PARAMETER CONTRACT RECOVERED — BUILD/PTX/INPUT/OUTPUT FREEZE PENDING**

The current CUDA Samples gitlink is a clean source input, but it is not
automatically source-equivalent to the approved historical parameterized
labels.  The relevant CUDA SDK 4.2 source is available in the clean GPU App
Collection history at the exact commit below.

| field | value |
| --- | --- |
| repository | `gpu-app-collection` |
| source commit | `b059fdae25c2aabf737486aada743fca114469ce` (`Adding scale-up options for 4 sdk apps`) |
| source root | `src/cuda/sdk/4.2/` |
| source access | clean repository object database; identities below are Git tree objects |
| build/run status | **not attempted during the active Paper-10 Base batch** |

## Exact source paths and parameter evidence

| approved workload | source path | tree Git object | source-backed command/input contract | source-defined verdict | E1 state |
| --- | --- | --- | --- | --- | --- |
| `BlackScholes` | `BlackScholes` | `dadb4787d9c05a78e86e91259f2d1e4df8d2bab7` | fixed `OPT_N = 100000`; no approved scale suffix is inferred | CPU/GPU L1 norm, `QA_PASSED` | build/PTX pending |
| `convolutionSeparable` | `convolutionSeparable` | `1b7beaa703800b27a3f63e2c55010d0695ecfd19` | `--size 3072`; derives `imageW=size/8`, `imageH=size/16` | L2 norm `< 1e-6`, `QA_PASSED` | build/PTX pending |
| `fastWalshTransform_11_19` | `fastWalshTransform` | `c3c37d39b9ab05ea6f97c75586cd14d500e37c40` | `-logK 11 -logD 19`; see `FWT_11_19_E1_RECOVERY.md` | L2 norm `< 1e-6`, `QA_PASSED` | simulator smoke pending |
| `scalarProd_13920` | `scalarProd` | `01adfd3922dd424b1f32f8a9df47fc5e4bff97a6` | `--size 13920` sets `VECTOR_N`; `DATA_N = VECTOR_N * 1024` | L1 norm `< 1e-6`, `QA_PASSED` | build/PTX pending |
| `scan` | `scan` | `2657e8dfa1feb3dcccb876f8b9b430c40b7ba7e8` | deterministic source default `N = 13 * (1048576 / 2) / 256` | source comparison, `QA_PASSED` | build/PTX pending |
| `sortingNetworks` | `sortingNetworks` | `52b68c51622139c6c5042fa20bc7a7725d997d27` | deterministic source default; exact launch work remains build-time recovery work | source validation flag, `QA_PASSED` | build/PTX pending |
| `transpose` | `transpose` | `813b148eae62d93be6ee04a3036a357ed5d93783` | `-dimX 512 -dimY 512` parsed by `getParams` | source check, `QA_PASSED` | build/PTX pending |
| `vectorAdd_6000000` | `vectorAdd` | `aa706c52ca5040466171c4043a6c334a0f7e23da` | `--size 6000000` is parsed by `ParseArguments` into `N` | elementwise check, `QA_PASSED` | build/PTX pending |

## Fidelity boundaries

- Do not reuse a current CUDA Samples binary for this legacy SDK 4.2 source
  identity.
- The common source commit is recorded before any Paper/DTC performance
  result; it neither changes selection nor selects a scale using DTC behavior.
- A future E1 build must materialize this exact commit in an isolated source
  tree, retain toolchain/build-command hashes, extract PTX separately, and
  freeze executable/PTX/input/verdict identities.
- M5.E2 remains blocked on M5.2's common formal anchor.
