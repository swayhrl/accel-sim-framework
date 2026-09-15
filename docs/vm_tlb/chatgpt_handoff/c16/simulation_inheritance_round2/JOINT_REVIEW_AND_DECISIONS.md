# Joint review and decisions

## 1. Combined status

### old174 archaeology V1

Commit: `872423194e393fac9ca85171c77bafa87bde389e`

Accepted facts:

- `/root/share` is host-backed shared storage.
- `/root/data` is host-backed in old174.
- Shared retained assets include historical M4A/M4B/M4C/M4I material.
- Git contains authoritative C12/C13/C14/C15 reports/provenance sufficient to identify many historical runs and hashes.
- C12 Prefill/Decode F0 formal trace/raw identities and historical Framework/Core identities were recovered.

Correction required:

- The Codex was already inside old174 but attempted to SSH to old174 and treated authentication failure as a blocker.
- Therefore `/workspace`, non-shared `/root`, `/tmp`, and overlay-private material were not directly inspected even though they were locally available.
- Previous `MISSING_OR_UNKNOWN` classifications for old-private paths remain conservative and valid, but are not final.

Known targeted private scopes from the V1 pack include:

- `/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN/decode1/*/run.log`
- `/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN/prefill/*/run.log`
- `/workspace/c14-dual-path-micro-runs/*`
- scientifically relevant C12-C15 material under non-shared `/root`
- scientifically relevant C12-C15 material under `/tmp`

### 174-new inventory V1

Commit: `0cc24b1d0d7829a95f9122937bf88dde8d403992`

Accepted facts:

- Git contains C12/C15 code/config/review-pack authority and current simulator-side entrypoints.
- `/root/share/workspace_migrated_20260905/...` exposes historical simulation-like artifacts to 174-new.
- Canonical node164 C16 root exists, but dedicated historical-simulation namespaces are absent.
- Current strong code path is `traceg.xz -> run_m4c_replay.sh -> simulator log -> export_m4c_telemetry.py -> summarize_m4c_runs.py`.
- No `accel-sim.out` exists in the fresh inventory worktree.
- Modern C16 `memory_access.jsonl` / C16WARP1 MREF-sharded binary data are not proven equivalent to `kernelslist.g + .traceg.xz` simulator inputs.

## 2. Scientific-status decisions

Preserve historical statuses; do not promote:

- C12 C5 F0 Prefill/Decode: historical `FORMAL` baseline authority.
- C12 candidate arms: preserve per-row historical qualification; no blanket promotion.
- C13 repaired exact-mode comparisons: `DIAGNOSTIC` unless original pack says otherwise.
- C14 dual-path microdiagnostics: `DIAGNOSTIC`, explicitly not full-ROI equivalent.
- C15 historical material: static/capability evidence only unless an exact dynamic artifact proves more.

Filename words such as `final`, `formal`, or `pass` are not scientific authority by themselves.

## 3. Migration policy

Canonical destination:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Historical simulator snapshot:

`provenance/historical_snapshots/old174_c12_c15_simulation/`

Normalized historical datasets:

`derived/datasets/historical_simulation/`

Shared exchange staging:

`/root/share/c12_c15_inheritance_exchange_v1/`

Rules:

1. Copy, never move.
2. Preserve source relative paths under explicit source-root prefixes.
3. Hash source and destination independently.
4. Do not copy Git source trees as raw scientific authority; record Git path + commit SHA instead.
5. Do not duplicate current C16 formal captures into the historical simulator snapshot.
6. `m4i-m4b-staged-*` remains a current/modern C16 provenance reference, not a C12-C15 historical simulator snapshot payload unless an exact lineage requires a small receipt/reference.
7. Private-only assets are exported only after proving they are not already represented by a byte-identical shared/Git authority.
8. No source deletion is authorized.

## 4. Modern C16 -> simulator boundary

Do not synthesize `.traceg.xz` from current MREF-sharded C16 formal traces merely to make the simulator run.

Current C16 MREF-sharded evidence intentionally lacks whole-kernel cross-MREF temporal order and may lack sufficient byte-width/instruction/synchronization fields for lossless Accel-Sim reconstruction. A fabricated order or invented width/coalescing semantics would be a modeling decision, not a conversion.

Round 2 may:

- prove an existing lossless producer if one exists;
- document the exact missing fields;
- design a future simulator-compatible capture contract;
- run historical traceg anchors.

Round 2 must not:

- claim current C16 sharded traces are full simulator traces;
- invent cross-shard ordering;
- promote modeled reconstruction to historical or C16 `FORMAL` evidence.

## 5. Round-2 completion target

Round 2 succeeds when:

- old174 private scopes are directly inspected and closed;
- every scientifically valuable private-only artifact is either exported with hashes or explicitly proven redundant/missing;
- selected shared historical simulator assets are copied to node164 canonical history with full manifests and destination hashes;
- historical Git authority is referenced by commit/path;
- 174-new has a documented, reproducible simulator build/replay path or a precise environment blocker;
- at least bounded parser/replay anchor checks are attempted on historical traceg evidence;
- current C16-to-simulator limitations are frozen without synthetic overclaim.
