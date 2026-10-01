# R19 FP8 line final closeout

Date: 2026-10-01

## Execution authority

R19 V1:
- branch: `hrl/awma-r19-fp8-readiness-109-v1`
- commit: `63de02aa82587680baca665d09101dc8c67222a2`
- formal label: `R19_FP8_RESULT_MIXED_NEEDS_REVIEW`

R19F1:
- branch: `hrl/awma-r19f1-fp8-readiness-109-v1`
- commit: `7375abd8e86c1523c1873913e8fffccf0b4e3a96`
- formal label: `R19F1_FP8_READINESS_RESIDUAL_PRESENT`

R19F2:
- branch: `hrl/awma-r19f2-fp8-software-counterfactual-109-v1`
- commit: `7b87638e74164cdffc21c0d280324bcb048b6a8d`
- tree: `7b47b1d50163d4a33704b243c1b7e797776b3594`
- formal label: `R19F2_FUSED_SOFTWARE_SUFFICIENT`

## Accepted scientific sequence

### V1 — numerical contract was not decomposed

The real Qwen2.5 layer0 up_proj input/weight and native Ada/SM89 TE FP8 representation path qualified, but the original-BF16-versus-complete-FP8 allclose gate failed.

That stop remains historically valid and is not reinterpreted.

### F1 — representation-matched decomposition exposed a real operator-boundary residual

Using the exact same represented FP8 input/weight and same native SM89 E4M3 consumer:

- online current-scaling A1 median = 0.085846 ms
- representation-ready D0 median = 0.062693 ms
- complete-call delta = 0.023153 ms / 26.97%

Input FP8 bits/scale, cached weight, consumer GEMM identity and outputs were closed. Thus a real representation-readiness residual existed at the single-Linear boundary.

### F2 Stage A — natural sibling sharing was insufficient

On the same real Qwen layer0 MLP, gate_proj and up_proj consume the same hidden tensor.

Natural software reorganization:
- B0: two independent TE current-scaling input quantizations
- S1: one shared exact TE input quantization feeding both gate/up
- D0: exact representation already ready

Complete natural MLP wall medians:
- B0 = 0.195725 ms
- S1 = 0.182693 ms
- D0 = 0.151110 ms

S1 still had a 17.29% complete-MLP residual to D0 and recovered only 29.21% of B0->D0 ideal headroom. This correctly triggered the bounded Stage B software counterfactual.

### F2 Stage B — exact one-launch software fusion closes the line

Pinned TE v2.19 and separately audited current-main exposed no direct reusable standalone one-launch per-tensor E4M3 current-scaling path for this exact boundary.

One opt-in bounded CUDA diagnostic was therefore implemented:
- single cooperative launch
- exact TE v2.19 current-scaling arithmetic
- exact FP8 bytes
- exact inverse scale
- same cached gate/up FP8 weights
- same TE gate/up GEMMs
- bitwise-identical gate/up and full-MLP outputs
- no custom GEMM

Stage-B complete MLP medians:
- S1 shared TE path = 0.187174 ms
- S2 exact fused shared = 0.154272 ms
- D0 representation-ready = 0.148045 ms

Result:
- S2->D0 residual = 4.04% of S2
- S2 recovers 84.09% of the S1->D0 remaining headroom
- paired-group S2-D0 sign is not uniformly positive
- architecture-review stability gate fails

Therefore:
`R19F2_FUSED_SOFTWARE_SUFFICIENT`

## Precise interpretation

This does **not** mean stock Transformer Engine v2.19 already solves the issue.

The fused path is a research diagnostic implementation, not a shipping TE path.

The accepted conclusion is:

> For this frozen real Qwen/SM89/current-scaling E4M3 boundary, the material representation-readiness residual observed with stock multi-kernel organization can be removed almost entirely by an exact software fusion while preserving FP8 representation, consumer identity and full-MLP output. The remaining <=4.04% complete-MLP gap is not stable enough to justify architecture review.

Thus the current architecture line is closed.

## What is still useful

The R19 sequence demonstrates a real workload/dataflow phenomenon:
- quantized representation readiness can be a material local cost;
- duplicate representation generation across sibling consumers is wasteful;
- launch-chain organization dominates more than the raw amax/scale/cast arithmetic alone;
- exact fused software/dataflow organization can recover most of the ideal headroom.

This is useful workload characterization and software-baseline evidence.

It is not a hardware mechanism result.

## Do not do next

Do not:
- start 174/Accel-Sim to rescue this line;
- add an FP8 quantization unit proposal from the current evidence;
- sweep more Qwen shapes/models just to find a positive;
- switch to Blackwell FP4/TMEM and treat it as validation of this Ada result;
- run NCU after the closure simply to find a large stall metric.

## Reopen conditions

Reopen low-precision representation readiness only if an independently motivated natural workload has one of these materially different boundaries:
- a representation cannot be software-fused or shared because producer/consumer ownership prevents it;
- scale/layout requirements are jointly dynamic and survive exact fusion;
- multiple consumers require incompatible representations;
- a future precision format/platform changes the legal representation contract;
- a full model/service workload independently re-exposes a material residual after equivalent strong software organization.

A new workload must qualify independently; do not reopen by parameter fishing on this same Qwen layer0 shape.

## Final lane state

- Lane F / FP8: STOP, current architecture line CLOSED
- Lane G / fast-weight: STOP
- Lane E / IBP: STOP
- node174 / Accel-Sim: STOP

Next work returns to problem discovery / preparation, not mechanism implementation.
