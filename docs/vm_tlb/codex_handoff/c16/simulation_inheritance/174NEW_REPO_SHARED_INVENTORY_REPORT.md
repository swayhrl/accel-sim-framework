# 174-new repository/shared inventory report

Status: `INVENTORY_COMPLETE_READY_FOR_JOINT_REVIEW`.

Branch/worktree: `hrl/c12-c15-174new-repo-shared-inventory-v1`, based on `103641562b6474e22192c19d1bd81dd12d88ce61`.

Completed a CPU/filesystem-only inventory of `configs/vm_tlb/`, `util/vm_tlb/`, `docs/vm_tlb/`, `/root/share`, `/root/data`, and `/root/share/mnt164/huangrulin/c16_ai_workload/`. Git source/config/review-pack authority is recorded with relevant commit SHAs. The C12 C5 pack is present in Git (22/22 historical PASS under old identities), while current entrypoints and hard-coded path/identity assumptions are separated into REUSE, REVALIDATE, and REFERENCE_ONLY.

`/root/share` is verified on `/dev/md127` ext4 in this container; `/root/data` is empty here. Visible shared trees include migrated M4B/M4C result logs, older L2/cache experiments, and the canonical C16 root. The planned node164 historical-simulation namespaces are absent. No files were copied, moved, deleted, rewritten, or run.

The exact modern-C16 gap is explicit: current C16 JSONL/binary-shard/object-map/fingerprint data is not proven to be simulator `kernelslist.g` + `.traceg.xz`, and no lossless converter or mapping of warp/coalescing/timing/PTW semantics was found. No `accel-sim.out` exists in this fresh worktree. Direct comparison is therefore limited to aligned locality/footprint measures until a hash-bound converter and bounded smoke are authorized.

Review pack: `docs/vm_tlb/review_packs/C12_C15_174NEW_REPO_SHARED_INVENTORY_V1/`. `SHA256SUMS` closes every generated pack/report file. Next action is joint review with old174 archaeology; Round 2 may then authorize selective archive or compatibility smoke.
