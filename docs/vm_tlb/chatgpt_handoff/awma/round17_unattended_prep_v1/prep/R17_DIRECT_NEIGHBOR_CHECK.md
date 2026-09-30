# R17 direct-neighbor check

Date: 2026-09-30.

CAGRA already implements multi-CTA search for low-batch cases. Stable cuVS also includes persistent CAGRA and dynamic batching for concurrent small requests.

SONG separates candidate locating, distance calculation and search-state update inside a dependent graph-search loop.

The inspected Jasper beam-search kernel uses one CTA per query and repeatedly advances frontier discovery, neighbor expansion, distance calculation and candidate maintenance.

These results close generic claims about low-batch underutilization, multi-CTA per query, persistent request handling and dynamic request aggregation.

The remaining R17 question is narrower: whether an isolated real query still has an unexplained GPU-local residual after mature CAGRA multi-CTA/search-width execution and runtime accounting.

State: `R17_DIRECT_NEIGHBOR_SCREEN_PASS_WITH_NARROWED_CLAIM`.
