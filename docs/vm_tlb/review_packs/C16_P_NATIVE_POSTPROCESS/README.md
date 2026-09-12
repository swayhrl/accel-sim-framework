# C16-P local native postprocess review pack

Status: `REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL`.

This is the only recommended entry point for C16-P review. It records local,
CPU-only handling of hash-closed Llama S1/S2 Nsight Systems reports. It does
not authorize a Lane-C selector freeze or any cross-lane scientific conclusion:
G's formal native producer checkpoint remains pending.

## Contents

- `S1_S2_SOURCE_MANIFEST.json` identifies the two consumed local raw reports,
  remote-export SQLite files, and all receipts used for the SHA closure check.
- `C_JOIN_KEY_SCHEMA_AUDIT.md` records the Lane-C field/key admission result
  and the closure metadata still requested from G.
- `LOCAL_NSYS_EXPORT_QUALIFICATION.md` records the passing frozen-report
  remote-versus-local SQLite comparison and the approved local CLI.
- `POSTPROCESS_SUMMARY.md` records the complete local S1/S2 population,
  compact outputs, and raw-index manifest hashes.
- `VALIDATION_SUMMARY.md` lists the executed checks; `OPEN_ISSUES.md` records
  the remaining producer, transfer, semantic, and retention boundaries.

## Data boundary

Full launch tables, profiler databases, and raw reports are intentionally not
in Git. The local raw index and postprocess manifest are at:

`/workspace/worktrees/accel-sim-vm-c16-p/artifacts/c16_p_native_postprocess/`

The S1/S2 local-export pipeline contains all 169,920 launches in
`local_exports_provisional/`. It is not a selector input until G's producer
checkpoint is committed, despite the passing local-export qualification.

## Source anchors and validation

- P branch base: `ed434519089efd59b5d0ac42e8bcdcdfeeeefa1f`.
- Raw report closure: each source's `CENSUS_EXPORT_VALIDATION.json` binds the
  report SHA, remote-export SQLite SHA, profile/runner/binding receipt SHAs,
  native identity, CUDA correlation coverage, stream count, and required NVTX
  ranges.
- P validation: full-population preservation, nonempty C key fields, composite
  C unit uniqueness, and `UNKNOWN` operator/layer preservation.

No GPU job, remote command, or G/A/C/H worktree was modified by this lane.
