# Validation summary

| Required no-GPU check | Result |
|---|---|
| `py_compile util/llm_trace_capture/*.py` | PASS |
| `bash -n util/llm_trace_capture/*.sh` | PASS |
| contiguous-weight planner self-test | PASS |
| metadata validator self-test | PASS |
| wrapper/KV fake-tensor self-test | PASS |
| rank 0 injection mock, smoke and trace ranks 0–3, missing/inconsistent rank rejection | PASS |
| ROI route/name static test | PASS |
| NCCL classifier synthetic-name test | PASS |
| host and capture-ready preflight static tests | PASS |
| checksum bootstrap and generic NVBit smoke dry runs | PASS |
| model-metadata resolver dry run | PASS |
| unauthorized M4A-C guard | PASS (`BLOCKED`) |
| GPU/NVBit/TP/NCCL/profiler/VA/trace-size execution | `CONDITIONAL_M4A_C_HOST_GATE`, intentionally not run |

No GPU was accessed, no model weight was downloaded, no trace was collected,
and no synthetic KV object was injected.
