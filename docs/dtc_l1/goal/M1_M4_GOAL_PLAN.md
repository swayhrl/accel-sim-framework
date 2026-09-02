# DTC-L1 M1-M4 Continuous Goal Plan

Status: **AUTHORIZED**

Purpose: implement a mechanism-faithful DTC-L1 model with strong observability and correctness evidence before final paper-result reproduction.

The goal intentionally separates implementation correctness from performance-target matching. No stage is accepted because a speedup resembles the thesis.

---

# 0. Global execution contract

## 0.1 Variants

Maintain distinguishable runtime/config variants:

- `LEGACY`: clean upstream-equivalent path; project instrumentation/features disabled.
- `PAPER_BASE`: thesis-style baseline with explicit bounded PIB, traditional MSHR, paper Tag-bank timing.
- `PAPER_IO`: whole-line 128B IO-DTC.
- `PAPER_OO`: whole-line 128B OO-DTC.
- `MODERN_OO_SECTOR`: later sector-readiness extension; never substitute it for paper whole-line evidence.

Equivalent names following existing configuration conventions are acceptable, but they must be unambiguous in logs and result CSVs.

## 0.2 Common fairness rules

Across Paper Base / IO / OO, keep unrelated GPU configuration identical. Core assumptions come from `DTC_L1_SPEC.md`.

All major architectural quantities must be configurable; paper values are presets, not magic constants.

## 0.3 Continuous progression

M1 -> M2 -> M3 -> M4 can run in one Goal-mode session. Passing a major stage authorizes the next. Any HARD gate failure blocks later stages.

---

# M1 — Foundation + Paper Baseline + Observability

Objective: establish a neutral integration layer, explicit paper Baseline, deterministic timing/resource abstractions, statistics infrastructure, parser plumbing, and invariants shared by later DTC modes.

## M1.0 Source integration audit

Before functional edits, map the actual built source path end-to-end:

`dynamic memory instruction -> coalescing -> ldst/L1 -> MSHR/miss queue -> NoC/L2 -> fill -> writeback/completion`.

Create `docs/dtc_l1/implementation/SOURCE_INTEGRATION_MAP.md` containing exact files/functions/types for:

- dynamic memory-instruction entrance;
- existing coalesced accesses and sector representation;
- L1D access object/call site;
- Tag Array probe/access;
- MSHR lookup/allocation/merge/full;
- miss queue and lower injection;
- response/fill path;
- dynamic instruction completion/writeback;
- Store path;
- Atomic path;
- Fence/barrier relevant path;
- architectural L1 bypass path;
- configuration parsing;
- statistics printing;
- exact relationship between standalone core and framework `gpu-simulator` source used by builds.

Identify whether an existing request/instruction identifier survives the entire lower-memory round trip. Prefer reuse. If no safe identity exists, document why a DTC identity is required.

M1.0 is audit-only except for persistent audit documentation and minimal test scaffolding needed to prove the source map.

## M1.1 Common memory-instruction context

Introduce a common project-side dynamic memory-instruction lifecycle representation or equivalent state that can support Base/IO/OO without changing upstream coalescing semantics.

Required semantic fields include at least:

- unique dynamic instruction identity;
- SM/warp identity and per-warp memory sequence if needed;
- op type;
- active mask/active-thread count where available;
- coalesced 128B line references;
- per-line sector mask;
- lifecycle state;
- timestamps needed by the latency breakdown.

For DTC, each logical reference is a coalesced **128B cacheline reference**. Multiple current simulator sector accesses belonging to one 128B line must be grouped under one line reference with a sector mask. Do not replace existing GPU coalescing with a new algorithm.

Provide a deterministic directed path that proves 32-lane address patterns generate 1/2/4/32 128B references as expected and that sector masks are preserved.

## M1.2 Paper Baseline PIB/backpressure

Implement the paper Baseline as the existing cache behavior plus an explicit bounded pending-instruction resource, default 8 entries, located after coalescing and before the L1 line-reference processing point established by M1.0.

