# First-layer GraphSAGE source semantics

## Exact pinned source path

The artifact's top-level `Makefile` installs its pinned DGL submodule after Legion. The DGL submodule reports version literal `2.1`; only a future runtime import receipt can prove which DGL library the 109 process actually loads. This audit uses the pinned DGL source, not a generic GraphSAGE description.

For `run_reddit_cpuasync_singlegpu`, the Legion Makefile fixes Reddit feature width 602, hidden width 256, two hops, FP32 (`FP16=False`), one GPU, and `DYN_CACHE=792`. `legion_graphsage.py::worker_process` constructs `SAGE(602,256,50,n_layers=2)`, wraps it in DDP, creates Adam in the trainer, and calls `train_one_step`. The sampler and trainer are distinct processes: `legion_server.py::Run` launches a compiled `sampling_server` binary, whereas the PyTorch/DGL model lives in the Python trainer. The sampler's two-slot CUDA IPC buffers are synchronized by semaphores.

Let `N0` be seed nodes, `N1` the unique sampled nodes after the first sampling hop, and `N2` after the second. `ipc_service.get_block_size` returns `(N2,N1,N1,N0)` for two hops; `cuda_get_next` returns `features[N2,602]` and the two edge arrays. `create_dgl_block` constructs first block `(N2,N1)` and second block `(N1,N0)`. The first block's destination nodes are the prefix `features[:N1]` according to the DGL block contract and `SAGEConv.forward`.

The sampler uses `atomicOr(accessed_map,...)` and `position_map` to insert a newly seen node into `sampled_ids` once and map each sampled edge to local `agg_src_off`/`agg_dst_off`. Thus one reconstructed row can feed multiple edges. For a frozen first block, define `r_i = count(e in E1 with agg_src_off[e]=i)`; `r_i` may exceed one. A destination-prefix row also supplies one `fc_self` input. The actual histogram and maximum `r_i` require the real frozen batch and are **NOT AVAILABLE** in this CPU-only Goal. An edge-parallel decoder would repeat decode for `r_i>1`, violating the accepted producer work.

## First-layer operation order

Pinned `SAGEConv.forward` has `aggregator_type="mean"`, `feat_drop=0`, `bias=True`. Because `in_src_feats=602 > out_feats=256`, `lin_before_mp=True`. For `X=features[N2,602]`:

```text
Z = fc_neigh(X)                         # one 602->256 linear for every source row
M = DGL g-SpMM(copy_u, sum)(E1, Z)      # each edge reads its source's Z row
M[j] /= max(in_degree[j], 1)             # DGL mean reducer
S = fc_self(X[:N1])                     # separate 602->256 linear, with bias
H1 = S + M                              # [N1,256]
ReLU/dropout(H1) -> second SAGEConv -> loss/backward/Adam
```

The transformed `Z[N2,256]` is already a baseline global-memory intermediate and is reused across edges; it is not the raw `X[N2,602]` buffer targeted by R19. Keeping DGL's g-SpMM preserves its selected edge traversal and degree division. Decoding per edge, summing raw features before `fc_neigh`, or changing the order of `fc_self + M` alters either work, reuse or FP32 rounding.

## Two full raw-feature writes before the model

The sampler allocates an IPC-exported `float_features` allocation for every pipeline slot (`InitializeFeaturesBuffer`) and its `StaticCache::transfer` writes full sampled rows into it. `training_backend/ipc_service.cpp::get_next` waits on the batch semaphore. Then `cuda_get_next` allocates a **second** `[N2,602]` GPU tensor and copies the entire sampler buffer with `cudaMemcpyDeviceToDevice`; the old `from_blob` view is commented out with a note that the copy performed better. `train_one_step` passes the second tensor to the model.

Eliminating only that D2D copy leaves the sampler's full dense materialization intact and is outside the prescribed P1/P2/P3 consumer designs. Any claimed direct-consumer D1 must specify both allocations and preserve the existing two-process lifetime/synchronization cost.

## Aggregation and determinism boundary

Pinned DGL `gspmm(mean)` computes `sum` followed by division by clamped in-degree. Its CUDA COO sum path calls floating-point `AtomicAdd`; CSR/CSC paths traverse sparse rows with their own order. The source constructs a COO block and does not prove which backend format/algorithm is selected at runtime. Floating-point atomic order and full-matrix versus tiled `nn.Linear` algorithms cannot be certified bitwise identical by source inspection. We therefore record baseline repeated-output determinism as `UNKNOWN_CPU_ONLY`; no numerical tolerance is silently inferred.

Primary anchors and blob SHAs are in `SOURCE_RECEIPTS.tsv`. NVIDIA's [CUDA floating-point guidance](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html) explains why changing reduction order can change rounded results; this generic fact does not establish that the frozen B0 run is nondeterministic.
