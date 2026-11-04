# Seven long-tail programs: fixed kernel mapping and evidence-ready analysis

This is static/read-only preparation, not a new performance result. Atlas commit `47a097aad4406893a07f8d230e1e0a850609bf39`; candidate application sources `accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1`; simulator Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`. No live output, simulator, trace capture, controller or source mutation was used.

`SOURCE_BINDINGS.json` supplies all31 source byte SHA, upstream paths and1-based line ranges; `fixed_atlas/` preserves the7 original audits. `KERNEL_SEQUENCE.json.gz` records all6844 exact ordinal/symbol/traceSHA/input/full-body-binding identities and preceding static HtoD commands. The18 Atlas phase rows include a separate second-reduction phase for the same SRAD global definition; there are17 unique source definitions.

| Program | Registered kernels | Exact sequence / source boundary |
|---|---:|---|
| cutcp | 11 | 11 identical symbols; source-compatible z-plane launches. Grid11×11, block8×2×8 from fixed Atlas headers. |
| histo | 80 | 20 exact registered prescan→intermediates→main→final groups;80 launches. Grid64/65/14×3/42 and blocks512/498/768/512 are frozen header facts. |
| GESUMMV | 1 | One gesummv_kernel,16 CTAs×256 threads; no iterative source termination. |
| 3DCONV | 254 | 254 ordered instances of one convolution3D symbol; grid8×32 and block32×8. Ordinal does not bind the kernel scalar plane i. |
| 3MM | 3 | K1 E←AB, K2 F←CD, K3 G←EF;1024 CTAs each, source explicit synchronization after every launch. |
| myocyte | 5993 | 5993 repeated RHS kernel launches, each2 CTAs×32threads;5993=13×461 is compatible with13 RHS calls per adaptive attempt, not proof of461 actual attempts or100 accepted integration steps. |
| srad_v1 | 502 | Exact502-launch sequence: extract;100×(prepare,reduce450CTA,reduce1CTA,srad,srad2);compress. Second reduce is the same unique symbol with a distinct phase/geometry. |

Body qualification means all declared trace CTAs/warps have terminal exits under the frozen binding. It does **not** certify original input numerical bytes, capture ELF/source equivalence, CPU work or whole-application correctness/completion. The older Atlas header-only body uncertainty and the later frozen body qualification are kept as different evidence layers.

## Read-first mechanisms and checks

### cutcp — af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8

Half-warp global bin loads stage8 float4 atoms/bin into shared AtomBinCache; every CTA reuses them for512 lattice points. Four per-thread output positions; no source global atomic. CTA batch barriers; CPU bin overflow/exclusion work and output conversion remain outside the GPU replay. Planes can reread overlapping bins without a B-output producer dependency.

11 grids agree with88³ padded lattice under candidate source; unpadded extents, atom bytes and CPU contribution are not certified by geometry.

After natural closure: Compare ordered plane interval cycles with accepted L2 reads/misses, issued DRAM atoms and retry events; do not label a later plane steady-state by ordinal. Compare within-design new misses/valid hits/evictions and lower_created versus shared staging. Shared atom reuse is not ordinary L1 reuse or measured MSHR merging.

Still missing: Per-object bin/output cache hits; Outstanding same-line lifetime overlap; Exact CPU/GPU whole-application time.

### histo — 2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64

Prescan samples part of input with shared reduction and2 range-word atomics; intermediates writes packed descriptors; every main y partition rereads its x descriptor stream and uses packed shared atomics plus conditional global tails/overflow; final reduces14 private slices. Host DtoH min/max governs main range grid; inter-kernel producer dependencies and barriers; source argv trailing4 is not consumed as a second algorithm parameter.

1140 registered commands include1060 HtoD,1041 before the first kernel and19 single-copy later boundaries. Command placement is bound; original image header/numerical validity and capture ELF remain unresolved.

After natural closure: Keep prescan/mapping/main/final separate and retain all20 group ordinals. Attribute GLOBAL reads/writes/atomics by printed access type, not all shared atomic work to L2. Test whether main descriptor rereads or final partial-slice reads accompany cycles/retry/DRAM changes; whole-cache misses cannot identify an array or prove an atomic contention cause.

Still missing: Histogram value distribution and exact hot-bin contention; Capture ELF/source initialization equivalence; Original image-content SHA and bounds/numerical validation.

### GESUMMV — 769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4

Two4096² matrices: fixed-j lane stride16384B; x warp-uniform; tmp/y contiguous ownership. Two4096-step per-thread accumulation chains. No source shared tile or parallel reduction. Limited16-CTA supply and dependent per-row arithmetic; actual overlapping request population is not established by two source streams.

NO_ARGS candidate dimensions and five HtoD commands totaling134266880B match object sizes. Capture source/ELF unbound; candidate S has uninitialized B/tmp/y, distinct from repaired alternatives.

After natural closure: Compare cycles, lower-created/Tag evictions, typed L2 reads and DRAM issued reads; distinguish retention/mapping association from FR/shared-credit relief. Only use compatible request-denominator latency means; row scatter footprint is not a measured simultaneous outstanding count.

Still missing: Source-to-capture ELF identity and original numerical contents; Per-array retention and tag-set conflicts; Complete L2→DRAM queue/service critical path.

### 3DCONV — 79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d

Candidate expression has15 terms but11 distinct coordinates, not a canonical27-point stencil; lane-contiguous k, shifted neighbors and B-plane stores. No shared staging or per-thread reduction loop. Source serializes planes; neighboring launches can reuse A planes but do not consume prior B. Repeated operands may be compiler-eliminated; source term count is not machine-load count.

Two initial64MiB HtoD commands, then254 kernels. Full declared trace body qualification is preserved; scalar i, capture ELF and full-application numeric/output semantics remain uncertified.

After natural closure: Retain per-instance sequence rather than averaging into one synthetic steady plane; compare cycles, L2/DRAM deltas, Tag evictions and lower requests. Check initial forced-tag state and cross-launch residency effects before claiming downstream-window saturation.

Still missing: Actual scalar i for each ordinal; Compiler elimination/emitted-load linkage to candidate source; Address-tagged proof of cross-plane cache reuse.

### 3MM — 977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d

Every phase has uniform left operand and lane-contiguous right/output operands,512-step accumulation. Eight CTA warps can reuse a right-row segment. E/F are written then read by K3. K1/K2 mathematically independent but source serialized; K3 consumes both. No shared tile/barrier in kernel. Accumulator source += does not fix emitted RMW frequency.

Seven initial1MiB HtoD commands. Candidate S E/F/G lack explicit zero initialization, whereas a corrected source exists; selected historical ELF is not bound to either.7MiB object sum does not prove L2 residency.

After natural closure: Compare the three true phases separately; K3 producer-consumer association needs valid-hit/new-miss/lower request and typed L2/DRAM evidence. A previous Hash gain does not imply F-window gain; preserve exact zero and regression. Distinguish common system improvement from extra DH benefit.

Still missing: Object-specific producer retention/hit proof; Capture binary and accumulator promotion; Native numerical equivalence/initial contents.

### myocyte — 977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992

Candidate mode0 only lane0 in each CTA works: ECC plus three sequential CAM helpers use a tiny scalar state/parameter slab. Device helpers are not separate kernels. Long math/dependency chains; source-repeated addresses do not prove pending merges. CPU constructs every Fehlberg stage, copies state/parameters, launches RHS, copies derivative/com and finishes flux/error control. It may retry/return early. Mode1 is an excluded alternative.

All5993 instances have exactly2 preceding HtoD commands,11986 total/2612948B. Do not infer periodic full-application progress, accepted timesteps, trajectory correctness or CPU walltime from the trace count.

After natural closure: Keep every RHS ordinal; use its own instruction/CTA identity and cycles. Do not replace unequal RHS instances with one periodic average or assign accepted step IDs. Compare DH finite-service item sums/integrals with retired/sample denominators and low request concurrency; tiny footprint or terminal0 does not prove lack of transient pressure.

Still missing: Accepted/rejected CPU step IDs and termination/output proof; Capture ELF/y.txt/params.txt binding; Candidate timeint truncation and CAM output-pointer/unwritten-com risk versus actual historical binary.

### srad_v1 — 0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4

Column-major502×458 image; contiguous/shifted neighbor streams plus four difference arrays and c. First reduce lane stride4B; second source m512 lane stride2048B, single CTA. Separate srad writes differences/c before srad2 updates I. Each group has reduction450→1 and CPU statistic roundtrip; next group consumes updated I. No source shared stencil tile or GPU atomic. Source repeated groups do not certify numerical application completion.

Five initial HtoD commands totaling927344B and502 registered kernels; source command100_0_5_502_458 is compatible, original image bytes/capture ELF/output unbound.

After natural closure: Keep reduction passes separate from stencil phases and retain100 exact group indices. Correlate their cycles/typed L2 reads/DRAM/retries with CH/DH P0/F. Do not subtract running maxima for per-phase pressure. Use interval additive DH service integrals and preserve one-CTA concurrency limitation versus450-CTA phases.

Still missing: Exact queue occupancy/wait distribution and critical path; Per-object inter-phase residency; Capture ELF/numerical validity; candidate second-pass remainder omits d_mul at reduce94–95.

## Ready to fill, with missingness preserved

`CLOSED_EVIDENCE_FILL_TEMPLATE.json` contains42 fixed CH/DH × P0/F128/F256 slots and disjoint ordinal selectors for all18 phases. Join by full input digest, actual design/profile, ordinal and exact symbol. Consume only qualified naturally closed source identities. Retain whole strict cycles, kernel intervals and their reconciliation separately. A phase total requires every selected boundary; keep missing counts and never replace missing by0. No per-program best-F selection is allowed.

`COUNTER_CONSUMPTION_RULES.json` and12 exact fixed-Core/Framework excerpts specify typed units/scopes. Key boundaries: accepted GLOBAL read32B sectors differ from all-access misses and DRAM write-allocation reads; retries are events, not requests or critical-path cycles; `gpu_stall_dramfull` is ICNT/subpartition admission pressure, not isolated DRAM queue time. Source Tag bank conflicts differ from mapping evictions. CH commonPIB256 and DH OO_PIB128 use different active paths; generic DH PIB8 is not its OO capacity. Service integrals need their matching samples/retired denominators; terminal gauges and running peaks cannot be differenced into phase pressure. MRQ latency is a request-population mean until bank assignment, not complete L2→DRAM latency; per-phase exact means remain unavailable without matching numerator/denominator.

With the fixed perf_sim_memcpy1 model, HtoD commands force L2 tag state rather than issuing ordinary timed DRAM traffic. The actual static command placements matter: every myocyte RHS has2HtoD, while SRAD only has5 initialHtoD. They do not measure CPU-copy wall time or prove cache hits/pending merges. F128/F256 change FR-FCFS capacity **and shared credits**, preserving10MiB L2/850MHz; mechanisms cannot be attributed to an isolated queue or equal-area CH/DH.

Candidate-source numerical risks already present in Atlas (GESUMMV/3MM initialization variants, myocyte integer time/CAM pointer risks, SRAD second-reduction remainder) remain audit caveats and are not silently patched or promoted to statements about the historical capture binary. The English v0.23 manuscript and all accepted/negative historical identities remain unchanged.

CPU checks cover31 fixed source SHA joins, seven exact static command sequences and disjoint phase coverage of6844 kernels. These are integrity/source checks, not new runtime measurements; all performance placeholders remain null.
