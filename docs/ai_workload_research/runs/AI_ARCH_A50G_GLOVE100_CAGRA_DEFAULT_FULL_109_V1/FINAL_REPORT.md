# Round A50G | Full default-path build fields pass; downstream packaging STOP

**Terminal: INDEX_RELOAD_OR_NUMERIC_NO_GO; precise cause POST_BUILD_ENGINEERING_STOP_UNIQUE_BUILD_CONSUMED.** The sole complete-base CAGRA build API was actually called, returned and synchronized. All five required index fields passed. A Python transfer-buffer view error then terminated the GPU child **before index serialization and before any search**. The live index object was lost on process exit. Rebuilding would violate this Goal's one-full-build hard limit; no second build or GPU retry was performed.

This is an avoidable execution-wrapper failure. It is **not** a detected numeric/recall failure, native SIGSEGV, hardware-resource failure or negative AUTO/SMALL result. The normative index/reload/numeric admission state is NO_GO because those downstream qualifications remain unperformed, not because bad numerical values were measured. No application or hardware conclusion can be drawn.

## Authority and isolation

Repository swayhrl/accel-sim-framework; independent branch `hrl/aiarch-a50g-glove100-default-native-full-109-v1`; fixed start `ea32eb190cf9697556f3560263b7a637563c69e7`, user-approved A50G contract. A50 review, A47/R1/R2 fixed evidence, original preregistration/data/env/quality and executed-source identities were read. Protocol bytes matched the previously read accepted version. All167 original A47/R1/R2 SHA+mtime checks and their HEAD/clean states were reverified after exit. Old env/data/cache/raw/worktrees were not changed; no coordinator merge or CURRENT_STATE edits.

## Actual gates and fields

| Gate | Actual outcome |
|---|---|
| G0 | PASS: frozen official env/wheels/libs/input/query identities, resources, dtype/formatter and script AST/compile checks |
| G1 complete-base build API | called once, returned, synchronized, all required fields PASS |
| G1 index save/load/numeric canary | NOT_RUN: pinned-buffer view exception before save; no serialized file |
| G2 calibration/report recall | NOT_RUN; h not selected |
| G3 four formal points | NOT_RUN; every point has0samples |
| G4 | evidence/corrected code/CPU verification/publication and STOP |

| Actual field | Value | Predicate |
|---|---|---|
| trained |true|true|
| size |1183514|true|
| dim |100|true|
| graph_degree |64|true|
| dtype_repr / normalized |class numpy.float32 / float32|true via np.dtype comparison|

The new-dataset100/old-index0 attach warning was retained and not misclassified; final observed dimension is100. Graph edge contents were not read/hash-validated. Native API/index metadata PASS does not stand in for serialized index, correct graph contents, search/recall or scientific timing.

Complete frozen FP32 base(1183514x100) was uploaded in the default CuPy stream and synchronized. `Resources()` and observed default RMM CudaMemoryResource/default CuPy None.malloc were used; no nondefault stream, explicit RMM pool or allocator setter. Build cosine/ivf_pq/degree64/intermediate128 stayed fixed; actual random seed for native build is UNKNOWN/not exposed. Actual RTX4080/76SM/CC8.9, Driver API13000/runtime12090 and cuVS26.10 source24ee1bf1cb17cad0ac611e39643af39ee1870124 were recorded.

## Input/query identity and unavailable scientific results

Original official HDF5485413888bytes SHA256 `544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`, original normalized FP32 base/query and original GT all remain read-only. No base truncation, random substitute, FP16, metric or quality alteration. Source/derived-file hashes are in DATA_AND_INDEX_IDENTITY.

Frozen calibration2000/report8000 sets are disjoint; timing2048report queries are distinct. Split SHA `0fb3e14cd9b4b9c97397235c5dddcd73b1a53bb5979b04ac5e3762f8c559c650`, timing-list SHA `f7ebf0825b6ba7e351df18c20f8e0cb559b37fdbf0775142d989161df7baafea` verified. No selection looked at new report performance; there are no search outputs at all.

| Formal point | Recall | Paired/native timing samples |
|---|---|---:|
| B1 AUTO |NOT_RUN|0|
| B1 SMALL |NOT_RUN, h not chosen|0|
| B256 AUTO |NOT_RUN|0|
| B256 SMALL |NOT_RUN, h not chosen|0|

Original canary atol1e-5/rtol1e-4, GTkth10+.001 tie rule and recall>=.95/same-B delta<=.005 were preserved but not actually tested against a CAGRA result. Frozen prior CPU oracle remains historical identity evidence only. Neither synchronized resident-query service nor complete CPU/H2D/search/D2H wall was collected. Build/supervision elapsed values are resource bookkeeping, not search-performance samples.

