# START — Recovery V3 Transfer / Local Prep Worker V11

Use this in a second Codex window dedicated to non-GPU pipeline work.

Read:

```text
C16_RECOVERY_V3_DUAL_WINDOW_COORDINATION.md
```

This worker is a transfer/local-prep worker only. It does not own scientific GPU execution or the active Git worktree.

Immediate work:

1. continue/resume exact-asset uploads such as AWQ only when remote I/O is allowed by Worker G;
2. continue local-only preparation for Qwen3-8B, DeepSeek-V2-Lite and other in-scope rows;
3. copy back completed raw/profiler payloads after Worker G closes measurement;
4. verify remote/local bytes + SHA and maintain immutable bulk receipts under `/root/share/c16_recovery_v3`;
5. never start model/GPU/nsys/NVBit execution;
6. never mutate/commit Worker G's active Git worktree;
7. do not touch the excluded user-managed Qwen3-30B-A3B tree.

Remote heavy I/O must use the shared exclusion protocol and yield priority to ready GPU jobs.

Local-only download/hash/metadata work may run continuously while GPU measurements execute.
