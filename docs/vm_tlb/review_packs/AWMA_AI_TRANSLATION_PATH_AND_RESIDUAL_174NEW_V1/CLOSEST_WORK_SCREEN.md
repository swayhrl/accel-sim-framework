# Closest-work screen

- Pichai et al. (DCS-TR-703 / ASPLOS 2014) explicitly model TLB access prior
  to or in parallel with a VIPT L1 cache. B1 is a conservative diagnostic of
  this known path choice, not a new mechanism.
- Yoon, Lowe-Power, and Sohi (ASPLOS 2018) use virtual L1/L2 caches to filter
  translation before cache hits, while paying virtual-tag, permission,
  synonym, coherence, and shootdown costs. This is why B2 cannot be represented
  as a free current-cache hit.
- Shin et al. (ISCA 2018) already batch/priority-schedule page walks from one
  SIMD instruction, including the last-walk progress observation.
- Neighborhood-Aware Translation and MPW address miss/walk locality or walker
  throughput, not the current hit-dominated path; MPW also reports a distinct
  no-translation-before-L1 sensitivity.
- LATPC already includes warp-instruction VPN coalescing, multi-VPN MSHR
  compression, regularity detection, and walk batching.
- Avatar's baseline is VIPT-parallel and CAST starts on L1-TLB misses; current
  hit-dominated path sensitivity alone does not establish Avatar applicability.
- MASK/RPAWS already cover broad translation/data interference or generic
  compute/memory pressure scheduling.

No existing-trace result passes the residual novelty gate. New native targets,
if supplied, must first demonstrate a material resource-specific residual after
B1 before a problem card can exist.
