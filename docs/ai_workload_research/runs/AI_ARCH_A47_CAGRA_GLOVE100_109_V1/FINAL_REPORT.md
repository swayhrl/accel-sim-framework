# Round A47 | GloVe100 / cuVS CAGRA native platform gate / STOP

**Scientific state: PLATFORM_OR_ASSET_NO_GO.** Real GloVe data and frozen official distribution qualification passed. Actual full native graph-build entry failed with SIGSEGV; a permitted small API diagnostic reproduced a driver/RMM stream-allocation fault. No qualified index, recall, calibration selection or timing result exists. This is a native platform/ABI admission failure, not a recall failure, software performance negative or hardware-headroom result.

Independent branch `hrl/aiarch-a47-cagra-glove100-native-109-v1`, fixed start `26ef7b20172495f26ed53248bfab792ae8af9040`. Executor Codex Lane M/node109 used a new worktree, environment, output and cumulative budget. No coordinator merge. Prior A26GR1/A45H heads and contents remain clean; C16/AWMA were not operated.

## Actual gates

| Gate | Result | Actual evidence |
|---|---|---|
| G0 | PASS | official24-wheel closure, SHA/platform/Python checks, offline install and pip check; Python and native cuVS embedded source commit exactly match |
| G1 | PASS | complete author HDF5,1183514x100 base,10000 query,top100 GT; finite/zero-norm/IDs/links; complete-base CPU cosine oracle32 queries |
| G2 | STOP | one complete-base cagra.build call attempted, process exit-11; no graph/index returned or saved; small API Dataset preparation passed but build again SIGSEGV |
| G3 | NOT_RUN | functional searches0, calibration checks0, chosen h unavailable; all four formal points and recall/timing NOT_RUN |
| G4 | Archived for single-branch publication | raw returns/CPU stack/version/input/budget receipts and SHA list; exact enclosing commit/tree/blob readback recorded on closeout |

Before the full build marker, the single RTX4080 device/runtime identity and small CuPy FP32 arithmetic assertion completed. They do not qualify CAGRA numerical correctness. The full GPU function was actually attempted; it was not skipped merely because the gate was unverified.

## Input and scientific contract

