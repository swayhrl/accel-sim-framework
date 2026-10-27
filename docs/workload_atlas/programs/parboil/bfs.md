# Parboil bfs

## 1. Program and algorithm

GPU frontier graph traversal with distance relaxation, using CSR-like Node int2 `(edge_start,edge_count)` and Edge int2 `(destination,cost)`, integer color/distance arrays and ping-pong frontier queues. Although named BFS, `visit_node` adds stored edge cost and atomicMin relaxes distances, rather than blindly assigning hop number (`kernel.cu:145-174`). CPU reads the graph and source, initializes WHITE/INF and starts a singleton frontier (`main.cu:74-107,148-151`).

## 2. Actual source authority and build information

Audited local root: `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/parboil/benchmarks/bfs/src/cuda`. Fixed upstream repository `accel-sim/gpu-app-collection`, commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. All nonhidden files in this program directory match upstream SHA256 byte-for-byte; see [source hashes](../../contributions/parboil/source_hashes.json). The enclosing local tree has no `.git`; `offline/manifest.lock` declares the commit, and independent content comparison supplies the stronger content evidence. Suite is Parboil; exact original Parboil release and historical capture source revision remain uncertified. `cuda_base` is a separate implementation and is not substituted here.

Build uses the program Makefile and `common/mk/cuda.mk:12-28,112-113`: configurable nvcc flags with default gencode targets 50/60/61/62/70/75. Historical effective command, compiler version, macro overrides, ELF SHA and PTX/SASS provenance are not recovered by reading these defaults. Trace headers record binary version 70, NVBit1.4 and tracer3; that is architecture metadata, not ELF identity.


## 3. Host calls and kernel sequence

Main copies frontier tail back before every launch, resets tail, and exits when frontier empty; queue overflow sets an error/exit path (`main.cu:177-259`). It chooses three possible implementations: frontier <= 512 uses1CTA `BFS_in_GPU_kernel`; intermediate frontiers use14CTAs `BFS_kernel_multi_blk_inGPU`; larger frontiers use general `BFS_kernel` with ceil(frontier/512) CTAs. All use512 threads. q1/q2 alternate with k parity, adjusted by switch_k from multi-level GPU execution. Thus launch count is not graph depth: first two kernels may process multiple levels internally. The general third kernel exists in the real host branch even though this frozen trace did not invoke it.

## 4. Detailed kernel implementation

All three call `visit_node`: mark source BLACK, read its cost, texture fetch Node and sequential outgoing Edges, atomicMin destination cost, atomicExch color, then append only improved/newly colored destinations to one of8 shared queues. Shared queue append atomically reserves tail, capacity400 per queue; a serial prefix sum concatenates queues (`kernel.cu:44-115`).

Single-CTA kernel (`:186-254`) keeps next frontier in shared512-element array, barriers between levels, exits empty or writes global q2 when frontier outgrows512. Multi-CTA kernel (`:271-362`) atomicOr reads global input queue, atomically allocates output spans, then uses a device-global counter spin barrier to continue while frontier is between512 and7168. The barrier explicitly assumes one CTA per SM (`:122-134`), and NUM_SM14 is a source constant, not detected hardware. General kernel (`:377-424`) performs one frontier round with shared queues and one tail atomicAdd/CTA. Source has no device-wide barrier in that branch.

## 5. Thread and address formulas

For lane l in warp w of CTA b, `t=512b+32w+l`; initial frontier `Q+4t` is contiguous. pid=Q[t] makes Node texture logical element pid (8B), color/cost `P+4pid`. At edge loop e=`Node[pid].start+r`, Edge texture element is8B at logical index e; destination id=Edge[e].x makes atomicMin address `Pcost+4id` and atomicExch `Pcolor+4id`. Same-thread successive edges differ8B logically; adjacent lanes follow different pid/e/id and have no constant stride (`:153-171`). These texture-element formulas do not establish physical texture addresses or ordinary-L1 routing.

Shared queue index q=tx&7, atomic reservation n gives shared element offset4*(400q+n). Concatenation writes global `Pout+4*(shift+prefix[q]+floor(tx/8)+r*sharers[q])` (`:103-114,323-329,417-423`). Consecutive lanes rotate among8 queues, so output stores are eight interleaved sequences, not necessarily globally consecutive at one instruction. Within a fixed q, lanes spaced8 increment element index1. Global tail and barrier counter are same4B words used by CTA leaders; atomicOr input loads in multi-kernel are source RMW operations even with value0.

