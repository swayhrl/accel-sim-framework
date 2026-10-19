# GLOBAL_COLD_CENSUS — bounded read-only source result

Observation UTC 2026-10-19T11:41:36.186990+00:00; client timezone Asia/Shanghai (UTC+8). Base `dc2f32bf28c85fded91beead53a2a3fd650de202`; remote coordination HEAD checked exactly. Independent execution branch `hrl/old174-global-cold-census-exec-20261019-v1`.

## Fast measured leaderboard

GiB = 2^30 B. These are disjoint source-visible allocation roots, Git contents excluded. **One protected RTL root is a lower bound**, so this is an observed leaderboard, not proof of complete host ranking. All TOP20 roots have zero multiple-hardlink entries. No release bytes are inferred from these sizes.

| Rank | Canonical source root | Allocated GiB | Current protection/status |
|---|---|---:|---|
| 1 | `/workspace/worktrees/accel-sim-decoupled-l2` | 245.489 | ACTIVE_KEEP |
| 2 | `/workspace/c16_assets` | 30.291 | ACTIVE_KEEP |
| 3 | `/workspace/m5-trace-immutable` | 27.460 | PROTECTED_DTC_L1 |
| 4 | `/workspace/c16_exchange` | 22.567 | HOLD |
| 5 | `/workspace/worktrees/accel-sim-c2p-cache` | 16.453 | ACTIVE_KEEP |
| 6 | `/workspace/repos/gpu-l2-cache-verilog` | ≥ 15.554 | PROTECTED_EP_L2 |
| 7 | `/workspace/worktrees/accel-sim-tls-cache` | 9.957 | ACTIVE_KEEP |
| 8 | `/workspace/ep_l2_potential20261017_lane5_results` | 6.382 | PROTECTED_EP_L2 |
| 9 | `/workspace/worktrees/gpu-l2-v3-signoff-46bf3a69` | 5.236 | PROTECTED_EP_L2 |
| 10 | `/workspace/worktrees/accel-sim-c2p-addr-observe` | 5.126 | ACTIVE_KEEP |
| 11 | `/workspace/worktrees/accel-sim-vm-c16-p` | 4.694 | HOLD |
| 12 | `/workspace/worktrees/accel-sim-l2-resource-char` | 4.049 | HOLD |
| 13 | `/workspace/builds/ep_l2_ft20261016_lane3_v1` | 3.504 | PROTECTED_EP_L2 |
| 14 | `/workspace/worktrees/gpu-l2-v3-signoff-463600cb` | 3.189 | PROTECTED_EP_L2 |
| 15 | `/workspace/dtc-service-closure-174-v1` | 2.514 | PROTECTED_DTC_L1 |
| 16 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906` | 2.290 | PROTECTED_DTC_L1 |
| 17 | `/workspace/m4c-c4-early-export-20260907-v1` | 2.242 | HOLD |
| 18 | `/workspace/vm-m4b-speculative` | 2.016 | HOLD |
| 19 | `/workspace/build/ep-l2-potential20261017-lane1-all-data-r1` | 1.976 | PROTECTED_EP_L2 |
| 20 | `/workspace/build/ep-l2-potential20261017-lane1-p2-r1` | 1.767 | PROTECTED_EP_L2 |

## Nonoverlapping project attribution

Project rows partition the measured roots, separating common trace children from their parent. Attributed bytes are not sole scientific ownership or authorized reclaim. AWMA/AI-ARCH rows with no discovered separate roots mean **unknown**, not absent or zero occupancy across aliases. Full EP-L2/DTC-L1 protection applies regardless of these provisional project labels.

| Project/accounting bucket | Observed GiB | Protected/shared GiB | Direct PID keep GiB |
|---|---:|---:|---:|
| Shared_protected_trace_dependencies | 226.932 | 226.932 | 0.000 |
| EP-L2 | 66.837 | 66.837 | 0.000 |
| C16 | 59.665 | 0.000 | 30.307 |
| DTC-L1 | 54.605 | 54.605 | 0.000 |
| Other_legacy_GPU_and_unresolved | 30.446 | 0.000 | 0.955 |
| C2P | 27.744 | 0.000 | 21.579 |
| Legacy_VM_GPU | 16.472 | 0.000 | 0.000 |
| Other_tmp_scratch | 15.809 | 0.000 | 0.000 |
| TLS | 11.823 | 0.000 | 9.957 |
| Local_software_environment | 2.021 | 0.000 | 0.000 |
| Mixed_TLS_C2P_ACTIVE | 1.393 | 0.000 | 1.393 |
| Bench_Traces | 1.298 | 0.000 | 0.000 |
| M2D | 0.466 | 0.000 | 0.000 |
| Local_software_cache | 0.082 | 0.000 | 0.000 |
| AWMA | UNKNOWN | 0.000 | 0.000 |
| AI-ARCH | UNKNOWN | 0.000 | 0.000 |

Total observed overlay scope: 553,614,499,840 B (515.594 GiB); 2,307,744 metadata entries, 35,236 disjoint roots. Primary scan stopped at 240s; optimized continuation visited only previously unvisited roots and took 4.5s. No scan loop remains. `/root/data` sidecar is 0.515 GiB, accounted separately; no free-space sum and no cross-view net-reclaim claim.

## C2P complete bounded breakdown and exclusions

All 436 discovered C2P-named roots are itemized, including small `/tmp` sources/tests/figures, the four C2P worktrees, their top-level roles and individual `hw_run` entries: **29,790,167,040 B = 27.744 GiB identified named scope**, excluding Git contents. Whole-project exclusive total remains **UNKNOWN** until unnamed roots/aliases, shared and future consumers are reconciled. This is explicitly not a releasable amount.

- Main Framework C2P cache worktree: 16.453 GiB; address-observe worktree: 5.126 GiB. They include code, builds, PPA tools, run products and analysis. Existing C2P repair/analysis jobs and stopped child jobs retain reader claims.
- Exact V9 build C2P1 current 424,570,880 B; C2P2 424,419,328 B; total 848,990,208 B = 0.790684 GiB, unchanged from historical allocation. Both build roots and 410/410 file metadata identities match V9. Their parent source trees contain additional bytes and are not V9 full-project archives.
- Mixed TLS/C2P root current 1,495,924,736 B (1.393188 GiB), above the historical 1,495,752,704 B by 172,032 B (active logs/metadata can change). **Excluded** from exclusive C2P. Original offloader PID1920891/start_ticks408369842 remains alive with this exact local root; its old 80GiB gate is not cleanup permission.
- C2P polybench trace parent is shared/protected by DTC-L1's exact `FAST64_PAYLOAD_MANIFEST.tsv`, including GEMM and other workloads; **excluded** from exclusive C2P. Historical four TLS shared trace roots (7,340,679,168 B) are nested inputs, not additive C2P bytes.
- M2D remains separate: exact V9 build 410,275,840 B, 205/205 current file metadata match; its whole parent is larger, and no release is authorized.

## High-value proof findings

The six P2/P3 C16 model shards alone occupy 20,802,138,112 B (19.374 GiB). Historical local materialization SHA records equal source immutable receipt SHAs, both files currently exist with matching expected lengths and different inodes/nlink1. No payload was rehashed. This establishes a strong **duplicate review candidate**, not fresh content identity or 164/native recovery. Parent outbound packages also retain code and provenance, so no whole-package release is proposed.

C16 has a live asset telemetry owner PID280466; tracked C16-P native source manifests still depend on `returned` profiles. AWMA/AI-ARCH dormancy was not assumed. Large common roots `decoupled-l2-pretraces`, `decoupled-l2-extract`, C2P polybench traces and M5 immutable traces are protected by checked EP-L2/DTC-L1 manifests. Size is not eligibility.

## Resource admission and exact boundary

Workspace f_bavail: start 13,819,568,128 B (12.870 GiB), end 13,702,602,752 B (12.762 GiB). Share available 44,375,302,144 B (41.328 GiB). See JSON for f_bfree distinction, RAM/cgroup and IO pressure. Concurrent free-space changes are **not audit reclaim**. Source remains below 16GiB TLS admission and below unrelated-project normal 48GiB workspace floor; TLS's narrow exception cannot authorize C16 work.

**Actions:** zero science unlink, zero payload archive/copy, zero TLS retransfers/restarts, zero registry/lease changes. Original B0010 and TLS Goals remain BLOCKED; B0001–B0009 remain closed ranges, not full P9 release proof. No sender, receiver or persistent watcher started.

**Next safe action:** source-owner C16 package closure and planned-reader review for the exact six model-shard paths in `SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json`, retaining code/provenance and source master models. Then draft one grouped model-only COPY_ONLY/recovery/release contract with realistic normal resource gates. No deletion approval is requested in this census. Current authorized/guaranteed immediate reclaim is **0 B**.

## Limits and handoff

Single scanner at nice19/ionice3; finite roots, deadlines and checkpoints; no `du /`, symlink following, Git object crawl, remote Share/164 payload read, or source payload hashes. The protected RTL repo exceeded 35s Python and 20s targeted du budgets, so retain its observed lower bound and do not recrawl. Scheduler probes are local only; historical references and mtime do not prove no future consumers. st_blocks is not an overlay-upper or reflink/net-df proof. Reports are SHA indexed, committed, pushed, fetched and independently read back from the remote execution commit; final verification is recorded by `REMOTE_READBACK_RECEIPT.json` in the isolated runtime directory and by the published follow-up receipt. This stage ends after publication; further archive or release is outside this Goal.
