# A26G GS-Scale real Rubble gated native discovery — G0 STOP

Fixed execution start: `9fc94371eea82473a3bd29197505b359da2c8d00`; branch `hrl/aiarch-a26g-gsscale-rubble-gated-native-109-v1`.
Contract/approval/investment/A25 were read in full; their exact blobs and SHA256 are in RUN_IDENTITY.json.
Approved record overrides historical pending-approval prose. Author source remains `6471e958f7e318f4870234d8107e0aa91c2d6932`, tree `bc99b237b3e050ddd46392acfe7adb8dd822b2a9`.

## Gate results

| Gate | Actual result | Evidence / limitation |
|---|---|---|
| G0 | **STOP — STORAGE_BOUND_UNKNOWN_STOP** | Fixed identities and current resource snapshot qualified; official data access located; pre-download expanded-storage upper bound not established |
| G1 | **NOT_RUN** | No full scene/COLMAP download, environment creation, installation or CPUAdam compile; G0 did not pass |
| G2 | **NOT_RUN** | No CUDA initialization, Torch import, native step or numerical/quality claim |
| G3 | **NOT_RUN** | No wall/timing/transfer/synchronization samples; no early or late training state observed |
| G4 | **PASS** | First complete packet pushed and independently fetched/verified; PUBLICATION_READBACK.json binds its exact commit/tree/blobs/SHA; final closeout commit is also verified before STOP |

## Scientific source access was actually checked and recovered