Official author endpoint [GloVe100 HDF5](https://ann-benchmarks.com/glove-100-angular.hdf5): **485413888 bytes**, local complete SHA256 **`544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`**. Entity ETag `9ef1a69a639809d4ae43efd5e6707fa1-58`; bound HTTPS range covered the full entity. Local SHA is execution identity, not an upstream-certified checksum. HTTPS HEAD403 was a packaging access issue: HTTP HEAD and HTTPS GET confirmed the same entity; no mirror or replacement input was used.

[ANN-Benchmarks fixed README](https://github.com/erikbern/ann-benchmarks/blob/2e081ad32c1eccab72dcb739ad886c310b90f715/README.md) supplies source/shape/GT provenance. [Stanford GloVe](https://nlp.stanford.edu/projects/glove/) states pre-trained vectors are PDDL1.0; the author benchmark derivative was used for approved research and is not redistributed. File attributes and source receipts are retained. HDF5 plugins disabled and external/virtual links or unknown filters rejected before reads. All original vectors retained, raw bytes unchanged; recorded FP32 unit normalization preserves cosine semantics. No FP16 or compression.

Fixed SHA256("20261014:"+decimal query ID) ordering yields2000 calibration/canary and8000 report queries, disjoint. The first2048 different report queries were frozen for timing; no query copying. Query index lists/digests, original field hashes and normalized-file hashes are in PREREGISTRATION/DATA_AND_INDEX_IDENTITY. CPU full-base oracle32 (FP64 evaluation of original cosine) matches publisher GT kth10 with maximum absolute error **1.5522863217e-08**. Original GT IDs unchanged. Publisher knn tie criterion `GT_distance_k10+0.001` and GPU distance tolerances atol1e-5/rtol1e-4 were frozen before GPU. No GPU recall values were obtained.

The preregistered four points remain B1/B256 x AUTO versus calibrated SINGLE_CTA+SMALL. Common k10/itopk128/width1/max_iterations64/random-mask/quality0.95/delta0.005 preserved. Candidate h9/h11 was not evaluated or selected. No condition was relaxed, no extra parameter scan or synthetic performance substitute was made.

## Frozen software and failure

Python3.12.3, cuVS-cu12/libcuvs-cu12/pylibraft-cu12/RMM26.10.0; CuPy14.0.1, NumPy2.5.4, h5py3.16.0. ENV_LOCK contains all24 official PyPI wheel URLs/bytes/SHA, dependency constraints and installed closure. No full ML framework/Docker/source rebuild. Both Python and native cuVS wheel embedded `GIT_COMMIT` are **24ee1bf1cb17cad0ac611e39643af39ee1870124**; CAGRA binding blob27880c8dd63e1d59a53c7e0cfbcbc8aef2727ae7 and planner blobda42f637dcd6fd1b299c425d353c77b3f1fe2f85 verified. No core-version substitutions.

Actual device RTX4080,76 SM,CC8.9; driver580.178.04 (Driver API13000), isolated runtime12090. System CUDA/driver were not upgraded. New RMM pool initial512MiB/max10GiB, explicit CuPy stream/cuVS Resources; loaded library file SHA identities saved. Native full-base call used cosine/ivf_pq/degree64/intermediate128 and unchanged FP32 normalized input.

Full build process exited **-11/SIGSEGV** after entering the official build API. No serialization or graph was produced. One permitted1024x100 synthetic API fixture (not a second scientific dataset/graph/performance point) was examined under the same shared lock with installed GDB CPU backtrace. GPU input and `make_device_padded_dataset` succeeded (padded, non-owning view, input owner retained); `cagra.build` again faulted. Main CPU stack: **libcuda!cuStreamGetId -> RMM Python memory-resource bridge -> librmm device_buffer::allocate_async -> libcuvs IVF-PQ build**. GDB batch return0 means debugger completed, not API PASS. Driver symbols/ABI stream root cause remains **UNKNOWN**; the stack does not prove which component is defective. Changing driver/core versions or repairing vendor mathematics is outside this admission. No further GPU retry or complete graph reconstruction occurred.

Ordinary wrappers were solved in this Goal: invalid historical NumPy version parsing, official endpoint HEAD/GET access, documented RMM allocator import and `/proc/stat` parentheses parsing. All failures and overhead remain in receipts. The platform failure is separated from those resolved packaging issues. No NCU/NSYS/NVBit, simulator, SM scan, training or new mechanism was run.

## Four-point outcome

| Point | Native recall | Formal samples | Result |
|---|---:|---:|---|
| B1 AUTO | unavailable |0| NOT_RUN, G2 failed |
| B1 SINGLE_CTA+SMALL | unavailable |0| NOT_RUN, h not selected |
| B256 AUTO | unavailable |0| NOT_RUN, G2 failed |
| B256 SINGLE_CTA+SMALL | unavailable |0| NOT_RUN, h not selected |

No AUTO/SMALL performance difference or hardware inference is made. No GPU search numerical qualification is claimed from CPU GT checks or trivial device arithmetic. Source-derived prospective planner choices are not reported as device-observed search.

## Resources and closeout

CPU preparation **3620.574s**, below2h. Total counted download **3128933154 bytes** (2.914GiB), data **485414912 bytes** (0.452GiB), including the probe and conservative Git metadata allowance. Download attempts never reset. Full checkout/private allocated **7895879680 bytes** (7.354GiB), free FS **92489011200 bytes** (86.137GiB). Peak sampled process-tree RSS **1496051712 bytes** (1.393GiB). Effective CPU affinity0,2,4,6; OpenMP cap4, BLAS requested1.

Shared lock `/data/c16/locks/c16_gpu_campaign.lock` opened existing without creation and acquired nonblocking. Cumulative holds **4.115052s**, includes failed native and debug wrapper/API attempts. Sampled native GPU-process peak **752MiB**; the short debug CUDA lifetime was not captured by its NVML samples, so sampled0 is not claimed as actual0. Pool max10GiB plus margin and independent sampling remained in force. All own GPU children ended, lock released; no resource limit violation was observed. Background prep was ended before GPU entry; formal measurement never started. HDF5/environment/normalized arrays stay private on109; no index exists and nothing was copied164.

Only this independent branch is published. SHA256SUMS verifies all evidence/scripts; the final Git ref is the enclosing commit to avoid self-reference. After commit/push/fetch-back, exact commit/tree/all new blobs and SHA/clean are verified in the final closeout receipt. **STOP; no next Goal.** Minimal follow-up is independent scientific/platform review of this pinned stream-allocation failure, not an authorized GPU experiment, parameter retry or driver upgrade.
