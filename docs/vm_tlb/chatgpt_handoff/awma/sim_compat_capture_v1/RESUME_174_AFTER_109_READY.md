# Resume plan — 174-new after node109 producer READY

Do not execute this file until node109 has reached:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

with a transferred READY/hash-closed producer bundle.

The accepted consumer checkpoint to resume from is:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
commit: 25aa29862239a408099639ae9d5f1a0ea4fee1e1
SIM_BASELINE_ID: SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
scope: HASH_BOUND_FIXED_WINDOW_10000
```

At that point create a fresh 174-new worktree/branch and execute the existing current-model consumer Goal, using the producer report as the only new input authority.

Required downstream sequence:

```text
producer READY receipt
-> independent destination rehash
-> exact workload/target identity check
-> actual traceg grammar/parser admission
-> COMPLETE + zero drop/overflow verification
-> stable SIM_INPUT_ID
-> structural trace diagnostics
-> fixed-window 10000-cycle baseline replay
-> at least one bounded repeat/determinism check
-> SIM_RUN_ID
-> normalized VM/TLB/PTW/cache/memory telemetry
-> immutable SIM_EVIDENCE catalog closure
```

Expected final state:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
FIRST_CURRENT_MODEL_BASELINE_SIM_PASS
```

Do not perform TLB/Segment/cache mechanism sweeps in this stage. Do not claim full ROI. Do not numerically calibrate against Native evidence beyond recording exact workload/target identity relation unless a separate Cross-view Calibration Goal is activated.
