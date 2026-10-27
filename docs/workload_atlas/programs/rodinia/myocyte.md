# myocyte - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

A cardiac myocyte91-equation ODE model with excitation-contraction coupling (46state positions) and three15-state calmodulin subsystems. CPU integrates with embedded Fehlberg7/8,13 RHS evaluations per attempt; GPU evaluates RHS pieces in mode0, CPU finishes intercompartment fluxes and adaptive error control. The model includes exponential/log/power ionic currents and binding reaction derivatives (`kernel_ecc.cu:435-930`, `kernel_cam.cu:175-348`). Inputs y.txt and params.txt are external arrays; output stores trajectory. Frozen100_1_0 means horizon100,one workload,mode0; the100 is not a kernel-count promise.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/myocyte` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/myocyte/` at this fixed commit. Historical capture-to-source/executable binding is separate.

`define.c:7-12` fixes FP32,32threads,91 equations,18 parameters. `Makefile:20-48` compiles a single main translation unit including both modes at-O3 -g, configurable GENCODE, then links lm/lcudart; several older targets default explicitly,70/75 are external variables here. Trace reports binary version70. Frozen mode0 is not the mode1 all-device solver route; compiler spill/register/local-memory extent and ELF/PTX identity are unbound.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/main.cu) | `ef4f058a22b22f815d56561d385493a1691e4b46` | `2623572e2c8ef2bfaf2d20ccea3ad67922d081b480f2c3dc24634732fda4d1d1` |
| [define.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/define.c) | `5a2d5afb39ea41e1e725159088489cf5d1b998a3` | `2038a43f688b05b83aef097cf004850db4005f9aeb88e0b15b0df30f66720fa0` |
| [work.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/work.cu) | `3076bfc5a122d096d8f03f711d04cd8479efca30` | `2e73867b5a8fbc5717c9a52f3a3f7a565549673eccdf4e58c44b7ea35fdfb0e9` |
| [master.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/master.cu) | `c7e04d9340f2f08dab429fa82fa2b3bfb36a53bf` | `7f8ce872c95dfb526c41014d70f385757b4d956b0c4a20705710798813c282b9` |
| [solver.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/solver.cu) | `e1b68fc48714aa40e1278ae7aaa1504bbefde3f7` | `3a45a27c0aba1615820ac473244b1e4d8599599e04d168e0717add516bb76429` |
| [embedded_fehlberg_7_8.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/embedded_fehlberg_7_8.cu) | `5ae965af84285050e7674ebbcadb5d7ee6b8b8b8` | `704b7cd89af9d8ea310a52a1e02aa3c6242fa85dfa4954cedda53e9ce1edd312` |
| [kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/kernel.cu) | `029ad151a0ad832f0de3072e43a2e7de441fb132` | `5089bc46c2b4ad67b2453efd409af15b724e4b6e7ba992cd73767dc8f0e6f080` |
| [kernel_ecc.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/kernel_ecc.cu) | `49440bad0a8c02c73b6378958249a036b3451fc7` | `f040d06bae409b9482a0d3928b83b15378277532e713bacb2aba7f7fe9aba1da` |
| [kernel_cam.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/kernel_cam.cu) | `ef8df950bcd3ef314bab62cfa3204352603f8880` | `a332e1242dd2a3622233c295da5dd2e85eb9cd1251d3188f9ee462ca7217c0f9` |
| [kernel_fin.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/kernel_fin.cu) | `f26da35b2629ad9bc74a3091a45de9f90f0e6364` | `ad64e6ef3af13e49495e70a65e33da3eb2a69c0a453f6288ee41ca95a651babc` |
| [work_2.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/work_2.cu) | `99652db8d9b880f8417439a4fc0c5c73df422bc7` | `6042ab92a48efd7dd0edeca2d9139b7543d829c8464d9715f631941f0c8fd879` |
| [kernel_2.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/kernel_2.cu) | `a1a90f96871a35d5acc4ea5ffc07779bf16f301d` | `14bea7ff02d016edb89761474fbf35c878e9635291f73c36b8df53220790d606` |
| [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/myocyte/Makefile) | `f26e958eb5ac353700195188eefa307453146abe` | `f42c781f502319c944bd9c1dac24a4d13f15cf42d9b0b7f98542b986b14e63e0` |

## 3. Host calls and kernel order

`main.cu:136-184` selects work() for mode0. work reads91 initial values and18parameters per workload, then calls CPU solver sequentially across workload instances (`work.cu:125-159`). Solver k1..xmax, each at most12 adaptive attempts (ATTEMPTS12, `solver.cu:63,144-268`), resets h1 per outer iteration and can return-1 after exhausted attempts. Each `embedded_fehlberg_7_8` calls **master13 times**, at205,225,...,445; CPU constructs stage states, then computes final weighted sum and error (`:199-469`). Every master copies364B state +72B parameters H2D, launches **kernel<<<2,32>>>**, copies364B derivative+12B com D2H, invokes plain CPU kernel_fin and replaces NaN/Inf derivative values with0.0001 (`master.cu:37-92`). Thus no asynchronous overlap between RHS stages can be inferred. Exactly one unique selected __global__ definition. Trace5993 RHS launches=13*461; this is consistent with461attempts but does not recover which outer steps retried or certify termination. The theoretical full100-step attempt range1300..15600 assumes no early failure;5993 alone cannot prove100accepted steps.

Mode1 is a distinct alternative: work_2 launches solver_2 once (`work_2.cu:199-228`), which contains device integrator/helpers. `kernel_2` is __device__, not another global launch. That alternative is compiled but not executed by selected0.

## 4. Detailed kernel implementation

