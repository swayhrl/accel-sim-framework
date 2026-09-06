# Extended-20 E1 CUDA-SDK source audit

Status: **SOURCE/PARAMETER/BUILD/PTX/OUTPUT-CONTRACT RECOVERED — SIMULATOR
OUTPUT SMOKE PENDING FOR ALL EIGHT MEMBERS**

The source authority for this audit is `gpu-app-collection`
`b059fdae25c2aabf737486aada743fca114469ce`, the historical commit that added
the SDK scale-up options.  Historical simulator traces remain runtime-planning
evidence only; they are not formal M5 results.

| Approved ID | source entry | source-backed input | output contract | source SHA-256 | E1 status |
| --- | --- | --- | --- | --- | --- |
| `BlackScholes` | `BlackScholes/BlackScholes.cu` | fixed `OPT_N=100000`, `NUM_ITERATIONS=1` | CPU/GPU L1 norm `<1e-6`, `QA_PASSED` | `7540eeeccf9c5489a51db0aafb99d1ff05488c9ee787c3afdbda0fc078dd452d` | source/build/PTX recovered; output smoke pending |
| `convolutionSeparable` | `convolutionSeparable/main.cpp` | `--size 3072` parsed; `imageW=size/8`, `imageH=size/16` | CPU/GPU L2 norm `<1e-6`, `QA_PASSED` | `6953fa19ba12aeea767610510d685bfb792d972dd46df790ae04e1e5748fabc0` | source/build/PTX recovered; output smoke pending |
| `fastWalshTransform_11_19` | `fastWalshTransform/fastWalshTransform.cu` | `-logK 11 -logD 19` parsed | L2 norm `<1e-6`, `PASSED` | `284332c572510b2415d23506f72e3d9f879c2c895ddb86e4e1d34b2033d2030e` | source/build/PTX recovered; see `FWT_11_19_E1_RECOVERY.md` |
| `scalarProd_13920` | `scalarProd/scalarProd.cu` | `--size 13920` parsed | CPU/GPU L1 norm `<1e-6`, `QA_PASSED` | `742008e11f8888c5521c913497a1b48fd8de104cbeff2dc6df24f667eab8ab8e` | source/build/PTX recovered; output smoke pending |
| `scan` | `scan/main.cpp` | source-fixed `N=13*(1048576/2)/256`; no workload arguments | exhaustive CPU/GPU scan comparison, `QA_PASSED` | `dba6488710d5d7ba6ac6b11d5441fad389b7e2431881c906047b1b66f0dbd7c0` | source/build/PTX recovered; output smoke pending |
| `sortingNetworks` | `sortingNetworks/main.cpp` | source-fixed `N=1024`, `numValues=65536`, one iteration | key/value integrity and order validator, `QA_PASSED` | `7460c5b6882bd6a86d086d19319822683831d8fb6021e111898a25d24a6cbfa8` | source/build/PTX recovered; output smoke pending |
| `transpose` | `transpose/transpose.cu` | `dimX512 dimY512` parsed; square/tile-multiple checks enforce validity | source `compareData`, `QA_PASSED` | `d0817747b77fb9f70c24a2a342f0ff659ddf1ceefeda60a9c62f4ac0ff53c563` | source/build/PTX recovered; output smoke pending |
| `vectorAdd_6000000` | `vectorAdd/vectorAdd.cu` | `--size 6000000` parsed | elementwise comparison, `QA_PASSED` | `14991a235ab811b5ff4cac639825a4e4238b2af3e3d1ca0a629134db5b5cd3d5` | source/build/PTX recovered; output smoke pending |

All eight use the legacy CUDA-SDK helper layer.  FWT proved that the original
Makefiles' obsolete compute_10--compute_62 targets must be replaced by a
recorded CUDA-11.8 `sm_52` build recipe and frozen helper artifacts.  Reuse
that approach per workload, then record executable/PTX hashes and execute the
source-defined output checker before declaring E1 complete.

## NVIDIA SDK 4.2 `shrutil` recovery

