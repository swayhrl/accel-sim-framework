# Gate results

| Gate | Result | Evidence / disposition |
| --- | --- | --- |
| P0 | PASS | SSH alias resolved; data mount selected; clean Git-provenance checkout placed on the host. |
| P1 | PASS | `host-preflight.json`: exactly four homogeneous SM86 3080 Ti GPUs, sufficient CPU/RAM/storage. |
| P2 | PASS | Locked Python packages and CUDA 12.6 toolkit installed locally on data disk; no driver action. |
| P3 | PASS | NVBit SHA checked; selected-toolchain build; capture-ready preflight PASS; generic raw trace, postprocess, `kernelslist.g`, archive and SHA256 PASS. |
| P4 | PASS | `p4-rank0-smoke-gloo.log` shows ranks 0–3 with `CUDA_INJECTION64_PATH=ABSENT`; `p4-rank0-trace-gloo.log` shows ranks 1–3 absent and rank 0 alone set to `tracer_tool.so`. Every rank reports SM86 and completed `cuda.synchronize()` plus Gloo barrier. |
| P5 | PASS | Authorized local-snapshot route verified all six staged files, the canonical ID, and frozen revision. A real four-rank NCCL TP=4 no-trace workload passed finite-logit and stable flat-weight-binding checks. |
| P6 | PASS | One real rank0-NVBit `DIAGNOSTIC_PILOT` `decode1` capture completed. It preserves 772 raw and 772 postprocessed trace files, the raw kernel list, classification, Weight/KV sidecar validation, and archive integrity. |
| P7 | PASS | The diagnostic archive copied to the main server with equal SHA256. The frozen SM86 parser initialized and processed 35 real trace kernels during a 75-second bounded smoke without a format/binary-version error. |
| P8 | COMPLETE | Pilot closeout is complete. The exact pilot status is `PILOT_PASS_READY_FOR_GOAL_CAPTURE`; the next permitted stage is G0 Goal admission. |

The first P4 trace attempt used NCCL and exceeded its 10-minute watchdog while
rank 0 performed NVBit's initial PyTorch-module instrumentation. It is
retained in the raw log index. The P4-only diagnostic was then changed to Gloo
for process synchronization while preserving each rank's real CUDA operation;
P5 remains the required real TP4/NCCL test and was not reached.

That historical note applies only to the initial blocked attempt. The repaired
P5 used real NCCL TP=4 and succeeded; no Gloo result is used as formal workload
evidence.
