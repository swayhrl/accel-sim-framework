# Window B — concurrent E01 canary while A C3 is nonterminal

Goal: `B10_CONCURRENT_E01_CANARY`

Status: `PREPARED / EXECUTION_ALLOWED_ONLY_WITH_FRESH_A_CONCURRENT_GATE`.

This is **not** full B9 execution. It authorizes only the smallest useful B runtime canary while Window A's formal C3 remains active and healthy.

## Authoritative inputs

- Framework branch: `hrl/vm-spec-farm-v0`
- B9 execution-preflight HEAD: `b9119d4dfe0f8c04f432caa2b7974c3ccfc38152`
- B simulator binary SHA-256: `2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915`
- B9 review pack remains the command/config/observable authority.

## External gate

While A is nonterminal, execution requires a fresh file:

`/workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt`

whose first line is exactly:

`A_CONCURRENT_RESOURCE_GATE_PASS`

and whose `expires_epoch` has not passed.

This concurrent attestation does **not** authorize E02-E10 or full B9 execution. `A_TERMINAL_CONFIRMED` remains required for the normal post-terminal B9 executor.

## Scope

Run only E01's two one-kernel decode smoke arms, sequentially:

1. `E01-generic`
2. `E01-pwc32`

Effective B concurrency is exactly 1. Stop after both arms or on the first failure/resource deferral.

Do not run E02-E10, B1 resume, full ROI, trace mining, or any other worker.

## CPU placement

Before starting, perform a read-only 5–10 second per-CPU/topology audit. Choose one logical CPU whose physical core is genuinely idle and whose SMT sibling is also idle. It must not be the A CPU or any sibling listed in the A attestation.

Pass that CPU explicitly to:

`util/vm_tlb/run_b10_concurrent_e01_canary.sh`

The canary runs itself at lower host priority (`nice +10`, low-priority best-effort I/O) and pins only the B child process to that selected CPU. Never alter A affinity/priority/cgroup.

## Resource policy

The runner rechecks before each arm:

- A PID still exists and accumulates CPU time;
- concurrent attestation is still fresh;
- `MemAvailable >= max(64 GiB, MemTotal/4)`;
- `SwapFree >= max(512 MiB, SwapTotal/4)`;
- no swap-in/out over the sample;
- host idle CPU >= 8%;
- iowait <= 5%.

Any failure is `RESOURCE_DEFERRED`; do not work around it.

## Result boundary

These two one-kernel results remain `SPECULATIVE_DIAGNOSTIC`. They may test H2/H5 and validate the new concurrency policy, but they are not full-ROI evidence and cannot be pooled numerically with Window A.

After E01 completes, STOP and report:

- chosen CPU and its sibling;
- attestation issued/expires epoch;
- pre/post resource snapshots;
- E01 generic and PWC32 exit status;
- cycles/IPC and required B9 translation observables;
- A PID still healthy;
- no E02-E10 started.

Window A should independently observe its own block-launch throughput for roughly 10–15 minutes after the canary begins. Do not self-authorize expansion from B.