A fully active aligned initial32lane queue load covers128B: one128B line/four32B sectors; unaligned up to two/five. Irregular destination atomics may occupy1..32 distinct sectors, possibly with repeated addresses; graph contents and atomics semantics decide aggregation/serialization. A sparse4B access can require32B transfer granularity, but exact physical amplification is not derivable from source. Warps/CTAs can share target cost/color words when graph edges converge; no precise count without graph content and scheduling.

## 6. Dataflow, locality, merging and concurrency

Traversal has a pointer dependency chain frontier -> Node -> Edge -> destination atomic -> queue append. Different vertices/CTAs provide independent chains; degree variation causes warp divergence. Shared frontier retention reduces global queue traffic for small frontiers, while medium traversal incurs global spinning and repeated RMWs. Same-node repeated requests are data-dependent, and atomic contention is not interchangeable with ordinary load miss merging. Host tail copies serialize phases; only the multi-CTA kernel has explicit intra-launch inter-CTA coordination.

## 7. Frozen input and trace binding

Frozen `P42-06`, input identity `1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0`, bundle `ff506808c7f46b0aafb46ae6deef722cd7f82cc59d438e6b2b035edca147594c` from `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json` at atlas base `3b28d3064`. Parameter encoding `_i___data_NY_input_graph_input_dat__o_bfs_NY_out`. Registered input identity is not newly certified original data-byte SHA. Small ordered header evidence: [trace_metadata.json](../../contributions/parboil/trace_metadata.json).

| Unique kernel | Grid | Block | Launches |
|---|---|---|---|
| `_Z17BFS_in_GPU_kernelPiS_P4int2S1_S_S_iS_iiS_` | `(1,1,1)` | `(512,1,1)` | 6 |
| `_Z26BFS_kernel_multi_blk_inGPUPiS_P4int2S1_S_S_S_S_iiS_S_S_S_` | `(14,1,1)` | `(512,1,1)` | 5 |

Scope remains `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`. Only kernelslist and first20 trace-header lines were read; capture-time ELF, original dataset-content linkage and full application completion remain uncertified. No raw output, workload identity or accepted result was modified.

Observed11 launches alternate single/multi starting and ending single (6/5). No `BFS_kernel` launch is recorded. This supports the branch history but does not prove11 BFS levels or native full completion. HtoD sizes encode270926 Node int2 elements and740426 Edge int2 elements if they correspond to these allocations; values and graph SHA are not recertified.

## 8. Source-provable architecture features

Irregular graph gather, texture Node/Edge path, global integer atomics and shared atomics, adaptive launch geometry, finite shared queue capacity, multi-level kernels and a software global barrier. The workload cannot be modeled as just a coalesced queue scan.

## 9. DTC-L1 / EP-L2 hypotheses requiring validation

DTC-L1: inspect destination convergence, pending same-line ordinary requests, queue stream Tag demand and whether texture paths bypass the studied structures. The global barrier can dominate timing independently of cache policy. EP-L2: distinguish atomicMin/Exch/Or/Add traffic and serialization from read caching; test convergent cost/color lines and counter hot spots. Counter waiting duration and forward progress require actual valid execution evidence. Do not automatically transfer graph behavior to Rodinia bfs or a same-name version.

## 10. Evidence and limitations

`SOURCE_VERIFIED=true` for the fixed content and source behavior below; `INPUT_BOUND=registered_identity_only`; `BINARY_BOUND=false`; `TRACE_SCOPE_BOUND=registered_sequence_only`; `RUNTIME_MEASURED=false` in this audit; `UNRESOLVED=true` for historical content/ELF/full-application linkage. These are independent dimensions. No GPU, native benchmark, capture, simulator or performance experiment was executed. No cache hit, MSHR merge, occupancy, latency, reuse distance or throughput was inferred as measured.


Fixed source references at commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`:

- [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/bfs/src/cuda/main.cu)
- [kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/bfs/src/cuda/kernel.cu)
- [config.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/bfs/src/cuda/config.h)
- [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/bfs/src/cuda/Makefile)
