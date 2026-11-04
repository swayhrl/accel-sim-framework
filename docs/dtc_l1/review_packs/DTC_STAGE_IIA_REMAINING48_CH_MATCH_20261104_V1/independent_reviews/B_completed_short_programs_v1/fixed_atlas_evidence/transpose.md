# transpose - source and behavior audit

## 1. Program and algorithm

A comparison program containing eight copy/transpose variants over a square float matrix. copy and copySharedMem preserve positions; naive/coalesced/padded/diagonal kernels produce a full transpose. FineGrained transposes within tiles without moving tiles; CoarseGrained exchanges tile positions without transposing their interiors. The latter two deliberately bypass full-transpose validation and are not equivalent algorithms.

## 2. Source authority and build

Reviewed immutable candidate accel-sim/gpu-app-collection@b059fdae25c2aabf737486aada743fca114469ce under src/cuda/sdk/4.2/. The freeze records cudasdk/9.1 capture paths, not certified source ancestry. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) contains file SHA-256 and Git blob IDs. Makefiles list CU/CC files and include ../../common/common.mk; capture-time nvcc flags, expanded macros and ELF SHA are not bound. Header binary version70 does not certify a compiler or build recipe. SOURCE_VERIFIED means this candidate implementation was read. transpose.cu:36-37 sets TILE_DIM16,BLOCK_ROWS16; :54 sets NUM_REPS1. Different CUDA sample releases commonly use32x8 tiles; those formulas cannot replace this16x16 implementation. The pointer-selected eight-kernel host switch is in :614-632.

## 3. Host control and launch order

Host parses dimX/dimY(:429-459),requires square sizes and integral tiles(:538-550),fills input with increasing values,computes CPU gold and copies input. For each kernel in order copy,copySharedMem,transposeNaive,transposeCoalesced,transposeNoBankConflicts,transposeCoarseGrained,transposeFineGrained,transposeDiagonal: warmup launch with nreps1; NUM_REPS outer launches with nreps1; one inner-timing launch with nreps=NUM_REPS(:648-671). With NUM_REPS1 this is3 per variant,24 total. Copy output is compared to original,partial variants bypass check,full variants to CPU transpose(:636-641).

## 4. Distinct kernels

copy(:197-208) direct load/store; copySharedMem(:210-231) loads shared[16][16],barrier,stores same coordinates. transposeNaive(:238-250) loads row-major and stores transposed strided addresses. transposeCoalesced(:254-277) loads shared[ty+i][tx],barrier,stores shared[tx][ty+i] at swapped tile coordinates. NoBankConflicts(:281-304) pads shared pitch17. Diagonal(:317-355) uses padded tile and remaps CTA coordinates,then same transpose. FineGrained(:366-384) reads same tile and stores transposed shared indices into same tile position. CoarseGrained(:388-409) swaps tile coordinates but stores shared[ty+i][tx]. Each has outer r<nreps and inner i=0; i<16;i+=16,so selected nreps1 gives one element/thread. Repeated timing launches are distinct from repetition inside a kernel.

## 5. Thread and address formulas

Let x=16*bx+tx,y=16*by+ty. All ordinary input addresses I+4*(x+W*(y+i)). copy/shared-copy output same index; naive output O+4*(y+H*x+i). Coalesced/padded output O+4*(16*by+tx+H*(16*bx+ty+i)),shared read[tx][ty+i]. Coarse same swapped global address but shared read[ty+i][tx]; fine output O+4*(x+H*(y+i)) with shared read[tx][ty+i]. Diagonal square case by'=bx,bx'=(bx+by)%grid.x; rectangular source branch linearizes bid then by'=bid%grid.y,bx'=(bid/grid.y+by')%grid.x; substitute primed coordinates in coalesced formula. Adjacent lane delta4B within16lane half warp,then next row; naive output lane delta4H B and lane15->16 transitions to next y. r repeats the same addresses;i would advance rows16,but selected tile has onlyi0.

## 6. Dataflow, coalescing, locality and concurrency

AtW=H512,base128B-aligned,each regular input/output warp consists of two64B row segments:2lines/4sectors for128usefulB; adjacent xCTAs cover the other half of the same128B row lines. Naive output full warp touches16distinct lines/sectors: two half warp rows write adjacent4B words in each of16columns. Thus128usefulB over512sectorB gives4x sector amplification (16*128B line footprint gives16x),not the32line pattern of a32wide tile. Coalesced stores restore two64B segments. Shared padding changes bank mapping without changing global logical data volume. Diagonal permutation changes tile-to-CTA mapping,not per-tile addresses or guaranteed schedule. All1024CTAs independent per launch; barriers/shared tiles constrain residence. Timing repetitions can repeat addresses but cache residence is unmeasured.

## 7. Frozen input and trace binding

Selected65151d2c661f88f3b463dba9a3ce49d98848affabe19a36ccf23295f3b1e8fdc,dimX512_dimY512,bundle0045bfe9... . HtoD1048576B=512^2*4;24launches,each grid32x32/block16x16,eight names each3times. Headers shared0(copy/naive),1024(copyShared/coalesced),1088(padded/coarse/fine/diagonal). Candidate repetitions agree with observed sequence; nreps arguments are inferred from recipe,not header-extracted.

## 8. Source-proven architectural features

Eight distinct kernel definitions; controlled variation of store stride,shared transpose/padding,partial transpose semantics and CTA permutation. Separate repeated launches and in-kernel memory repetitions are explicit. No atomics,texture or data-dependent global pointer traversal.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: naive scatter versus coalesced stores, neighboringCTAs touching opposite line halves and three timing launches offer testable differences in tags,pending sharing and physical retention; shared bank effects are a separate service path. EP-L2: store-sector expansion,partial-line writes and CTA tile ordering may affect tag/data/write queues. Header geometry permits static footprint derivation but cannot establish scheduling conflicts,merge counts,latency or speedup causality.

## 10. Evidence and limitations

Fixed transpose/transpose.cu:36-54,197-409,429-459,538-557,614-671. SOURCE_VERIFIED=candidate; INPUT_BOUND=yes(shape/record); BINARY_BOUND=no; TRACE_SCOPE_BOUND=24-launch recipe consistent; RUNTIME_MEASURED=no new measurements. Partial variants are deliberately not full transposes; do not describe the entire registered program as one optimized transpose kernel.

Immutable source files (all references above use this commit and their stated line numbers): [transpose.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/transpose/transpose.cu).