The original `gpu-app-collection` source tree retains the applications but
not the legacy `shrutil` implementation.  The exact missing helper was
recovered from NVIDIA's official CUDA 4.2 Linux GPU Computing SDK archive:
`gpucomputingsdk_4.2.9_linux.run`, SHA-256
`f671601d2656d2f85aca6db5b21b5dad0170ce145281b92777da7f188f96a311`.
Only its `shared` source/headers were extracted in an isolated temporary
directory; no legacy toolkit was installed and no workload source changed.

| Original helper artifact | SHA-256 |
| --- | --- |
| `shared/src/shrUtils.cpp` | `d6177f8e69b10c0f757a620df27c24734a2ab04dcf712bfc6d823d401c645678` |
| `shared/src/cmd_arg_reader.cpp` | `649e7088af739857c8a753469e820d81d3ca292b3af18ac1e516e75358ab0d76` |
| `shared/inc/cmd_arg_reader.h` | `70a4abe9f904657102accee0ae2548be66871660f10af229d36d356b349c27fe` |
| `shared/inc/exception.h` | `339544482d43132e1a1446b3509b106a38b57b6a201a4d59daf410f7e0a862ce` |
| reconstructed `libshrutil_x86_64.a` | `3a16b504d7311059596cd56fffd5d71e89c822c6eb8da980d2025a94b033471b` |

The library is a recorded CUDA-11.8 host rebuild of the original helper
sources, not a handwritten substitute.  It exports the previously unresolved
`shrLog`, `shrLogEx`, and `shrSetLogFileName` symbols.  Linked with the
already frozen CUDA-SDK `libcutil_x86_64.a`, it closes the build-only helper
gap for the five affected SDK workloads below.  Their source-defined output
smokes remain required before E1 PASS.

## vectorAdd CUDA-11.8 build recovery

The isolated `sm_52` CUDA-11.8 reconstruction, using the frozen helper
headers and `libcutil_x86_64.a` already identified in
`FWT_11_19_E1_RECOVERY.md`, completed without source changes:

| Artifact | SHA-256 |
| --- | --- |
| `vectorAdd` executable | `9e918f96f53d53cd0c398363347e5b0fcfd8731e35df5a8e846c8e034e0051f3` |
| `vectorAdd.ptx` | `cec2086a1c730e34fc8d9f9c0cc89d90d04b65f225854cb3ef8cf81accc12a59` |

The PTX exposes `_Z6VecAddPKfS0_Pfi`.  This is build provenance only; no
simulator output smoke was launched while the controlled M5.0B worker pool is
at its recorded safe concurrency.

## scalarProd CUDA-11.8 build recovery

`scalarProd.cu` source-includes `scalarProd_kernel.cu`; the latter is a build
dependency, not a separate link unit.  The isolated CUDA-11.8 `sm_52` build
therefore used the top-level CUDA source plus `scalarProd_gold.cpp` and the
same frozen helper set:

| Artifact | SHA-256 |
| --- | --- |
| `scalarProd` executable | `4105a92a3a45d3b9267743ee75bccfb696745893fd3bfa411854ec0c310c9445` |
| `scalarProd.ptx` | `88dfcd7c0ef9190b87a01dc64b5bd1d9e92c3d2b5c4d2ec1881ea52dbe1f3aa1` |

The PTX exposes `_Z13scalarProdGPUPfS_S_ii`.  This is build provenance only;
its source-defined output smoke remains queued behind the M5.0B worker-pool
closeout.

## transpose build/PTX recovery

The isolated CUDA-11.8 `sm_52` PTX extraction completed with source hash
unchanged:

| Artifact | SHA-256 |
| --- | --- |
| `transpose` executable | `2a1dadb36963a1f2847c0c9460f2091d78fab7c25eec1d045c4fc85374fa0573` |
| `transpose.ptx` | `6f831e96b1e375ff49deccd5b3bba2bb8b8a46656d898cce54cb22feee0d94ed` |