A live dynamic memory instruction occupies one PIB entry until the baseline simulator's true completion point. When full, admission stops and backpressure reaches the memory-instruction entrance.

Do **not** convert the baseline into IO FIFO retirement. Preserve existing baseline completion ordering; PIB is a capacity/backpressure model.

Paper Baseline MSHR default is 32 entries and uses the current traditional L1 MSHR semantics. Distinguish entry-full and merge-full when the source makes them distinct.

## M1.3 Common paper Tag-bank timing

Implement explicit paper Tag-bank arbitration for Paper Base/IO/OO:

- 4 banks;
- `bank = logical_set_index % 4`;
- max 1 line reference/bank/cycle;
- max 4 Tag references globally/cycle.

Within one dynamic instruction, different-bank line references may be served in parallel. Same-bank references wait for later cycles. Process instruction Tag work deterministically in entrance order so IO Tag-check ordering is preserved. Later pipeline stages may overlap normally.

Every depicted architectural stage is one cycle unless the frozen spec says otherwise. Bounded stage queues backpressure upstream.

## M1.4 Unified stats/assertion framework

Build the common counter/event framework defined in `COUNTER_INVARIANT_SPEC.md` before DTC performance work.

Support configurable verbosity approximately equivalent to:

- level 0: minimal;
- level 1: aggregate formal/diagnostic counters;
- level 2: histograms/latency breakdown;
- level 3: bounded event trace for directed debugging.

Level 3 must be bounded/filterable by SM/warp/instruction/address and must not default to unbounded per-request logging.

Add framework parser/output support early enough that every M1-M4 integrated run emits machine-readable compact summaries.

Create:

- `CONFIG_KNOB_MAP.md`;
- `COUNTER_OUTPUT_MAP.md`.

## M1.5 LEGACY neutrality and Baseline closeout

Retain a `LEGACY` mode that bypasses all paper PIB/Tag timing/DTC behavior and is intended to match the frozen clean upstream build exactly.

Compare clean upstream vs project code in `LEGACY` using the required test set. Required exact fields are listed in the validation matrix.

If exact neutrality fails, M1 fails. Do not continue to DTC implementation.

M1 review pack: `docs/dtc_l1/review_packs/M1_FOUNDATION/`.

---

# M2 — IO-DTC Whole-Line Read Path

Objective: implement the read/load mechanism that removes the traditional DTC-side MSHR bottleneck while preserving finite physical allocation, Tag bandwidth, lower-memory capacity, FIFO completion, and physical-space deadlock behavior.

## M2.1 Logical Tag -> Physical line mapping

Use frozen logical geometry:

- 16KB logical space;
- 128B line;
- 32 sets x 4 ways;
- LRU.

A DTC Tag entry contains at least valid/tag/physical-id/LRU metadata.

Physical pool defaults to 80KB = 640 x 128B lines and is independent of Tag-bank location.

## M2.2 Physical allocator

Implement RR allocation over free physical lines with configurable aggregate width, paper default 4 successful allocations/cycle.

Required behavior:

- multi-line instructions can allocate across multiple cycles;
- allocations already made are retained when a later required line cannot allocate;
- no rollback;
- stalled partially allocated instructions retain their physical resources;
- release is visible to allocation in the same cycle;
- small-space circular dependency/deadlock must emerge naturally.

Do not encode a capacity-specific deadlock rule.

## M2.3 IO hit/miss/no-MSHR behavior

For read line references:

- Valid hit: use mapped physical line; no lower request.
- Pending hit: attach to the existing pending physical allocation; no duplicate lower request.
- New miss: choose logical LRU victim, allocate new physical line, install new Tag->Physical mapping, mark new physical data Pending, and create one lower read request.

The DTC L1 must not use the traditional L1 MSHR as its capacity/merge mechanism. L2/lower-level MSHRs remain unchanged.

## M2.4 Lower request credits and issue bandwidth

Model the frozen paper abstraction:

