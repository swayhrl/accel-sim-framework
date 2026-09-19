# AWMA 109 20h Acceptance Contract V3

Date: 2026-09-20

## 1. Accepted upstream

Execution authority:

`hrl/awma-e1-shape-oracle-moe-harness-109-v2`

`56096d32bd5cd783286e1b5e5e612b6019f926d0`

Accepted:
- E1 shape-specific input/oracle contract;
- raw/AWQ q_proj/down_proj M1/M256 native timing;
- frozen AWQ implementation switch;
- Q30 S2/T2048 state authority remains accepted.

## 2. Raw/AWQ claim scope

Unless a same-input semantic mapping is separately proven:

`DEPLOYMENT_LEVEL_COMPARISON_ONLY`

Always distinguish:
- raw natural-deployment-derived activation;
- AWQ natural-deployment-derived activation;
- implementation-specific shape path.

Do not publish a pure “AWQ speedup” claim from these deployment-level points alone.

## 3. Threshold diagnostic

Frozen AWQ condition must remain exactly the installed runtime condition.

Required core transition points:

for each role:
- AWQ M1023
- AWQ M1024

Preferred raw controls:
- raw M1023
- raw M1024

Use the same real M2048 activation pool prefix and preserve rank `[1,M,K]`.

M1023/M1024 outputs get their own shape-specific oracle/repeatability gate.

## 4. Profiling acceptance

Before expensive NCU:
- use isolated module replay;
- create NVTX/range or another exact selector;
- run a canary proving expected kernels are selected.

Zero selected kernels:
`SELECTOR_UNRESOLVED`.

Only after canary:
collect supported metrics discovered from installed NCU.

Never invent unavailable metrics or zeros.

Native timing must remain uninstrumented CUDA-event timing.

## 5. E1 mandatory profiling set

Highest-value contrasts:

- down_proj raw M1
- down_proj AWQ M1
- down_proj raw M256
- down_proj AWQ M256

These capture the direction reversal.

If selector/profiler is reliable and time remains, extend to q_proj M1/M256 raw/AWQ.

## 6. Same-quantized-weight decomposition

Allowed only using the exact same AWQ qweight/qzeros/scales.

For one preselected role, default down_proj:

A. deployed AWQ quantized GEMM path;

B. one-time dequantized weight + FP16 matmul, dequantization outside timed region;

C. per-invocation dequantization + FP16 matmul, dequantization inside timed region.

Required:
- exact input authority;
- numerical comparison;
- explicit timing boundary;
- no new backend implementation.

Run only shapes relevant to explaining the threshold and core contrast:
M1, M256, M1023, M1024.

## 7. E3 harness acceptance

Authority:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

A new test harness is allowed.

Natural N canary must prove:
- exact accepted hidden state;
- real gate/router;
- exact natural selected_experts/routing_weights;
- same expert modules/weights/backend;
- same weighting/combine semantics;
- output agreement under a frozen repeatability contract.

No P/U timing if N fails.

P:
joint token permutation of hidden/routes/weights, inverse output permutation, same expert histogram, output equivalence required.

U-active:
natural active expert set only, same M/top-k/total assignments, deterministic balanced expert IDs, per-token routing-weight values preserved in rank slots, explicit `SYNTHETIC_ROUTING`.

## 8. Opportunity G1

Qwen2.5-0.5B existing asset/revision only.

Priority:
- B1/T8192/D32
- then B4/T2048/D32

New scenario IDs.
Exact token authority.
Native timing + lightweight kernel census.
No default detailed trace.

## 9. Opportunity G4

Llama3.2-1B existing asset only.

At most two pre-frozen raw linear roles x M1/M256.

Same shape-specific input/oracle discipline.

Claim:
`RAW_CROSS_MODEL_SHAPE_HOLDOUT`

not AWQ validation.

## 10. NCU protocol opportunity

Only after normal profiling works.

Same target/metrics under supported replay/cache-control settings.

Claim:
profiler protocol sensitivity only.

Never call cache-control a TLB flush.

## 11. Detailed capture gate

Pre-frozen candidate:

`AWQ down_proj M1023 vs M1024`

because it straddles the frozen implementation threshold with nearly identical M.

Capture only if:
- both points are accepted;
- path switch is observed in frozen runtime;
- exact module/kernel selection works;
- the contrast remains scientifically useful after native/resource diagnosis;
- projected total raw <= 16 GiB;
- >=3h remain before final closeout.

Partial capture:
`PARTIAL_NOT_ADMITTED`.

Do not substitute a different “interesting” pair after seeing results without marking it exploratory.
