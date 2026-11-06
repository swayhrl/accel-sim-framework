# 3DGS primary evidence and Q1 collision review

This is a CPU-only literature review, with no new training or performance measurements. Numeric entries in GS_PRIMARY_LITERATURE.json are authors' results; page/table locators and privately retained PDF hashes bind their scope.

| Work | Verified identity | Evidence boundary | Main collision with Q1 |
|---|---|---|---|
| [GS-Scale](https://99dhl.github.io/assets/pdf/asplos26_gsscale.pdf) | ASPLOS 2026 final; arXiv2025 is its preprint date | Real software testbeds; deferred optimizer contains an epsilon approximation | GPU geometry, CPU optimizer overlap, forwarding and zero-gradient memory reduction already exist |
| [CLM](https://cs.nyu.edu/~apanda/assets/papers/asplos26-cvm.pdf) | ASPLOS2026 author final | Real single-GPU training, explicit enhanced baseline and ordering/cache ablations | Camera reuse, selective appearance transfer and early optimizer finalization already hide CPU-GPU work |
| [TideGS](https://arxiv.org/abs/2605.20150v2) | ICML2026 Spotlight; v2 2026-05-26 | Real A5000/3090/A800 results; some frontier values are extrapolated | SSD-CPU-GPU working sets, delta transfers, trajectory ordering and asynchronous writeback already exist |
| [GSArch](https://ieeexplore.ieee.org/document/10946749/) | HPCA2025 DOI confirmed | Publisher abstract only; primary full methodology unavailable | Gaussian reuse, gradient filtering and bank-conflict hardware are prior art; no silicon/simulation claim is independently verified here |

The complete experiment-group register in the JSON separates capacity, training-throughput, quality, ordering/overlap, resource utilization and cost studies. Their denominators differ. Neither a maximum capacity gain nor a single-GPU cost advantage is automatically an end-to-end speedup. CLM's 10kHz SMsActive and TideGS's 1Hz nvidia-smi utilization also measure different things.

Q1 should remain a critical-path diagnostic. Our inference is that broad camera reuse, SH-transfer reduction, optimizer overlap and working-set prefetch are already absorbed by strong software. The next useful question is whether significant exposed wait survives those implementations on a qualified workload, after CPU thread count, affinity, NUMA, pinning and I/O contention are controlled. An OMP change that feeds the GPU faster is a software confound until separated from any GPU architectural variable. Overlapped CPU, communication and GPU durations must not be added as disjoint costs.

Numerical contracts differ: GS-Scale approximates deferred Adam; TideGS discards optimizer moments on eviction, cold-restarts admission, and changes view order. Its current repository setup also differs from the paper's runtime/batch/cache defaults. CLM's batch-internal mathematical equivalence does not establish floating-point identity. None of these author choices silently changes our acceptance rules.

No hardware candidate is promoted from these papers or from our current review. A future measured residual needs an explicit denominator and a controlled hardware hypothesis; if CPU scheduling or existing overlap removes the wait, classify SOFTWARE_ABSORBED. GSArch fulltext remains a declared primary-source gap instead of importing an unverified third-party simulator story.

Public paper downloads total approximately 9.93 MB and are private audit artifacts; no model/data download, CUDA import, GPU observation, lock or installation occurred. GS_PRIMARY_DOWNLOAD_INDEX.json gives exact SHA256 values.
