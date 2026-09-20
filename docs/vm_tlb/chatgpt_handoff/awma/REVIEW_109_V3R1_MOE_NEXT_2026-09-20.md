# ChatGPT Scientific Review — 109 V3R1 and Next MoE Characterization

Date: 2026-09-20

Reviewed execution branch:
`hrl/awma-109-20h-unattended-e1-e3-v3r1`

Final remote HEAD:
`c766a9d8ede59ef4b81ffd151ac49c839495a115`

## 1. Accepted closure

The resumed campaign materially closed the previously missing engineering gates.

Accepted:

- isolated AWQ down_proj M256 NCU canary produced a real report and selected `gemm_forward_4bit_cuda`;
- same-qweight/qzeros/scales implementation decomposition closed at M1/M256/M1023/M1024;
- exact Q30 expert-loop harness was materialized;
- N direct-experts canary = bitwise PASS;
- P joint token/routes/weights permutation + inverse output = bitwise PASS with unchanged expert histogram;
- U-active uses the same natural active set, M=2048, top-k=8, total assignments=16384, distinct experts/token and max-min active count=1;
- G1 controlled long-context/batch scenarios were honestly labeled;
- G3 profiler protocol reports were produced;
- Llama M1 raw holdout closed with M256 fail-closed due to insufficient real rows.

## 2. E1 decomposition interpretation

For AWQ down_proj:

### M1
- deployed quantized GEMM: 0.063392 ms
- one-time-dequant + matmul: 0.214016 ms
- per-call dequant + matmul: 0.720768 ms

At tiny M, deployed quantized GEMM is strongly favored.

### M256
- deployed quantized GEMM: 0.475392 ms
- one-time-dequant + matmul: 0.356128 ms
- per-call dequant + matmul: 0.824544 ms

At M256, predequantized matmul is faster than deployed quantized GEMM, while paying dequant every call is much slower.

### M1023
- deployed quantized GEMM: 1.889280 ms
- one-time-dequant + matmul: 1.679072 ms
- per-call dequant + matmul: 2.043872 ms

### M1024
- deployed dequant+matmul path: 1.900544 ms
- one-time-dequant + matmul: 1.363968 ms
- explicit per-call dequant + matmul: 1.797120 ms

This establishes that the fixed AutoAWQ path threshold is an implementation policy with a shape-dependent tradeoff, not a universal “quantized is faster” property.

The next stage should explain this with resource metrics, but E1 is now secondary to the stronger MoE routing result.

## 3. E3 result

Expert-region median timing:

- N natural = 14.396416 ms
- P histogram-preserving permutation = 13.949952 ms
- U-active balanced within natural active set = 12.076672 ms

Descriptively:

- P is ~3.1% lower than N;
- U-active is ~16.1% lower than N;
- U-active is ~13.4% lower than P.

These values are not yet sufficient for a causal “load balancing gives 16%” claim because:

- only one P ordering was tested;
- only one U-active construction/order was tested;
- token ordering and expert-count shape both affect execution;
- the frozen expert loop may execute experts serially, so the relevant mechanism may be expert GEMM granularity/utilization rather than parallel tail imbalance.

## 4. Next scientific question

The next main question is:

> With active expert set, total assignments, expert modules, routing-weight values and backend held fixed, how does expert-assignment skew change the distribution of expert GEMM shapes and GPU execution efficiency?

This is a workload/microarchitecture characterization question.

It is not yet an architecture mechanism proposal.

## 5. Required causal controls

The next stage should:

1. estimate token-order sensitivity with several histogram-preserving P permutations;
2. estimate balanced-case order sensitivity with several row permutations of the same U-active assignment;
3. construct a deterministic skew continuum between natural histogram and uniform active-set histogram;
4. measure expert-level shape/efficiency at histogram-derived token-count quantiles;
5. validate the trend on the accepted Q30 S0/T128 state as an independent small-M holdout;
6. profile representative expert shapes/resources;
7. complete the E1 down_proj resource explanation as secondary evidence.

No new model download or architecture mechanism is authorized.
