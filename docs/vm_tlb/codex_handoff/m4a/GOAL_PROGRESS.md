# M4A-C Goal progress

Goal: `M4A_C_FORMAL_CAPTURE`

| Gate | Status | Framework source SHA | Evidence / next action |
| --- | --- | --- | --- |
| G0 | PASS | `f994fc9156329b0335f56702dafc2884ce003fe8` | Repaired pilot status is exactly `PILOT_PASS_READY_FOR_GOAL_CAPTURE`. Re-admission found clean source, four idle homogeneous SM86 RTX 3080 Ti GPUs, retained local snapshot verified, CUDA 12.6/PyTorch 2.6.0+cu126, and 978 GiB free. |
| G1 | PASS | `f994fc9156329b0335f56702dafc2884ce003fe8` | Canonical ID/revision are supplied from the six-file manifest-verified local snapshot. Network model access is disabled; no HF credential is needed or recorded. |
| G2 | READY | `f994fc9156329b0335f56702dafc2884ce003fe8` | Launch exactly one `FORMAL` prefill ROI with rank0-only NVBit, then archive and copy it back before decode1. |
| G3–G8 | NOT_STARTED | — | Formal prefill/decode1 evidence does not yet exist. |

## Pilot evidence retained on the main server

- R3/P5 four-rank real TP4 evidence:
  `/workspace/m4a-rented-host-pilot/r3-p5-local-smoke-final/`
- R4/P6 diagnostic archive and checksum record:
  `/workspace/m4a-rented-host-pilot/r4-diagnostic-decode1/`

The diagnostic trace is not formal evidence. No formal run ID or archive exists
at the time of this progress update.
