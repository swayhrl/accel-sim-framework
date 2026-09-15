# CODEX Goal — 174-new canonical historical-simulation inheritance

## Status

Executable Goal. Run on 174-new reached by:

`ssh root@10.208.130.174 -p 2239`

This Goal is CPU/filesystem/build/simulator-smoke only. No GPU workload.

## Inputs

Authoritative inputs:

- Round-2 `JOINT_REVIEW_AND_DECISIONS.md`
- old174 archaeology V1: `872423194e393fac9ca85171c77bafa87bde389e`
- 174-new inventory V1: `0cc24b1d0d7829a95f9122937bf88dde8d403992`
- current Git source/config authorities identified by the inventory pack

Canonical root:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Shared source root:

`/root/share/workspace_migrated_20260905/`

Parallel old174 exchange root:

`/root/share/c12_c15_inheritance_exchange_v1/`

## Objective

Make 174-new the long-term owner of historical C12-C15 TLB/Cache simulation evidence and replay capability without conflating historical simulator data with current C16 formal capture data.

This includes:

1. creating the canonical node164 historical-simulation namespace;
2. copying selected scientifically relevant shared historical assets into it with independent hash closure;
3. consuming private-only exports from old174 if they become available during the Goal;
4. generating normalized experiment-lineage/catalog datasets;
5. reconstructing a reproducible simulator build/replay path where possible;
6. attempting bounded historical parser/replay anchors;
7. freezing the current modern-C16-to-simulator compatibility boundary.

## Phase A — canonical namespace

Create:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c12_c15_simulation/`

Recommended layout:

```text
old174_c12_c15_simulation/
├── manifests/
├── shared_archive/
│   └── root_share/
├── private_export/
│   ├── workspace/
│   ├── root_private/
│   └── tmp/
├── git_authority/
└── receipts/
```

Create normalized dataset root:

`/root/share/mnt164/huangrulin/c16_ai_workload/derived/datasets/historical_simulation/`

Do not place historical simulator payloads into current `captures/raw/`.

## Phase B — migrate shared historical assets

Start from the shared assets proven by V1. At minimum evaluate these exact source trees:

- `/root/share/workspace_migrated_20260905/m4_batch_20260906/m4a-rented-host-pilot`
- `/root/share/workspace_migrated_20260905/m4_batch_20260906/m4c-formal-controls-20260903T220000Z`
- `/root/share/workspace_migrated_20260905/m4_batch_20260906/m4bs-formal-replay-20260903T180000Z`
- `/root/share/workspace_migrated_20260905/results/ep_l2_streaming_reuse`

Treat this separately:

- `/root/share/workspace_migrated_20260905/m4_batch_20260906/m4i-m4b-staged-f96b7ea9-5bdd4b55`

The M4I tree is modern/current C16-related staging/provenance and must not be blindly duplicated into the historical simulator snapshot. Record a reference/receipt if lineage requires it; otherwise leave it in its current authority location.

For each candidate shared tree:

1. determine scientific role and status from Git/review-pack evidence;
2. create a deterministic source tree manifest with relative path, byte size, SHA-256;
3. copy content into `shared_archive/root_share/<relative-source-path>/` preserving relative structure;
4. independently hash destination files/tree;
5. require source/destination equality;
6. write an archive receipt binding source path, destination path, source tree hash, destination tree hash, bytes, file count, scientific status, lineage IDs, and authority documents.

No source deletion.

If an asset is clearly redundant and already byte-identical in node164, record `CANONICAL_ALREADY_PRESENT` rather than recopying.

## Phase C — consume old174 private export

The old174 Goal runs in parallel and may publish:

`/root/share/c12_c15_inheritance_exchange_v1/PRIVATE_EXPORT_READY.json`

Do not block Phase A/B on this receipt.

Near the end of the Goal:

1. check for `PRIVATE_EXPORT_READY.json`;
2. verify its bound manifest/hash files before trusting payload;
3. if `private_only_payload_count > 0`, copy those payloads into canonical `private_export/` preserving the export-relative structure;
4. independently rehash source staging and node164 destination;
5. create destination admission receipts;
6. do not delete the exchange staging or old174 source.

If the receipt is not yet available after all independent work is complete, wait only a bounded interval and finish with `PRIVATE_EXPORT_PENDING`, not an indefinite wait. A later short reconciliation round may consume it.

## Phase D — Git authority index

Do not copy Git source trees as archival payload.

Create immutable authority tables that bind at least:

- repository
- Git path
- commit SHA
- role
- scientific status
- historical/framework/core identity where relevant

Include:

- C12 C5 review pack and provenance matrices;
- C13 repaired exact-mode authority;
- C14 dual-path microdiagnostic authority;
- C15 authority;
- M4B/M4C configs;
- trace manifests;
- registration maps;
- replay/analyzer/post-processing entrypoints.

## Phase E — normalized lineage datasets

Under:

`derived/datasets/historical_simulation/`

produce at least:

- `C12_C15_EXPERIMENT_LINEAGE.tsv`
- `C12_FORMAL_BASELINES.tsv`
- `HISTORICAL_SIMULATION_ASSET_CATALOG.tsv`
- `HISTORICAL_CONFIG_AND_CODE_AUTHORITY.tsv`
- `HISTORICAL_RESULT_STATUS.tsv`

The lineage table must support:

`trace -> config -> Framework/Core/binary -> invocation -> raw output -> derived result -> conclusion`

Unknown fields remain explicit `UNKNOWN`; never infer missing identity from nearby filenames.

## Phase F — reconstruct simulator runtime

Goal: make 174-new capable of future historical-compatible replay, not merely hold files.

Inventory V1 found no `accel-sim.out` in the fresh worktree. Resolve this actively.

### Required attempts

1. Locate any already-built compatible simulator binary in shared/private exported history; record SHA and provenance, but do not assume portability.
2. Locate exact Git commits for historical C12 authority:
   - Framework `d64408a97d76a320a6d49468653d416e33677af8`
   - Core `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
   - historical binary SHA `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
3. In isolated worktrees/build dirs, attempt a documented historical-compatible rebuild if source commits are available.
4. Separately identify the current recommended Core/Framework build path for modern future replay.
5. Record compiler/CUDA/toolchain identity and produced binary SHA.

Do not overwrite normal worktrees or historical binaries.

A rebuilt binary is not the historical binary unless the SHA exactly matches. Otherwise classify it as `REBUILT_COMPATIBILITY_RUNTIME`.

## Phase G — bounded historical replay/parse anchors

Do not rerun the whole C12 matrix.

Use the strongest available historical traceg authority and choose bounded anchors that test the inherited chain.

Minimum target:

- one Decode-side anchor;
- one Prefill-side anchor if practical;
- one telemetry/post-processing smoke.

Preference order:

1. exact historical trace/config + exact historical binary if found and runnable;
2. exact historical trace/config + rebuilt compatibility runtime;
3. trace parser/locality-only smoke if full simulator runtime remains blocked.

Bound runtime per replay attempt; do not allow a multi-hour runaway during this inheritance Goal.

For each attempt record:

- trace/list SHA
- config SHA
- Framework/Core SHA
- binary SHA
- command
- timeout
- return status
- first/terminal simulator evidence
- parsed telemetry counts
- comparison to historical expected values where comparison is semantically valid

Allowed replay classifications:

- `EXACT_HISTORICAL_BINARY_REPLAY_PASS`
- `COMPATIBILITY_REBUILD_REPLAY_PASS`
- `TRACE_PARSER_ONLY_PASS`
- `REPLAY_BLOCKED_ENVIRONMENT`
- `REPLAY_FAIL_RESULT_MISMATCH`

Do not label a bounded/micro replay as reproducing a full-ROI formal result.

## Phase H — modern C16 compatibility decision

Produce:

`SIMULATOR_INPUT_COMPATIBILITY_DECISION.md`

It must explicitly state whether current C16 formal artifacts contain enough information for lossless Accel-Sim `traceg` reconstruction.

Current default is fail-closed: **not proven**.

Audit required fields such as:

- dynamic instruction order within warp/kernel;
- static instruction identity;
- opcode/access kind;
- byte width;
- active mask;
- per-lane addresses;
- warp/CTA identity;
- kernel launch ordering;
- synchronization/control information required by the trace grammar;
- information required for coalescing and simulator memory request generation.

If any required field/order is absent, do not build a fake converter. Instead define a future `SIMULATOR_COMPATIBLE_CAPTURE_CONTRACT` listing exactly what 109 would need to record for future replay.

Existing C16 MREF-sharded evidence remains valid for its scoped offline footprint/object analyses.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C12_C15_174NEW_CANONICAL_INHERITANCE_V2/`