It exposes the source-defined copy and transpose kernel family, including
`_Z18transposeCoalescedPfS_iii` and `_Z24transposeNoBankConflictsPfS_iii`.
The original-SDK `shrutil` recovery closes the host link without changing the
workload.  Its `compareData`/`QA_PASSED` output smoke remains pending.

## scan and sortingNetworks PTX recovery

The CUDA-11.8 `sm_52` PTX extraction succeeds directly from the frozen source
without changing any workload file:

| Workload artifact | SHA-256 | selected PTX entry evidence |
| --- | --- | --- |
| `scan.ptx` | `4f6e50a4f9261d45e629ca41f320263b9b2c7447ef5f430757ab402f8012b722` | `_Z19scanExclusiveSharedP5uint4S0_j`, `_Z20scanExclusiveShared2PjS_S_jj`, `_Z13uniformUpdateP5uint4Pj` |
| `bitonicSort.ptx` | `51183222eae756509ae91d7caf473ebfbf7434439577299ac8dc3127c5c32e17` | shared/global bitonic sort and merge entries |
| `oddEvenMergeSort.ptx` | `55470b3f5ff3f7730bab10116e7b8b820cb5a498c9d9453e98d6605d7c2e1f9a` | shared/global odd-even merge entries |

| Executable | SHA-256 |
| --- | --- |
| `scan` | `ccde0db460fdc40f3a7671e541de2b103d6cb7f9a1baf9a9e803f1ffbd1fd305` |
| `sortingNetworks` | `5e35f98af2db0b2ca74f6051673f854d13a943d73ca30fd1bc0a3841c0eaecb5` |

Both host builds use the recovered original SDK helper.  Their source-defined
output checkers remain pending; no build-only artifact is treated as E1 PASS.

## convolutionSeparable PTX recovery

The CUDA-11.8 `sm_52` extraction from the frozen
`convolutionSeparable.cu` source succeeds without changes:

| Artifact | SHA-256 | PTX entries |
| --- | --- | --- |
| `convolutionSeparable` executable | `089fa57a17c51f9b634d8c32de5f3d5d2395f03746f41d038358227363df1d09` | n/a |
| `convolutionSeparable.ptx` | `6642ed9bb4cff7627b7f2d2318770203ea996dc6b15a4bd9b422afad5e8c4f8c` | `_Z21convolutionRowsKernelPfS_iii`, `_Z24convolutionColumnsKernelPfS_iii` |

The source-defined `--size 3072` host setup and L2-norm checker remain part
of the required executable/output smoke.  PTX extraction alone does not close
that E1 member.

## BlackScholes PTX recovery

The source is the approved Black-Scholes option-pricing workload (not a Monte
Carlo substitution).  Its isolated CUDA-11.8 `sm_52` PTX extraction preserves
the recovered fixed input contract:

| Artifact | SHA-256 | PTX entry |
| --- | --- | --- |
| `BlackScholes` executable | `4eeb72dbddbf3246d54a6ead4dff63a0d8acb77c805d5afb4f8d3b1cc7c81356` | n/a |
| `BlackScholes.ptx` | `301372d7f0f6fe0e02cf74605b325c9f8c0bb9808b7448cb97f9d954cbacf489` | `_Z15BlackScholesGPUPfS_S_S_S_ffi` |

The executable now links only through the recovered original-SDK helper
sources.  Its source-defined L1-norm `QA_PASSED` smoke remains pending.

No member enters E2 until M5.2 freezes the common Core/Framework/config/parser
anchor and the complete E1 identity tuple is rechecked.

## Offline source-object revalidation (2026-09-06)

The eight approved source-file SHA-256 values in the first table were
independently recomputed directly from the clean GPU App Collection object
database at commit `b059fdae25c2aabf737486aada743fca114469ce`; all eight
match exactly.  The available clean checkout remains at
`dad09cb0487845edc7524ded814c6cde9f0ef6a1` with no worktree changes, so the
historical source commit is read by object identity rather than inferred from
the checkout tip.  This is source-provenance revalidation only: it neither
reruns nor rehashes the isolated executable/PTX artifacts, freezes generated
inputs, executes an output smoke, or changes the M5.2 E2 gate.

