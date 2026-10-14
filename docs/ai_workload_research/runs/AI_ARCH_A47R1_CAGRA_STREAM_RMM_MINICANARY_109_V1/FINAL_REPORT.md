# Round A47R1 | Default-resource tiny CAGRA qualification / STOP

**State: DEFAULT_API_STILL_FAILS.** The default-resource/default-stream1024x100 build was actually called once. It returned through the API and completed synchronization, but the required index qualification predicate failed; C0 is not PASS. C1 was not run. There was no new SIGSEGV and no search/recall/performance result.

Branch `hrl/aiarch-a47r1-cagra-stream-mr-minicanary-109-v1`, fixed start `25b04ce3bc00f82d684de905870fd93c8942830d`. New worktree/output/cache/tmp; original A47 `ce92807ca80e1a694e41376eab3dd6b146824fd8` environment/input/evidence read-only. No coordinator merge or continuation of the full A47 workload.

| Gate / path | Actual outcome |
|---|---|
| G0 | PASS:123 frozen wheel/library/input/evidence hashes and mtimes reverified; old worktree clean; current CPU/RAM/FS/GPU capacity checked |
| Initial packaging startup | exited1 after IMPORT_PASS; formatting allocator module=None caused TypeError; no input construction or build call |
| C0 after bounded formatting repair | IMPORT_PASS, GPU_INPUT_PASS, RESOURCES_READY, PADDED_DATASET_PASS, BUILD_ENTER; one build call; synchronized return then AssertionError; exit1, no SIGSEGV |
| C1 | NOT_RUN: C0 index qualification failed; total two GPU child processes already consumed |
| Publication | independent report/raw/hash packet; enclosing commit/tree/blob checked after single-branch push/fetch-back; STOP |

## Frozen identity and actual configuration

Existing Python3.12.3, cuVS/libcuvs/pylibraft/RMM/librmm26.10.0, CuPy14.0.1, NumPy2.5.4. No environment creation, installs, upgrades or scientific-data/dependency download. Original wheel SHA and loaded-library SHA reread in bounded chunks. Source `Resources()`/`Resources(stream=stream.ptr)` and Dataset signature were read from frozen A47 cache. Installed RMM stream-ordered-memory header matched A48 fixed Git blob `e2655e2fb2d8a61654ab18d79062d49e36a19a6b`. [Version-fixed RMM source](https://github.com/rapidsai/rmm/blob/v26.10.00/cpp/include/rmm/mr/detail/stream_ordered_memory_resource.hpp) shows stream/event handling and StreamGetId use; this is a source explanation, not proof of an actual faulting stream. No GPU imports occurred during CPU identity inspection.

C0 observed RTX4080/76 SM, Driver API13000/runtime12090, cuVS commit24ee1bf1cb17cad0ac611e39643af39ee1870124. Actual default per-device RMM type **CudaMemoryResource**; CuPy allocator callable label **None.malloc** (its Python module attribute is None, not an absent allocator). No set_current_device_resource, explicit PoolMemoryResource or cp.cuda.set_allocator call was used. Data was generated and uploaded on the default CuPy stream (observed default pointer-is-zero), then device synchronized. `res=Resources()` was explicitly passed to both Dataset and build APIs. The cuVS stream field is **REQUESTED_STREAM=DEFAULT_RESOURCES_STREAM**; actual C++ internal stream/faulting handle is UNKNOWN.

Input is the approved synthetic seed20261014,1024x100 FP32 with identical original fixture normalization. CPU/GPU roundtrip bytes matched; input SHA256 **`01a2c2f8a7e56b7a440fa183734d4297a1945a3dbbd6baedb27c1c3695b2478c`**. Padded Dataset returned device/padded/non-owning with dtype(2,32,1); x/g/ds/res owners remained alive. Requested cosine/IVF-PQ/degree64/intermediate128 remained unchanged. No GloVe vectors were parsed, uploaded or rebuilt; the existing HDF5 was read only to reverify its SHA.

## Failure and interpretation

The actual C0 API returned; res.sync and complete device sync ran. Native warning: **new dataset dimension100 does not match index dimension0**. The conjunction requiring `trained`, size1024, dim100, degree64 and float32 then raised AssertionError. Individual returned property values were not logged before this conjunction, so the exact failed property is **UNKNOWN**; do not infer every property value from the warning. No BUILD_PASS or CLEAN_EXIT was produced, and API return alone cannot count as index qualification.

This differs from the historical explicit-pool/nondefault-stream SIGSEGV. It does **not** establish a repaired platform, a single stream cause, a driver bug or allocator-only cause. Default-path index semantics remain unqualified; stream sensitivity cannot be assessed without a valid C0/C1 pair. C1 was strictly not attempted, and no third process, crash retry, GDB, memory-resource grid, alternative build backend, vendor patch or version substitution was used.

The first process failed in our optional metadata formatter before input/build. We corrected only string formatting, retained its complete raw log/receipt and counted its GPU occupancy/process. The second process performed C0's sole build call. We did not hide the initial process or reset the two-process/300-second budget. Once actual C0 failed qualification, STOP followed as the contract requires. This ordinary packaging repair did not alter scientific data, default resources, build semantics or ABI.

## Resources and STOP

Two GPU child processes total; **one actual cagra.build**, zero C1 build calls. Shared existing campaign lock acquired nonblocking; cumulative occupancy **1.590239s** including both startups and cleanup. Peak sampled GPU memory **286MiB**; process-tree RSS **905826304 bytes** (0.844GiB). Tiny input, no explicit large pool and independent watchdog constrained the2GiB limits; short NVML sampling is not a guarantee of every instantaneous peak. CPU effective affinity0,2; OpenMP cap2, BLAS requested1. CPU preparation before first entry **149.162s**, below30min. New output/worktree allocated **5500928 bytes**, below128MiB; free FS **92484472832 bytes**, above64GiB.

Scientific data/dependency download=0, installation=0, system/driver/core changes=0. Runtime/JIT/cache/tmp were directed to new output, bytecode writes disabled.123 original hashes+mtimes and old A47 HEAD/clean were rechecked after exit. All own GPU children ended, shared lock released, final CPU metadata check found no compute process. Resource elapsed values are supervision/budget receipts, **not tiny-API or application performance**.

FINAL_REPORT/GATES/RUN_IDENTITY/CONFIG_AND_OBSERVATION/RESOURCE_RECEIPT, exact raw logs and SHA256SUMS provide independent review. Only this branch is published; exact enclosing Git commit/tree/new blob/SHA readback is recorded on closeout. **STOP; no next Goal or restored full GloVe graph/search/recall/performance authorization.**
