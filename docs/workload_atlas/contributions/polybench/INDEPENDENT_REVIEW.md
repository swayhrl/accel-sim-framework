# Independent cross-review by PolyBench auditor

## Particlefilter naive: independent source read

Fixed source: `accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1`, `src/cuda/rodinia/3.1/cuda/particlefilter/ex_particle_CUDA_naive_seq.cu`. Independently read lines113-134,430-590,612-670; this review does not rely on the Rodinia report text.

- The only GPU kernel in this implementation resamples particles. The random-walk/likelihood video access is CPU code at481-501; GPU signature113 has arrayX,arrayY,CDF,u,xj,yj and no video/image pointer. Labeling its GPU CDF scan as random image access would mix CPU/GPU boundaries.
- Thread i=128*bx+tx (115; threads_per_block128 at32). A valid input1000 gives8 CTAs/1024 launched threads with24 inactive. The frame loop473 is k=1..Nfr-1; Nfr10 predicts9 source launches568, not10. Each iteration copies six double vectors557-562, synchronizes569, reads xj/yj572-573, then CPU reassigns/reset weights581-585. This feedback is a CPU-mediated inter-frame dependency.
- At active loop iteration x, all still-scanning warp lanes address `BCDF+8*x`, a uniform same-address load, while `Bu+8*(i0+lane)` has lane stride8B. CDF iteration stride8B is loop locality, not lane scatter. Early break122-125 is data dependent; maximum1000 iterations, actual mean/distribution unknown. No source formula provides pending overlap probability or cache hit rate.
- For full aligned32-lane double u or xj/yj vectors, the256B span touches2 128B lines and8 32B sectors. CDF uniform8B fits1 line/sector under alignment; its next x spans a new sector every4 aligned doubles/line every16. Predicates and unknown alignment can change boundary counts.
- Gather arrayX[index]/arrayY[index] at131-132 uses index determined by CDF/u, with fallback index=Nparticles-1. Lane address delta8*(index[l+1]-index[l]) is data dependent. CPU forms CDF cumulative weights543-546 and ordered u=u1+i/N549-552. With valid nonnegative normalized weights/finite CDF, index is nondecreasing across increasing u; this supports ordered possibly duplicated gathers, not arbitrary random addresses. Exact footprint, scan length and duplication require input values.
- DTC-L1 candidate: CDF pending sharing among still-active lanes/warps, conditionally on timing; EP-L2 candidate: repeated small CDF and gathered position vectors across phases. Tiny8-CTA source grid and CPU copies constrain supply. No measured merge/latency/queue quantity is inferred.

This independently agrees with the Rodinia auditor's source summary. Capture-ELF equivalence, actual numeric CDF distribution, scalar input identity and complete trace bodies remain separate binding questions.

## PolyBench address self-check

All9 reports have10 sections; source snapshots round-trip their SHA256 hashes and all20 preserved CU/Makefile/helper files match coordinator fixed-commit blob proofs. Source launch predictions match bounded header counts for every program, including254 plane launches for3DCONV. Header/source agreement is not body completeness.

The independent coordinator review and this auditor agree on ATAX/MVT/BICG lane-versus-loop strides,16-CTA supply, GEMM broadcast/coalesced mapping, and2DCONV interior aligned nine-tap union9 lines/18 sectors (individual centered tap1/4; shifted2/5). For3DCONV, this audit additionally derives15 terms/11 coordinates, union17 lines/42 sectors per full aligned interior warp:2*(3lines,6sectors)+4*(2,5)+3*(1,4). These are address-set footprints, not issued transaction measurements.

Numeric caveats are preserved independently: ATAX y/tmp,3MM E/F/G,GESUMMV B/y/tmp are uninitialized before the source GPU accumulation. BICG zeroes its output first; MVT initializes all four vectors. Existing frozen results/identity are untouched.