- per-SM L1 lower issue width = 1 request/cycle;
- global outstanding lower-read capacity across 8 SMs = 256 by default.

A request token is acquired when a new lower request is committed into the bounded lower-request system and released exactly once at response completion. Queued + in-flight requests must never exceed the configured global cap.

If the existing source offers an equivalent bounded structure, Codex may map onto it only after documenting equivalence in the source map/config map.

## M2.5 Physical allocation identity / fill safety

A fill must target the physical allocation originally assigned to the miss, even if the logical Tag has since been evicted/reused.

Use a safe existing request UID if source-backed; otherwise use an explicit allocation identity such as `{phys_id, generation}`.

Required property: a delayed response can never fill a recycled physical line belonging to another allocation. Generation/identity mismatch is a fatal invariant failure in debug validation.

## M2.6 IO FIFO PIB and release

IO default PIB depth = 256 and retire width = 1 instruction/cycle.

Only FIFO head may retire. Head retirement requires all referenced data ready.

On logical Tag replacement, the victim's old physical line is retained as a release dependency instead of being immediately reused. Release it at the specified IO instruction-completion point. Same-cycle release visibility applies.

IO does not require OO Ref Count or OO Merge Mask.

## M2.7 IO deadlock watchdog

Implement a detector, not a recovery mechanism.

When configured no-progress threshold is reached with live work, emit a compact state dump including:

- PIB occupancy/head identity/state;
- free/allocated physical count;
- partially allocated instructions and lines held;
- pending lower requests and outstanding credits;
- last progress-event cycle.

Directed undersized-pool tests may classify this as `EXPECTED_RESOURCE_DEADLOCK`. Default 80KB occurrence is a HARD failure.

## M2.8 IO observability

Add IO-specific physical allocation, pending-hit, duplicate-after-Tag-eviction, partial-allocation, and HOL counters defined in the counter spec.

M2 review pack: `docs/dtc_l1/review_packs/M2_IO_READ/`.

---

# M3 — OO-DTC + Ref Count + Merge + Sector Extension

Objective: implement correct out-of-order ready retirement and active physical-line lifetime management, validate whole-line paper mode first, then add the modern sector-readiness extension.

## M3.1 Random-access PIB / ready selection

OO default PIB depth = 128 and retire width = 1 instruction/cycle.

Any eligible ready entry may retire; use deterministic `oldest_ready` as the default selection policy unless frozen source evidence mandates another policy. Keep the policy configurable if practical.

OO may bypass older unready entries, but must obey later ordering constraints added for Store/Atomic/Fence in M4.

## M3.2 Ref Count and Tag visibility

Frozen Ref Count granularity:

> one coalesced 128B cacheline reference held by a live PIB instruction contributes one reference to the physical 128B line.

Valid hit, Pending hit, and New miss each create the appropriate line reference and increment Ref Count once for that coalesced line reference. Retirement/completion releases that reference exactly once.

Physical lifetime rule:

`reclaimable = (tag_valid == 0) && (ref_count == 0)`.

Logical Tag replacement clears the old physical line's `tag_valid`; it does not free the line while references remain.

Use the paper-compatible default Ref Count width of 13 bits, but parameterize it.

## M3.3 Shadow Ref checker

In directed/debug mode, independently recompute expected per-physical-line reference counts from all live OO PIB entries and compare against modeled Ref Count every cycle or at every relevant state transition.

Any mismatch is a HARD failure. Disable or sample this expensive checker for full workloads as needed.

## M3.4 Merge/wakeup

Whole-line paper mode uses pending-data merge/wakeup at 128B line granularity.

Pending hit registers the waiting PIB dependency. Fill wakes every registered dependency exactly once and clears the corresponding merge state.

Protect against PIB-slot reuse with slot generation or an equivalent identity so a delayed fill cannot wake a different instruction that reused the slot.

## M3.5 Active reclamation

If a physical line has `tag_valid=0` and remaining refs, retain it. When its final reference reaches zero, free it immediately with same-cycle allocator visibility.

Track immediate vs deferred reclamation and deferred lifetime.

