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
| `scalarProd_13920` | `scalarProd/scalarProd.cu` | `--size 13920` parsed | CPU/GPU L1 norm `<1e-6`, `QA_PASSED` | `742008e11f8888c5521c913497a1b48fd8de104cbeff2dc6df24f667eab8ab8e` | source recovered |
| `scan` | `scan/main.cpp` | source-fixed `N=13*(1048576/2)/256`; no workload arguments | exhaustive CPU/GPU scan comparison, `QA_PASSED` | `dba6488710d5d7ba6ac6b11d5441fad389b7e2431881c906047b1b66f0dbd7c0` | source recovered |
| `sortingNetworks` | `sortingNetworks/main.cpp` | source-fixed `N=1024`, `numValues=65536`, one iteration | key/value integrity and order validator, `QA_PASSED` | `7460c5b6882bd6a86d086d19319822683831d8fb6021e111898a25d24a6cbfa8` | source recovered |
| `transpose` | `transpose/transpose.cu` | `dimX512 dimY512` parsed; square/tile-multiple checks enforce validity | source `compareData`, `QA_PASSED` | `d0817747b77fb9f70c24a2a342f0ff659ddf1ceefeda60a9c62f4ac0ff53c563` | source recovered |
| `vectorAdd_6000000` | `vectorAdd/vectorAdd.cu` | `--size 6000000` parsed | elementwise comparison, `QA_PASSED` | `14991a235ab811b5ff4cac639825a4e4238b2af3e3d1ca0a629134db5b5cd3d5` | source recovered |

All eight use the legacy CUDA-SDK helper layer.  FWT proved that the original
Makefiles' obsolete compute_10--compute_62 targets must be replaced by a
recorded CUDA-11.8 `sm_52` build recipe and frozen helper artifacts.  Reuse
that approach per workload, then record executable/PTX hashes and execute the
source-defined output checker before declaring E1 complete.

No member enters E2 until M5.2 freezes the common Core/Framework/config/parser
anchor and the complete E1 identity tuple is rechecked.
