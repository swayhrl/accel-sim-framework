# M5.0BF — execution-path & lower-cap fidelity gate

Status: **AUTHORIZED IN PARALLEL — M5.0C JOIN-GATED**

## Mandatory ordering

M5.0B and M5.0BF are authorized to proceed in parallel.  M5.0BF uses an
isolated Core/Framework worktree, build, and output namespace; it must not
stop, restart, signal, reconfigure, duplicate, or otherwise disturb the five
live M5.0B execution-driven jobs.  M5.0BF may complete its fidelity decision
before those jobs reach natural terminal states.

M5.0C is the join barrier and is prohibited until **both** conditions hold:

1. M5.0B has complete workload/provenance closure: every live Base job has a
   natural terminal state and source-defined output, strict parser, registry
   identity, and final lifecycle/accounting status; and
2. M5.0BF has an accepted terminal outcome with frozen formal execution-path
   and platform configuration.

This gate changes no live M5.0B job, configuration, workload, parser, Core
source, or experimental meaning.

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
the identical executable, input, launch, and cache semantics.

Run only the minimum pilot needed to decide one of:

- `TRACE_FORMAL_PATH_VALID`, or
- `EXECUTION_DRIVEN_REQUIRED`.

PTX execution-driven and SASS trace-driven cycle equality is not required and
must not be used as the criterion.  The criterion is mechanism/lifecycle
equivalence plus stable Base/IO/OO causal behavior against the M5.0B anchors.

### Q1 formal execution-policy closeout

If Q1 concludes `TRACE_FORMAL_PATH_VALID`, trace-driven Accel-Sim becomes the
**default formal performance execution path** for the remaining M5 campaign:
Paper-10 Base/IO/OO formal measurements, M5.1--M5.5 sweeps, and later
Extended-20 E2/E3 members whose workload satisfies the trace semantic
contract.  The current execution-driven M1--M4 and M5.0B evidence remains the
mechanism/correctness validation anchor, source/provenance reference, and
causal cross-check; it need not be rerun execution-driven solely because later
formal performance measurement uses the trace path.

If a particular workload has a semantic requirement the trace path cannot
faithfully preserve—such as unsupported ordering, atomic, or cache-control
behavior—classify that workload explicitly and use execution-driven only for
that workload.  Do not revert the whole campaign by implication.  If Q1
instead concludes `EXECUTION_DRIVEN_REQUIRED`, retain execution-driven as the
formal path and record the exact trace-semantic requirement that failed.

`TRACE_FORMAL_PATH_VALID` closeout must freeze the trace format/version,
tracer/NVBit source SHA, trace workload/input identity, trace parser/frontend
SHA, Core SHA containing the DTC path, formal platform/config SHA, and proof
that Base/IO/OO all traverse the same DTC timing mechanism.

### Q1 decision — current Paper-10 formal campaign

**`EXECUTION_DRIVEN_REQUIRED`** is selected for the current Paper-10 formal
campaign. The static audit proves that a semantically admissible trace would
enter the same DTC timing mechanism, but no local trace satisfies the required
exact source, input, launch-ABI, and cache-semantics identity: the archived
BICG, GESUMMV, and 2DConv candidates have source/ABI mismatches, and the
archived SpMV candidate has a different matrix/input. A fresh NVBit trace
cannot be generated on this host because no NVBit-capable GPU device is
visible. This is a provenance/semantic-contract failure for these formal
workloads, not a claim that the trace frontend is defective.

Accordingly, the current formal Paper-10 campaign retains execution-driven
mode. The rejected-trace BICG smoke remains nonformal transport/lifecycle
evidence only and cannot reverse this decision. If an exact frozen trace is
later supplied, it may be evaluated for that workload under the Base/IO/OO
contract without relabelling the current campaign or any existing result.

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

### Q3 observability contract

