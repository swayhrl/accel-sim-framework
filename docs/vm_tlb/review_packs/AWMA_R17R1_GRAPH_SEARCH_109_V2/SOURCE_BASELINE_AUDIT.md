# Stable cuVS benchmark-base source audit

Stable authority: `NVIDIA/cuvs v26.08.01 @ 25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`, installed `cuvs-cu12==26.8.1`. The exact `python/cuvs_bench/cuvs_bench/config/algos/cuvs_cagra.yaml` SHA256 is in `PARENT_AUTHORITY.json`.

- The official benchmark `base` group lists `graph_build_algo: ["NN_DESCENT"]`, `itopk: [32,64,128,256,512]`, and `search_width: [1,2,4,8,16,32,64]`. Its `persistent` group is a separate SINGLE_CTA control and lists IVF_PQ; it does not redefine the main base graph.
- The accepted V1 scientific graph was built with the *Python API* default `build_algo="ivf_pq"` (C enum value 1), not with benchmark-base NN_DESCENT. R17R1 Stage A is explicitly a search-quality completion on that accepted graph, not a silent graph change.
- Stable `search_single_cta.cuh` caps itopk at 512. Stable `search_multi_cta.cuh` maps global itopk to `num_cta_per_query=max(requested search_width,ceil(itopk/32))`, with internal 32-candidate CTA pools. At itopk512, MULTI_CTA width<=16 does not raise CTAs/query beyond 16, motivating only widths 32/64 in the conditional A2 ladder.
- Stable `search_plan.cuh` resolves Q1 AUTO to MULTI_CTA at all planned itopk<=512 on the 76-SM RTX4080 (`max_queries=1 < 152`). Thus AUTO at the qualified 512/1 point is source-identical to the forced MULTI_CTA candidate, not an independent formal arm.
- The original official normalized `glove-100-angular` base/query and GT remain hash-identical to V1. Squared Euclidean over L2-unit vectors preserves angular/cosine ranking; no dtype/metric normalization change was made.

Stage A succeeded at 512/1 on the original IVF_PQ index. The conditional NN_DESCENT build was **not** triggered; neither the YAML fact nor the parent quality stop is rewritten as a performance result.
