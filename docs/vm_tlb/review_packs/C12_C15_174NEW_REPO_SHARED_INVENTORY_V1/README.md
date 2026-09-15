# C12–C15 / 174-new repository and shared-storage inventory (V1)

Inventory-only closeout from Framework HEAD `103641562b6474e22192c19d1bd81dd12d88ce61` on branch `hrl/c12-c15-174new-repo-shared-inventory-v1` (2026-09-15 UTC). No GPU workload, simulator replay, migration, or mutation of C16 formal raw was performed.

Recommended reading order: this file, `CURRENT_SIMULATION_ENTRYPOINTS.md`, `C16_TO_SIMULATOR_INTERFACE_GAPS.md`, then the TSV evidence tables.

## Authority boundary

Git is authoritative for source/config/analyzer identity. The C12 C5 pack is available in Git and records 22/22 PASS arms, but its run paths and historical identities are legacy (`/workspace/...`, Core `57bb71...`, Framework anchor `d64408...`); this is documented evidence, not a claim of current executability. Shared-storage observations are filesystem facts only and carry `FORMAL`, `DIAGNOSTIC`, or `UNKNOWN` labels only where the referenced documents support them.

## Findings

- C12/C15 simulation code, configs, analyzers, review packs, and provenance ledgers are already present in Git (`GIT_AUTHORITY_ONLY`); do not copy source trees as authority.
- Exact tracked-path discovery found 35 paths containing `C12`, 48 containing `C15`, and no paths containing `C13` or `C14`; absence is recorded, not treated as proof that old174-private material never existed.
- `/root/share` is mounted from `/dev/md127` (ext4) and is therefore the verified shared-visible root in this container. `/root/data` exists but is empty in this view. This proves visibility here, not historical old-container exclusivity.
- Visible historical simulation-like outputs are under `/root/share/workspace_migrated_20260905` (including C12/M4B/M4C result trees) and are not yet represented in the canonical node164 historical-simulation namespace.
- Canonical node164 C16 root is visible and structured; `provenance/historical_snapshots/old174_c12_c15_simulation` and `derived/datasets/historical_simulation` are currently absent.
- Modern C16 derived data is JSONL/binary-shard/object-map based. The current Accel-Sim launcher requires a `kernelslist.g` whose entries name `.traceg.xz` files, plus SM86 base/trace configs. No evidence shows a direct converter from C16 `memory_access.jsonl` or `mref_*.bin` to simulator `traceg.xz` in this inventory.
- No executable `accel-sim.out` is present in this fresh worktree, so even the modern launcher is **not runnable today** without a separately built compatible Core runtime.

## Classification policy

Visibility classes follow `SOURCE_CLASSIFICATION_AND_MIGRATION_POLICY.md`; scientific status is never inferred from filenames. `GIT_AUTHORITY_ONLY` means retain path and commit SHA. Shared filesystem artifacts are read-only observations and remain `SHARED_VISIBLE_UNCHANGED` unless provenance is insufficient (`MISSING_OR_UNKNOWN`).

## Round-2 recommendations

Revalidate the old174 pack's exact Core/framework/config/trace chain, prove shared visibility from both endpoints, and create a dedicated node164 historical namespace only for artifacts that are not already shared and are scientifically valuable. Before any replay, adapt or replace hard-coded `/workspace` paths and establish a converter whose output schema is proven against the simulator parser.
