# Window A — concurrent resource gate while C3 is still running

Goal: `A_CONCURRENT_RESOURCE_GATE`

Status: `PREPARED / READ-ONLY-TO-A / MAY_AUTHORIZE_BC_CANARIES`.

This gate exists because Window A remains the formal priority workload, while the host may have enough spare CPU/memory capacity to run one tightly bounded Window B canary and one tightly bounded Window C compile canary concurrently.

It does **not** authorize any change to the running C3 simulator. The active C3 process must not be stopped, restarted, reprioritized, affinity-pinned, cgroup-moved, rebuilt, or reconfigured.

## Current concurrency budget

While C3 remains nonterminal, a successful gate authorizes at most:

- Window B: **1** simulator worker, only the prepared one-kernel E01 canary pair, sequentially;
- Window C: **1** low-priority focused compile/test process, no full simulator build;
- Window A: the existing C3 simulator remains untouched and highest priority.

No other new simulator-heavy workload is authorized by this gate.

## Gate implementation

Use:

`util/vm_tlb/issue_a_concurrent_resource_attestation.sh`

The script reads only `/proc`, CPU topology/frequency state, and the named A PID. It writes only a small attestation file; it does not modify any process or scheduler state.

Recommended invocation from the independent progress-review worktree:

```bash
bash util/vm_tlb/issue_a_concurrent_resource_attestation.sh \
  --pid <CURRENT_C3_SIMULATOR_PID> \
  --output /workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt
```

A PASS file begins exactly with:

`A_CONCURRENT_RESOURCE_GATE_PASS`

and expires automatically after 20 minutes by default. B/C must reject stale attestations.

## Resource policy

The gate is intentionally conservative. Over a short sampling window it requires:

- A simulator process still exists and accumulates CPU time;
- `MemAvailable >= max(64 GiB, MemTotal/4)`;
- `SwapFree >= max(512 MiB, SwapTotal/4)`;
- zero swap-in and zero swap-out delta during the sample;
- whole-host CPU idle fraction >= 8%;
- whole-host iowait <= 5%;
- the A process remains runnable/sleeping normally and is not dead/stopped/zombie.

A failed gate removes any stale concurrent PASS attestation and authorizes nothing.

## Canary protection rule

B/C concurrent work must run with lower host priority than A, use explicit idle physical cores that do not share A's SMT sibling, and stop at their prepared canary boundaries.

After B/C canaries begin, Window A should continue read-only monitoring. Compare A's block-launch progress over roughly 10–15 minutes against its recent baseline. Report `A_CONCURRENT_CANARY_HEALTH = DEGRADED` if any of these occur:

- A CPU utilization becomes persistently abnormal;
- block-launch throughput falls materially (roughly >20% versus the recent local baseline without an obvious kernel-phase explanation);
- swap-in/out begins;
- iowait becomes persistently elevated;
- A PID/state/supervisor becomes unhealthy.

Do not modify A to compensate. If degradation is observed, instruct B/C to stop/defer their own canary work.

## Evidence boundary

This attestation means only: "the host had spare resources for the bounded concurrent canaries at issuance time." It does not mean C3 is terminal, does not create `A_TERMINAL_CONFIRMED`, and must never unlock B9 full execution or C10-B full regression/replay.

The formal terminal gate remains `docs/vm_tlb/codex_handoff/A_C3_TERMINAL_TO_C4_FINALIZE.md`.