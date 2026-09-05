# M5.0B live review checkpoint

Status: **SUPERSEDED CAP-256 CLOSEOUT — NOT A FORMAL RESULT OR M5.0B PASS**
Snapshot: `2026-09-05T22:44:19+08:00`

## 2026-09-05 researcher-authorized cap-256 closeout

The natural-terminal wait condition is withdrawn. After final read-only
topology/identity/progress snapshots, graceful `SIGTERM` was sent only to the
five run-owned PGIDs. All five process groups exited within 30 seconds; no
SIGKILL, restart, deletion, reconfiguration, or signal to an observer was
used. Output directories/logs/counters remain preserved. Every row is exactly
**`RESEARCHER_ABORTED_SUPERSEDED_CAP256`** — not FAIL, DEADLOCK, TIMEOUT, or
PASS — because its 80-SM/cap-256 configuration is superseded by the frozen
80-SM/cap-10240 formal candidate.

| workload | runner / simulator / PGID / SID | final wall / CPU | final progress evidence | retained directory |
| --- | --- | --- | --- | --- |
| ATAX | `3572154 / 3572276 / 3572144 / 3572132` | `1-12:53:17 / 1-12:49:43` | perf `748146232`, mtime `23:05:27+08:00` | `/tmp/dtc-l1-m5-0b-ratio0-base-atax-recovery24h-20260904` |
| MVT | `3572157 / 3572277 / 3572147 / 3572132` | `1-12:53:17 / 1-12:54:26` | perf `782407276`, mtime `23:05:27+08:00` | `/tmp/dtc-l1-m5-0b-ratio0-base-mvt-recovery24h-20260904` |
| SYR2K | `3572155 / 3572296 / 3572149 / 3572132` | `1-12:53:17 / 1-12:46:11` | perf `202045667`, mtime `23:05:26+08:00` | `/tmp/dtc-l1-m5-0b-ratio0-base-syr2k-recovery24h-20260904` |
| 2MM | `3572159 / 3572310 / 3572150 / 3572132` | `1-12:53:17 / 1-12:57:47` | perf `307693405`, mtime `23:05:26+08:00` | `/tmp/dtc-l1-m5-0b-ratio0-base-twomm-recovery24h-20260904` |
| SYRK | `3572158 / 3572311 / 3572148 / 3572132` | `1-12:53:17 / 1-12:56:37` | perf `216775883`, mtime `23:05:25+08:00` | `/tmp/dtc-l1-m5-0b-ratio0-base-syrk-recovery24h-20260904` |

All five final logs printed `-gpgpu_dtc_l1_lower_outstanding_cap 256`; this
establishes the obsolete identity. Final host snapshot after closure retained
about `144 GiB` MemAvailable and `86 GiB` free `/tmp`; no artifact cleanup was
performed. M5.0BT exact trace capture, not these partial runs, now gates
M5.0C.

## HISTORICAL SNAPSHOT — SUPERSEDED

The remainder is a pre-termination snapshot retained only for provenance/debug.
It is not current authority and must never instruct a future Goal to wait for,
restart, or close these five cap-256 runs.

This was a read-only review checkpoint. It did not restart, signal,
reconfigure, duplicate, or relabel any live simulator; it contains no raw log,
binary, trace, build tree, or perf-counter payload.

## Branch and gate state

| item | identity / state |
| --- | --- |
| active Framework branch | `hrl/decoupled-l1-exp-m5-v0@ddc362c1715c4b26eb9d4ee9ff0234a36248ead2` |
| M5.0BF evidence branch | `hrl/decoupled-l1-exp-m5-bf-v0@87b40479be3e30880695d2afe267cb17ea5a0fd0` |
| M5.0BF outcome | `EXEC_PATH_REQUIRED + PLATFORM_CONFIG_FROZEN`; formal 80-SM, cap-10240 policy is integrated in the active Framework branch |
| M5.0B validated Base members | canonical SpMV, BICG, GEMVER, GESUMMV, 2DConv (`5 / 10`) |
| M5.0B live members | ATAX, MVT, SYR2K, 2MM, SYRK (`5 / 10`) |
| M5.0C gate | closed: M5.0BF is PASS, but all five M5.0B live members still require natural-terminal correctness/provenance/lifecycle closure |