## M3.6 Whole-line OO closeout before sector work

All whole-line OO directed tests and invariants must pass before implementing sector readiness. Failure blocks sector work.

## M3.7 Modern sector extension

Preserve:

- one 128B logical Tag -> one 128B physical line;
- line-level `tag_valid`;
- line-level Ref Count using the frozen coalesced-128B-reference semantics.

Refine readiness only:

- 4 x 32B sectors;
- per-sector INVALID/PENDING/VALID;
- per-sector OO merge state;
- per-sector pending dependencies in `wait_cnt`.

Example required behavior: if one instruction references S0 valid + S1 pending + S2 invalid within one physical line, line Ref Count contribution is +1 while `wait_cnt` gains 2 pending sector dependencies.

Sector mode is implementation/validation evidence in M3/M4; final performance interpretation is deferred to M5.

## M3.8 IO-vs-OO causal directed validation

Construct long/short latency streams showing:

- IO younger-ready entries blocked behind unready head;
- OO younger-ready entries retire early at max 1/cycle;
- total dynamic operations and returned data semantics remain identical.

M3 review pack: `docs/dtc_l1/review_packs/M3_OO_SECTOR/`.

---

# M4 — Store / Atomic / Fence / Architectural Bypass + Compute Bring-up

Objective: attach non-load memory operations to the DTC instruction lifecycle while preserving current simulator memory semantics, then run real available Chapter-4 compute workloads under Base/IO/OO as diagnostic bring-up.

## M4.0 Source-backed memory-op semantics audit

Before changing Store/Atomic/Fence behavior, create `docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`.

For Load, Store, Atomic, Fence, and architectural bypass, establish from current source:

- whether it enters L1D;
- whether it performs Tag lookup;
- current hit/miss/write-allocate/no-write-allocate/write-through/write-back behavior;
- lower request type;
- whether/when a response returns;
- exact point at which simulator considers the dynamic instruction complete;
- scoreboard/pending-write interaction;
- ordering/fence interaction;
- bypass semantics.

Do not invent a new write policy. If a required behavior remains ambiguous after source audit, STOP.

## M4.1 Store lifecycle

Preserve the current baseline write policy. Integrate Store into the DTC pending-instruction lifecycle so it contributes correctly to:

- PIB occupancy;
- completion timing;
- IO FIFO head-of-line blocking;
- OO ready/retire eligibility;
- Fence/order requirements.

Store does not automatically imply DTC physical allocation; follow the source-backed cache/write policy established in M4.0.

## M4.2 Atomic lifecycle

Reuse the simulator's existing lower-level Atomic semantics. DTC should wrap the instruction lifecycle; it must not reinvent the memory-side atomic operation.

Hard rule: Atomic side effects must never be collapsed by read Pending-hit merge logic. Two executed atomics to the same address remain two architectural operations.

Add an assertion/counter that can detect accidental atomic merge/loss.

## M4.3 Fence / ordering

Reuse existing simulator ordering/scoreboard mechanisms where source-backed. Fence need not allocate a physical cacheline unless current architecture semantics require it.

OO retirement must not violate required same-warp memory ordering across unresolved fences. Add directed tests and an invariant for this ordering.

## M4.4 Architectural bypass

Preserve existing cache modifiers / architectural L1 bypass behavior. Keep this distinct from the thesis DTC policy-driven bypass, which remains out of scope.

A bypass operation may still participate in instruction lifecycle/PIB waiting if its current completion semantics require it, but it must not perform DTC Tag/physical allocation merely to simplify implementation.

## M4.5 Mixed-operation regression

Run directed mixed Load/Store/Atomic/Fence/bypass sequences under LEGACY, Paper Base, IO, OO.

Verify operation counts, side effects, ordering, lifecycle completion, and all shared invariants.

## M4.6 Framework presets / workload manifest

Create reproducible presets for at least:

- LEGACY;
- PAPER_BASE;
- PAPER_IO;
- PAPER_OO;
- sector mode if retained for diagnostic smoke.