`kernel.cu:7-124`: bx0,tx0 invokes device kernel_ecc with state offset0; bx1,tx0 sequentially calls kernel_cam for offsets46,61,76 and parameter offsets0,5,10, with Ca inputs state35,36,37. All31other lanes perCTA do no work; no CTA barrier/shared allocation in selected kernel. The global kernel timeinst argument is int (`kernel.cu:7`) while master receives fp timeinst (`master.cu:5`); launch argument conversion truncates fractional Fehlberg stage times before the device helpers receive them. This is actual selected-source time semantics, not an assumed continuous-time RHS evaluation. ECC scalar loads state0..39 except unused22nd local, writes46 derivative positions, with read-after-write coupling in current sums. CAM loads15state positions,6parameter values, computes reaction rates and writes15derivatives per compartment; helpers are device functions, not independently launched kernels. CPU kernel_fin (`kernel_fin.cu:4,66-106`) updates Ca and intercompartment fluxes; it has no __global__/__device__ qualifier.

**Static source risk:** `kernel_cam.cu:348` writes `d_finavalu[com_offset]` for offsets0,1,2, despite having d_com parameter. ECC writes those same derivative positions (`kernel_ecc.cu:694-696`) in another CTA, without ordering/atomic. `d_com` is allocated in work.cu113-116 and copied back in master60, but selected GPU body does not write it. This is an apparent output-pointer bug and potential cross-CTA write race plus uninitialized com consumption. Preserve this as a separate source audit, not a retroactive assertion about historical trace/binary numerics.

## 5. Thread and address formulas

All active addresses are scalar fields at fixed offsets, not one equation/lane. For state/derivative address B+4o; ECC offsets0..45, CAM46+j,61+j,76+j, j0..14. Parameters Bp+4p, p15forcycle and p=parameterOffset+1..4,16,17forCAM (`kernel_ecc:435`, `kernel_cam:175-214`). CAM Ca loads B+4*35,36,37 (`kernel.cu:71,87,103`). No adjacent-active-lane stride exists: each warp has only lane0 active. At a scalar4B instruction, sector useful fraction4/32 and line fraction4/128; subsequent instructions may reuse that line. Under128B-aligned allocation the full91float slab spans3lines/12sectors, parameters72B span1line/3sectors, com12B1line/1sector. These are union footprint bounds, not observed fetch counts. ECC's startup scalar loads ofsuccessive offsets have+4B instruction-to-instruction spacing; CAM similarly loads contiguous15-state spans, but later arithmetic accesses/reloads follow dependencies rather than a uniform loop. CTA1 runs3CAM calls sequentially, offset jumps15floats=60B. Both CTAs read some same state lines (Ca35..37 and parameters), so cross-CTA line overlap is possible with only2active threads. Between RHS launches CPU rewrites device state/params using same allocations; addresses reused but data changes. Apparent racing stores to derivative0..2 share exact byte addresses with ECC, not merely a hash collision.

## 6. Dataflow, locality, coalescing and concurrency

At most2CTAs and2active lanes per selected RHS, with long scalar arithmetic chains. Independent startup state loads may expose some memory-level parallelism; ionic-current expressions depend on loaded values/math results. No large warp-level load fanout or many-CTA parallelism exists in mode0. CPU integration, copies and dependent adaptive control serialize launches. Tiny state gives potential spatial/repeated-address locality but cannot compensate for lack of active warps. Source scalar temporaries could spill; this requires binary evidence, not a claim that hundreds of declared fp variables mean local-memory traffic.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-27`: `IDENTITY_FROZEN`; parameters `["100_1_0"]`.
- Selected input digest `977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992` is the registered identity, not automatically original-file SHA.
- Bundle `f89e66d04510f7ce2989971e0f0a33efc69881ccd2418d181ab52b26cd5ddbcc`.
- Trace entry `/root/workspace/assets/traces/bundles/f89e66d04510f7ce2989971e0f0a33efc69881ccd2418d181ab52b26cd5ddbcc/tree/kernelslist.g`.
- Existing scope `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: Only ordinary trace identity for this program in the72-input matrix; no outcome-dependent replacement. Keep its recorded source/command/content identity. Exact capture-time executable/input-content and full-application provenance are not newly certified.

Header inventory: 5993 kernel entries, 17979 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z6kerneliPfS_S_S_` | `(2,1,1)` | `(32,1,1)` | 5993 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED: one selected global definition,5993 registered launches,2x32geometry, only2active lanes;13RHS evaluations perattempt; CPU kernel_fin and adaptive solver; no selected GPU atomic/shared barrier; apparent CAM output-pointer/race and unwritten com risk. Mode1 solver_2 is a different execution model and is not silently merged. INPUT/TRACE structure does not certify trajectory or accepted step count.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: tiny repeated state and two active lanes make tag-capacity pressure unlikely from these arrays alone; investigate measured PIB/data dependency waiting versus limited independent work before attributing benefit to tags. Same-line overlap across2CTAs could be measured but not presumed merged. EP-L2: copy-driven state refresh and a tiny kernel footprint may make kernel/copy residency boundaries more relevant than many outstanding independent lines; exact copy cache effects require runtime/model contract. Do not apply mode1 workload-scaling intuition to mode0. Correctness/source-binary risks must accompany mechanism interpretation.

## 10. Evidence and limits

Source-bound launch count is dynamic via adaptive attempts and possible early return.5993/13 divisibility supports RHS grouping, not completion proof. Original y/params hashes, accepted CPU output and executable linkage are unresolved here. All selected mode0 host/control/helpers were read; mode1 is identified only as an excluded branch. Static pointer defect is not patched and accepted scientific results unchanged. No new run occurred.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