## Exact wrapper error and bounded repair

After build, the first B1/AUTO functional preparation constructed Buffers(1). CuPy pinned allocations may expose an **alignment-rounded underlying buffer**: requested400bytes for100float32 values exposed512bytes/128elements. `np.frombuffer(pinned,dtype=float32).reshape(1,100)` therefore raised **ValueError: cannot reshape array of size128 into shape(1,100)**. Search had not been called. Process exit1 released the unsaved in-memory index; no index file or recoverable checkpoint exists. This should have been prevented by preallocation checks and save-first ordering.

Within this same Goal, the deterministic engineering repair was made concrete and CPU-verified:

- Every pinned view now passes an explicit element count (query Bx100, ID/distance Bx10; calibration/timing views likewise).
- B1/B256 buffer shapes are checked before a future unique full-build call.
- Corrected runner saves and hashes the built index immediately after required-field PASS, before any downstream buffer/search helper.
- CPU tests with512-byte-rounded buffers passed B1/B256 shape, dtype and contiguous-view checks. No GPU reconstruction/test was run after the stop; this CPU test is not proof that downstream native phases pass.

`tools/aiarch_a50g/native_executed.py` preserves the exact executed source; `native.py` is the corrected **unexecuted** code, distinct SHA identities in ENGINEERING_REPAIR/RUN_IDENTITY. Original failure/phase logs and build entry/fields were not discarded or overwritten. The one-build scientific limit prevents an apparently simple process restart from repairing the missing checkpoint in this authorization.

## Resources and safety

GPU original shared lock acquired nonblocking and released after the own child ended. Cumulative hold **3.959299s**, sampled process-tree RSS **2817036288bytes** (2.624GiB), sampled GPU **1600MiB**. Early watchdog margins were11.25GiBVRAM/7.5GiBRAM/1.875GiBnewdisk with15sdeadline reserve; no limit violation was observed. Sampling is not an exact instantaneous peak proof.

CPU preparation278.173s below30min, effective affinity0,2,4,6; OpenMP cap4 and BLAS requested1. New worktree/output allocated5771264bytes (5.504MiB), free FS92465778688bytes (>64GiB). Data/dependency download, installation, core compilation, system/driver changes=0. Runtime caches/bytecode policy isolated. Final CPU metadata confirmed no compute process. No NCU/NSYS/NVBit, simulator, training, second dataset, parameter scan or new mechanism.

## Unique smallest next recommendation — proposal only

First independently review this engineering interruption and the corrected buffer/save ordering. **Only if separately authorized for one additional full build**, execute one checkpointed default-only continuation protocol as a new bounded contract. Do not reinterpret this run's unused45min as another build permission, and do not spend another round debugging nondefault streams or changing vendors/drivers: the current blocker was our wrapper after native field success.

Concrete future sequence: reuse all current frozen source/data/query/GT and env; new independent output/ledger; under the original nonblocking lock, validate actual B1/B256 pinned-buffer shapes and host/device transfer completion **before** the sole full build. Build once, record all index fields, then immediately save/hash before any functional helper. Preserve that checkpoint and allow only load-based bounded wrapper recovery thereafter. Reload with precreated Index/Dataset and live owner;32-query full-base numeric/ID canary, fixed6calibration candidates plus<=2functional configs, common h9/h11 at unchangedrecall>=.95/delta<=.005,8000report quality,3fresh processes x10ABBA/BAAB paired blocks at four points, then raw/remote readback/STOP. No broadening of parameters or source changes.

Proposed resource ceiling remains original: new downloads/install0, newdisk<=2GiB/freeFS>=64GiB, RAM<=8GiB/VRAM<=12GiB,CPU<=4, preparation<=30min, shared-lock<=45min, raw<=64MiB, **one newly and explicitly authorized full build**. These are proposed caps, not measured minimum full-scale requirements. Busy lock/other GPU work, identity/precision change, native failure/invalid fields, canary/reload/quality failure or resource/deadline exceed ->STOP; no repeated build. AUTO sufficient/no stable complete-wall gap is a legitimate negative; SMALL advantage first means existing software configuration, not hardware headroom. The proposal is not executed or automatically authorized.

## Publication / hard STOP

Only the independent A50G branch adds this report, actual fields/error/raw/asset/resource receipts, SHA index and minimal executed/corrected scripts. HDF5/env stay private; no full serialized index was produced, and no data/index was copied164 or committed. One commit/push/fetch-back checks exact enclosing commit/tree/all new blobs and SHA,clean; final receipt is separate to avoid self-reference. **STOP, no next GPU Goal.**
