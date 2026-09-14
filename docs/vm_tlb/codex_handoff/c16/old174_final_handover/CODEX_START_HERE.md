# Codex Start Here — Old174 Final Handover V0

Current branch:

```text
hrl/c16-old174-final-handover-to-2239-v0
```

Read completely before doing any work:

```text
docs/vm_tlb/codex_handoff/c16/old174_final_handover/HANDOFF.md
```

Execute the handoff exactly once as the final continuous C16 AI-workload closeout on old174.

Primary objective:

> Produce the complete `C16_OLD174_FINAL_HANDOVER_TO_2239` review pack that inventories old174 model/input/runtime/trace/script/storage authority, classifies historical scientific value, and tells 174-new / 109 / 164 exactly what remains to preserve or migrate.

Start by verifying:

```text
git branch --show-current
git rev-parse HEAD
git status --short
git worktree list
```

Then inspect the existing accepted authorities before scanning the filesystem:

```text
494ccc0f5e6be3bba71d35a58c8c61a60b61988a  adopted input authority V1
4b5c2bb79b9e2e79bed8bef10365bf34be6f6cdd  V2A historical frozen-input recovery result
649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9  RTX3090 closeout inventory
b75f26674a09705659e770ab2134351414aa3c93  RTX4080 R5 clean authority
```

Important source roots include at least:

```text
/root/share/c16_recovery_v3
/workspace/c16_exchange
```

Do not assume these are the only roots; discover other C16-relevant old174 roots in a bounded way and record them.

Required output:

```text
docs/vm_tlb/review_packs/C16_OLD174_FINAL_HANDOVER_TO_2239/
```

with the exact required files defined by `HANDOFF.md`.

Hard requirements:

```text
NO GPU/CUDA/Llama/NVBit/NCU/NSYS execution.
NO tokenizer.
NO token regeneration.
NO bulk data transfer.
NO delete/move/rename/compress of existing evidence.
NO historical authority fabrication.
NO change to RTX3090/RTX4080 R5/adopted-input scientific boundaries.
NO unrelated decouple-L1/L2 changes.
NO secrets in Git.
```

Use existing receipts and the accepted 3090 inventory rather than needlessly rehashing tens of GiB. For uncertain items, record `UNKNOWN` / `OPEN_ISSUE`; do not guess.

The final decision is only:

```text
OLD174_HANDOVER_COMPLETE
```

or

```text
OLD174_HANDOVER_BLOCKED
```

A historical gap should block takeover only if it materially prevents future 109 capture, 174-new ingest/analysis, or 164 archive. Do not block merely because an obsolete historical file cannot be recovered when its scientific limitation is already accurately recorded.

After generating and validating the review pack:

1. inspect `git diff`;
2. confirm no pre-existing scientific evidence was changed;
3. generate/verify review-pack `SHA256SUMS`;
4. commit;
5. push;
6. stop;
7. report the exact items required by HANDOFF section 13.

Do not start the new 109→174-new→164 pipeline from old174 after this step.
