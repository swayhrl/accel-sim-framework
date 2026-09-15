# C16 Qwen3-30B-A3B archive — current state before execution

## Purpose

This file is the bootstrap state for a **fresh Codex window**. Do not assume access to any previous chat/worktree state beyond what is written here and what is present in Git / the filesystem.

## Accepted C16 storage state

The previous model-asset consolidation is closed.

Accepted cleanup authority:

```text
commit: a3510070ff051f62f15d78d48c86c87741432b16
status: OLD174_MODEL_PAYLOAD_CLEANUP_PASS
```

Long-term C16 root on node164:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Existing canonical models live under:

```text
assets/models/<model>/<revision>/
```

Historical evidence lives under:

```text
provenance/historical_snapshots/
```

Current Pipeline V1 scientific data lives under its own `captures/`, `catalog/`, and `derived/` namespaces. **This asset task must not write model files into Pipeline capture/catalog namespaces.**

## New completed download to archive

Treat the whole source root as discovery/inventory scope:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

Known model-specific subtree:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/metadata/
Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Do **not** assume that only this subtree contains authoritative receipts/state/logs. Discover the source layout first.

Exact intended model identity:

```text
model_id: Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Historical download progress expected 16 weight shards and used approximately `61,066,575,648` bytes as the total weight-shard payload anchor. This number is a reconciliation clue, not a substitute for the actual index/files/receipts.

## Destination

Canonical reusable model asset:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Historical download provenance:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/
qwen3_30b_a3b_download_v1/
```

## Scientific boundary for this round

This round is **asset closure only**.

It must not:

- run the model;
- create prospective token/input bindings;
- quantize or alter weights;
- start layer streaming/replay;
- use NSYS/NCU/NVBit;
- mutate node109 model/capture state;
- delete the completed source download.

The execution plan for later RTX4080 layer-streaming / exact-layer-replay characterization is already stored separately under:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
QWEN3_30B_A3B_4080_TRACE_PLAN_V1.md
```

Do not execute that plan in this asset round.

## Storage/copy lessons already learned

The node164 path is reached through the accepted SSHFS-backed C16 data root. Use content-oriented copy semantics; do not depend on preserving UID/GID/mode as scientific identity.

For large payload transfer, preserve resumability and verify bytes independently after copy. The scientific asset identity is the deterministic file set + sizes + SHA256 + exact model revision, not Unix ownership metadata.

Single-writer promotion is sufficient for this asset round. Never overwrite an existing canonical final path; if a final destination unexpectedly exists, inspect/compare and fail closed rather than replacing it.