## BlackScholes local `sm_70` build preflight (2026-09-06)

An isolated, non-executing CUDA 11.8 build preflight reconstructed the exact
SDK 4.2 `BlackScholes` source object for `sm_70`. This is host-side build
evidence only: SIM_HOST has no visible GPU, so it does **not** establish a
real-V100 executable identity, a source-defined `QA_PASSED` output verdict,
or trace-capture eligibility.

| item | identity / result |
| --- | --- |
| source commit | `gpu-app-collection@b059fdae25c2aabf737486aada743fca114469ce` |
| source inputs | `BlackScholes.cu` `7540eeeccf9c5489a51db0aafb99d1ff05488c9ee787c3afdbda0fc078dd452d`; `BlackScholes_gold.cpp` `33d9a614eca99e4907711236161aa9799cefa68cce34d758132a634675b136dc`; `BlackScholes_kernel.cuh` `1a49728f87f3b95bbeb05e9d7e8b9a04854901a8f9993437db71c399ab829dbf` |
| compatibility inputs | original-SDK `libshrutil_x86_64.a` `3a16b504d7311059596cd56fffd5d71e89c822c6eb8da980d2025a94b033471b`; frozen `libcutil_x86_64.a` `ebc5bcfe63ec81ece16dd14ee57811c780e93df1776a49a04d62f800e989e412`; `cutil_inline.h` `c7abcf2902af637e6c83ff677c74135aaaa706879ddbccf3190ce48b06278ddc`; `shrQATest.h` `07f691c08d7bac6ee3ca93169e6a9288a3d4d1a2bc855af1c1beb340877f7f55` |
| toolchain | CUDA 11.8.89 `nvcc`; `-arch=sm_70 -O2 -cudart shared` |
| raw linked executable | first isolated build SHA-256 `1d581ce9830e6e60a9856bdd213670239d518773dd166bd372203bd6a5c87895`; do not use as the canonical artifact because nvcc emits a per-build temporary local symbol name |
| canonical executable | `strip --strip-unneeded` after link: two independently materialized builds are byte-identical at SHA-256 `ccbb7ebec30a02cc8ad00c726f4af524dceb175352dd3d6cc424917f467d5639` |
| PTX | SHA-256 `dc3f48102d762167cece9f06ee353a4aba4cb0651493d12cc261e970bdbaccc3`; expected `_Z15BlackScholesGPUPfS_S_S_S_ffi` entry present |
| classification | `LOCAL_SM70_BUILD_PREFLIGHT_PASS`; retain `SOURCE_READY`, not `BUILD_READY` |

The V100 step must rebuild from the same inputs (or prove byte-identical
toolchain equivalence), execute the source-defined L1-norm `QA_PASSED`
checker, freeze input/runtime/launch identities, and then complete the
dynamic trace-semantic audit. This preflight must not be substituted for
those physical-device gates.

The post-link stripping is an artifact-normalization step only. The two raw
ELFs differ only in nvcc-generated local `tmpxft_*` names in `.strtab`; their
dynamic symbol tables and `.nv_fatbin` sections are byte-identical. The
canonical stripped artifacts are byte-identical, retain the same dynamic-link
surface and fatbin, and do not change workload source, CUDA launch geometry,
or any simulated mechanism. M5-E1-003 records the recovery and regression.

## VectorAdd and scalarProd local `sm_70` build preflights (2026-09-06)

Each row below was materialized twice from the frozen SDK 4.2 object, built
with CUDA 11.8 `-arch=sm_70 -O2 -cudart shared`, and normalized with the
M5-E1-003 post-link rule.  The two canonical ELFs and the two PTX files match
byte-for-byte for each workload; generated artifacts remain outside Git.

