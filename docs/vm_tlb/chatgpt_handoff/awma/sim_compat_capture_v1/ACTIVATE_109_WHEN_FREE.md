# Activation note — node109 is now free; activate producer Goal

Status: **ACTIVE**.

The user has confirmed node109 is available for this work. The previous wait condition is satisfied.

Accepted upstream checkpoint:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
consumer-preparation commit: 25aa29862239a408099639ae9d5f1a0ea4fee1e1
SIM_BASELINE_ID: SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
```

Open a fresh Codex window on node109 and use:

```text
CODEX_ACTIVATION_109_NOW.md
```

as the operator entrypoint. It will direct Codex to the full producer Goal and contracts.

Even though node109 is reported free, Codex must still inspect and acquire:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

before any formal GPU capture. Never bypass a live lock.

Preferred stage stop:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

with a READY/hash-closed bundle transferred through the accepted pipeline.

After producer PASS, stop node109 work. The next stage returns to 174-new for independent rehash/admission, `SIM_INPUT_ID`, 10k replay, determinism and Simulation Evidence closure. Do not start simulator mechanism sweeps on node109.
