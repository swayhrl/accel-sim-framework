# Author-input request template

Use the relevant block below before labelling a generated trace as an exact
paper reproduction.  Include the paper DOI/title and a concise statement that
we are reproducing the cache mechanism using Accel-Sim V100 SASS traces.

## TLS Cache

Subject: workload/input details or trace artefact for TLS Cache reproduction

Hello authors,

We are reproducing *Exploiting intra-chip locality for multi-chip GPUs via
two-level shared L1 cache* with Accel-Sim.  Could you share either the trace
artefact or the exact workload recipe for Table 2?

1. Exact suite release/commit for Mars, Rodinia, SHOC and Parboil.
2. Exact command line and data file for every workload, especially Mars SS,
   SHOC FFT/SORT/GEMM/ST2D/REDC size and pass count, and Parboil SPMV matrix.
3. CUDA toolkit, driver, compiler flags, target GPU ISA, and whether binaries
   were compiled with line information, debug flags, or library versions.
4. Whether measurements use a warm-up, a kernel subset, a dynamic instruction
   cap, or all application kernels to completion.
5. Trace format/tool version and any preprocessing/filtering before simulation.
6. The multi-chip address mapping/page size and exact configuration files used
   for the ICL classification and the main performance plots.
7. On CUDA 11.8/V100, Mars SimilarityScore (`512 128`) creates two NVBit CUDA
   contexts: a 199-kernel MapperCount stream and an 182-kernel MapReduce sort
   stream.  Does your trace workflow model these as separate streams, and if
   so what ordering/scheduling policy should a single-context simulator use?

If an artefact can be shared, a manifest with binary hashes, data hashes and
kernel lists is sufficient; raw traces are not required initially.

Thank you.

## C2P Cache

Subject: workload/input details or trace artefact for C2P Cache reproduction

Hello authors,

We are reproducing *C2P-Cache: Scalable GPU L1 Cache Sharing via Concurrent
Candidate Pruning* with Accel-Sim.  Table 2 names 24 workloads but does not
identify their exact inputs.  Could you share either your trace artefact or:

1. Exact release/commit and command line/input file for each ISPASS, Rodinia,
   Parboil, PolyBench and Pannotia workload.
2. In particular: ISPASS BFS graph and RAY dimensions; Pannotia color_max,
   fw_block, mis and pagerank graph files; and whether Parboil MRI means
   `mri-q` or `mri-gridding`.
3. CUDA toolkit/driver/compiler flags, target GPU ISA, and trace-tool version.
4. Whether all kernels run to completion, and any warm-up/kernel filtering or
   dynamic instruction limits.
5. The exact baseline configuration and mapping of paper workload names to
   trace directories.

A table containing command lines, file SHA256 values and kernel lists would
let us reproduce the inputs without transferring large traces.

Thank you.

## FRC Cache

Subject: original workload/configuration artefact request for FRC reproduction

Hello authors,

We are reproducing *Improving GPU Cache Hierarchy Performance with a Fetch and
Replacement Cache*.  We understand the paper uses AMD OpenCL SDK 2.5 and an
HD7770-like Multi2Sim configuration, so NVIDIA SASS traces cannot reproduce
the original instruction stream.  Could you share:

1. The Multi2Sim revision/patch and GPU/cache configuration files.
2. Exact AMD APP SDK 2.5 workload commands and data sizes for all 16 tests.
3. Any simulator checkpoints/traces, plus warm-up/termination conditions.
4. The scripts used to generate the reported OPC and cache statistics.

This will let us separate an architecture-faithful FRC reproduction from our
existing CUDA/QV100 causal mechanism port.
