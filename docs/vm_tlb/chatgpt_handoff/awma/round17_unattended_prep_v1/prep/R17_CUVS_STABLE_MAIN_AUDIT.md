# R17 cuVS source audit

Date: 2026-09-30. Preparation only.

Authorities:
- stable: `NVIDIA/cuvs v26.08.01@25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`
- comparison: `NVIDIA/cuvs@d3df668c77da45bce9f7ff80b6adc62f91d4ba01`

The low-query routing relevant to R17 is materially unchanged in the inspected snapshots. Persistent AUTO selects SINGLE_CTA. Non-persistent AUTO selects SINGLE_CTA only when itopk<=512 and max_queries>=2*numSM; otherwise it selects MULTI_CTA. For Q1, AUTO therefore already represents the low-query MULTI_CTA path.

Stable MULTI_CTA derives `num_cta_per_query=max(search_width,ceil(itopk/32))`. This makes width=1 and width=2 redundant at itopk 64,128,256: both produce 2,4,8 CTAs/query respectively. The future review draft can use itopk 64/128/256 at width=1, plus at most one point such as itopk64/width4 if an extra parallelism challenge is needed.

Dynamic batching aggregates concurrent requests and is a serving control, not an intrinsic isolated-Q1 solution. Persistent remains SINGLE_CTA-only and is a launch/request control.

Stable cuVS-bench already sweeps itopk 32..512 and search_width 1..64. These are legitimate software knobs but do not require an exhaustive R17 sweep.

State: `R17_SOURCE_BASELINE_AUDIT_PASS_CONTRACT_CAN_BE_SIMPLIFIED`.
