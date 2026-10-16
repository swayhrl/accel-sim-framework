# Storage-Ops status: COPY_GATE_BLOCKED

- Run: `20261016_storageops_01`; audit 2026-10-16T12:14:26.371876+00:00 through 2026-10-16T12:14:27.703773+00:00 (UTC).
- Frozen Goal: `543a88d63f899ccfa4f6c569245496d6deb8fdf2`. Execution branch: `hrl/ops-174new-164-archive-exec-v1`.
- Executor: SSH `hrl-174-new`, root on `huangrulin-sshfs-174`, mount namespace `mnt:[4026535153]`.
- Execution checkout is independent at `D:/repo/storage-ops-174new-164-exec-v1`; no shared source Git refs, worktrees, lane registry, or scientific results were written.
- PRECHECK executed. COPY / VERIFY / CLEANUP: **NOT_RUN**. Transfer manifest has zero data rows.
- Source objects copied/deleted: **0 / 0**. Ops-released Lane5 workspace bytes: **0**.
- Lane5 actual `/workspace` is absent in this SSH namespace. Its device/quota relation to all visible candidates is unproven.
- Strict SSH to historical `admin-wcx@10.208.130.164` failed authentication (exit 255). Authenticated identity, remote data device and authorized archive root remain unknown.
- The observed `mnt164` mount is `fuse.sshfs`; this fact alone does not establish an authorized archive root. It was never traversed, copied into, or used as transit.
- This run has **not recovered build capacity**. The 48 GiB floor and all lane resource limits remain unchanged. Lane5 independent remeasurement is null.

Next: obtain the exact usable 164 SSH identity/port/archive root/fingerprint and a read-only route or independent mount/df/stat snapshot for Lane5 `/workspace`; then repeat the affected gates before any transfer. No tmp_pack deletion approval is requested yet: the actual source list, backup and verification are unavailable.

See `PRECHECK.md`, `CANDIDATES.csv`, `APPROVAL_REQUIRED.md`, and `SPACE_BEFORE_AFTER.json`. Publication is verified separately in `PUBLICATION.json`; absence of that file means publication has not yet been recorded.