The historical DTC terminal report contained only lower-credit peak and final
drain state; it could not establish the required time-weighted lower
outstanding average.  The isolated BF Core therefore adds two
statistics-only, per-simulated-core-cycle counters:
`DTC_L1_lower_outstanding_cycle_sum` and
`DTC_L1_lower_outstanding_sample_cycles`.  Their quotient is the Q3 lower
outstanding average.  The sample is taken after that cycle's core-pipeline
admission/completion transitions.  It neither changes lower-credit admission,
lower-credit release, timing, scheduling, nor any existing assertion.

Q3 also exports the source-defined conventional-L1
`LINE_ALLOC_FAIL` aggregate as
`DTC_L1_baseline_l1d_line_allocation_fail_events`.  It means all candidate
cache lines were reserved, and is the required true Tag/cacheline-allocation
signal.  It remains distinct from `DTC_L1_primary_stall_tag_bank` (DTC
Tag-bank arbitration), baseline MSHR entry/merge failures, and miss-queue or
native downstream pressure.

The Q3 extractor records both `DTC_L1_lower_cap_full_events` and the existing
source-emitted `DTC_L1_nonexclusive_lower_cap_full_cycles` under distinct JSON
keys.  The latter is the required lower-cap-full-cycle field for comparison;
the former remains an admission-attempt diagnostic and must not silently be
substituted for it.

The compact extractor output is schema `dtc_l1_m5_0bf_q3_v2`.  Version 2
requires the lower-occupancy sum/sample pair, distinct lower-cap event and
cycle fields, and the source-defined `LINE_ALLOC_FAIL` aggregate; no older Q3
JSON may be compared or relabelled as a complete-metrics result.

Any Q3 run launched before this instrumentation is available remains a
non-decisive pre-instrumentation diagnostic.  It may establish that a
candidate executes and has no immediate hard failure, but it cannot freeze a
cap or platform because the required average is absent.  A separately built,
isolated Core and repeat of the minimum Base-only candidates is required
before Q3 closeout; this has no effect on the live M5.0B jobs.

The instrumented Core was CMake Release-built in its own disposable namespace
`/tmp/dtc-l1-m5-0bf-metrics-build` from Core
`3f23c4aa198ef6acfa1354a473a7fd151d05af3e`; target `cudart` compiled
successfully.  The resulting `libcudart.so` SHA-256 is
`d39481291fe688f18a3867ecec0c21b8ee3d8a800d351848a0b075b67cca7a9c`.
No target named `dtc_l1_m1_common_test` or
`dtc_l1_completion_accounting_test` exists in this CMake configuration and
CTest declares zero tests, so validation is a clean production-runtime build
plus the existing static/strict-parser checks—not an invented unit-test PASS.

After a pre-launch host audit found 512 logical CPUs, approximately 107 GiB
MemAvailable, `vmstat` `si=0`/`so=0`, and no active swap I/O, the complete-
metrics BICG Base-only minimum was launched in isolated, no-timeout sessions:

| candidate | runner PID | simulator PID | output directory |
| --- | ---: | ---: | --- |
| 80 SM + cap 256 | 3547071 | 3547120 | `/tmp/dtc-l1-m5-0bf-q3-valid-bicg-80sm-cap256-20260905` (natural terminal; checked) |
| 80 SM + cap 10240 | 3547072 | 3547122 | `/tmp/dtc-l1-m5-0bf-q3-valid-bicg-80sm-cap10240-20260905` (natural terminal; checked) |
| 80 SM + cap 1048576 | 3547073 | 3547124 | `/tmp/dtc-l1-m5-0bf-q3-valid-bicg-80sm-cap1048576-20260905` (natural terminal; checked) |

At the first 56-second read-only sample, all three simulators were live with
approximately one CPU each, growing simulator cycle/instruction counters, and
no assertion/fatal/deadlock/output-mismatch signature.  The run identities
pin BICG binary SHA-256 `db1cc9246ee97389b32396d3b20294a3c8a89139067cabcda93ec87d0ed1f84b`,
PTX SHA-256 `8a0f2ab72a5ac679037e17cfd2f748e7e53ce119c03648948fe8771058c98485`,
the reviewed per-candidate config hashes, and the instrumented runtime hash
above.  They are live diagnostics, not completed results or a frozen Q3
decision; the five M5.0B processes remain untouched.

