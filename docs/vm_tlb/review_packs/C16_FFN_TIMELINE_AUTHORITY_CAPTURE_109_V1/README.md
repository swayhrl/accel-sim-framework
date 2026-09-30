# C16 FFN Timeline Authority Capture — Lane 7 / node109

Task: `C16_FFN_TIMELINE_AUTHORITY_CAPTURE_109_V1`.

Purpose: timeline authority only for the exact accepted Qwen2.5-7B AWQ natural
`CONTROL_GUD84` D0–D3 decode.  This producer emits correlation-authoritative raw
tables and does not compute FFN headroom, oracle ceilings, or mechanism value.

Final state: `TIMELINE_AUTHORITY_CAPTURE_PASS`.

One outer GPU lock covered the OFF/ON neutrality pair and the single formal
capture.  OFF/ON and ON/formal outputs, 420-entry call order, 336 occurrence
identities, module classes, policy semantics, and all 7,441 CUDA kernels
(name/count/order/grid/block) matched exactly.

The formal capture contains 560 semantic ranges: 336 projections, 112 SiLU
activation ranges, and 112 multiply ranges.  Attribution uses the CUDA runtime
launch inside the semantic NVTX scope and its correlation ID to the GPU kernel;
GPU-time overlap is never used as the ownership rule.
