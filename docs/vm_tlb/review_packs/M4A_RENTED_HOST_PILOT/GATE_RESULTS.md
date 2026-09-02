# Gate results

| Gate | Result | Evidence / disposition |
| --- | --- | --- |
| P0 | PASS | SSH alias resolved; data mount selected; clean Git-provenance checkout placed on the host. |
| P1 | PASS | `host-preflight.json`: exactly four homogeneous SM86 3080 Ti GPUs, sufficient CPU/RAM/storage. |
| P2 | PASS | Locked Python packages and CUDA 12.6 toolkit installed locally on data disk; no driver action. |
| P3 | PASS | NVBit SHA checked; selected-toolchain build; capture-ready preflight PASS; generic raw trace, postprocess, `kernelslist.g`, archive and SHA256 PASS. |
| P4 | PASS | `p4-rank0-smoke-gloo.log` shows ranks 0–3 with `CUDA_INJECTION64_PATH=ABSENT`; `p4-rank0-trace-gloo.log` shows ranks 1–3 absent and rank 0 alone set to `tracer_tool.so`. Every rank reports SM86 and completed `cuda.synchronize()` plus Gloo barrier. |
| P5 | BLOCKED | Locked gated-model metadata query returned `LocalTokenNotFoundError`; no download or substitution attempted. |
| P6 | NOT RUN | Prerequisite P5 failed. No diagnostic Llama `decode1` trace exists. |
| P7 | PARTIAL | P1–P4/NVBit evidence copied back with matching SHA256. Frozen parser smoke is not applicable without the required P6 Llama trace. |
| P8 | COMPLETE | This blocked closeout/report/pack was written; STOP for review. |

The first P4 trace attempt used NCCL and exceeded its 10-minute watchdog while
rank 0 performed NVBit's initial PyTorch-module instrumentation. It is
retained in the raw log index. The P4-only diagnostic was then changed to Gloo
for process synchronization while preserving each rank's real CUDA operation;
P5 remains the required real TP4/NCCL test and was not reached.
