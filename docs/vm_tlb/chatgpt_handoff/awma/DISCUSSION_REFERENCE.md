# AWMA Discussion Reference — Repaired Hit Path + E1 Authority

Date: 2026-09-19

## 1. Why the mainline question changed

The per-access repair materially changed Q05 completion, then repaired requalification showed that the large translation-path sensitivity survives real predecessor context.

Repaired results:

```text
isolated R0/I0 = 1,654,548 / 674,179
P34 R0/I0      = 1,619,068 / 758,082
P8 R0          = 1,675,884
```

P34 natural is close to isolated natural, while P34 Q05-only I0 still removes more than half of target cycles.

Therefore “the old result is mostly cold isolated replay” is not supported after repair.

## 2. Why PTW is not the immediate target

Repaired P34 target delta has:

```text
L1 misses = 3,396
L2 misses = 108
walks     = 15
```

but:

```text
L1 lookup launches = 3,090,412
L1 lookup service requester-cycles = 30,904,120
```

Most accumulated requester-level translation time is associated with the configured L1 lookup service.

This does not prove real hardware spends 10 exposed cycles for every access.
It proves that the current simulator result is highly exposed to that model assumption.

## 3. Why the next 174 task is model validity

The current 10/80 configuration is not hardware calibrated.

A mechanism result built directly on it could become circular:

1. assume large per-access lookup cost;
2. observe large modeled opportunity;
3. design hardware to remove the assumed cost.

The next step must instead measure the repaired model's sensitivity envelope.

Use target-only P34 variants:

```text
10/80 existing
5/80
2/80
0/80

10/40
10/0

0/0
I0 existing
```

This distinguishes:
- L1 service sensitivity;
- L2 service sensitivity;
- residual VM-path cost after lookup service is zero.

It does not calibrate RTX4080 latency.

## 4. Why 0/0 and I0 are different controls

0/0 keeps the VM/lookup machinery present but removes configured lookup service delay.

I0 bypasses the functional translation path with identity translation.

Therefore:

`cycles(0/0) - cycles(I0)`

is a useful model-relative residual.

It may be positive or negative because timing changes can alter ordering/hit behavior.
Do not force additivity.

## 5. Why the old lookup matrix cannot simply be reused

Before the per-access repair, most downstream accesses never passed through VM translation.

The old lookup-latency matrix was therefore evaluated under a different effective access population.

Its qualitative lessons may motivate the repaired matrix, but its numeric values are historical only.

## 6. Why a non-Attention screen remains useful

If Prefill GEMM under the repaired model also shows strong 10/80 -> 0/80 sensitivity, then the issue is not unique to FlashAttention's specific access structure.

If it does not, family structure matters.

This is a representativeness/model-validity check, not a mechanism evaluation.

## 7. Why the previous E1 Goal stopped

The previous 109 Goal correctly required an exact activation/module-replay authority.

It found none in the current node109/node164 audit and refused to synthesize one.

That was scientifically correct.

The scheduling mistake was treating absence of a pre-existing authority as the end of E1 rather than authorizing a producer to create a new one from accepted model/token inputs.

## 8. Historical raw/AWQ evidence already available

A prior raw/AWQ paired-replay stage established:

- an exact common 2048-token S2 input;
- raw layer-0 selective replay;
- raw Mode A/B equivalence.

It deliberately failed closed on AWQ semantic target binding because a generic fused CUDA kernel could not be uniquely mapped back to one WQLinear module.

The new E1 does not solve that by launch-order inference.

It binds directly to the Python module object:

```text
model.layers.0.self_attn.q_proj
model.layers.0.mlp.down_proj
```

and saves live module inputs/outputs.

## 9. Why tensor rank is frozen

The core shape diagnostic uses:

```text
M1   = [1,1,K]
M256 = [1,256,K]
```

not flattened `[M,K]`.

AWQ implementations may use dimension/rank-based heuristics.
Flattening can select a different backend path and would mix shape with a wrapper-induced implementation change.

If the preserved natural rank itself causes a path switch between M1 and M256, that is a valid result.

## 10. Natural deployment versus controlled semantic comparison

Raw and AWQ models can produce different live activations.

Natural-deployment measurements keep those differences and answer:

> what does each deployed model actually execute for the same token input?

A stronger same-input comparison requires proof that raw and AWQ module inputs share the same semantic coordinate system or a validated transform exists.

If AWQ absorbed scaling prevents that proof, the comparison remains:

`IMPLEMENTATION_LEVEL_ONLY`

This is not a failed experiment.

## 11. Why E3 is independent

Q30 MoE routing already has exact S2 state/replay authority.

Its scientific question does not depend on Qwen2.5 raw/AWQ activation authority.

Thus E1 and E3 are independent tasks sharing only the physical RTX4080 lock.

E1 STOP no longer propagates to E3.

## 12. E3 first-wave controls

Use:

- N natural routing;
- P histogram-preserving permutation;
- U-active active-set-preserving balancing.

P isolates ordering while keeping per-expert counts.
U-active changes load balance without simultaneously expanding the active expert working set.

Synthetic routing remains explicitly synthetic.

## 13. Profiling correction

The previous pipeline's zero-kernel NCU attempts demonstrate selector failure, not hardware counter absence.

Historical AWQ profiling already showed L1/L2/DRAM byte metrics can be collected on the 4080.

Next E1 profiling should use an isolated module-replay process/NVTX range and a selector canary before collecting metrics.

## 14. Still not authorized

No TLB/PTW/cache mechanism should start from the current results.

The next decision comes only after:
- repaired lookup-model sensitivity is quantified;
- E1 authority/core results are available;
- E3 light routing diagnostic closes or explicitly stops.
