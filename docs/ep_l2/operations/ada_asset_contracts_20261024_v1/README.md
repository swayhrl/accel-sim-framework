# Ada ordinary input capsules and extended-domain evidence

The ordinary trace format remains ADA7/SM89. A new isolated host observer captures supported HtoD source bytes without changing the frozen producer55 or its device instrumentation sources. Its final candidate additionally checks the direct pre-kernel synchronization return, rejects a second CUDA context lifetime before header reset, and journals recognized direct launches. It is a source-byte observation profile, not a complete CUDA initial-state snapshot or hardware timing qualification.

## Exact released ordinary profile

| Artifact | SHA256 |
| --- | --- |
| Producer ELF | c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352 |
| Capsule and lifecycle validator, output V4R2 | 7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388 |
| Final contract | 315fb51c10ca6351421afee22d8712767c609bce0c7f38577d7e63b5aadf975b |
| Initialization scope addendum | f7196678b81715dda1c2d45ebeed5b94351b29925f6450dbaa7bbab66dfc870a |

GPU109 frozen root: /data/c16/ada_trace_extensions_v8_20261024_v1/frozen/producer_v7_input_c8cfa41fcabc_r2  
Native review copy: /root/data/ada_trace_extensions_v8_20261024_v1/evidence/ordinary_input_release_c8_r2/frozen

common.h, inject_funcs.cu and ada_semantics.h have exactly the same SHA as frozen producer55. Original trace fields, one-record-per-source-SASS grammar, register classes, widths and symbolic constant offsets are unchanged. Host changes are explicit: source-byte file/hash capture, completion checks, and fail-closed context/launch journals. No new CALL, texture, Graph, JIT or asynchronous-memory ISA domain is admitted.

A native observer run loads NVBit but disables SASS instrumentation and retains the producer's existing launch synchronization. It is not a pure unloaded or timing-equivalent baseline. Its actual input hash is compared with the instrumented run; equivalence is never inferred from source or seed.

## Actual GPU and CPU verification

Ten new executions cover observer/instrumented pairs for sync, Async, runtime-random input, constant65, and Vector4M. Every pair completes its own numerical reference. Sync, Async, constant65 and Vector4M have identical observed input bytes across the pair. The runtime-random pair is explicitly INPUT_DIFF; each instrumented result uses its own reference.

Vector4M captures two16,000,000-byte HtoD arrays. All2,125,000 source SASS records,64M active source lane instructions,125000 terminating warps, and12M global lane addresses are checked. Every address is base+4*i, and the two actual HtoD device destinations equal the two LDG bases. Constant65 retains54 records/1353 active source lanes,579 constant lane accesses, and all65 dynamic bank3 indexed offsets and global stores.

Thirty prepared CPU negative fixtures reject unknown copy API, default plus nondefault Async streams, path/ID aliasing, invalid completion proof/boundary/order, context/range errors, corrupt/truncated data, missing/extra launch traces, wrong function/stream, missing process end, and context-address reuse. Five actual GPU negative paths reject invalid HtoD copy, cap overflow, Graph, multiple launch streams, and a second context lifetime. Their ordinary native counterparts complete the intended API checks.

The context negative is concrete: the same CUcontext address5a70a97686d0 is reused after reset. The new producer aborts at BEGIN2 before resetting kernel filenames/counters. The first complete seven-record raw trace remains intact. This preserves failure evidence; it does not claim multi-lifetime support. The old simpleTemplates failure that overwrote an earlier raw file cannot be repaired by renaming the surviving file.

The existing producer pre-kernel cudaDeviceSynchronize return is now saved and checked directly before recording completion. Source-byte capture inserts no additional GPU synchronization. Async completion uses an existing application stream/context synchronization or the producer's existing pre-kernel synchronization.

An Async host source must remain allocated and unchanged from API return through completion. This interval requires an independent source rule. Rechecking the host source at API return alone does not prove the full DMA lifetime. The measured snapshot fixture's pinned host array is unchanged until after the same-stream kernel, stream synchronization, DtoH, and complete65-element reference, then freed.

## Initialization boundaries

The four admitted copy APIs are cuMemcpyHtoD_v2, its ptds variant, cuMemcpyHtoDAsync_v2 and its ptsz variant. Each journal pairs entry, successful return, and an allowed completion proof, binds unique copy IDs to exact raw filenames, checks one input context, bounds pointers/bytes, and treats default stream0 as an actual Async stream ID.

