# A50G corrected continuation — native index/reload/numerics pass, calibration QUALITY_NO_GO

**Final scientific state: QUALITY_NO_GO.** The packaging correction was actually executed successfully. One additional full-base build, authorized by the user's instruction “那你改正。然后接着做”, was saved and reloaded with identical search outputs. All six fixed 2000-query calibration configurations then failed the unchanged recall>=0.95 gate. No common h was eligible; h selection, independent report recall and all four formal timing points are NOT_RUN. This is measured negative quality evidence, not a performance or hardware result.

## Identity and authorized recovery

Publish only `hrl/aiarch-a50g-glove100-default-native-full-109-v1`, with original start `ea32eb190cf9697556f3560263b7a637563c69e7` and immediate parent `d74ba0225516e60aa1c18b7ee87c88abfc34e0c9`. A new recovery worktree/output and local-only recovery branch isolate all changes. The old A50G STOP report and code remain unchanged in this tree; the original A50G worktree remains at d74ba022 and clean. No coordination branch merge, old environment/cache change or old task restart occurred.

The earlier full build returned fields but its process lost the unsaved index on a pinned-memory NumPy reshape error. The latest explicit user continuation was interpreted and announced as permission for **one additional complete build**, without resetting GPU/download/disk/CPU budgets or changing scientific conditions. Total A50G complete-base build API calls=2: original1 + recovery1. There was no third build, no saved-only retry and no algorithm/source repair.

Original official GloVe100 HDF5:485413888B, SHA256 `544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`. Full FP32 normalized1183514x100 base, original10k queries/GT and frozen2000calibration/8000report split were reused read-only. Split SHA `0fb3e14cd9b4b9c97397235c5dddcd73b1a53bb5979b04ac5e3762f8c559c650`; timing2048-list SHA `f7ebf0825b6ba7e351df18c20f8e0cb559b37fdbf0775142d989161df7baafea`. No query split, seed mask, dtype, normalization, GT, threshold or build/search parameter change.

## Gates and corrected execution

| Gate | Actual result |
|---|---|
| G0 | PASS; all167 frozen A47 files hash/mtime/size, environment metadata, source, query identity and script AST checked |
| G1 | PASS; real pinned allocation and transfer preflight, full build fields, save/hash, owner-safe reload, ID/distance numeric checks |
| G2 | QUALITY_NO_GO; all6 fixed calibration settings tested on2000queries each, no eligible h |
| G3 | NOT_RUN; all4 formal points have0samples; no fresh timing processes launched |
| G4 | Actual raw results, negative evidence, budget/SHA receipts and publication; STOP |

Actual pinned allocation exposed B1 buffers512/512/512B for logical400/40/40B and B256 buffers131072/16384/16384B for logical102400/10240/10240B. Explicit element counts fixed the view shapes. Actual default-stream H2D/D2H roundtrips passed **before** the additional complete build. The full index was saved and hashed immediately after required-field qualification, before any canary helper. No subsequent wrapper exception occurred.

Observed cuVS26.10 wheel commit `24ee1bf1cb17cad0ac611e39643af39ee1870124`, CuPy14.0.1/default allocator None.malloc, default RMM CudaMemoryResource, default Resources/default CuPy stream; RTX4080/76SM/CC8.9. No explicit pool, nondefault stream, allocator/resource override, installation, download or core compilation. Exact versions and source/library hashes are recorded, and frozen files were rechecked after GPU exit.

## Index, numerical qualification and recall

Built and reloaded fields independently all passed: trained=True, size1183514, dim100, graph_degree64, dtype repr class numpy.float32, normalized float32. Build cosine/ivf_pq/degree64/intermediate128 unchanged. The normal initial dimension100/old0 dataset-attach warning remains in raw logs and was not treated as a failure.

The library also produced a236-byte cuFile diagnostic: compatible mode and a mount-table option lookup error. It is preserved in `raw/cufile_runtime.log`. Index serialization completed and reload/byte-identical results independently passed; no GPUDirect-storage claim is made and no platform setting was changed.

Saved index **776387032B**, SHA256 **`205aa012e08ef9fa28b9b1a82126aab7396fcd33d02e64fe552c219ff2efc65c`**, include_dataset=True. Precreated Index plus live owning padded-device Dataset were used for reload. All actual searches use that one graph. Logical graph element hash is UNKNOWN; serialized SHA does not prove an independently hashed graph view. The complete index remains private at `<RECOVERY_OUTPUT>/glove.index` and is not in Git or copied164.

Two fixed AUTO functional configurations used B1/32canary queries and B256/256calibration queries; before/after reload IDs **and distances were byte-identical**. Returned IDs legal/nonduplicate; distances finite and consistent with original FP64 cosine reference at atol1e-5/rtol1e-4. The frozen32-query **full1183514-base** FP64 oracle's kth10 threshold agrees with original GT. Worst returned-distance absolute error across the actual calibration outputs was about **2.061e-7**. Numerical distance PASS is distinct from approximate top-k recall PASS: the former passed, the latter failed. The functional B1 canary recall was0.93125; B256's256-query aggregate was0.848046875, both retained without hiding misses.

