# Stable-source CAGRA capability audit

Scientific runtime source: `rapidsai/cuvs` tag `v26.08.01`, peeled commit `25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`. Runtime wheel: `cuvs-cu12==26.8.1`, SHA256 in `SOURCE_RUNTIME_RECEIPT.json`. The current-main commit named in the handoff was not used for runtime behavior or performance.

Source-bound facts:

- `python/cuvs/cuvs/neighbors/cagra/cagra.pyx`: Python `IndexParams` default `build_algo="ivf_pq"` (stable C enum `IVF_PQ=1`), metric `sqeuclidean`, intermediate degree 128, final graph degree 64. This **differs from the separate C++ parameter heuristic**; the Python default was used unchanged. Python `search()` accepts preallocated `neighbors` and `distances` buffers, which this screen supplied.
- `cpp/src/neighbors/detail/cagra/search_plan.cuh`: for nonpersistent, `AUTO` resolves to `SINGLE_CTA` only when `itopk<=512` and `max_queries>=2×SM`; otherwise `MULTI_CTA`. On the actual SM89 76-SM device the threshold is 152. Thus at fixed itopk64, Q1/Q32 AUTO aliases MULTI_CTA and Q256 AUTO aliases SINGLE_CTA. Source-proven aliases were not redundantly profiled as additional full arms.
- `cpp/src/neighbors/detail/cagra/search_multi_cta.cuh`: requested global itopk maps to `num_cta_per_query=max(search_width,ceil(itopk/32))`; the internal per-CTA pool uses 32 candidates and internal search width 1. Thus 64/128/256 correspond to 2/4/8 CTAs/query for widths 1 or 2. A mode difference may change actual search work and quality; it is not a pure hardware counterfactual.
- `cpp/include/cuvs/neighbors/cagra.hpp`: persistent mode is supported only with SINGLE_CTA. It was not run: recall failed before the persistent/host-control gate. The source warns that concurrent allocations/copies can block a persistent context.
- `python/cuvs/cuvs/neighbors/cagra/cagra.pyx`: index graph+dataset serialization and reload are supported, and the built uncompressed graph was serialized and hash-closed. Reloaded graph `(1,183,514,64)` and dataset `(1,183,514,100)` were exposed as device views during the screen.

This is a source/runtime capability table, **not** evidence of a GPU-local residual. The quality gate stopped the experiment before strong Q1, formal timing, wrapper fallback, persistent control, profiling or holdout.
