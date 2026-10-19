# Original 174 cross-project cold asset census and reclaim planning — 2026-10-19

## User instruction, precedence, and hard protections

User asks to find and eventually migrate **as much unused original174 data as is worthwhile**, not limited to TLS; all projects other than **EP-L2** and **DTC-L1** are potential *audit* candidates, with **C2P lower priority**, but C2P's full measured size must be reported. This authorizes a cross-project **read-only inventory, risk assessment, archive planning, and exact release proposals**, NOT bulk deletion of unreviewed scientific sources, unique outputs, Git objects or shared traces.

This is a NEW, bounded **cross-project inventory/capacity diagnosis** workstream, independent of the two original TLS-V10 Goals, which are currently BLOCKED; do not automatically restart them, reinterpret a scientific receipt, create a second TLS sender, retransfer B0001–B0009, change P9 selector/txid/target, or delete any P9 source originals before its **full 141-file** true164 archive and independent native restore plus user-authorized exact release gate.

Latest verified reference:
- old174 TLS Source: `swayhrl/gpu-l2-cache-verilog:hrl/ops-174-tls-v10-source-exec-v1` at `f844d5fabef9aa615b121e77ddc13c32c5c8e472`.
- 174-new TLS Target: `swayhrl/accel-sim-framework:hrl/tls-v10-174new-target-exec-v1` at `b574e7ff452a7554cea41bb0fc2a93509daf789a`.
- old174 `TLS_V10_P9_PUBLIC_B0010_SOURCE_BLOCKED_AUDIT.json` at source commit above: 9 windows B0001–B0009 closed, 705,152,417 B durable true164/native *range* proof, NO full-file/group restore/release; old174 available `f_bavail` 15,720,431,616 B vs scoped 16GiB=17,179,869,184 B (short 1,459,437,568 B before projected control writes), Share available 44,375,363,584 B. There are 8,495,133,307 frozen original bytes left. These are historical snapshots, not current resource admission.
- Source and Target V9 archives ended `3891fcd93a7ac5c3361d8f476d3c41036104b151` and `c870ca77456d4d4d70a110411fa5c60934976666`; do not rerun V9 or alter its archive contents.
- Prior 16GiB TLS-COPY_ONLY and exact P9_PUBLIC-postrestore release are **narrow, original-identities-bound** policies at Framework `f8baa3acfdbd2f420c108d4d4baff0432ef38822`. The 16GiB exception is NOT transferable to a new unrelated project's archiving or deletion. Other current resource and authority rules still apply.

### Absolutely protected source projects

EP-L2 **entire project line** and DTC-L1 **entire project line**: all source trees, Git, builds, currently retained compile binaries, run results, review packs, provenance, simulations, inputs, shared trace dependencies, active jobs, and their cross-project dependents. Mark `PROTECTED_EP_L2` / `PROTECTED_DTC_L1`, with occupied (allocated), logical and role labels if cheap metadata-only. **Do not archive, rewrite, relocate, dedup, compress, unlink, or change reader paths for these** in this workstream. Do not use project *directory names* as sole ownership evidence; e.g. a common trace inside another worktree that is still consumed by EP-L2 or DTC-L1 is protected.

For other lines (TLS, AWMA, C16, AI-ARCH, C2P, M2D, general old GPGPU-Sim, shared traces, old bench/tests), **candidate does not mean inactive**. Protect all live/current/scheduled readers, dirty or uncommitted source, science-authority inputs, unique outputs, unknown ownership, shared cross-project dependencies and existing Git/history. Include active users and storage device boundaries. No deleting whole worktrees or touching running PIDs.

## Actual objective and ranking

Obtain a **source-side allocated-bytes and recoverable-bytes inventory** that explains where original174 physical source filesystem space resides and ranks high-value cold assets. Find multiple-GiB cold projects before more tiny cache cleanups; maximize *safe measurable* source reclaim once separately approved. Aim for a reliable first-stage report promptly, not a perpetual exhaustive recrawl.

