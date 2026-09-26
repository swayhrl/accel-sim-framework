# C16 E1 bounded decode context trace ? final producer review pack

Status: `C16_E1_BOUNDED_DECODE_TRACE_QUALIFIED_V1`

The node109 producer captured three consecutive natural Qwen2.5-7B-Instruct-AWQ decode iterations D1-D3 with no CUDA persisting-L2 intervention or access-policy window. Dynamic kernels 2926-7440 are retained in natural order, including all intervening attention, gate, up, down, normalization, elementwise, copy, KV-related and other runtime kernels.

## Final closure

- selected decode interval: D1 + D2 + D3;
- kernel count: 4515 = 1505 per decode;
- raw compressed bytes: 105,451,668,600;
- traceg compressed bytes: 9,464,308,892;
- dynamic trace instructions: 16,313,481,995;
- CTAs: 3,653,040;
- up_proj semantic occurrences: 28/28 per decode;
- intervening non-up kernels: 4347;
- terminal drop/overflow/partial: 0/0/0;
- strict grammar and official Accel-Sim parser: PASS for 4515/4515;
- exact up_proj qweight regions: 28 independent stable allocations, 33,947,648 bytes each;
- trace-address canaries: direct numeric hits for layers 0, 14 and 27;
- node164 independent verify, admission, catalog and positive ACK: PASS.

The durable authority path is:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03`

The address claim remains `TRACE_SIDE_VALIDATED_SIM_L2_MAPPING_PENDING_174`: runtime CUDA VA and trace-native numeric addresses are proven equal by real-artifact canaries, but no simulator-internal L2 mapping claim is made.

No Accel-Sim/GPGPU-Sim execution, mutation, mechanism implementation or mechanism experiment was started.
