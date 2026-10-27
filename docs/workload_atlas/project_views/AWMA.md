# AWMA reuse view

This atlas supplies source semantics for future address-translation analysis. It does not establish AWMA admission of a DTC input or equivalence of virtual address spaces.

Use [ATAX/MVT/BICG cross-review](../CROSS_REVIEW.md) to separate lane stride, thread loop stride and broadcasts. For page size P, project a proven byte address a to floor(a/P) only after identifying the simulator address domain, allocation bases and mapping. A128B line footprint is not a TLB working set. A line-level merge is not a translation-MSHR merge.

[Parboil sgemm](../programs/parboil/sgemm.md) exposes plane strides and shared reuse; [particlefilter_naive](../programs/rodinia/particlefilter_naive.md) and [CFD](../programs/other/cfd.md) expose dependent gathers. Exact page counts for data-dependent indices need the admitted input. [sad](../programs/parboil/sad.md), [bfs](../programs/parboil/bfs.md) and conditional [kmeans](../programs/other/kmeans.md) require compiled special-path identification.

Multi-kernel pipelines make translation lifetime relevant. [EP/DTC member equivalence](../CROSS_PROJECT_MAPPING.md) concerns registered trace content; it does not equate ASIDs, allocator mappings, translation policy, page tables or warm state. A later AWMA study needs its own source/binary/trace/mapping/configuration identities.
