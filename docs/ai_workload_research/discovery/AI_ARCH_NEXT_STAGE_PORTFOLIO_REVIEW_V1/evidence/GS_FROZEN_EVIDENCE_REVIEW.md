# GS frozen evidence review

This is a scope reconfirmation of accepted A44/A28/A45H/A46 evidence, not a new runtime discovery. Native authority remains cf80f6ec07a31eccdaff264c3bce64e0511179f8 (tree c66008a9da553d06a00195c8c133c3e7ec16692d). Coordination is frozen at ed365741b230718f6ffc1ccbed125fc2566aac15. Branch existence is not execution evidence. Exact report/tool/raw blobs and SHA256 are in the JSON manifest.

R0/R1/R2/R4 are accepted, R3 is bounded real training/early functional qualification. Both host trajectories ran continuously from zero to15200. They share every cameraID but end at6,672,954 and6,684,932 Gaussians, so their late times are not paired-state speedup evidence. No200k convergence, matched time-to-quality or lateGPU-only result exists.

## Accepted observer and interval interpretation

The old observer mixed H2D copy_ host calls into a D2H-like tag; its directional breakdown is disqualified. The corrected fixed AST observer classifies destination names and source lines, separates metadata/ID/gradientD2H from parameterH2D enqueue, and records parameter-forwarding Adam. Old raw remains indexed. Source model math was not changed.

A44 already accepted the following recomputation. All intervals below are host monotonic unions per diagnostic step; no CUDA duration is added.

| Window | Diagnostic / next original-body mean ms | Cross-thread waits ms | Main-thread waits ms | Worker sync ms | Worker-sync overlapping CPUAdam ms |
|---|---:|---:|---:|---:|---:|
|100?200|47.172 /39.268|7.834|6.378|2.983|see JSON|
|14500?14600|186.431 /132.480|30.871|14.084|17.573|15.813|
|15100?15200|147.425 /133.810|32.128|14.746|17.382|17.382|

The original summarizer unions all synchronize tags, including GPU-worker L728 and main-thread L1023/L1074. Removing worker L728 reproduces A44's14.084/14.746ms. Every L728 interval is contained in its recorded GPU-worker host envelope. Raw does not store OS thread IDs; interpretation also relies on fixed source lines and accepted A44 attribution. The30?32ms values are not recoverable main-thread stalls or hardware speedup bounds.

CPUAdam per-step intervals are57.746/64.779ms and next-parameter forwarding41.855/45.489ms. GPU-worker host envelope ends first in45/49 and50/50CPUAdam-call steps; signed CPUAdam-end minus worker-end means37.115/40.413ms. This locates a processing/hand-off candidate under OMP16, not a pure device-aligned Adam exposed tail. Step14500 alone is2.454757s; excluding it gives other49diagnostic mean140.139ms. Diagnostic first50 and original-body next50 use different cameras, so their difference is not exact observer overhead.

## Full-N scans versus actual updates and thread policy

Accepted A28/A45H source audit distinguishes calculate_update_ids' three full-N passes plus visible-ID marking/collection from selected Adam updates U; update_counter increments N and resets U. Natural N_visible/U/counter distributions were not logged in GR1. The globalGaussian count must not be multiplied by all parameters to fabricate update counts or DRAM bytes.

Original omp_set_num_threads64 remains, while real native training caps OMP at16. The canary proves its bounded numerical fixture and thread cap, not author64training performance. Accepted A45H synthetic CPU component measurements already show OMP8 beats16 for two Adam shapes while scans can prefer16. These are software counterevidence, not real-late wall speedups. A46 additionally notes terminal torch_threads64 despite entry requests1 and effective OMP limits1/8/16: do not describe PyTorch threads as always1. Author64real-training counterfactual remains unmeasured.

## Reuse, SH transfer, optimizer and checkpoint limits

All15200cameraIDs agree across old/corrected replays; each reviewed100stepwindow has100distinctcameraIDs. Camera sequence is not stableGaussianIDs or Gaussian-set intersection. Densification changes row identities; cross-step cache hit/reuse remains unmeasured.

A28's static source model has196B appearance,392B CPUmoments,708B all-parameter+moments per Gaussian, or944B if allgradients materialize. A nominal active transfer model196BH2D+196BD2H+4BID=396B assumes confirmed int32IDs and materialized payload; it is not measured PCIe traffic. SH rendering degree ramps0..3, while full45shN coefficients are prepared/uploaded in the audited source. Early unnecessarySH transfer is a software hypothesis; three gradient-copy source lines execute in early diagnostics, but payload sizes, nonzero gradients and active update counts are absent.

GS-Scale already has deferred/parameter-forwarding Adam. CLM already studies CPUoffload, camera reuse, doublebuffer and overlap. CLM4K/batch4/differentCOLMAP and GS-Scale1K/batch1/200k are different science identities, not interchangeable baselines.

The15200external stop can leave pending CPU-pipeline gradients. No complete validated late optimizer/counter/RNG/loader checkpoint exists. Splat-only state cannot establish a valid late resume. Resource receipts establish bounded sampled RSS/VRAM/thread use; they do not identify CPUbandwidth, cache, PCIe or SM causality.

## Portfolio consequence and provenance

Use this as already accepted evidence, not another request for the same CPU audit. Strong same-semantics software/thread-policy explanation, natural visible/update sets, complete late-state provenance, physical-resource attribution and long quality remain open. No retraining, GPU trace, lock action or new mechanism is authorized.

The author source hashes are registered in frozen SOURCE_PROVENANCE, but their original Git blob objects were unavailable locally. No source fetch or active private directory search was performed. Detailed scan/SH/checkpoint statements therefore cite accepted fixed A28/A45H/A46 audits; this review independently reads only frozen report/index/tool/raw Git blobs. CPU resource/read-range receipts and reproducible definitions are in the JSON. No large raw is copied.


## Q1 late-window minimum-contract supplement

The frozen verified config has max_steps200000, steps_scaler1, refine_start500, refine_stop15000, refine_every100 and reset_every3000. Keep these original values; no forced densification disable is needed to choose a post-refine window.

Both historical trajectories last change net N at step14900, then stay at their separate final counts through15200. Existing [15050,15200) has150stable-N records, mixing100ordinary and50diagnostic steps. [15100,15200) has only100records (50diagnostic,50ordinary); including final15200 yields101, not150. The existing pure original-body late subset is [15150,15200),50records. Net N stability is not permanentGaussianIDs, unchanging membership or optimizerstate; weights/moments/counters still evolve.

A future Q1 contract must preregister original schedule, late-window observer/ordinary denominators and valid continuously reached or fully restored state provenance. Existing incomplete checkpoints/pending-gradient stop cannot supply that restore. Same seed/camera order across thread policies still does not guarantee matched densification states.

GR1 sampled process-tree RSS peak26,337,488,896B (24.529GiB) exceeds16GiB. Its old host ceiling48GiB is historical authority, not a new resource grant. Q1 needs an independent memory cap/qualification with buffer and charged-memory headroom; it cannot inherit the Qwen16GiB contract.

Keep original64thread request distinct from effectiveOMP16. A45H's historical24logicalCPUs/affinity0?23 is not a current allowed-cpuset reading. Future authorized qualification must bind allowed logical CPUs, process-tree budget, OMP/Torch terminal state and P/Ecore/SMT/affinity confounding. No current asset/process/cpuset inspection was performed for this supplement.
