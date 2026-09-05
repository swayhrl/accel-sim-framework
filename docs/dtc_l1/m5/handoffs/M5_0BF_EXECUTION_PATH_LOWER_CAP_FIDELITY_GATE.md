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

The original thesis platform is the **2-SM Unified-Cache GPGPU**.  It is the
source of the lower-credit scaling anchor; the earlier M0 `8 SM` mechanism
abstraction must not be used to derive that ratio.  The formal Accel-Sim
reproduction is explicitly allowed to use a modern larger platform: V100/SM7
style `80 SM` is the primary candidate and `64 SM` is the platform-size
sensitivity candidate.

The audit must identify the exact source, commit/config lineage, and researcher
evidence by which the current SM7-derived `80 clusters x 1 core = 80 SM` value
entered M5.  The inherited SM7 platform value alone is not sufficient
justification to freeze it.

The record must quantify the architectural consequences for workload occupancy,
simulator wall time, global lower-request pressure, L2/MC provisioning, and
comparability with the intended DTC mechanism model.  No SM count may be
silently retained or changed solely because it improves a result.

## Q3 — global lower-cap fidelity

The researcher-confirmed scaling rule is **256 aggregate lower credits at 2
SM**, or **128 credits/SM**.  It is not the superseded `8 SM + 256`
interpretation.  Consequently, the current `80 SM + cap 256` combination
provides only 3.2 credits/SM and is `CURRENT_INVALID_SUSPECT`, suitable only as
a diagnostic control.  Existing Base evidence already shows lower-cap
saturation for SpMV, BICG, GEMVER, and 2DConv.  The gate must decide whether
that synthetic global cap prematurely masks intended L1 PIB/Tag/MSHR
bottlenecks.

The platform/scaling nomenclature is fixed for this gate:

| term | definition |
| --- | --- |
| `THESIS_PLATFORM` | 2-SM original Unified-Cache GPGPU |
| `RESEARCHER_SCALING_RULE` | 256 aggregate credits at 2 SM = 128 credits/SM, linearly scaled |
| `FORMAL_ACCELSIM_PLATFORM_CANDIDATES` | 80 SM primary V100/SM7-style; 64 SM secondary sensitivity |
| `CURRENT_INVALID_SUSPECT` | 80 SM + cap 256 inherited synthetic behavior |

Use **Base-only** diagnostics.  IO/OO speedup may not select a cap.  The
architecturally motivated candidates are:

| candidate | fidelity question |
| --- | --- |
| `80 SM + cap 256` | current inherited synthetic-cap behavior; diagnostic only |
| `80 SM + cap 10240` | primary formal candidate; preserves 128 credits/SM scaling |
| `80 SM + natural/high cap` | tests whether bounded native NoC/L2/DRAM queues become the downstream limit first |
| `64 SM + cap 8192` | platform-size sensitivity; preserves 128 credits/SM scaling |
| `2 SM + cap 256` | thesis-platform scaling anchor, not a restriction on formal Accel-Sim size |

A minimal Base-only sweep may include intermediate caps only to locate where
the synthetic global cap stops being the dominant Base bottleneck; it must at
minimum compare `80 SM + 256`, `80 SM + 10240`, and `80 SM + natural/high`,
with `64 SM + 8192` if platform-size sensitivity is needed.  `2560` is not a
proportional 80-SM candidate and must not be presented as one.  For every
candidate, record lower outstanding average/peak, lower-cap-full cycles,
PIB-full cycles, MSHR-full cycles, true Tag/cacheline-allocation stalls,
L2/subpartition/DRAM queue pressure, Base cycles, and IPC.  Select only by
architecture/model fidelity, Base-only structural-stall behavior, absence of a
premature synthetic mask on PIB/MSHR/Tag-cacheline bottlenecks, and interaction
with real bounded NoC/L2/DRAM queues—not by a larger DTC speedup.

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