| workload | source / helper identity | canonical stripped executable | PTX / entry proof |
| --- | --- | --- | --- |
| `vectorAdd_6000000` | `vectorAdd.cu` `14991a235ab811b5ff4cac639825a4e4238b2af3e3d1ca0a629134db5b5cd3d5`; `sdkHelper.h` `cb528eeda1e7acd502e5eabcfbecf7d7e2be4cf3a135e6acd264552bd1cc2139`; frozen `libshrutil` / `libcutil` identities above | `a094fb3127f036f4093df19af97514178d5e8f31802811e4ee055772b6369dbf` | `1a07ff58ad7d971fa715e9431ae4e82b42d2a6ba8bc4f54837335b18fef19d21`; `.target sm_70`, `_Z6VecAddPKfS0_Pfi` |
| `scalarProd_13920` | `scalarProd.cu` `742008e11f8888c5521c913497a1b48fd8de104cbeff2dc6df24f667eab8ab8e`; `scalarProd_gold.cpp` `92ba199e8966651519e7e504cdb45c9a9cbf9498b100fb771898e159ec47f611`; `scalarProd_kernel.cu` `49a6709c6ceded5a52f0d1c965999f240defd855f9bf82e07d622516f12b2c76` | `ad32f09b32e0027fec23ec4b98819f27339fedca5133c61b9f23c8931985e701` | `3f353726337a2d64611f23c3d6a5a643253d0ff570e2d763f478cc60e5fb481e`; `.target sm_70`, `_Z13scalarProdGPUPfS_S_ii` |

SIM_HOST did not execute either binary because it has no visible GPU. The
approved `--size 6000000` and `--size 13920` V100 output-smoke identities,
their source-defined verdicts, and dynamic trace-semantic audits remain
mandatory. Both rows remain `SOURCE_READY`, not `BUILD_READY` or
`TRACE_CAPTURE_READY`.

## Transpose, scan, and sortingNetworks local `sm_70` build preflights (2026-09-06)

Each candidate was independently materialized twice from the exact SDK 4.2
tree, built with the same CUDA 11.8 `sm_70` recipe, and normalized under
M5-E1-003.  Canonical executable and PTX identities are byte-identical within
each workload; no generated artifact is committed.

| workload | SDK 4.2 tree / selected source | canonical stripped executable | PTX / entry proof |
| --- | --- | --- | --- |
| `transpose` | tree `813b148eae62d93be6ee04a3036a357ed5d93783`; `transpose.cu` `d0817747b77fb9f70c24a2a342f0ff659ddf1ceefeda60a9c62f4ac0ff53c563` | `32d1117cc6ca10e9603579b951e52b1ecc3eaaf903ca33d3bb8503c03191bd1f` | `7aaf1e3e0c7f4630f00c5cbbcceae53c35032d6b0186862f4a33c855a8e3c43c`; `.target sm_70`, copy/coalesced/no-bank-conflict kernels present |
| `scan` | tree `2657e8dfa1feb3dcccb876f8b9b430c40b7ba7e8`; source set `scan.cu`, `main.cpp`, `scan_gold.cpp`, `scan_common.h` is frozen by that tree | `de62da05169fc396c0b4d30e9c567ebfd2375f9748bfe262ea336fb5942b2545` | `299081b50a3100ffbb5b4f343bb7766dee7cccb2ed86da47c578cf51675c443b`; `.target sm_70`, shared scan and uniform-update entries present |
| `sortingNetworks` | tree `52b68c51622139c6c5042fa20bc7a7725d997d27`; `main.cpp` `7460c5b6882bd6a86d086d19319822683831d8fb6021e111898a25d24a6cbfa8`, with the two exact kernel source files in the tree | `6ccc7c1c7da8076875f3428264b3f9342e83d173d672454aec45bb2e41d16b32` | bitonic `70c564fbd016b9a210b83af5ca9ff7c124d8ee65f9d993fb1ce5c392b516f407`, odd-even `4ddbeb0569cccb6603db60ab87d374a00841d247c7b16dad0b7c905a81618093`; both `.target sm_70` with expected shared-sort entries |

None of these local builds executed a source-defined output checker on a V100,
and no dynamic trace-semantic audit has occurred.  Their approved real-device
input/launch/output identities remain mandatory; all three remain
`SOURCE_READY`, not `BUILD_READY` or `TRACE_CAPTURE_READY`.
