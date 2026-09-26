# Closest-work and novelty screen

Screen date: 2026-09-26. Author proposals are separated from this stage's
simulator evidence.

## Primary closest work

- Rogers, O'Connor, and Aamodt, **Cache-Conscious Wavefront Scheduling**
  (MICRO 2012, DOI `10.1109/MICRO.2012.16`) uses a locality detector and warp
  throttling to reduce cache contention. Primary author page:
  https://engineering.purdue.edu/tgrogers/publication/rogers-micro-2012/
- Chen et al., **Adaptive Cache Management for Energy-Efficient GPU
  Computing** (MICRO 2014, DOI `10.1109/MICRO.2014.11`) coordinates
  reuse-distance cache bypass with warp throttling in response to cache/MSHR/
  on-chip congestion. Author manuscript:
  https://people.csail.mit.edu/xchen/docs/micro-2014.pdf
- Xie et al., **Locality-Driven Dynamic GPU Cache Bypassing** (ICS 2015)
  performs runtime GPU L1 bypass management and explicitly treats MSHR/cache
  resource pressure. Author manuscript:
  https://hzhou.wordpress.ncsu.edu/files/2022/12/ICS_15.pdf
- Yuan, Bakhoda, and Aamodt, **Complexity Effective Memory Access Scheduling
  for Many-Core Accelerator Architectures** (MICRO 2009) addresses GPU DRAM
  request scheduling, row locality, and bank parallelism. Primary project page:
  https://www.microsoft.com/en-us/research/publication/complexity-effective-memory-access-scheduling-many-core-accelerator-architectures/
- Ausavarungnirun et al., **Managing DRAM Latency Divergence in Irregular
  GPGPU Applications** (SC 2014, DOI `10.1109/SC.2014.16`) coordinates GPU
  memory scheduling to control warp latency divergence:
  https://ieeexplore.ieee.org/document/7012998/
- Abaie et al., **Memento: An Adaptive, Compiler-Assisted Register File Cache
  for GPUs** (ISCA 2024, DOI `10.1109/ISCA59077.2024.00075`) couples a register
  cache with issue scheduling using compiler-estimated reuse distance. This is
  a different storage level, but it establishes that generic resource-aware
  issue policy is not by itself a novelty claim:
  https://upcommons.upc.edu/entities/publication/04d929ad-6bb3-46b3-ba5e-186704b951e2
- **RPAWS: A Resource-Pressure Aware Warp Scheduler for GPGPU** (IEICE ELEX,
  2026) explicitly uses compute/memory instruction classes and backend-unit
  busyness to prioritize warp queues:
  https://www.jstage.jst.go.jp/article/elex/advpub/0/advpub_23.20260028/_article/-char/en

## Candidate screens

### A. Scale-dependent L1-MSHR / DRAM balance

Our evidence: the exact L1/M1 GEMV pair responds in the same direction but at
different magnitude, and L1 responds similarly to two distinct resources.

Gate result: **FAIL_CLOSEST_WORK_DIFFERENTIATION**. The finite interaction and
online signals are real, but cache contention, MSHR/resource congestion, warp
throttling, bypass, and backend-pressure scheduling are already explicit goals
of the work above. Current evidence supplies an AI-trace characterization, not
a distinct mechanism problem or missing signal.

### B. Non-monotonic memory-service scaling

Our evidence: SPLITKV regresses under DRAM 2x; L1 DRAM upper is worse than its
2x point; T0 one-cycle L1 latency is worse than its 16-cycle point.

Gate result: **FAIL_LOCALIZED_CAUSE**. The DRAM ratio also changes derived
turnaround terms, and Observatory scheduling predicates lack producer-domain
provenance. The non-monotonic responses are retained, but they do not identify
a clean online policy or a closest-work-distinct architecture problem.

No architecture problem card is emitted.