Create `docs/dtc_l1/implementation/WORKLOAD_MANIFEST.md` mapping thesis names to available framework workloads/inputs with status:

- `EXACT_MATCH`;
- `SOURCE_EQUIVALENT_CONFIRMED`;
- `APPROXIMATE_PROXY`;
- `UNRESOLVED`.

Do not silently substitute `gemv`, `gesu`, or any other name when exact provenance is unresolved.

## M4.7 Workload bring-up

Use the same trace/input/config across Paper Base/IO/OO. Initially bring up the available compute set most directly corresponding to Chapter 4, including when available and provenance-verified:

- bicg;
- atax;
- mvt;
- syrk;
- syr2k;
- 2mm;
- 2DConvolution/conv2d equivalent if confirmed;
- Parboil spmv;
- gesummv/gesu only after mapping is documented;
- gemv only after exact source/input is resolved.

All M4 workload results are `DIAGNOSTIC`. The purpose is full-kernel completion and mechanism sanity, not final speedup claims.

For each Base/IO/OO triplet automatically verify:

- same dynamic instruction counts;
- same Load/Store/Atomic/Fence counts;
- no unexpected deadlock;
- no assertion/stale-fill/Ref/Merge errors;
- closed PIB/lower-token accounting;
- valid result provenance.

Invalid runs must not enter aggregate speedup tables.

## M4.8 Compact analysis outputs

Generate machine-readable summaries including at least:

- `summary.csv`;
- `stall_breakdown.csv`;
- `occupancy.csv`;
- `latency.csv`;
- `traffic.csv`;
- `io_hol.csv`;
- `oo_ref_merge.csv`;
- `mechanism_sanity.csv`.

The mechanism sanity table should place Base/IO/OO side-by-side for PIB pressure, outstanding requests, MSHR stalls, physical occupancy, pending hits, IO HOL, OO out-of-order retirement, Ref Count usage, duplicate-after-eviction traffic, lower traffic, and cycles.

Add non-fatal causal warnings for suspicious combinations such as large IO speedup without MLP/PIB change, large OO-over-IO improvement with near-zero IO HOL, high pending merge without corresponding lower-request reduction, or no-free-physical stalls while measured occupancy is low.

M4 review pack: `docs/dtc_l1/review_packs/M4_COMPUTE_BRINGUP/`.

---

# 5. Commit and review boundaries

Use semantic commits; exact source file grouping may follow the implementation, but preserve separable intent approximately as:

- M1.0 source audit;
- M1 lifecycle/frontend plumbing;
- M1 Baseline PIB/Tag timing;
- M1 stats/assertions/parser;
- M1 closeout;
- M2 IO Tag/physical allocation;
- M2 miss/fill/no-MSHR;
- M2 retire/release/deadlock instrumentation;
- M2 closeout;
- M3 OO PIB/Ref Count;
- M3 merge/wakeup/reclaim;
- M3 sector extension;
- M3 closeout;
- M4 memory-op audit;
- M4 Store/Atomic/Fence/bypass integration;
- M4 workload infrastructure;
- M4 workload bring-up;
- M4 closeout.

Never use `git add .` or `git add -A`.

Each major review pack must include at least:

- `README.md`;
- `SOURCE_ANCHORS.md`;
- `COMMIT_HISTORY.md`;
- `CHANGED_FILES.md`;
- `VALIDATION_SUMMARY.md`;
- `INVARIANT_SUMMARY.md`;
- `COUNTER_SANITY.md`;
- `OPEN_ISSUES.md`;
- `RAW_LOG_INDEX.tsv`.

M4 additionally includes compact workload CSVs and workload provenance.

---

# 6. Final STOP boundary

After M4 passes:

- push final Core/Framework branches;
- set `codex_handoff/LATEST_REPORT.md` to `READY_FOR_M5_REVIEW` with final SHAs and review entry points;
- STOP.

Do not begin Chapter-4 result reproduction or M5 experiments in this goal.