including at least:

- `README.md`
- `MIGRATION_SUMMARY.md`
- `NODE164_ARCHIVE_MANIFEST.tsv`
- `NODE164_ARCHIVE_RECEIPTS.tsv`
- `SOURCE_DESTINATION_HASH_CLOSURE.tsv`
- `PRIVATE_EXPORT_INGEST_STATUS.md`
- `GIT_AUTHORITY_INDEX.tsv`
- `EXPERIMENT_LINEAGE.tsv`
- `SIMULATOR_RUNTIME_RECONSTRUCTION.md`
- `REPLAY_ANCHOR_RESULTS.tsv`
- `SIMULATOR_INPUT_COMPATIBILITY_DECISION.md`
- `FUTURE_SIMULATOR_COMPATIBLE_CAPTURE_CONTRACT.md` if lossless conversion is not possible
- `OPEN_GAPS.md`
- `SHA256SUMS`

Codex report:

`docs/vm_tlb/codex_handoff/c16/simulation_inheritance/174NEW_CANONICAL_INHERITANCE_REPORT.md`

## Acceptance criteria

A strong PASS requires:

- canonical node164 historical namespaces created;
- all selected shared scientific payloads copied and source/destination hash-closed;
- old174 private export ingested if available and valid;
- normalized lineage tables produced;
- Git authority bound by commit/path;
- simulator runtime reconstruction attempted actively, not merely declared missing;
- bounded historical replay/parser anchors executed where technically possible;
- current C16->simulator boundary frozen without invented semantics;
- no source or current formal raw mutated/deleted.

Allowed final statuses:

- `C12_C15_174NEW_INHERITANCE_PASS`
- `C12_C15_174NEW_INHERITANCE_PASS_PRIVATE_EXPORT_PENDING`
- `C12_C15_174NEW_INHERITANCE_PASS_REPLAY_ENVIRONMENT_BLOCKED`
- `C12_C15_174NEW_INHERITANCE_PARTIAL_TRUE_DATA_GAP`

Do not use a missing local `accel-sim.out` as a reason to stop before attempting the documented runtime reconstruction.

## Forbidden

Do not:

- run GPU workloads;
- alter current C16 formal captures;
- synthesize temporal order for MREF shards;
- invent missing access widths/opcodes;
- call a rebuilt binary the historical binary without exact SHA identity;
- rerun the entire C12-C15 experiment matrix;
- delete any source copy;
- modify ChatGPT-owned handoff files.

## STOP

After final review-pack hash closure, commit/push, verify clean worktree, and STOP.
