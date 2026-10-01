# Future 109 replay ledger — blocked after source design

This is a frozen **admission schema**, not an executable 109 manifest. Values that require the forbidden Reddit download or GPU capture remain `NOT_CAPTURED`. With `D1=NOT_DEFINED`, neither B0 nor D1 performance is authorized by R19E1.

| Frozen field | Authority/value now | Required before any later independent authorization |
| --- | --- | --- |
| Input identity | Original `dgl.data.RedditDataset()`; no scaled-up topology or synthetic features/IDs | Dataset bytes/hash and author preparation-script output hashes |
| Batch selection | First eligible real training minibatch in a predeclared epoch/order that has at least one pinned-host cache miss; never search for a fast batch | Exact epoch/iteration and raw sampled node IDs/edge arrays and hashes |
| Two-hop graph | Legion fanout `[25,10]`, first block `(N2,N1)`, second `(N1,N0)` | `N0/N1/N2`, ordered `agg_src_off/agg_dst_off` for both blocks, degree and source-reuse histograms |
| Cache snapshot | Exact author IBP(C/M) cache layout/capacity/bitmask/Mask/Bitval; at least one host miss | Immutable cache rows, mapping, hit/miss bitmap, compressed-row hashes, PCIe-read bytes |
| Feature identity | FP32 source feature row bits and `[N2,602]` decoded tensor contract | Per-row and aggregate feature SHA-256, full bitwise reconstruction receipt |
| Model state | `SAGE(602,256,50,n_layers=2)`, FP32, trainer-owned DDP/Adam | Full model and first-layer `fc_neigh/fc_self` weight hashes, Adam state, RNG/AMP flags |
| Process topology | Sampler + trainer, one GPU, two IPC pipeline slots, existing semaphores and MPS/stream settings | Exact process/container/CUDA/DGL/Torch versions, stream IDs and IPC handle/layout receipt |
| First-layer output | Pinned expression in `GRAPH_SAGE_SEMANTICS.md`; bitwise B0 repeat status unknown | 30 B0 correctness-only output/gradient hashes; then bitwise or frozen interval per `NUMERICAL_CONTRACT.md` before performance |
| B0 | Author Legion+IBP(C/M) CPU-async path (`DYN_CACHE=792`), existing full sampler buffer and full trainer D2D copy; no source patch | Exact command/config/input/binary hashes after separate admission |
| D1 | `NOT_DEFINED` — P1/P2/P3 all failed same-boundary design gate | A new authorized, causally matched patch/control and numeric receipt would be necessary |
| Future timing | No timing in this Goal | If ever reauthorized: 10 warmups, 30 matched replays with exact state restore; primary complete-step median, exposed `get_next` wait, producer→first-layer completion, raw-buffer bytes, extra IPC bytes, correctness; `<5%` complete-step response would fail investment screen |

The original parent card's 109 test description is superseded by the R19E1 design verdict until a new review explicitly resolves D1. No source-only analysis can supply sampled IDs, cache contents, feature hashes or baseline repeated-output values.
