# Cooperative progress during trace initialization

Issue: DTC-TELEMETRY-INIT-20261025. Scope: Framework repair branch only.

State: OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED -> CPU-REGRESSED.
Scientific replay remains a separate new-generation validation owned by DTC-MAIN.

## Problem and repair

The native scalarProd-DH and lavamd-CM/CH attempts stopped after six successful
progress packets. Their first cycle continued bulk-loading CTA text traces, but
the only SIMULATE observation was after cycle() returned. Existing 30-second
producer freshness therefore expired during useful same-thread parsing work.
The historical raw, sequence, resource and process evidence is preserved in
the DTC-MAIN failure diagnosis package. CPU parsing versus input/pipe/scheduling
cost cannot be uniquely reconstructed from the historical syscall trace.

The Framework now registers its producer in a simulation-thread-local scoped
slot while constructing/initializing the framework and running its simulation
loop. CTA initialization and text/tracez parser work boundaries call a
cooperative heartbeat. Hot loops check the clock only once per 1024 work units;
CTA/subchunk boundaries also check directly. Packets retain the original
10-second cadence, PID generation, input/ROI, phase epoch and sequence rules.
They reuse the last coherent retired-instruction observation. Parsing never
increments completed. Background prefetch threads have no slot and cannot
keep a blocked simulation thread artificially fresh.

No Core pointer is added to the producer and no simulation/cache/timing state
is written. Same-value fresh records do not reset the existing 600-second
semantic-retirement deadline. A successfully emitted terminal prevents later
cooperative heartbeats. Scope unwinding does not fabricate a NATURAL terminal.
Socket errors still disable the producer with no reconnect or replay.

The inherited 1,048,576-record ceiling remains finite; this branch does not
change the receiver, freshness timeout, retirement timeout or wall deadline.
Historical 8192-record myocyte failures remain invalid and preserved.

## Regression

The standalone CPU test compiles the actual repaired text parser and tracez
reader, not a simulator. It checks:

- 8196 exact authenticated records and a normal terminal;
- text, xz text and a two-subchunk tracez stream including prefetch;
- ordinary list/stride/delta and TMA list/delta memory address decoding;
- opt-out produces identical decoded values and no telemetry;
- thread-local isolation, nested scope unwind and ERROR/NATURAL ordering;
- a real 33-second decoding window with a constant completed value and fresh
  packets, followed by the original receiver's stale/failure latch checks;
- the unchanged RuntimePolicyB still stops at 600 seconds with fresh but
  same-valued semantic progress (synthetic time and stub resource domains).

Run with explicit deployment receiver/policy paths:

    python3 gpu-simulator/tests/test_ag7_cooperative_progress.py \
      --build-dir /isolated/cpu-tests --cuda-include /qualified/cuda/include \
      --receiver-source /qualified/telemetry_receiver_cap1m.py \
      --runtime-policy-source /qualified/runtime_policy_wall90_v1.py

Detailed CPU/build results are external artifacts and are not committed as
raw logs, binaries, datasets or build trees. The final executable must be built
after the clean source commit, with the independently repaired Core library.

## Deliberate limits

The observer runs only at real cooperative work boundaries. A single blocking
system call, allocation, decompression call or prefetch join that itself lasts
over 30 seconds still fails closed. This repair does not introduce external
timer heartbeats, make a stalled process appear to retire instructions, or
guarantee completion for an input with no semantic retirement for 600 seconds.
No old result is relabeled or automatically retried by this source change.
