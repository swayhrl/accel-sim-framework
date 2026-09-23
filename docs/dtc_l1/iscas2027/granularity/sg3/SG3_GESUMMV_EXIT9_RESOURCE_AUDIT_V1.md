# SG3 GESUMMV exit -9 resource audit (V1)

This is a local operational audit, not a scientific result or a causal claim.

The preserved SG3 GESUMMV A1 IO and OO attempts terminated with status `-9`
at `2026-09-22T15:52:34Z` and `2026-09-22T16:01:16Z`. Both have empty
stderr and incomplete stdout, so neither produces a valid simulation result.
The supervisor log places both terminals in the expanded-concurrency window;
six BICG IO A2 jobs had been launched at `15:16:19Z` through `15:16:24Z`.

The accessible cgroup `memory.events` snapshot after the incident reported
`max=7298`, `oom=0`, and `oom_kill=16`. This is resource-pressure evidence,
but it is cumulative and has no per-PID/timestamp binding. Kernel-ring access
was denied and the queried kernel journal yielded no matching PID/event record.
Therefore exit `-9` is **not** attributed to OOM or to any simulator mechanism.

Disposition: preserve the immutable FAIL attempts; issue only fresh-UUID
retries; cap heavy GESUMMV simulator concurrency at two across SG1/SG3/SG5;
strict-validate every retry immediately on terminal. This changes neither
Core/runtime/config/trace identity nor the scientific contract.
