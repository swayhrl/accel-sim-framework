# C16 node109 GPU serialization policy

Ownership: ChatGPT

Multiple Codex windows may prepare work in parallel, but node109 has one RTX4080 and formal/diagnostic GPU work must never overlap unless an experiment explicitly studies concurrency.

## Shared lock

Use:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Before any model load, native timing, NSYS, NCU or NVBit execution:

1. create `/data/c16/locks` if absent;
2. acquire the shared lock with `flock`;
3. while holding the lock, verify there is no unrelated GPU compute process;
4. perform the bounded GPU action;
5. release the lock immediately after the action.

Suggested pattern:

```bash
mkdir -p /data/c16/locks
flock -w 7200 /data/c16/locks/c16_gpu_campaign.lock bash -lc '
  nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
  # bounded GPU action
'
```

A process observed from the current bounded action is allowed. An unrelated C16 or user GPU process is a fail-closed boundary; do not kill it automatically.

CPU-only asset/hash/script work may continue outside the lock.

## Measurement isolation

Do not overlap:

- native timing with another model/profile run;
- NSYS with NCU or NVBit;
- NCU with NVBit;
- NVBit with another model load/capture;
- bulk model/data transfer with a formal timing/profile measurement when avoidable.

Diagnostic rehearsal output must never be promoted to FORMAL merely because the lock was held.