# Original174 second-batch seven-asset fast retirement

Status: **DONE — 7 DONE / 0 HOLD**

Execution date: 2026-11-04 (Asia/Shanghai)

## Per-asset result

| Workload | Asset | Status | Files | Allocated bytes unlinked | Observed `df` delta | Preserved controls |
|---|---|---:|---:|---:|---:|---|
| cutcp | `TRACE_9d6ff92257d20b4b` | DONE | 11 | 11,010,949,120 (10.25 GiB) | 11,010,846,720 (10.25 GiB) | `kernelslist.g`, `stats.csv` |
| scan | `TRACE_d6c21d018154d3b5` | DONE | 33 | 5,329,186,816 (4.96 GiB) | 5,328,838,656 (4.96 GiB) | `commandlist`, `kernelslist`, `kernelslist.g`, `stats.csv` |
| stencil | `TRACE_5e9aefe64e214679` | DONE | 100 | 3,718,279,168 (3.46 GiB) | 3,717,259,264 (3.46 GiB) | `kernelslist.g`, `stats.csv` |
| kmeans | `TRACE_9ad2f284f8c2a318` | DONE | 3 | 3,551,653,888 (3.31 GiB) | 3,551,625,216 (3.31 GiB) | `commandlist`, `kernelslist`, `kernelslist.g`, `stats.csv` |
| histo | `TRACE_777ae84f37927c4e` | DONE | 80 | 3,211,350,016 (2.99 GiB) | 3,203,883,008 (2.98 GiB) | `kernelslist.g`, `stats.csv` |
| 3MM | `TRACE_cf75342164f0b212` | DONE | 3 | 2,918,154,240 (2.72 GiB) | 2,918,109,184 (2.72 GiB) | `kernelslist.g`, `stats.csv` |
| 3DConvolution | `TRACE_694a568c425385d3` | DONE | 254 | 1,084,080,128 (1.01 GiB) | 1,074,282,496 (1.00 GiB) | `kernelslist.g`, `stats.csv` |

## Totals

- Exact `.traceg` files unlinked: **484**
- Logical bytes unlinked: `30,822,447,511` (**28.71 GiB**)
- Source allocated bytes unlinked: `30,823,653,376` (**28.71 GiB**)
- Controller-window `df` increase: `30,789,111,808` (**28.67 GiB**)
- SSD available before: `11,181,944,832` (10.41 GiB)
- SSD available after final resource snapshot: `41,958,305,792` (**39.08 GiB**)

Every file had a durable per-file INTENT before non-recursive unlink and a matching DONE afterward. All Source directories remain and contain only their frozen non-target control/scientific files. Directory uid/gid/mode/mtime were restored; ctime is not restorable after unlink.

## Archive and protection

All seven genuine164 bundles retained their frozen SOURCE_MANIFEST, COMMIT, range/tree receipts, member set and sizes. Every recovery `RESTORE.sh` entry remains present. Existing full-SHA/COMMIT evidence was reused; no 30 GB body rescan and no full native restore were performed.

Bank Diagnosis, atomic_add_bw, M5 ATAX/MVT, historical packages, SRAD, lavaMD and HybridSort matched their before/after protection snapshots. No unrelated Source, scientific result, registry, reservation, controller, budget, Git object or server109 state was modified.

## Remaining resource pressure

- Current contract-required available space: `92,553,609,216` (86.20 GiB)
- Current contract headroom: `-50,595,303,424` (**-47.12 GiB**)
- Registered native write reservations: `83,896,565,760` (78.13 GiB)
- Basic floor margin after cleanup: `33,301,262,336` (31.01 GiB)

The cleanup restored substantial physical SSD capacity but the full science reservation contract still does not pass. DTC/EP resource owners must reconcile their reservations separately. This Goal did not alter them.

## Durable evidence

- `SECOND_BATCH7_EXACT_RETIREMENT_INTENT_DONE.json`
- `SSD_RECLAIM_ACCOUNTING.json`
- `POST_RESOURCE_STATUS.json`
- `checkpoint/` with execution start, per-asset PRE/whitelist/INTENT/DONE, deterministic per-file journals, final controller and independent post-audit

The publication commit and final remote readback are recorded in `GITHUB_PUBLICATION_RECEIPT.json`. No additional asset cleanup was started.
