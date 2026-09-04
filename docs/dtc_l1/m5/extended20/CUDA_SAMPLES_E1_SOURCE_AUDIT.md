# Extended-20 E1 CUDA Samples source audit

Status: **SOURCE MATERIALIZED — BUILD/PTX/INPUT/OUTPUT FREEZE PENDING**

This is an E1 source-provenance record only.  It does not authorize a build,
a simulator run, or an Extended M5.E2 result.  In particular, it does not
silently substitute the current CUDA Samples behavior for a historical
parameterized workload label.

## Reproducible source materialization

The `gpu-app-collection` clean-source gitlink recorded in
`M5_E1_EXTENDED20_FORMALIZATION.md` was materialized in a new, isolated,
clean checkout:

| field | value |
| --- | --- |
| upstream | `https://github.com/NVIDIA/cuda-samples.git` |
| required gitlink commit | `db3eea23946bca2e90a75eca2b5b3e07158a9e11` |
| detached checkout HEAD | `db3eea23946bca2e90a75eca2b5b3e07158a9e11` |
| checkout location | `/tmp/dtc-l1-m5-e1-cuda-samples.bLsXEe` |
| working-tree state | clean before this audit |

The checkout is an E1 source input, not a Framework artifact.  Its absolute
path is recorded only to make this particular evidence reviewable; the commit
and upstream URL are the reproducible identity.

## Selected-source inventory

All paths below are tree objects in the detached commit.  `CMakeLists.txt`
hashes identify the source-defined target construction.  No executable or PTX
hash is claimed before an isolated reproducible build.

| approved workload | source path | source tree Git object | CMake SHA-256 | source compatibility finding |
| --- | --- | --- | --- | --- |
| `BlackScholes` | `Samples/5_Domain_Specific/BlackScholes` | `d3dcb338b2fc0385f5d108dd0431888b6d659784` | `bb5373ee5f75457a874e9fd8db20ddd148604d8573f3a9fe81a2a0090374a65b` | target `BlackScholes` exists; deterministic workload/input and source verdict remain to be frozen. |
| `convolutionSeparable` | `Samples/2_Concepts_and_Techniques/convolutionSeparable` | `1af59ff1246d536f020268aa59a63e9064c6cb69` | `d44c96b15b93d16c6476f919440c41e92a5488c5d25789084256aa6ed85d8fb0` | target exists; the pre-existing `--size 3072` lead is not accepted until this source's argument handling is established. |
| `fastWalshTransform_11_19` | `Samples/5_Domain_Specific/fastWalshTransform` | `0e17f9a6b89547956632112db296e815373bb376` | `bd8ee007cc7792a6e52df7c6b55d5bbf483ed0448a775c732fe80d7d17b2dd33` | target exists, but this revision does not establish the required legacy `-logK 11 -logD 19` contract.  Keep `FWT_11_19_E1_RECOVERY.md`'s recovered `b059fdae…` source separate; do not mix source and parameter identities. |
| `scalarProd_13920` | `Samples/2_Concepts_and_Techniques/scalarProd` | `332d9d9c5a472cd6d8df5206cb5daf98278c58d8` | `3a7e8bdd5b508ef02b8de6b7d06ede29638b3a885b3923d92ca4e7323d811f9e` | target exists; the historical `13920` parameter is not frozen by this source audit. |
| `scan` | `Samples/2_Concepts_and_Techniques/scan` | `2bf2367d48239ae572fd7922dec82f7d0ae136a4` | `796a5f5892558137905eef3ff533d52e725bf73567f5cf6cfb822767f1687844` | target exists; launch/input/verdict still require source-level recovery. |
| `sortingNetworks` | `Samples/2_Concepts_and_Techniques/sortingNetworks` | `d45c743584c6d5c971cd5ce2adf38ef287cdae1e` | `f6e9ad15366246bb457a19f7eb04f23b8bd52da8d22f8f4be09e647df19f2c79` | target exists; launch/input/verdict still require source-level recovery. |
| `transpose` | `Samples/6_Performance/transpose` | `a253522af50cd76bb0642c548016d77114eee9ac` | `ae774eeec6b80debbd85abdbd9139d6b8fee7ac284a10b9473cf9f45869b9e80` | target exists and source parses `-dimX`/`-dimY`; the exact `512x512` launch remains pending an isolated source/build check. |
| `vectorAdd_6000000` | `Samples/0_Introduction/vectorAdd` | `5a8383caf34d0f1563c8f4faa5c5c12ddb201418` | `2d4e74b6c1fc65bca68cd1140c193c90b9934105ddffa4b5e416fc8adbb09ff2` | target exists, but this revision hard-codes `numElements = 50000`; it is not source-equivalent to the approved 6,000,000-element label.  Recover a compatible source or source-backed wrapper before E1 acceptance. |

## Explicit boundaries

- The CUDA-11-style current sample tree is **not** evidence that the approved
  parameterized labels have equivalent work amounts.
- The `fastWalshTransform_11_19` identity remains the separately recovered
  legacy SDK source and must retain its exact executable/PTX/input/verdict
  trail.
- `vectorAdd_6000000` must not be downgraded to the current source's
  hard-coded 50,000-element run.
- E1 stays incomplete until all build, executable, PTX, input, output-check,
  and launch identities are frozen; M5.E2 remains blocked on M5.2.
