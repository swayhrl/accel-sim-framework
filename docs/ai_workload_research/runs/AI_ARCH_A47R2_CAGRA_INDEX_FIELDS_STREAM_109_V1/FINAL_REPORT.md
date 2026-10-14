# Round A47R2 | Corrected index fields and stream canary / STOP

**C0_DEFAULT_PASS_C1_STREAM_SENSITIVE.** C0 completed one1024x100 native cosine/IVF-PQ build, all five required index predicates and clean exit0. C1 ran immediately afterward in a separate fresh process with identical input/default allocator and only the admitted explicit cuVS stream configuration change. It exited **SIGSEGV(-11) during explicit stream/Resources initialization**, before Dataset wrapping and before any build. This supports frozen-environment configuration sensitivity, not a proved invalid handle, driver bug or allocator-only cause. No further GPU activity followed.

Independent branch `hrl/aiarch-a47r2-cagra-index-fields-stream-109-v1`, fixed start `bbbe9d89d05e268f7dc958886a571fb327c44584`, node109, client date2026-10-15. New worktree/output/tmp/cache; original A47 and A47R1 remain immutable. No coordinator merge. This run neither changes historical STOP reports nor grants a full GloVe experiment.

## Actual gate/field evidence

| Item | C0 default Resources | C1 explicit nonblocking stream Resources |
|---|---|---|
| Input hash/CPU-GPU roundtrip | PASS | PASS, identical |
| Default per-device RMM | CudaMemoryResource | same |
| Default CuPy allocator | None.malloc callable | same |
| Dataset wrapping | padded/device/non-owning, PASS | NOT_RUN |
| Actual cagra.build calls |1|0|
| trained |true|NOT_READ|
| size |1024|NOT_READ|
| dim |100|NOT_READ|
| graph_degree |64|NOT_READ|
| dtype_repr |class numpy.float32|NOT_READ|
| dtype normalized |float32|NOT_READ|
| Each required predicate |all5 true|NOT_RUN|
| Exit |0,CLEAN_EXIT| -11,SIGSEGV |

G0 passed actual frozen Python3.12.3, cuVS/libcuvs/pylibraft/RMM/librmm26.10.0, CuPy14.0.1, NumPy2.5.4 identity and CPU-only wrapper tests. The metadata formatter with module=None, dtype class/instance normalization, AST/compile and expected input hash were tested **before** GPU entry. No packaging retries were needed. The parent admitted C1 only after C0 BUILD_FIELDS_PASS/CLEAN_EXIT and zero-exit, without a new Goal or confirmation.

Index property reads were individually logged before any qualification predicate. `dtype_repr` is **`<class 'numpy.float32'>`**, while `np.dtype(idx.dtype)==np.dtype('float32')` is true. This concretely confirms A49's defective old string assertion on a valid current FP32 result; it does not retrospectively fabricate old R1 property values. The original new-dimension100/old0 native warning remains in raw C0 output, followed by actually observed final dim100. It was not treated as failure.

The optional C0 public graph-view bridge returned a DLPack conversion ValueError, recorded **OPTIONAL_NOT_QUALIFIED**. Required metadata qualification stays PASS as contracted. Graph contents/ID range/hash were not observed; no full graph numerical validation or recall is claimed. The failed optional operation was not rerun after C1's real crash.

## Single-variable identity and precise failure boundary

Synthetic seed20261014,1024x100FP32 and original FP32 normalization; input SHA256 **`01a2c2f8a7e56b7a440fa183734d4297a1945a3dbbd6baedb27c1c3695b2478c`** matched the R1 preregistered value and both new arms. Both prepared/uploaded on default CuPy stream then fully synchronized. C0 uses explicit `Resources()`; C1 creates/retains `cp.cuda.Stream(non_blocking=True)` and requests `Resources(stream=stream_owner.ptr)`. No pool or allocator setter was called; all data/resource owners remain live through their execution paths. Requested stream categories are **REQUESTED_STREAM**, not observed C++ internal handles.

C1's last successful phase is GPU_INPUT_PASS. Faulthandler reports the source line containing **both nonblocking stream creation and Resources(stream=...) binding**. Because those subcalls share a source line and this run has no native register dump, the exact subcall/handle is **UNKNOWN**. Do not assert that C1 reached CAGRA build or that it reproduced the exact historical A47 native stack. There was no third process, crash retry, GDB, altered input, vendor patch, driver/library change, search or profile.

