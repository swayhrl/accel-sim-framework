# C16 RTX4080 NVBit 1.7.5 userspace qualification (U8)

Status: `PARTIAL_PASS_OFFICIAL_AND_PYTORCH_DIAGNOSTICS`.

All work ran as `huangrulin` in `/data/c16`; no root, driver, CUDA, kernel, or Docker mutation was used.

| Step | Status | Evidence |
| --- | --- | --- |
| U8.1 archive/core | `PASS` | Archive SHA `e2290da5e35a43fc4c74917dd08e1d41ece3e21bfca6fd7c6dc590c9c8385328`; core SHA `562348c32b88bf3e5b32d1895202893adb79f32b896e3cac56b29a306de40a12`. |
| U8.2 SM89 closure | `PASS` | Official vectoradd and `instr_count_bb.so` built with CUDA 12.8 and `ARCH=sm_89`. |
| U8.3 vectoradd native | `PASS` | Official output: `Final sum = 100000.000000; sum/n = 1.000000`. |
| U8.4 official instr_count_bb | `PASS` | NVBit 1.7.5 loaded, instrumented vectoradd kernel 0, counted 50,066 instructions, exit 0. |
| U8.5 C16 no-match/zero-trace | `PARTIAL_FAIL_TOOL_CLOSURE` | Python fixture exit 0 and zero trace files, but the custom no-op tool emitted no NVBit/READY marker. |
| U8.6 PyTorch elementwise | `PASS` | NVBit loaded; six CUDA kernels observed/counts emitted; fixture checksum `68722556928.0`; exit 0. |
| U8.7 PyTorch GEMM | `PASS` | NVBit loaded; CUDA GEMM `ampere_sgemm_64x32_sliced1x4_tn` observed/counts emitted; fixture checksum `549741854720.0`; exit 0. |

Raw run root: `/data/c16/results/C16_U8_NVBIT175_20260914T111145Z`. `FINAL_SHA256SUMS.txt` SHA256 is `6c801de25d08a58bf04f8ef6a5349665bfeb3ee6d99e28795e530d935cb30f8e`.

The NVBit 1.7.5 README states a historical driver requirement of `<=575.xx`, but official and PyTorch diagnostic injection succeeded on RTX4080/SM89 with driver `580.178.04`. No driver/root handoff is justified. The U8.5 custom no-op loader issue remains a userspace tool-closure problem.
