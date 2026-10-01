# Translation literature notes, independent of C16 measurements

Updated 2026-10-01. This document is a reusable literature index. The per-paper disclosure matrix and chronological problem → mechanism → residual analysis for the present screen are in `docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_V2_TRANSLATION_TLB_SCREEN/`.

| Failure mode | Primary sources | Applicability boundary |
| --- | --- | --- |
| TLB reach and allocator contiguity | [Mosaic](https://research.ece.cmu.edu/safari/pubs/mosaic-micro17.pdf); [Avatar](https://zoon17.github.io/pdfs/avatar_micro24.pdf) | Large virtual page spans alone do not prove physical contiguity, promoted mappings or elapsed-time benefit. |
| Warp VPN locality and MSHR capacity | [LATPC](https://yonsei.elsevierpure.com/en/publications/latpc-accelerating-gpu-address-translation-using-locality-aware-t/); [DEPOT](https://arxiv.org/html/2606.00486) | Page sharing can amplify an interference miss; reach overflow is a different class. TLB miss count alone does not select a mechanism. |
| Page-walk service throughput | [SoftWalker](https://zoon17.github.io/pdfs/SoftWalker_micro25.pdf); [cuPTW](https://maxkev1n.github.io/publications/sigmetrics-2026/3805633.pdf) | Requires observed queueing/blocked time and a platform-specific cost model. |
| LLM weight/KV translation competition | [Cheon et al.](https://doi.org/10.1109/LCA.2026.3693796); [local extraction from the supplied PDF](../paper_specs/SEGMENTATION_LLM_2026.md) | Evaluated with a modified contiguous-weight allocator and synthetic long-context KV pressure; not a measured C16 result. |
| Wafer-scale remote translation | [HDPAT](https://sarchlab.org/hdpat_hpca_2026.pdf); [Clover](https://scholarx.skku.edu/item/cb5add4f-a64d-45b1-8982-b7b845ec6d77); [RIPPLE author listing](https://sarchlab.org/publication) | Mesh hops, remote page-table fetch and distributed GMMUs are absent from a single-GPU C16 capture. RIPPLE quantitative details remain unknown without full text. |
| UVM migration versus translation | [GPUVM](https://arxiv.org/abs/2411.05309); [ACOPT](https://www.sciencedirect.com/science/article/pii/S0167739X25003437) | Migration, remote residence and MCM/IOMMU path must not be inferred from resident local-memory page IDs. |

The key reusable method is to obtain an address-domain page behavior result first, then measure translation-specific blocked time, then compare against large pages, layout/allocator, MSHR/prefetch and segmentation controls. Workload evidence must come from the workload being studied. Simulator results on other applications and AWMA results cannot fill a C16 measurement gap.
