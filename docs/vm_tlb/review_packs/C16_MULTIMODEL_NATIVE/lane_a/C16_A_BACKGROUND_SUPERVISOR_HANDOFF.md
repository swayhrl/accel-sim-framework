# C16 A background asset supervisor handoff

Status: `BACKGROUND_ASSET_SUPERVISION_ACTIVE_NO_AUTO_PACKAGE_PUBLICATION`.

This handoff changes Lane A from an interactive long-running Goal to detached,
operational-only asset supervision.  It does not authorize or perform GPU,
CUDA model load, profiler, NVBit, simulator, SASS, full-ROI, Git package
publication, or a dynamic scientific conclusion.

## Detached worker audit

Snapshot from `2026-09-12T15:38:25Z`, recorded by the local heartbeat.  All
listed processes have `TTY=?` and a session ID distinct from Codex's active
terminal session.

| Role | PID / PPID / SID | Exact command or current asset | State |
| --- | --- | --- | --- |
| Wave-1 AWQ curl | `142955 / 1219985 / 142955` | fixed `Qwen/Qwen2.5-7B-Instruct-AWQ@b25037543…`, shard 1, HTTP/1.1 `--continue-at -` | active, `3,508,404,360 / 3,996,422,976` bytes |
| Wave-2 30B wrapper | `233645 / 1 / 233645` | `c16_qwen3_30b_downloader.py --run` | detached, one-worker 1 MiB/s policy |
| Wave-2 30B curl child | `233651 / 233647 / 233645` | fixed `Qwen/Qwen3-30B-A3B@ad44e777…`, shard 1 | active, `748,212,224 / 3,999,417,504` bytes |
| Wave-1 finalizer | `279286 / 1 / 279286` | `c16_wave1_shard_finalizer.py --watch-seconds 15` | unique detached low-I/O observer |
| Background heartbeat | `280466 / 1 / 280466` | `c16_background_asset_supervisor.py --watch-seconds 60` | detached operational telemetry |

The existing stable AWQ and 30B workers were not stopped, restarted, or
reconfigured.  The finalizer was safely replaced only because the old observer
had a 30-second cycle and could not handle the now-shrunk unresolved set; the
replacement accepts any remaining set and holds a distinct single-instance
lock.  It only observes curl-owned temporary files and performs finalization
after a curl exits.

## Persistent operational paths

All paths below are external runtime state, not scientific review artifacts.

| Purpose | Path |
| --- | --- |
| Runtime root | `/workspace/c16_assets/c16-a/background/` |
| Detached stdout/stderr logs | `/workspace/c16_assets/c16-a/background/logs/` |
| PID files and finalizer lock | `/workspace/c16_assets/c16-a/background/pids/` |
| 60-second heartbeat | `/workspace/c16_assets/c16-a/background/status/C16_A_BACKGROUND_STATUS.json` |
| Per-worker operational state | `/workspace/c16_assets/c16-a/background/status/workers/` |
| Operational ready markers | `/workspace/c16_assets/c16-a/background/receipts/` |

The heartbeat reports real available bytes, current/expected bytes, recent
throughput, last growth timestamps, PID/process details, immutable verified
shard counts, P2/P3 readiness, 30B verified count, and a last-error field. It
is explicitly non-scientific telemetry.  It refreshed at least twice while the
detached daemon was active; the two active transfer rates were approximately
274 KiB/s and 281 KiB/s in successive observations.

## Immutable and recovery boundaries

`P2_READY.json` exists locally because all four raw Qwen2.5-7B shards have
their own immutable size-plus-single-SHA receipts.  It names the pinned
revision and receipt paths only.  It does **not** Git-add, commit, push, or
publish `C16_GPU_PACKAGE_P2`; a later short review Goal must perform that
formal package action. `P3_READY.json` is absent until AWQ shard 1 is likewise
closed.  The 30B ready marker is absent until all sixteen shards close and is
not eligible for P0--P3 or RTX3090 execution.

`c16_wave1_resume_supervisor.py` is a future-only, guarded entrypoint.  It
refuses a live curl or an immutable receipt, requires explicit operator
confirmation after about fifteen minutes of no growth and confirmed
process/connection failure, then resumes the same partial path with the fixed
revision and HTTP/1.1 range continuation.  It has bounded transport retry and
delegates exact-size plus one whole-file SHA-256 closure to the unique
finalizer.  The background daemon itself never starts/stops/retries downloads
and never executes Git operations.

## Static acceptance

- `py_compile` passed for the background supervisor, guarded resume entrypoint,
  and revised finalizer.
- The finalizer's single-instance detached process is alive at 15-second
  cadence; no second finalizer was left running.
- The 30B downloader is alive and remains one low-priority worker. Its original
  85 GiB start gate was recorded at launch; its 15 GiB pause gate remains in
  force. No concurrency increase is permitted before both P2 and P3 close.
- Exiting the interactive Goal does not signal any listed download or
  supervision process.
