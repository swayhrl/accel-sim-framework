# Activation note — start node109 only when free

Current state entering this stage:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
consumer-preparation commit: 25aa29862239a408099639ae9d5f1a0ea4fee1e1
SIM_BASELINE_ID: SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
```

Node109 is allowed to remain occupied by unrelated/Native work. This producer stage has no urgency that justifies interrupting another formal capture or GPU task.

When node109 becomes free:

1. fetch this coordination branch;
2. create a fresh worktree/branch;
3. read `CODEX_GOAL_109_SIM_COMPAT_CAPTURE_V1.md` in full;
4. execute it in Goal mode;
5. acquire `/data/c16/locks/c16_gpu_campaign.lock` before any formal GPU capture;
6. stop at `SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS` with a READY/hash-closed bundle transferred through the accepted pipeline.

Do not start a Codex process now merely to wait for the GPU lock. Start the Goal when node109 is actually available.

After producer PASS, do not immediately invent downstream work on node109. The next consumer stage returns to 174-new for independent rehash/admission, `SIM_INPUT_ID`, 10k replay, determinism and Simulation Evidence catalog closure.
