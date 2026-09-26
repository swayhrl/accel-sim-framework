# Closest work after the strong baseline

## Exact residual: modeled L1 lookup latency on a hit-dominated path

The residual is not an uncovered AI-specific translation request type. It is
the cost of servicing one remaining unique VPN group through a 10-cycle L1 TLB
lookup on a sequential translation-before-data-cache model. Most lookups hit,
but the diagnostic also shortens miss detection; the claim is therefore
hit-dominated rather than hit-exclusive.

- Pichai, Hsu, and Bhattacharjee (DCS-TR-703 / ASPLOS 2014, section 5,
  `https://scholarship.libraries.rutgers.edu/view/pdfCoverPage?download=true&filePid=13643522050004646&instCode=01RUT_INST`)
  explicitly place
  TLB access prior to or in parallel with a virtually-indexed,
  physically-tagged L1 cache and discuss hit-time/port tradeoffs. This directly
  covers hiding ordinary TLB-hit latency with cache lookup.
- Yoon, Lowe-Power, and Sohi, “Filtering Translation Bandwidth with Virtual
  Caching” (ASPLOS 2018, sections 1 and 4.1,
  `https://arch.cs.ucdavis.edu/assets/papers/asplos18-gpu-virtual-caches.pdf`),
  send coalesced requests to virtual L1/L2 caches
  without a TLB access and translate only after an L2 virtual-cache miss. This
  is an existing, stronger cache/translation-path intervention for filtering
  translation work, with its own synonym/coherence cost.
- Additional small/fast TLB levels or a lower TLB latency are conventional TLB
  hierarchy design points, not an AI-specific mechanism.

## Retired diagnostics

H1 has high overlap with Shin et al., ISCA 2018 (sections III--IV,
`https://www.csa.iisc.ac.in/~arkapravab/papers/GPU_page_walk_scheduler_ISCA_18.pdf`):
their baseline already
coalesces same-page requests from one SIMD instruction; progress is determined
by the last walk; their scheduler attaches instruction identity, batches walks
from the same instruction, and prioritizes lower estimated translation work.
AWMA's unique walk population is small relative to L1 hits and PWQ-full is
zero; repeated MSHR-full retries on some targets are retained as an observed
symptom, not declared absent or converted into runtime fraction.

H2's prerequisite is false in the accepted source. The reverse accessq scan
selects the head group first, so a non-head prelaunch cannot win the sole L1
port before a simultaneous eligible head group. Generic demand-over-prefetch
priority would not be a novelty claim in any event.

LATPC full-text review further closes warp-instruction page coalescing,
unique-VPN regularity, multi-VPN MSHR compression, and walk batching as known
capabilities. None is renamed as an AWMA candidate.

## Boundary

Changing the data-cache address model to VIPT/virtual caching, adding a faster
TLB level, or lowering the frozen 10-cycle parameter would be a platform/path
design study—not the differentiated residual mechanism required by this Goal.