Actual RTX4080/76SM/SM89, Driver API13000/runtime12090; cuVS embedded commit24ee1bf1cb17cad0ac611e39643af39ee1870124. The frozen binding blob27880c8dd63e1d59a53c7e0cfbcbc8aef2727ae7 was CPU-verified. [Fixed dtype conversion source](https://github.com/NVIDIA/cuvs/blob/24ee1bf1cb17cad0ac611e39643af39ee1870124/python/cuvs/cuvs/common/cydlpack.pyx) returns the NumPy FP32 type; this motivated correct dtype normalization. A49 supplied the fixed C++ initial-attachment warning explanation; this run's final property evidence is separate from source inference.

## Resources and archival integrity

Two fresh GPU processes, **one total tiny build**, no prebuild repair, no completed C1 build. Existing `/data/c16/locks/c16_gpu_campaign.lock` opened without creation, acquired nonblocking and held **2.601539s** cumulative including import/optional diagnostic/crash/cleanup. Peak sampled GPU **286MiB**; process-tree RSS **903643136 bytes** (0.842GiB); C0 rusage peak892317696bytes. Sampling can miss transient peaks; small input/no large pool plus independent watchdog maintained2GiB caps. These elapsed values are budget/supervision, not tiny or application performance.

CPU affinity0,2, OpenMP cap2, BLAS requested1. CPU preparation93.038s below30min; new worktree/output allocated5525504bytes below128MiB, free FS92478132224bytes above64GiB. New data/dependency download/installation/compilation=0. Runtime caches redirected to new task; old env not modified. All143 original A47/R1 hashes and mtimes and both historical HEAD/clean states reverified after exit. GPU children ended and lock released; final read-only metadata found no compute process. No full GloVe parsing/upload/build, search, recall, B1/B256 timing, NCU/NSYS/NVBit, simulator or mechanism.

## Concrete next experiment proposal ONLY

**Recommendation:** stop nondefault-stream/vendor workaround probing. If independent review finds the original ANNS question worth the next controlled investment, request **one complete continuous default-resource/default-stream GloVe Goal**: identity/asset/resource preflight -> one full graph -> serialize/reload/owner qualification -> numerical/recall canary -> bounded h calibration -> four original native timing points -> archive/STOP. This is **not authorized or started** by this R2 result.

Unique question/new evidence: on the same original complete real graph and fixed recall, does official AUTO leave a stable complete-search software configuration gap versus one calibrated SINGLE_CTA+SMALL setting at B1/B256? R2 now supports the default tiny build API, but full-scale memory, save/load, graph/search numerics, quality and wall remain unknown. Keep allocator and Resources defaults for all paths; do not benchmark explicit stream/pool variations.

Proposed minimum bounded resource envelope: **downloads/install0**, reuse only read-only A47 venv/HDF5/normalized arrays/query/GT; **new disk<=2GiB**, FSfree>=64GiB; CPU<=4workers, RAM<=8GiB, VRAM<=12GiB; GPU existing-lock<=45min, CPU preflight<=30min, raw/summary<=64MiB. The complete-base FP32 data+degree64uint32 graph arithmetic lower bound is~740MiB, **not peak memory or measured full-build cost**.2GiB additional disk allows one serialized index plus small cache/raw; the12GiB/45min ceilings carry conservative original native-admission limits, not a claimed measured full-scale minimum. Recheck footprint before extraction/save; if these proposed caps cannot be met, STOP rather than silently expand.

Executable plan (detailed machine-readable counterpart NEXT_EXPERIMENT_PROPOSAL.json):

1. After separate review/user approval, create another isolated execution worktree/output/ledger. Static-check public Dataset/view conversion, correct dtype predicate and frozen file/query identities. Never execute old A47 native.py unchanged: it contains the explicit pool/stream setup and obsolete dtype check.
2. Under nonblocking original lock and no external GPU task, use `res=Resources()`, default-stream FP32 upload+device sync, `ds=make_device_padded_dataset(g,resources=res)`, one `cagra.build(IndexParams(cosine,ivf_pq,64,128),ds,resources=res)`. Record each required field and all predicates before judging. Retain owners; no resource setter or nondefault stream.
3. `cagra.save(path,index,include_dataset=True,resources=res)`,sync/hash; precreate `Index()` and `Dataset()`, call `cagra.load(index,path,out_dataset=owner,resources=res)` and retain owner. Verify the same numerical canary. If optional graph-view bridge is unsupported, use serialized graph+dataset SHA as allowed original identity and mark logical graph hash UNKNOWN; no false full graph verification.
4. Preserve original query split, canary32 full-base cosine reference(atol1e-5,rtol1e-4), k10/itopk128/width1/iterations64 and other frozen search values. At most6calibration candidates(twoB x AUTO/h9/h11) plus2functional checks; common selected h must satisfyrecall>=.95 and same-B difference<=.005, then minimize calibration-only two-B geometric mean perquery complete-host wall.
5. Validate8000 report queries at each actualB/max_queries; same index. Use original2048 different report queries for3fresh processes x10ABBA/BAAB paired blocks at four points. Preallocate equal buffers; all transfers/defaultResources default-stream operations fully synchronized. Separate GPU-resident-query synchronized host search from complete CPU-ready/H2D/search/D2H wall; do not call it pure kernel without coverage proof. Stop other heavy task preparation while timing; retain all slow/outlier samples and correctly hierarchical uncertainty.
6. Closeout raw identity/quality/budget/pair effects and exact remote commit/tree/blob/SHA, thenSTOP. No follow-on hardware work.

Strong software counterevidence and stops: AUTO is an official heuristic, not globally best tuning. SMALL wins first mean existing block/hash/reset/algorithm choice, not hardware SMEM/cache benefit. AUTO no slower, identical paths or unstable complete-wall difference is a valid NO_GAP. Lock busy/other GPU task, source/dtype/input/algorithm change, real native failure/invalid fields, resource/time violation, bad canary, no common h, recall<.95 ordelta>.005 ->STOP with all evidence; no rebuilding crashes, new h/iteration grids, lowered quality, driver/version workaround, extra dataset or profiler. If review deems value insufficient, park ANNS and separately select a real Q-S/AI workload; no automatic vendor debugging loop.

## Publication / hard STOP

Only this branch adds the complete report, per-field/predicate evidence, C0/C1 raw logs, resource/snapshot receipts and minimum code. SHA256SUMS verifies artifacts; enclosing Git HEAD carries final commit/tree identity, independently read back after one commit/push/fetch. Original results/coordinationCURRENT_STATE were not rewritten. **STOP; no next GPU Goal or full-index authorization inferred.**
