# Unified publication wrapper V2 — commit timeout only

This is a separate candidate. No running source, process, Git state/index/lock, scientific state, or dispatcher was modified. The bridge is byte-identical to V1. V2 privately transforms the same exact old publisher and retains V1's independent index, explicit old/new consumer roots, publication-state trigger, common PUBLOCK, fixed128 scope and all statistical/source checks.

The only executable behavior change from wrapper V1 is `GitPublication.run`: `commit` receives300 seconds; every other Git command retains60 seconds. No automatic retry, rollback, reset, index-lock deletion or remote overwrite is added. All original fail-closed HEAD/remote equality, exact staging, no-overwrite leaf and remote manifest readback checks remain. The original watch loop and error receipts remain unchanged.

## Read-only incident observation

Main reported the first real unified snapshot had38 closed cells and no validation errors, followed by the commit command's60-second timeout. The later read-only `LAST_WATCH_ERROR.json` observation already showed `read-tree` failing on `CLEAN_UNIFIED_BACKGROUND_INDEX.lock` (epoch1794019973.7954524); no successful unified WATCH_STATE advancement was present. The old publisher also showed its separate BACKGROUND_INDEX lock failure. This observation does not establish whether a commit/ref update or push actually completed.

A timeout alone never authorizes re-commit or lock deletion. Before Main arms V2, Main must use the existing serialized publication recovery procedure to confirm whether a Git child/lock is active, preserve the timeout and lock evidence, and compare local HEAD, remote branch, reflog/commit leaf/manifest, and readback receipts. If the intended commit is already local or remote, adopt/finish that exact transaction after verifying its manifest; do not generate a replacement or silently mark it lost. If local/remote diverged, the old validate_head gate intentionally holds for Main reconciliation. The wrapper cannot decide this from an absent WATCH_STATE or timeout alone.

Main alone may switch callers after this reconciliation and D narrow source review. This author did not stop either publisher or issue any Git/process command. The shared publication lock continues to serialize remote writes; existing scientific models are unrelated and remain untouched.