### BICG terminal checkpoint — Q3 representative, still non-decisive overall

All three BICG candidates naturally reached
`GPGPU-Sim: *** exit detected ***`, and each source-defined BICG checker
reports zero CPU/GPU comparison mismatches.  Strict summaries close PIB
admit/retire at `3145984/3145984`, final PIB/lower outstanding at zero, and
lower acquire/release at `19186845/19186845` (cap 256) or
`19187022/19187022` (cap 10240/high).

| candidate | cycles / instructions / IPC | lower avg / peak / full cycles | PIB / MSHR / true allocation | native downstream pressure | compact Q3 evidence |
| --- | --- | --- | --- | --- | --- |
| 80 SM + cap 256 | `51041920` / `184803328` / `3.6206186601` | `74.1975749737` / `256` / `77761587` | `30536937` / `0` / `895862507` | chiplet `0`, L2-DRAM `0`, DRAMfull `0` | `generated/m5_0bf_q3_bicg_80sm_cap256.json` |
| 80 SM + cap 10240 | `50083030` / `184803328` / `3.6899390472` | `75.7330360204` / `512` / `0` | `13522489` / `0` / `893775912` | chiplet `0`, L2-DRAM `0`, DRAMfull `0` | `generated/m5_0bf_q3_bicg_80sm_cap10240.json` |
| 80 SM + cap 1048576 | `50083030` / `184803328` / `3.6899390472` | `75.7330360204` / `512` / `0` | `13522489` / `0` / `893775912` | chiplet `0`, L2-DRAM `0`, DRAMfull `0` | `generated/m5_0bf_q3_bicg_80sm_cap1048576.json` |

Thus the researcher-proportional `10240` row is identical to the explicit
high-cap row for every required BICG Base-only metric and has no synthetic
lower-cap-full event/cycle.  In contrast, cap `256` is full for `77761587`
cycles, doubles BICG PIB-full cycles, and has no compensating native queue
pressure; it is an artificial global lower-credit bottleneck rather than the
intended natural downstream limit.  This is positive evidence that cap
`10240` is not the dominant artificial limiter for this representative and
that `80 SM + 256` must remain diagnostic-only.  It does **not** yet freeze
the formal platform: all three GESUMMV controls remain live, and no Q3
diagnostic is added to the formal result registry.

The second required representative is the known non-lower-cap-saturated
control, source-equivalent GESUMMV.  Its same three complete-metrics,
Base-only candidates were launched after the same no-swap host audit:

| candidate | runner PID | simulator PID | output directory |
| --- | ---: | ---: | --- |
| 80 SM + cap 256 | 3551706 | 3551756 | `/tmp/dtc-l1-m5-0bf-q3-valid-gesummv-80sm-cap256-20260905` |
| 80 SM + cap 10240 | 3551707 | 3551758 | `/tmp/dtc-l1-m5-0bf-q3-valid-gesummv-80sm-cap10240-20260905` |
| 80 SM + cap 1048576 | 3551708 | 3551755 | `/tmp/dtc-l1-m5-0bf-q3-valid-gesummv-80sm-cap1048576-20260905` |

Each identity pins binary SHA-256
`32da3ab10c6b0cdb0a7e9af569899e51ebb302a19602f9d37e3377469ab6447e`,
the exact PTX artifact SHA-256
`484a2f76bcd03e27ff8cdcd7920a9ea2f36a755116e07ed057302432a1f936f2`
used by the already strict-validated M5.0B GESUMMV run and registry, the
reviewed config hash, and runtime SHA-256 above.  These fresh processes are
live diagnostics only; output checking (`verify_m5_polybench_output.py gesu`),
strict parsing, Q3 extraction, and Base-only comparison remain mandatory at
natural terminal state.

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
