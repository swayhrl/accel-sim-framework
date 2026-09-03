# Extended-20 E1 CUDA-SDK source audit

Status: **SOURCE/PARAMETER/OUTPUT-CONTRACT RECOVERED — BUILD/PTX/SMOKE PENDING
EXCEPT FWT**

The source authority for this audit is `gpu-app-collection`
`b059fdae25c2aabf737486aada743fca114469ce`, the historical commit that added
the SDK scale-up options.  Historical simulator traces remain runtime-planning
evidence only; they are not formal M5 results.

| Approved ID | source entry | source-backed input | output contract | source SHA-256 | E1 status |
| --- | --- | --- | --- | --- | --- |
| `BlackScholes` | `BlackScholes/BlackScholes.cu` | fixed `OPT_N=100000`, `NUM_ITERATIONS=1` | CPU/GPU L1 norm `<1e-6`, `QA_PASSED` | `7540eeeccf9c5489a51db0aafb99d1ff05488c9ee787c3afdbda0fc078dd452d` | source recovered |
| `convolutionSeparable` | `convolutionSeparable/main.cpp` | `--size 3072` parsed; `imageW=size/8`, `imageH=size/16` | CPU/GPU L2 norm `<1e-6`, `QA_PASSED` | `6953fa19ba12aeea767610510d685bfb792d972dd46df790ae04e1e5748fabc0` | source recovered |
| `fastWalshTransform_11_19` | `fastWalshTransform/fastWalshTransform.cu` | `-logK 11 -logD 19` parsed | L2 norm `<1e-6`, `PASSED` | `284332c572510b2415d23506f72e3d9f879c2c895ddb86e4e1d34b2033d2030e` | source/build/PTX recovered; see `FWT_11_19_E1_RECOVERY.md` |
| `scalarProd_13920` | `scalarProd/scalarProd.cu` | `--size 13920` parsed | CPU/GPU L1 norm `<1e-6`, `QA_PASSED` | `742008e11f8888c5521c913497a1b48fd8de104cbeff2dc6df24f667eab8ab8e` | source/build/PTX recovered; output smoke pending |
| `scan` | `scan/main.cpp` | source-fixed `N=13*(1048576/2)/256`; no workload arguments | exhaustive CPU/GPU scan comparison, `QA_PASSED` | `dba6488710d5d7ba6ac6b11d5441fad389b7e2431881c906047b1b66f0dbd7c0` | source/PTX recovered; executable/output smoke pending |
| `sortingNetworks` | `sortingNetworks/main.cpp` | source-fixed `N=1024`, `numValues=65536`, one iteration | key/value integrity and order validator, `QA_PASSED` | `7460c5b6882bd6a86d086d19319822683831d8fb6021e111898a25d24a6cbfa8` | source/PTX recovered; executable/output smoke pending |
| `transpose` | `transpose/transpose.cu` | `dimX512 dimY512` parsed; square/tile-multiple checks enforce validity | source `compareData`, `QA_PASSED` | `d0817747b77fb9f70c24a2a342f0ff659ddf1ceefeda60a9c62f4ac0ff53c563` | source/PTX recovered; original `shrutil` executable link dependency pending |
| `vectorAdd_6000000` | `vectorAdd/vectorAdd.cu` | `--size 6000000` parsed | elementwise comparison, `QA_PASSED` | `14991a235ab811b5ff4cac639825a4e4238b2af3e3d1ca0a629134db5b5cd3d5` | source/build/PTX recovered; output smoke pending |

All eight use the legacy CUDA-SDK helper layer.  FWT proved that the original
Makefiles' obsolete compute_10--compute_62 targets must be replaced by a
recorded CUDA-11.8 `sm_52` build recipe and frozen helper artifacts.  Reuse
that approach per workload, then record executable/PTX hashes and execute the
source-defined output checker before declaring E1 complete.

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

## transpose PTX recovery and executable-link boundary

The isolated CUDA-11.8 `sm_52` PTX extraction completed with source hash
unchanged:

| Artifact | SHA-256 |
| --- | --- |
| `transpose.ptx` | `6f831e96b1e375ff49deccd5b3bba2bb8b8a46656d898cce54cb22feee0d94ed` |

It exposes the source-defined copy and transpose kernel family, including
`_Z18transposeCoalescedPfS_iii` and `_Z24transposeNoBankConflictsPfS_iii`.
The executable link remains correctly incomplete: the historical source calls
`shrLog`, `shrLogEx`, and `shrSetLogFileName`, while the recovered frozen
`libcutil_x86_64.a` does not define those `shrutil` symbols and no reachable
`gpu-app-collection` historical tree contains their implementation/archive.
Do not substitute a locally invented logger and do not mark the output smoke
as complete; this is a tooling-dependency recovery item, not a DTC or workload
semantic failure.

## scan and sortingNetworks PTX recovery

The CUDA-11.8 `sm_52` PTX extraction succeeds directly from the frozen source
without changing any workload file:

| Workload artifact | SHA-256 | selected PTX entry evidence |
| --- | --- | --- |
| `scan.ptx` | `4f6e50a4f9261d45e629ca41f320263b9b2c7447ef5f430757ab402f8012b722` | `_Z19scanExclusiveSharedP5uint4S0_j`, `_Z20scanExclusiveShared2PjS_S_jj`, `_Z13uniformUpdateP5uint4Pj` |
| `bitonicSort.ptx` | `51183222eae756509ae91d7caf473ebfbf7434439577299ac8dc3127c5c32e17` | shared/global bitonic sort and merge entries |
| `oddEvenMergeSort.ptx` | `55470b3f5ff3f7730bab10116e7b8b820cb5a498c9d9453e98d6605d7c2e1f9a` | shared/global odd-even merge entries |

These are source/PTX identities only.  The host executables and their
source-defined output checkers remain pending until the exact legacy helper
link surface is recovered; no PTX-only artifact is treated as an E1 PASS.

No member enters E2 until M5.2 freezes the common Core/Framework/config/parser
anchor and the complete E1 identity tuple is rechecked.
