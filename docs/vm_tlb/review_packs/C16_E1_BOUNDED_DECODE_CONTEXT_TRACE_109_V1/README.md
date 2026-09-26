# C16 E1 bounded decode context trace ? producer review pack

Status: `PENDING_NODE164_VERIFY_ADMIT_ACK`

This pack records the node109 producer capture of natural Qwen2.5-7B-Instruct-AWQ decode iterations D1-D3. The selected interval is dynamic kernels 2926-7440 inclusive: 4515 kernels, 16,313,481,995 trace instructions and 3,653,040 CTAs. All intervening model traffic is retained.

Producer-side gates are PASS:

- exact accepted model/config/input/token identity;
- generated tokens `[23578, 11, 323, 3950]`;
- three contiguous stable decode iterations;
- 4515/4515 raw terminal/accounting and XZ integrity;
- 4515/4515 post-processed traceg artifacts;
- strict grammar and official Accel-Sim parser closure;
- 28 exact up_proj qweight allocation regions;
- direct numeric trace-address canaries for layers 0, 14 and 27.

The trace-side address result is `TRACE_SIDE_VALIDATED_SIM_L2_MAPPING_PENDING_174`. No simulator-internal mapping claim is made.

Node164 verification/admission/positive ACK is still pending in this interim commit. Do not use the final qualification label until the follow-up ACK commit.
