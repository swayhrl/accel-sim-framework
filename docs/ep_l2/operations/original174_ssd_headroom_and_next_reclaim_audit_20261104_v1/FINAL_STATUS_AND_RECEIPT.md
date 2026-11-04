# Original174 SSD headroom and next reclaim audit

Status: **READ_ONLY_AUDIT_COMPLETE — NO DELETION**

Snapshot date: 2026-11-04 (Asia/Shanghai)

## Second batch status

The October 28 seven-asset retirement was **not executed**. All frozen Source data files remain present with their frozen identities; no matching retirement INTENT/DONE receipt was found.

| Workload | Asset | Status | Current upper-layer allocation |
|---|---|---:|---:|
| cutcp | `TRACE_9d6ff92257d20b4b` | `SOURCE_PRESENT` | 10.25 GiB |
| scan | `TRACE_d6c21d018154d3b5` | `SOURCE_PRESENT` | 4.96 GiB |
| stencil | `TRACE_5e9aefe64e214679` | `SOURCE_PRESENT` | 3.46 GiB |
| kmeans | `TRACE_9ad2f284f8c2a318` | `SOURCE_PRESENT` | 3.31 GiB |
| histo | `TRACE_777ae84f37927c4e` | `SOURCE_PRESENT` | 2.99 GiB |
| 3MM | `TRACE_cf75342164f0b212` | `SOURCE_PRESENT` | 2.72 GiB |
| 3DConvolution | `TRACE_694a568c425385d3` | `SOURCE_PRESENT` | 1.01 GiB |

Actual space released by the second batch: **0 bytes**. A future exact retirement of all seven is expected to release about **28.71 GiB**.

All seven currently have: unchanged Source identity, no FD/mmap/writer, no exact-path registry or scheduled-script reference, exact overlay upper-layer presence, and matching genuine164 Manifest/COMMIT/member sizes plus restore entry.

## Current SSD and resource headroom

- `/root/data` available: `11,405,590,528` bytes (**10.62 GiB**)
- Free inodes: `215,724,247` of `234,422,272`
- Base floor without science reservations: `8,657,043,456` bytes; current margin above it: **2.56 GiB**
- RUNNING/unclosed registered write reservation: `76,110,983,168` bytes (**70.88 GiB**)
- All registry reservations used by the current contract: `84,432,482,304` bytes (**78.63 GiB**)
- Contract-required available space: `93,089,525,760` bytes (**86.70 GiB**)
- Contract headroom: **-76.07 GiB**

DTC reservations dominate: V100 full sweep 35 GiB, DTC-L2 MLP 24 GiB, Stage-IIA remaining48 8.75 GiB and first16 2.5 GiB. EP-L2 contributes about 0.63 GiB of nonzero active reservation. About 7.75 GiB remains attached to CLOSED/COMPLETE DTC requests because the current contract sums every registry request without filtering by state.

Original174 `/root/share/mnt164` is the local MD127 shadow. Genuine164 was verified only from new174 at `admin-wcx@10.208.130.164:/home/shared`. No archive Sender/Receiver lock was held.

## Recent space growth

Available space fell by about **22.84 GiB** from the 2026-10-28 snapshot.

| Directory | Current allocation | Recent finding |
|---|---:|---|
| `/root/data/ep_l2_dtc_l1_native_v2` | 10.42 GiB | Shared registry/history; request_history is 10.95 GB total and added ~3.91 GB since Oct 28 |
| `/root/data/dtc_l2_mlp_exploration_20261027_v1` | 6.92 GiB | DTC-L2; ~3.47 GB recent growth; currently active |
| `/root/data/ep_l2_full_workload_performance_20261027_v1` | 5.61 GiB | EP-L2; ~3.97 GB recent growth; currently active |
| `/root/data/ep_l2_multiworkload_event_timeline_20261027_v1` | 2.03 GiB | EP-L2 raw/restored outputs |
| `/root/data/dtc_main_v100_sweep_20261025_v1` | 1.41 GiB | DTC V100 sweep; active reservation |
| `/workspace/worktrees/accel-sim-decoupled-l2/hw_run` | 173.43 GiB | Historical/active Trace and experiment tree; 186.22 GB total |

The active November 4 Stage-IIA directories are currently small, but their registered future write reservations are large. These scientific directories were observed only and are not cleanup candidates in this audit.

## Ranked next reclaim candidates

1. **Second batch seven assets** — `READY_FOR_SEPARATE_FAST_RETIREMENT` — expected 28.71 GiB
   All Source identities unchanged; no current or planned exact-path reader; exact upper-layer allocation; true164 Manifest/COMMIT/member-size and restore checks pass.

2. **atomic_add_bw** — `READY_AFTER_SEPARATE_USER_AUTHORIZATION` — expected 4.66 GiB
   Both raw .trace and processed .traceg are in the frozen archive. No exact current or planned reader was found; owner should still confirm no alias-based atomic experiment dependency.

3. **Bank Diagnosis** — `HOLD_PLANNED_READER` — expected 8.33 GiB
   run_decoupled_l2_selected_bank_gate.sh defaults to this Source root. Retire only after the EP-L2 owner accepts restore-before-reuse or changes the dependency.

4. **M5 ATAX/MVT** — `HOLD_IMMUTABLE_OWNER_REVIEW` — expected 10.79 GiB
   Complete raw and processed content is archived, but m5-trace-immutable and prior contract require a dedicated owner decision and conservative requalification.

Historical packages remain HOLD because no trusted independent whole-object archive proof was found:

- `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodina-3.1.tgz` — 14.30 GiB — `HOLD_NO_TRUSTED_INDEPENDENT_ARCHIVE_PROOF`
- `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/parboil.tgz` — 8.67 GiB — `HOLD_NO_TRUSTED_INDEPENDENT_ARCHIVE_PROOF`
- `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/accelwattch-artifact-appendix.tar` — 36.94 GiB — `HOLD_NO_TRUSTED_INDEPENDENT_ARCHIVE_PROOF`
- `/workspace/m5-trace-immutable/syr2k/syr2k.tar.zst` — 3.54 GiB — `HOLD_NO_TRUSTED_INDEPENDENT_ARCHIVE_PROOF`
- `/workspace/m5-trace-immutable/2mm/2mm.tar.zst` — 3.18 GiB — `HOLD_NO_TRUSTED_INDEPENDENT_ARCHIVE_PROOF`

The previously retired `polybench.tgz` is absent and must not be replayed. M5 SYR2K and 2MM packages remain explicit archive-proof HOLDs.

## Recommendation and authorization boundary

Recommended next action: authorize one exact fast-retirement batch for the seven unexecuted second-batch assets. If a staged approach is preferred, begin with cutcp and scan. Consider atomic_add_bw separately after its project owner confirms no alias-based atomic experiment dependency.

Do not retire Bank Diagnosis until the EP-L2 owner resolves the default old-path dependency in `run_decoupled_l2_selected_bank_gate.sh`. Do not retire M5 ATAX/MVT without a dedicated immutable-owner authorization. Do not delete historical packages without new independent archive proof.

Every future deletion requires separate user authorization. This audit performed no unlink, migration, process control, registry edit or science-task modification.

## GitHub state

Audit base HEAD and remote readback before this report: `20eb6c4deb0e9ee62e58cfe2fc038ef63adf4001`. The publication commit and final remote readback are recorded in `GITHUB_PUBLICATION_RECEIPT.json`.