Classify each **non-overlapping canonical physical source root** as:
- `PROTECTED_EP_L2`, `PROTECTED_DTC_L1`
- `ACTIVE_KEEP` — actual process/FD/cwd/argv/scheduler/lease/planned reader/writer
- `CODE_GIT_KEEP` — source, Git trees/packs, clean/dirty/untracked code, editable config, reproducibility instructions
- `SHARED_DEPENDENCY_KEEP` — trace/input used by multiple projects or linked by protected lines
- `COLD_EXCLUSIVE_ARCHIVE_CANDIDATE` — provably unused, exclusive non-code science products with a verifiable source lineage (COPY_ONLY candidate, NOT unlink authority)
- `ALREADY_164_ARCHIVED_RESTORE_VERIFIED` — identical original still present but accepted matching true164 original-byte proof and independent native full-file restore; requires fresh source owner identity, activity and separate exact release authorization
- `TRASH_REPRODUCIBLE_CANDIDATE` — proven redundant/officially re-downloadable *ordinary non-scientific* cache only, with source-owned exact safe cleanup eligibility
- `HOLD` — uncertain uniqueness, symlinks/hardlinks/other owners, insufficient real storage or stale proof.

Rank eligible candidates by **conservatively measurable bytes likely to increase actual source f_bavail after release**, independent source evidence, inactivity, risk, restore cost and scientific project priority. At least create high-, medium-, low-priority tiers. Report hard upper bounds versus authorized/currently-releasable bytes separately; never advertise gross `du` bytes as guaranteed net `df` gains.

User priorities: protect EP-L2 and DTC-L1 absolutely. Among nonprotected assets prioritize high-return dormant projects incl. historical TLS outputs and any verified cold AWMA/C16/AI-ARCH/GPU experiment trees; C2P is **lower priority** but gets an exact breakdown and historical comparison. Do not assume AWMA/C16/AI-ARCH are dormant: inspect current owner/current lineage first. M2D separate from C2P, and shared trace bytes not exclusive C2P.

## Known exact old snapshot anchors (must verify present/allocated at *current source*)

**C2P is not yet fully inventoried.** V9 two source build roots:
- C2P1 `/tmp/c2p-gpgpu-pre-attribution-20260822/build`, 205 files, 424,570,880 allocated B (~0.395 GiB); 164 archive + all-file bytes/full-content native restore were previously verified (numeric native file metadata sampled, not all files).
- C2P2 `/tmp/c2p-gpgpu-build-20260821/build`, 205 files, 424,419,328 allocated B (~0.395 GiB), same verification scope.
- Combined these **two known C2P builds** = 848,990,208 B (~0.791 GiB) allocated on the old V9 snapshot. Do not count M2D in C2P.
- Mixed TLS/C2P `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/tls-c2p-v100-20260822`, historical 1,495,752,704 allocated B (~1.393 GiB), offloader PID1920891 was alive and gated at 80 GiB in old snapshots; **do not touch** until current process/ownership proof.
- Two named + mixed are **distinct known roots**, ~2.184 GiB previously measured, not the entire C2P line, not an instantly releasable total.
- V9 M2D independent `/tmp/m2d-core-g21/build`, 205 files, 410,275,840 allocated B (~0.382 GiB): classify as M2D not C2P.
- Prior TLS-only classification lists **7,340,679,168 B** in four **shared** trace root dependencies; only one path is named `c2p-polybench-full-20260821/.../traces` (1,110,691,840B). These roots remain shared inputs and may have protected downstream consumers. Avoid double count/nondestructive use audit.
- Prior V9 `/workspace/repos/gpu-l2-cache-verilog-v3r2-clean/build` 769,466,368 B and `-v3r1r-clean/build` 599,670,784 B contain potential valuable verification/signoff history and are EP-L2-adjacent, so are PROTECTED, not easy space reclaim.
- Existing P9_PUBLIC 141 frozen files / 2,897,674,240 B original allocated; original P9 is still SOURCE_KEEP, nine partial windows not a release proof.

These are baseline historical receipts, **NOT current complete measured project occupancy**. Measure current source-inclusive and exclusivity without summing overlap.

## Inventories to produce (bounded, shallow-to-deep)