Kernel argument bank0 bytes are not captured. Frozen source/argv and explicit argument rules are required. Memset and D2D initialization require source/dataflow rules. Managed/mapped host writes, graphics/external resources, unknown/batch/generic/array/2D/3D copy mechanisms are outside this profile. Symbol bytes are captured only when the upload is actually observed as a supported HtoD call; constant65 proves its256-byte table, not every symbol mechanism. A destination GPU VA is distinct from the simulator's symbolic constant-bank identity.

Capsule success is separate from numerical acceptance, full trace completeness, and consumer compatibility. Source-specific launch-count/API oracles remain mandatory: a self-consistent commandlist alone cannot prove that an unobservable launch mechanism was covered. Unknown initialization coverage remains INITIALIZATION_COVERAGE_PENDING.

Parent independently restored both true164 objects, verified536+238 members and64,001,812 recovered raw bytes, reran all ten positive and30 negative cases, and checked every actual launch function-handle pair. Its limited source-byte release is pinned by PARENT_C8_OBSERVED_HTOD_RELEASE_V1.json SHA14c56c21a34dcedf2524248a9787bf7e005d6a574c0b97d6a1e77b718565ef6e. Each production job must satisfy the parent gates; consumer qualification is not automatically granted.

The c8 control object is objects/stage_evidence_input_capsule_c8_109_20261024_v1/payload.tar,21,708,800 bytes, SHA54391026f49ef2d896fe9a1ec27560266555e6680eb3e74520ff4f700afadd42. It references exact raw members of the earlier object SHA f2b875c226456fdf58600a352f47fbff49fb231953c6ae941d0a30455b37c58b. materialize_c8_capsule_v2.py verifies both full tar/member sets, writes each content hash once to a private cache, reconstructs independent raw files, checks their full SHA, and reruns qualification. It also supplies the function-handle check missing from the frozen7d00 validator. Source copies remain KEEP.

Earlier snapshot candidates and their failures remain intact. The older b772 validator admitted a synthetic unknown API and default-plus-nondefault Async streams; parent review exposed these and no release used them. V3 fixed those guards; the final V4R2 additionally binds the new producer and context/launch lifecycle.

## ELF-owner mapper

The independent frozen mapper SHA is a2e7ee38aa722465250c53096aea50bcd93623fea5b60114486538429dce1f6e. nvdisasm JSON emits embedded callee symbol views with nonzero start offsets, while PLR attributes those physical PCs to the owning .text section. Mapping each JSON function independently from PC0 falsely reported missing instructions.

The mapper proves symbol section/value ownership with ELF metadata, normalizes each view to the physical owning section, requires complete16-byte executable-section coverage, checks every non-NOP against PLR and every PLR PC/opcode against JSON, and synthesizes no dependencies. The empty-module rule remains strict. Five positive binaries and six corruption/missing-row negatives pass their expected outcomes. The existing streamcluster typed rows remain exactly equal.

The coordinator's fixed150-ELF census reports70 ordinary static passes,68 genuine special domains and12 remaining mapper holds after normalization;48 former owner-alias holds become correctly classified special-domain work. These are static classifications, not completed captures.

## Extended domains remain separate

Actual compute70 PTX is JIT-compiled by the109 driver to SM89. The dumped loaded cubin SHA41425beaa2ecbd5a0bdc3e3f992bcb8be328c17dce22c9a335d2a280ac399bf1 matches a second fresh process. Metadata records driver ptxas13.0.100; nvdisasm12.8 cannot provide PLR for this new ELF ABI. A private official NVIDIA nvdisasm13.0.85 package resolves that analysis step, with package and binary hashes retained. The full45-record/834-source-lane trace plus15 internal auxiliary operations/287 lanes validates; consumer qualification is still independent.

A new -Xptxas=-O0 fixture produces real WARPSYNC R2 with an embedded relative call, rather than the NOP emitted by earlier optimized fixtures. Its N65/block37 native reference passes. All264 source records/5266 active source lanes,16 auxiliary operations/296 lanes,65 actual CALL/RET targets and65 named WARPSYNC participant lanes validate. Uniform named masks match the physical executing groups. Consumer ordering and a finite exact native smoke remain active work; a producer result does not establish a simulator or timing pass.

The scientific simulator campaign remains4/8 application attempts consumed. None of the GPU capture, source-byte, mapper, restore or CPU negative tests consumes another simulator application credit. The V100 EP baseline and old scientific Goals remain unchanged.
