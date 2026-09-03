# Extended-20 E1 recovery — fastWalshTransform_11_19

Status: **SOURCE/BUILD/PARAMETER RECOVERED — SIMULATOR OUTPUT SMOKE PENDING**

This is E1 preparation only.  It neither promotes historical traces to formal
M5 evidence nor authorizes an E2 run before the M5.2 common anchor.

## Recovered source identity

The exact parameterized source is `gpu-app-collection` commit
`b059fdae25c2aabf737486aada743fca114469ce` (`Adding scale-up options for 4
sdk apps`), path `src/cuda/sdk/4.2/fastWalshTransform/`.  In contrast to the
later CUDA-11 sample, its `ParseArguments` consumes `-logK`/`--logK` and
`-logD`/`--logD` before setting `log2Kernel`/`log2Data`.

| source member | SHA-256 |
| --- | --- |
| `fastWalshTransform.cu` | `284332c572510b2415d23506f72e3d9f879c2c895ddb86e4e1d34b2033d2030e` |
| `fastWalshTransform_gold.cpp` | `a505c0c951ac03681d573edc76faaad79b5a50198cca4f77e251770da3461ab6` |
| `fastWalshTransform_kernel.cu` | `2814fd1baab947978a42fa7c0823492923e4e027e9fe2cf901ee6c628451d30f` |

The compatibility helpers required by this legacy SDK source are frozen by
path and hash, rather than silently replaced: `cutil_inline.h`
`c7abcf2902af637e6c83ff677c74135aaaa706879ddbccf3190ce48b06278ddc`,
`shrQATest.h`
`07f691c08d7bac6ee3ca93169e6a9288a3d4d1a2bc855af1c1beb340877f7f55`,
and `libcutil_x86_64.a`
`ebc5bcfe63ec81ece16dd14ee57811c780e93df1776a49a04d62f800e989e412`.

## Frozen candidate input and output contract

The candidate command is exactly:

```text
fastWalshTransform -logK 11 -logD 19
```

The source derives dimensions `kernelN=2^11` and `dataN=2^19`, then fills both
arrays with `srand(2007)`.  It compares CPU and GPU results using the L2 norm
and accepts only `L2norm < 1e-6`, printing `PASSED` and exiting through
`shrQAFinishExit(..., QA_PASSED)`.  This source-defined verdict is the future
M5 output checker; the historic trace label alone is not one.

## Isolated build reproduction

The legacy Makefile's compute_10--compute_62 list is obsolete for CUDA 11.8.
The recovered source was instead built in an isolated temporary directory with
CUDA 11.8 `nvcc`, `-arch=sm_52 -O2 -cudart shared`, explicit compatibility
include paths, and the frozen static `libcutil_x86_64.a`.  The linked binary
SHA-256 is `803c30e66c9fdd1351ca160339dda5a36ed50f8622d04e542ec7bda36529fa4b`.
An independent `nvcc -arch=sm_52 -O2 -ptx` extraction produces PTX SHA-256
`6f686af5312be4c91922ae0e7d30e60bb64fc1413addd4aeb7aefac07c3bd387`, with
the expected `fwtBatch1Kernel`, `fwtBatch2Kernel`, and `modulateKernel` entry
points.

## Remaining E1 gate

Run this exact binary/PTX under the future M5 formal runtime/config only after
the common M5.2 anchor is frozen; require the source-defined `PASSED` output,
strict parser/provenance capture, and explicit simulator compatibility.  The
pre-existing L2 trace manifest remains historical runtime-planning evidence
only and is not reused as a formal M5 result.