1. Confirm original174 namespace `mnt:[4026534768]`, current exact `/workspace` device and `statvfs(f_bavail,f_bfree,f_frsize,fsid)`, Source Share, cgroup/RAM, current writers/active project registry. Treat simultaneous `df` changes as other writers, not evidence of old release. No host ext4 reserved block changes. Source overlay and bind-mount `/root/data` may have the **same underlying filesystem accounting with different device IDs**; report physical backing/potential overlap, never total their free space.
2. Fast metadata-based **shallow** census: actual `/workspace/worktrees`, `/workspace/repos`, `/workspace/build`, `/workspace` loose roots, `/tmp`, and bounded known `/root` generated/cache roots; `/root/data` only if the actual writable allocation and owner scope is confirmed, no full 3.8-TB filesystem crawl. Tag active vs protected roots before heavy I/O. Single source scanner, low CPU/I/O niceness, capacity and reader gates, and periodic checkpoints. Avoid following symlinks, bind mounts, Git object recursion, remote mounted164/Share or other owners. `du` is an estimate; record apparent vs allocated, device, hardlink count, sparse or reflink uncertainty, overlay lower-only ambiguity, and current timestamps.
3. For top largest nonprotected roots only, dive to depth2–3 and separate CODE/source/trace/build/results/checkpoint/cache, last real writer/activity, exact owners and repro metadata. Prefer at least one TOP20 ranked table and per-project totals, plus C2P exhaustive bounded breakdown. No mass hashing of all historical raw; hash only chosen final frozen candidate in a later, separately admitted transfer.
4. Use identical snapshots for size comparisons; check multi-project/shared roots and aliases to prevent nested double-count. For every C2P root enumerate original project ownership, unique bytes and any path overlapping prior TLS manifest/V9 or shared trace roots, collect current offloader PID/FD/cwd and future planned reads, all original vs164 full restore pointer match, and recompute source current allocated sum of known roots. Report "C2P overall unknown" until all relevant roots and consumers are accounted.
5. Publish `CURRENT_OLD174_SPACE_AND_IO_PRESSURE.json`, `SOURCE_COLD_CENSUS_PROJECT_SUMMARY.csv`, `SOURCE_COLD_CENSUS_TOP20.csv`, `SOURCE_COLD_CENSUS_C2P_BREAKDOWN.csv`, `SOURCE_COLD_CENSUS_SHARED_DEPENDENCIES.json`, `SOURCE_COLD_CENSUS_PRIORITY_AND_RELEASE_GATES.md`, `SOURCE_COLD_CENSUS_PROGRESS.md`. Each receipt links source path, filesystem/inode, allocated/current observed bytes, source/code/trace/result role, project owner, last writer, consumer proof category, any prior164 archived/restore SHA, prospective immediate bytes *upper bound*, release authority state `NOT_GRANTED` until exact approval. GitHub receipts only small text; never GB raw.

## Separate Archive and Source Release

- This new audit **DOES NOT** replace original TLS 16GiB policy, Source/Target signed READY or original P9 exact141 conditional post-full-native-restore release approval. B0010 stays HOLD until separate external legal space recovery and fresh original source 16/40/64/resource/reader gates, then resume **same** B0010 from original Goals; do not retransfer nine closed ranges.
- For a **new non-TLS project**: identifying idle outputs allows a proposal to copy/archive to true164. It does not invoke the unique TLS 16GiB exception. A per-project or grouped-source copy-only resource plan, isolated destination, selector and true164 restore controls require **separate narrow authority** where original workspace48GiB floor would otherwise fail.
- For a **scientific source release**: even if target is fully archived/restored, require exact user approval of its SHA-frozen selector and current source readers, save source code/Git/provenance, use a qualified source-owner crash-safe exact-file journal; no root-level/glob deletion. Prior V9 C2P/M2D sources are SOURCE_KEEP and not silently authorized by this broad review.
- Normal, manifest-proven expendable caches may be *proposed* for separate explicit cleanup within current Source owner and active restrictions, but broad inventory should be READ-ONLY first. No new deletions before the prioritized candidate list and applicable clear authority.

## Division of work

Only ONE new original174 `GLOBAL_COLD_CENSUS` source inventory Goal; it does metadata only and never obtains an active TLS sending lease. 174-new can independently examine existing real164 V9/TLS metadata/restore index and rank duplicates, but may not run a second receiver or read massive source trees via shared mounts. When candidate shortlist exists, request one grouped explicit archive/release policy for source owner, then roll validated oldest/highest-value assets in bounded batches. Preserve original TLS-V10 Goals BLOCKED and 174-new archived bytes until trigger, not process restart.

Time and effort: prioritize an initial source TOP20 + per-project sizes within a bounded audit turn; don't postpone result waiting for exhaustive full SHA. End with exact blocker and what user authorizations would unlock the largest *measurable* reclaim. No automatic EP-L2/DTC-L1 modification or other source cleanup as a side effect.
