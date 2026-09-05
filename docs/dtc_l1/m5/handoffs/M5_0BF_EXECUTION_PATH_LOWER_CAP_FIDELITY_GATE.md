# M5.0BF — execution-path & lower-cap fidelity gate

Status: **PENDING — EXECUTION PROHIBITED UNTIL M5.0B NATURAL-TERMINAL CLOSURE**

## Mandatory ordering

M5.0BF must not execute while any current M5.0B recovery process is live.
Its entry condition is complete M5.0B workload/provenance closure: every live
Base job reaches a natural terminal state and has its source-defined output,
strict parser, registry identity, and final lifecycle/accounting status
recorded.  M5.0C is prohibited until M5.0BF PASS.  This gate changes no live
job, configuration, workload, trace, parser, Core source, or experimental
meaning.

Existing execution-driven M5.0B results remain validation/provenance anchors.
They are not performance results for any subsequently changed formal platform
configuration.

## Q1 — trace-driven DTC equivalence

The audit must prove a source path, not infer compatibility from shared
configuration files.  It must trace one dynamic memory instruction from the
Accel-Sim trace-driven frontend through the modified DTC-L1 Core and establish
whether it reaches the same validated execution-driven mechanism points:

1. LD/ST timing pipeline and coalescing/access-queue point;
2. DTC PIB admission and Tag-bank arbitration;
3. Tag-to-Physical allocation and pending-hit merge/lower-request path;
4. IO/OO retirement and pending-write/scoreboard completion path.

The trace representation must be source-audited for preservation of dynamic
memory-instruction grouping, warp/active mask, memory opcode and space,
per-lane addresses, read/write semantics, and all cache/bypass semantics used
by Paper-10.  Prefer an existing exact, provenance-compatible PolyBench trace.
If none exists, determine whether a fresh NVBit trace can be generated with
the identical executable, input, launch, and cache semantics; do not make one
until this gate is allowed to execute.

Run only the minimum pilot needed to decide one of:

- `TRACE_FORMAL_PATH_VALID`, or
- `EXECUTION_DRIVEN_REQUIRED`.

PTX execution-driven and SASS trace-driven cycle equality is not required and
must not be used as the criterion.  The criterion is mechanism/lifecycle
equivalence plus stable Base/IO/OO causal behavior against the M5.0B anchors.

## Q2 — SM-count fidelity

The audit must resolve the explicit mismatch between the M0 frozen mechanism
model (`8 SM`) and the current M5 SM7-derived configuration (`80 clusters x 1
core = 80 SM`).  It must identify the exact source, commit/config lineage, and
researcher evidence by which 80 SM entered M5.  The inherited SM7 platform
value is not sufficient justification.

The record must quantify the architectural consequences for workload occupancy,
simulator wall time, global lower-request pressure, L2/MC provisioning, and
comparability with the intended DTC mechanism model.  No SM count may be
silently retained or changed solely because it improves a result.

## Q3 — global lower-cap fidelity

The current synthetic global DTC lower-outstanding cap is 256.  M0 paired
`8 SM + 256`, or 32 outstanding requests/SM under a proportional reading;
current M5 pairs `80 SM + 256`, or 3.2 requests/SM.  Existing Base evidence
already shows lower-cap saturation for SpMV, BICG, GEMVER, and 2DConv.  The
gate must decide whether that synthetic global cap prematurely masks intended
L1 PIB/Tag/MSHR bottlenecks.

Use **Base-only** diagnostics.  IO/OO speedup may not select a cap.  The
architecturally motivated candidates are:

| candidate | fidelity question |
| --- | --- |
| `8 SM + cap 256` | preserves the M0 paired model directly |
| `80 SM + cap 2560` | preserves the M0 32-request/SM scale |
| `80 SM + natural/high cap` | lets bounded NoC/L2/DRAM queues become the downstream limit |

A minimal Base-only diagnostic sweep of `256 / 512 / 1024 / 2048 / 2560 /
natural` is permitted only to locate where the synthetic global cap stops being
the dominant Base bottleneck.  For every candidate, record lower outstanding
average/peak, lower-cap-full cycles, PIB-full cycles, MSHR-full cycles, true
Tag/cacheline-allocation stalls, L2/subpartition/DRAM queue pressure, Base
cycles, and IPC.  Select only by architecture/model fidelity and removal of an
unintended artificial bottleneck—not by a larger DTC speedup.

## Required terminal declaration

M5.0BF must declare exactly one terminal outcome:

1. `TRACE_PATH_VALID + PLATFORM_CONFIG_FROZEN`;
2. `EXEC_PATH_REQUIRED + PLATFORM_CONFIG_FROZEN`; or
3. `RESEARCHER_DECISION_REQUIRED`.

If SM count or lower-cap definition changes, preserve current M5.0B
execution-driven evidence but do not silently reuse its performance counters
as formal results under the new platform configuration.  Only an outcome (1)
or (2), with a frozen platform identity and all source/fidelity evidence,
constitutes M5.0BF PASS and permits M5.0C.