Official [Rubble archive](https://storage.cmusatyalab.org/mega-nerf-data/rubble-pixsfm.tgz) HEAD: 200, 9,773,995,561 bytes, Accept-Ranges bytes. ETag is multipart metadata, not SHA256.
Range 0–65535 and last 32 bytes both returned 206 with matching Content-Range; partial SHA256 is preserved. No complete-archive hash is claimed.
The 64 KiB compressed prefix exposes real Rubble/val/rgbs and a JPEG entry, not a complete member inventory.

Node Google Drive connections timed out. This ordinary access problem was recovered with controller-side, official HTTP metadata reads, without running another node or changing source/hardware.
The fixed [author README](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/README.md) links the public COLMAP root.
Its root→mill19→rubble-pixsfm→sparse→0 chain was parsed, then official binary HEADs verified:

| Actual public file | Size (bytes) | Binary HEAD |
|---|---:|---|
| cameras.bin | 64 | 200 / application/octet-stream |
| images.bin | 427,380,490 | 200 / application/octet-stream |
| points3D.bin | 162,597,265 | 200 / application/octet-stream |

Total COLMAP bytes: 589,977,819. Listings and binary HEADs establish discoverable/accessibly offered files; camera/image/point byte correspondence remains untested until a legal download.
**INPUT_SCIENTIFIC_PAYLOAD_BLOCKED is not the result.** Missing prepublished SHA256 is also not the stop reason; contract permits freezing first lawful complete downloads.
Official publisher research release/access was checked; code license is not silently treated as a blanket dataset redistribution license. No raw images/COLMAP are published.

## Exact binding resource-admission failure

G0 item 3 requires reliable small metadata/same-origin tar index when archive expansion is unknown, and mandates STORAGE_BOUND_UNKNOWN_STOP if disk safety cannot be established before the large download.
Current same-filesystem free space is approximately 134 GiB, above 64 GiB reserve; this is not an actual disk-space exhaustion result.
The public directory request returned 404. Two bounded, candidate same-origin index/manifest HEAD probes returned 404; this does not prove an index exists nowhere.
The gzip footer has ISIZE **1,213,739,008**, which is a gzip member's size modulo 2^32. Even assuming a single member, its possible total is `1,213,739,008 + n × 4,294,967,296`; metadata does not establish n or a <=60 GiB all-task upper bound; multiple members further weaken a last-footer total-size claim.
A near-1 JPEG compression estimate or a guessed wrap count cannot qualify raw expansion + 4× derivatives + environment/build/cache/checkpoints under the hard cap.
A newly generated full tar index requires reading the complete archive, which cannot retrospectively satisfy this contract's pre-download admission gate. No unbounded extraction or large download was used to find out.
The original science, input, versions, quality requirements and resource limits were not relaxed.

## Software preflight and bounded engineering work

Eleven author files were read through official GitHub contents API at the exact ref; every returned Git blob was independently recomputed from decoded bytes.
Source identity includes the trainers, CPUAdam, parser, setup, install and requirements. Raw author code is private, not copied into this Git evidence packet.
Official Torch 2.2.0+cu121 and torchvision 0.17.0+cu121 CPython 3.10 wheel URLs/SHA were located; IPEX 2.2.0 and NumPy 1.26.4 official CPython 3.10 distributions were identified with SHA and size.
This is **PARTIAL release metadata**, not a resolved transitive ENV_LOCK or compiler/ABI PASS. Full closure/install did not continue after the binding G0 storage stop.
CPUAdam's real hardcoded-64 thread cap test and CUDA 12.6/cu121 compatibility were not attempted or claimed.
HTTP total deadline needed two precise fixes; successful 25-second enforcement receipts are archived. Raw-host DNS failure was recovered through the same-ref official API. PowerShell receipt summation was corrected from serialized byte counters.
These resolved tool problems are not the STOP reason, and no runtime gate was predeclared impossible.

## Actual budget and native evidence

Official HTTP entity body bytes: **2,143,328** (node109 561,614; controller source metadata 1,581,714), including 65,568 bytes of bounded scene archive ranges. These counters exclude protocol/TLS and Git transport; no full scene/COLMAP or software distribution payload was downloaded.
New worktree/private receipt/controller metadata plus small Git/output overhead: conservative **<16 MiB**, far below 60 GiB; same filesystem remains >64 GiB free. Exact logical counts/scope are in BUDGET_USAGE.json.
Node metadata collection used one worker/thread; observed collector RSS high-water 23,728 KiB. No model, DataLoader, pinned buffers, compilation or runtime process tree was launched. Initial fetch/controller reader RSS was not separately instrumented.
Shared-lock preflight acquired nonblocking and released in approximately 7.2 microseconds; GPU runtime lock hold **0 seconds**. No GPU device query was made; allocated/reserved/task GPU allocations **0** because no CUDA activity was launched, not a claimed device-monitoring measurement.
Preparation remained far below four hours. CUDA/Torch import, GPU kernels/copies, training, profiling, simulator, SM scan and mechanisms: **0**.

Real continuous training reached: **NOT_STARTED** (0 steps), not EARLY_ONLY. Late state was not evaluated.
Strong-software residual wall, CPU Adam service, ID/gradient D2H, parameter H2D, GPU execution and unhidden sync: **UNKNOWN / NOT_MEASURED**, with zero samples and no speedup/headroom claim.

## Closeout and remaining issues

RUN_IDENTITY/GATES/ASSET_MANIFEST/ENV_LOCK/BUILD_RECEIPT/THREAD_LIMIT_RECEIPT/BUDGET_USAGE/FUNCTIONAL_QUALITY/OBSERVABILITY_SUMMARY/FINAL_DECISION and raw sanitized HTTP/source/storage/engineering receipts are archived with SHA256SUMS.
Old A16R1, V1R1 and A24 HEADs/cleanliness were rechecked; their models/environments/caches and C16/AWMA remain untouched. No coordination merge or successor Goal.
Remaining prerequisite: a reliable official expanded member/size manifest or an independently reviewed change expressly permitting a budget-capped full-archive admission scan. It is not authorized automatically here.
The report's enclosing commit/tree/blob and all committed SHA values are verified by push/fetch-back closeout; self-referential hashes are not embedded.
First-packet readback: commit `0e00d87f4aabd3650d2b0732f1497dba05ddd9e0`, tree `ce899d402271cc16508f731edba429c7554f6aaa`; all 20 initial files matched. Only this independent branch is published. After remote verification, **STOP and await independent ChatGPT scientific review**.