The source/build/config/result identities for the validated five are immutable
in `M5_0B_PROGRESS_CHECKPOINT.md`,
`M5_0B_RATIO0_BASE_BATCH.md`, and `m5/generated/result_registry.json`.
Existing M5.0B measurements retain their validation/provenance role and are
not silently relabelled as formal results under the subsequently frozen
80-SM/cap-10240 platform.

## Protected live jobs

All five have the frozen ratio-zero `PAPER_BASE` config SHA-256
`993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366` and
runtime SHA-256
`f115144d6009bab4af6d8ab0d86b69e54e8449a4c76a3809561571d32075a453`.
`perf mtime/bytes` is active-output evidence only; no current terminal
cycle/instruction counter is claimed from it.

| workload | PID | output directory | elapsed / accumulated CPU | state / RSS KiB | perf mtime / bytes |
| --- | ---: | --- | --- | --- | --- |
| ATAX | 3572276 | `/tmp/dtc-l1-m5-0b-ratio0-base-atax-recovery24h-20260904` | `1-12:32:10` / `1-12:28:38` | `Sl` / `843776` | `22:44:19.544+08:00` / `729321845` |
| MVT | 3572277 | `/tmp/dtc-l1-m5-0b-ratio0-base-mvt-recovery24h-20260904` | `1-12:32:10` / `1-12:33:21` | `Sl` / `757760` | `22:44:19.319+08:00` / `764332601` |
| SYR2K | 3572296 | `/tmp/dtc-l1-m5-0b-ratio0-base-syr2k-recovery24h-20260904` | `1-12:32:10` / `1-12:25:06` | `Sl` / `1531904` | `22:44:19.158+08:00` / `199115587` |
| 2MM | 3572310 | `/tmp/dtc-l1-m5-0b-ratio0-base-twomm-recovery24h-20260904` | `1-12:32:10` / `1-12:36:42` | `Sl` / `1376256` | `22:44:19.675+08:00` / `303550171` |
| SYRK | 3572311 | `/tmp/dtc-l1-m5-0b-ratio0-base-syrk-recovery24h-20260904` | `1-12:32:10` / `1-12:35:32` | `Sl` / `1286144` | `22:44:18.199+08:00` / `213833158` |

At the snapshot, every PID existed and each perf-counter file had just been
updated.  A scan of each live `m5_run.log` found no natural-exit marker,
simulator fatal, assertion failure, deadlock report, or output-mismatch
signature.  These facts classify the rows as **SLOW_BUT_PROGRESSING**, not as
results or as evidence of simulator-level terminal accounting.

## Host envelope and preservation

The host had 512 logical CPUs, `MemAvailable=144600496 KiB`, no active swap
I/O (`vmstat si=0`, `so=0`), and `/tmp` free space `88 GiB`.  The historical
2-GiB swap allocation remains almost full, so this checkpoint admits no new
simulator job despite current memory headroom.  The three pre-existing,
untracked active-Framework generated artifacts remain deliberately unmodified
and uncommitted:

- `m5_r5dv3_spmv_io_ratio0.json`
- `m5_r5dv3_spmv_oo_ratio0.json`
- `m5_result_registry.jsonl`

## Exact resume condition

For each natural terminal, first verify immutable run identity and normal
simulator exit; then run the source-defined output checker, error scan, strict
parser, final PIB/lower/inflight accounting-drain validation, and result
registry update.  Only after all five rows pass this sequence may M5.0B PASS,
`M5_0B_WORKLOADS.md` be finalized, and M5.0C begin.  Extended E2 remains
prohibited until M5.2; no Extended or replacement Paper job was launched.
