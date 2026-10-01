# START HERE — AWMA R19F2 FP8 strong-software counterfactual

Date: 2026-10-01

Scientific parent:
`7375abd8e86c1523c1873913e8fffccf0b4e3a96`

Parent conclusion:
`R19F1_FP8_READINESS_RESIDUAL_PRESENT`

Accepted parent facts:
- real Qwen2.5 layer0 up_proj input/weight;
- TE v2.19.0 current-scaling E4M3 on RTX4080/SM89;
- representation-matched numerical gate passed;
- online A1 and representation-ready D0 used identical input FP8 bits/scale, identical cached weight representation, identical output, and the same exact SM89 E4M3 GEMM;
- complete-call A1 0.085846 ms vs D0 0.062693 ms, delta 0.023153 ms / 26.97%;
- A1-only four preparation kernels total about 5 us GPU service in NSYS; the full formal delta is larger and includes launch/dependency/runtime effects.

R19F2 is a **software/dataflow challenge before architecture admission**.

It does not authorize hardware, 174 or a new precision format.

Execution branch:
`hrl/awma-r19f2-fp8-software-counterfactual-109-v1`

All CUDA/NSYS/NCU actions use:
`/data/c16/locks/c16_gpu_campaign.lock`

Do not run another model or shape.
