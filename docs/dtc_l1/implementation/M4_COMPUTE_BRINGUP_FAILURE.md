# M4 compute bring-up failure — PolyBench 2DConv

Status: **HARD FAILURE — STOP**

Date: 2026-09-03. This supersedes the prior fence-only stop as the active
M4 blocker. The fence reachability resolution remains applicable, but its
F00/F01 disposition cannot close M4 while a source-reachable compute workload
fails a DTC correctness assertion.

## Reproduction identity

- Core branch/SHA: `hrl/decoupled-l1-m1m4-v0`
  `56a9230e4a538b69a30673ebdf66c42526fb324a`.
- Framework branch/SHA before this evidence commit:
  `hrl/decoupled-l1-exp-m1m4-v0`
  `8d7174942bdcc458a3b929348a84dbaf4e610224`.
- Workload source: local
  `gpgpu-workloads:suites/polybench-gpu-wrapper/pb_2dconv`, executable
  `pb_2dconv`, extracted PTX `pb_2dconv.1.sm_52.ptx`.
- Workload repository SHA: `de9cf4293f418877aa9cdb6a2395338ca06674a6`.
- Temporary isolated run root:
  `/tmp/dtc-l1-m4-workloads-4COmJy/polybench_2dconv/`.
- Invocation contract: copied workload directory; copied config; only
  `-gpgpu_dtc_l1_mode` differs (Base=1, IO=2, OO=3); no workload source,
  binary, PTX, input, cache policy, or unrelated GPU option was changed.
  `CUOBJDUMP_SIM_FILE=unused`, `PTX_SIM_USE_PTX_FILE=1`, and
  `PTX_SIM_KERNELFILE=pb_2dconv.1.sm_52.ptx` select the recorded extracted
  PTX path. The M4 Core runtime library is
  `/tmp/dtc-l1-core-build/libcudart.so`.

## Results

| Variant | Result | Evidence |
| --- | --- | --- |
| PAPER_BASE | `TIMEOUT_DIAGNOSTIC` at 240 seconds | log SHA-256 `8a4d444b9910484caec58dc6eb2170f01b62395c5cfbba1b4095ec37639f1118` |
| PAPER_IO | **HARD FAIL** | log SHA-256 `df126bf48a0b9e6ca044fd9a9bafa6431ea120aeed2c265e8807060dce3f734a` |
| PAPER_OO | **HARD FAIL** | log SHA-256 `0669057df76b43a5305f635327d9dde3770ac5ce57fae728ae1e9709233739c5` |

The IO run aborts at:

```
shader.cc:2824: ldst_unit::dtc_l1_io_complete_instruction
Assertion `pending >= dependencies' failed.
```

The OO run aborts at:

```
shader.cc:3068: ldst_unit::dtc_l1_oo_complete_instruction
Assertion `pending >= dependencies' failed.
```

The corresponding configuration SHA-256 values are Base
`ec2a9871fc7ecbaff057f9486935792b45fe711d9569888a6d3c7f2453cd7823`, IO
`43d87dbd6e971d882ac7c1375126517d32679178196667ef26fbee3006eb6610`, and
OO `3bfc63db580f89b3ed7e845e175f3593a6d76b12ce200623a84390e178061b44`.
They differ only in the documented DTC mode value.

## Scope and disposition

This is a source-reachable cacheable-load completion/accounting failure in a
real compute workload. It is unrelated to the authorized `FENCE_OP`
source-unreachability disposition and cannot be classified
`SOURCE_UNREACHABLE_NA`.

No repair was attempted: the active Goal contract requires a STOP on a new
HARD failure. No M4 workload triplet, F00 closure, review pack, M5 work, or
performance conclusion is claimed from this attempt.

The Core commit above adds only M4 source-domain Load/Store/Atomic/FENCE_OP
observability and passed a full Core build plus both CTests before this run.
It does not alter request routing, cache policy, completion, `membar`, or
fence semantics. The new runtime failure must be independently diagnosed and
authorized before resuming M4.
