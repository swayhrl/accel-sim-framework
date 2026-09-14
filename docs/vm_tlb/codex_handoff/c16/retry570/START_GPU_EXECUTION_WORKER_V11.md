# START — Recovery V3 GPU Execution Worker V11

Use this in the existing Goal window that owns the active branch/GPU scientific execution.

Read:

```text
C16_QWEN0_ADDRESS_ZERO_ROOT_CAUSE_HANDOFF.md
C16_RECOVERY_V3_DUAL_WINDOW_COORDINATION.md
```

Keep all existing Recovery-V3 scope/storage/runtime contracts unless superseded here.

Immediate priorities:

1. preserve/SHA-close the latest Qwen0 corrected-tracer canary;
2. do D1 offline trace forensics before launching another same-target GPU run;
3. if an identical repro is already running, let only that one finish; otherwise defer repro until D1/D2 classification;
4. run at most the bounded D2/D3 GPU diagnostics required by the root-cause tree;
5. while diagnosis is CPU-side, schedule another already-ready GPU row instead of idling the RTX3090;
6. maintain Worker-G ownership of active Git worktree/commits;
7. honor the shared GPU/remote-I/O exclusion protocol.

Do not allow AWQ or another asset transfer to act as a global barrier.

Do not broaden Qwen0 target/filter/shape merely to obtain nonzero records.

Do not begin R6 for Qwen0 until R5 address-bearing requirements genuinely pass.
