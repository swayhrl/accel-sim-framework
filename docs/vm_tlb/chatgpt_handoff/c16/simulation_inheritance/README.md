# C12–C15 Simulation Analysis Inheritance

Owner: ChatGPT coordination.

This handoff coordinates the complete inheritance of historical TLB/Cache simulation assets from the old 174 Docker (`root@10.208.130.174 -p 2233`) into the new 174 analysis Docker (`root@10.208.130.174 -p 2239`).

The two containers are known to share host-backed `/root/share` and `/root/data`, but their private container layers (`/workspace`, other `/root/*`, `/tmp`, etc.) must not be assumed shared.

The current C16/Qwen0 capture and analysis mainline is independent and must not be interrupted by this archaeology task.

## Read order

1. `CURRENT_STATE.md`
2. `SOURCE_CLASSIFICATION_AND_MIGRATION_POLICY.md`
3. `DISCUSSION_REFERENCE.md`
4. the role-specific Codex goal:
   - old174: `CODEX_OLD174_SOURCE_ARCHAEOLOGY.md`
   - 174-new: `CODEX_174NEW_REPO_AND_SHARED_INVENTORY.md`
5. `ACCEPTANCE_AND_MERGE_PLAN.md`

## Round-1 objective

Run two CPU-only, read-mostly inventories in parallel:

- **old174** reconstructs filesystem/provenance authority for C12–C15 historical simulation runs and identifies anything that exists only in the old container-private layer;
- **174-new** inventories the Git/code/config/review-pack authority and the currently visible shared filesystem roots.

Round 1 does **not** perform bulk migration or rerun simulations.

## Round-2 objective

After ChatGPT jointly reviews both inventories, 174-new will become the single long-term owner of the historical simulation analysis lineage. Only then will irreplaceable old-container-only artifacts be copied (copy-not-move), validated, cataloged on node164, and a bounded set of historical anchors replayed for compatibility.

## Canonical long-term storage

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Historical simulation material, when admitted later, should live under a dedicated historical namespace rather than current C16 formal captures.
