# C16 FFN Timeline Authority Capture — Lane 7 / node109

Task: `C16_FFN_TIMELINE_AUTHORITY_CAPTURE_109_V1`.

Purpose: timeline authority only for the exact accepted Qwen2.5-7B AWQ natural
`CONTROL_GUD84` D0–D3 decode.  This producer emits correlation-authoritative raw
tables and does not compute FFN headroom, oracle ceilings, or mechanism value.

Current state: CPU identity/source preflight complete; capture pending one outer
GPU lock covering OFF/ON neutrality and the single formal run.