| B | Fixed configuration | Tie-aware recall@10 | Strict ID recall@10 | Quality |
|---|---|---:|---:|---|
| 1 | AUTO | 0.9117 | 0.8995 | FAIL |
| 1 | SINGLE_CTA+SMALL h9 | 0.8178 | 0.8040 | FAIL |
| 1 | SINGLE_CTA+SMALL h11 | 0.8178 | 0.8040 | FAIL |
| 256 | AUTO | 0.8178 | 0.8040 | FAIL |
| 256 | SINGLE_CTA+SMALL h9 | 0.8178 | 0.8040 | FAIL |
| 256 | SINGLE_CTA+SMALL h11 | 0.8178 | 0.8040 | FAIL |

All6 candidates are below0.95. B1 AUTO vs either SMALL differs by0.0939, above the0.005 same-B limit; B256 deltas are0 but both sides fail0.95. No h9/h11 is eligible and neither is selected. Five single-CTA calibration outputs have identical neighbor/distance SHA, including both h values and B256 AUTO; this is output identity, not an explanation of all quality loss. No h-timing selection or quality-threshold relaxation was attempted.

An independent **CPU-only** verifier reloaded all10 raw NPZ sets (4before/after canary +6calibration), recomputed FP64 distances using a separately expressed NumPy sum, frozen tie-aware and strict recalls, all output hashes, and reload identity. It confirmed the actual quality STOP. It also rechecked188 old asset hashes/mtimes (167frozen +21prior-A50G files), the old clean worktrees/HEADs and serialized-index SHA. Its peak RSS was525103104B. Full outputs/query IDs/per-query hits are archived; no report-query result was generated.

| Formal point | Report recall | Formal samples |
|---|---|---:|
| B1 AUTO | NOT_RUN |0|
| B1 SMALL | NOT_RUN; h unselected |0|
| B256 AUTO | NOT_RUN |0|
| B256 SMALL | NOT_RUN; h unselected |0|

No GPU-resident service or CPU/H2D/search/D2H formal wall was measured. Build/save/load elapsed values are budget bookkeeping only. No 3fresh-process x10paired-block comparison or speedup can be reported.

## Source-qualified path interpretation

`EFFECTIVE_PATHS.json` separates REQUESTED, SOURCE_DERIVED and DEVICE_OBSERVED facts. Fixed source with observed76SM selects AUTO B1 MULTI_CTA (global traversed HASH bit11 plus CTA-local visited SMALL bit9,4CTAs/query), AUTO B256 SINGLE_CTA+SMALL bit9, and forced SINGLE_CTA+SMALL bit9 or11. Small reset intervals are source-derived2/14 for bit9/11; multi-CTA visited table resets each iteration. Standard FP32 cosine descriptor dim100 selects source-derived team8. Forced block128 is requested; AUTO final dynamic block and actual device iteration/distance counts are UNKNOWN. No launch tracer/profiler was added. These are possible software-path differences, with no qualified timing or hardware-benefit claim.

## Cumulative resources and preserved assets

Original shared lock was acquired nonblocking, no external compute task was found, and it was held through the owned GPU child exit. Recovery held **11.853784s**, prior held3.959299s, cumulative **15.813083s** of2700s. Sampled cumulative RSS peak **2833670144B** (2.639GiB); sampled cumulative VRAM peak **1600MiB** (recovery1582MiB). Sampling can miss instantaneous peaks; early watchdog margins retained. Effective CPU affinity0,2,4,6/OMP limit4, requested OMP/BLAS1. No limit violation was observed.

Current original-plus-recovery new allocation at archival inventory **795963392B** (0.741GiB), including the776387032B serialized index, separate new worktree/cache/raw and original6111232B carried usage. Same FS free **91674116096B** (85.378GiB), above64GiB. Small final report/checksum/Git publication growth is checked again in final private readback receipt. CPU preparation cumulative upper estimate325.311s, below1800s. Added data/dependency downloads/installations=0. No old caches/env were cleaned or modified; no NequIP/3DGS/C16/AWMA task was started. All task GPU children ended, original lock released, final compute-process metadata empty.

## Unique minimal next proposal — not started

Perform an **independent CPU-only source/output audit** of this fixed-quality deficit before proposing more GPU work: compare per-query misses/neighbor overlap between B1 AUTO and the five identical single-CTA outputs, check recorded full-base GT/tie identities and exact fixed-source termination/candidate-retention semantics. Inputs and executable steps are in NEXT_STEP_PROPOSAL; no rebuilding, searching, CUDA import or new data. A sufficient small audit envelope is GPU0/download-install0, CPU<=4, RAM<=2GiB, newdisk<=64MiB, <=20minutes. Stop on identity mismatch, need for old-file mutation, CUDA/new dependencies or envelope exceed. The proposed audit is not executed as a new Goal here.

Current frozen configuration cannot support the intended equal-quality four-point performance comparison. Any subsequent GPU quality repair requires a separately reviewed and explicitly approved quality-first contract; do not silently expand itopk/iteration/hash choices or lower recall. No AUTO/SMALL performance or cache/SMEM headroom conclusion follows from failed recall. Await independent scientific review; **no automatic next GPU task**.

## Publication

Only the original A50G execution branch is pushed. This recovery adds a distinct report/raw directory and minimal recovery scripts, preserving every earlier STOP blob. Raw NPZ identities are unchanged; text paths are redacted while API parameters/return codes remain intact. The index, base/HDF5 and environment remain private. SHA256SUMS covers the report/evidence/scripts. Exact commit/tree/all added blob+SHA fetch-back and clean worktree checks are completed separately to avoid a self-referential commit SHA. STOP.
