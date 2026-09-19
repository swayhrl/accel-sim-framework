# ChatGPT Review — 109 Replay Repeatability / MoE Hook V1

Date: 2026-09-20

Reviewed execution branch:

`hrl/awma-e1-repeatability-moe-hook-109-v1`

Reviewed final HEAD:

`137157d3a22c1b70e3bafa64ac9b56c3309fdcd9`

Parent:

`10c1c19fd0314a187a772ea83034d71a64eb569a`

Ancestry:

exactly one execution commit ahead of the expected parent.

## 1. Accepted result

Stage status:

`AWMA_E1_REPLAY_REPEATABILITY_AND_MOE_CONTROL_HOOK_109_V1_ACCEPTED_WITH_SCOPE`

The following are accepted:

- AWQ qweight/qzeros/scales/bias are identical across five reloads;
- direct replay of the exact saved M256 pools is bitwise deterministic within and across reloads;
- frozen repeatability contract for the direct M256 call is `BITWISE_EQUAL`;
- AWQ authority node164 provenance is closed;
- Q30 S2/T2048 state authority remains valid.

## 2. The M2048-live-slice vs M256-replay mismatch is not yet a valid replay-failure conclusion

The only persistent mismatch is:

```text
natural full-sequence module call: input shape [1,2048,K]
take output rows [0:256]
vs
direct module replay: input shape [1,256,K]
```

with:

- q_proj max_abs = 0.03125
- down_proj max_abs = 0.001953125

These are not the same operator invocation shape.

Therefore output equality is valid only if the implementation is shape-invariant over this change.

The prior V1 contract implicitly treated the first 256 rows of an M=2048 call as the output oracle for an M=256 call.
That assumption must now be audited.

## 3. Strong implementation-switch hypothesis

Public AutoAWQ `WQLinear_GEMM` source currently contains the following forward-path heuristic:

```text
FP16_MATMUL_HEURISTIC_CONDITION = x.shape[0] * x.shape[1] >= 1024
```

and selects:

- large shape: dequantize weights + FP16 matmul;
- smaller shape: quantized `gemm_forward_cuda`.

For preserved rank `[1,M,K]`:

- M=2048 satisfies the large-shape branch;
- M=256 does not;
- M=1 does not.

This public source is supporting evidence only.

The exact installed/frozen AWQ runtime used by the experiment remains authoritative and MUST be inspected locally before the hypothesis is promoted.

## 4. Revised E1 authority semantics

If the frozen local runtime proves a shape-dependent implementation dispatch between M=2048 and M=256:

- the natural M=2048 live input remains a valid real-activation source;
- the first 256 input rows remain a valid M256 activation pool;
- the first row remains a valid M1 activation;
- the M=2048 live OUTPUT slice is NOT the oracle for the M=256 call;
- each experimental shape must create and validate its own output oracle by executing that exact shape.

Thus:

`REAL_ACTIVATION_INPUT_AUTHORITY`

and

`SHAPE_SPECIFIC_OUTPUT_REPLAY_AUTHORITY`

must be treated as separate evidence objects.

The direct M256 bitwise-determinism result already strongly supports the second object for AWQ M256.

## 5. Required frozen-runtime proof

The next stage must record:

- exact installed `awq/modules/linear/gemm.py` path and SHA256;
- exact AutoAWQ package version/source identity available locally;
- exact AWQ extension SHA/version;
- actual forward dispatch condition from the installed source;
- kernel sequence for q_proj/down_proj at M=2048, M=256 and M=1.

If M2048 and M256 use different implementation paths, reclassify the old live-slice mismatch as:

`INVALID_CROSS_SHAPE_OUTPUT_ORACLE`

not `REPLAY_EQUIVALENCE_FAIL`.

If the installed source does NOT switch paths, continue diagnosis and do not automatically resume E1.

## 6. E1 core can resume under the corrected shape-specific oracle contract

For each accepted real activation input pool:

### M256
- input = first 256 real live rows, shape preserved as `[1,256,K]`;
- output oracle = direct M256 invocation;
- repeatability gate = exact same M256 invocation across reloads.

### M1
- input = first row of the same real pool, shape `[1,1,K]`;
- output oracle = direct M1 invocation;
- repeatability gate = exact same M1 invocation across reloads.

Do not compare either output bitwise against the M=2048 natural output slice.

The natural M=2048 call remains a deployment anchor and implementation-path reference.

## 7. Raw-side authority

The next stage should close exact raw q_proj/down_proj activation pools under the same S2 token authority.

Use the same separation:

- natural M=2048 input as real activation source;
- shape-specific M256/M1 output oracles produced by the exact raw module invocation.

Do not require an M2048 output slice to equal the M256/M1 output if the raw backend also changes algorithms by shape.

## 8. Optional implementation-transition diagnostic

If the frozen AWQ source proves the threshold is exactly M=1024 for preserved rank `[1,M,K]`, a bounded transition diagnostic is authorized after the E1 core:

Preferred one-role diagnostic:

`down_proj`

Shapes:

- M=1023
- M=1024
- M=2048 natural/full-shape anchor

Record:
- kernel path;
- native timing;
- traffic/resource evidence if selector canary passes.

This is an implementation-transition diagnostic, not part of the mandatory core 8 points.

## 9. E3 hook conclusion

The prior stage stopped because no provenance-qualified direct-experts harness had already been materialized.

That is a valid fail-closed result, but it does not imply a diagnostic harness cannot be created.

The next stage may materialize a local experts-control harness from the exact accepted frozen Q30 runtime source if and only if:

1. it uses the exact accepted expert modules/weights/backend;
2. it copies/calls the exact expert dispatch/combine semantics from the frozen source;
3. natural N through the harness reproduces the accepted natural expert-path output under the runtime repeatability contract;
4. no expert math, weight format, backend, or residency policy is changed.

This is a test harness, not a model or architecture mechanism.

## 10. E3 harness role

The harness must make explicit inputs:

- hidden states;
- selected_experts;
- routing_weights.

It may internally perform the same token grouping/dispatch/expert execution/combine loop as the frozen model source.

Natural N is the qualification canary.

P is the permutation-invariance validation of the harness.

U-active is allowed only after N and P pass.

## 11. Next 109 stage

`AWMA_E1_SHAPE_SPECIFIC_ORACLE_AND_MOE_HARNESS_109_V2`

Scientific priorities:

1. prove/disprove the frozen AWQ shape-dependent path-switch hypothesis;
2. correct the E1 output-oracle contract;
3. close raw exact activation authority;
4. execute E1 core M1/M256;
5. optionally characterize the M1024 implementation transition;
6. materialize/qualify the exact Q30 experts-control harness;
7. run E3 N/P/U-active if the harness qualifies.

No new model, detailed trace campaign, or architecture mechanism is authorized.
