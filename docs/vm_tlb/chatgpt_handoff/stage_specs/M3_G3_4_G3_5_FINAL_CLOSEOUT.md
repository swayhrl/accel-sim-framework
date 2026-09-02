# M3 G3-4/G3-5 — Final Timing Baseline and Macro Closeout

Ownership: ChatGPT

Status: AUTHORIZED AFTER G3-2C/G3-3 PASS

## Objective

Finish the reusable timing-realistic single-GPU VM baseline as one continuous Codex Goal:

`G3-4A page-size foundation -> G3-4B TLB lookup timing -> G3-5 latency accounting and causality -> G3-CLOSEOUT -> M1_M3_VM_BASELINE_CLOSEOUT`

Every gate is an internal checkpoint. Continue automatically only on PASS. Any correctness/provenance ambiguity is a hard STOP.

This stage still excludes Segmentation, target-paper L2-TLB sub-entry/coalescing, synthetic KV injection, page fault/migration/UVM/MCM, and multi-ASID claims.

## Accepted entry anchors

Core/GPGPU-Sim:
`1b18b3c5da6e5ba22e4a03c20e3adce498311336`

Framework/Accel-Sim evidence:
`a3af1f34b4e6fcac4f43faf8d80d8a914eb34958`

Accepted prior stages:
- M1 PASS
- M2 PASS after M2-RF
- G3-1 PASS
- G3-2/G3-2B PASS
- G3-2C radix-prefix hierarchy PASS
- G3-3 generic PWC PASS

Do not rewrite prior accepted semantics to simplify this stage.

---

# Gate G3-4A — 64KB / 2MB page-size foundation

## Modeling decision

Generic M3 v0 may select one translation page size per simulation/controller run. Simultaneous mixed-size mappings are not required for M3 closeout unless the existing implementation already supports them cleanly.

Therefore:
- `64KB-only run` is required;
- `2MB-only run` is required;
- `mixed 64KB+2MB in one run` is optional for generic v0;
- do not implement a mixed-page policy merely to satisfy a checklist;
- if mixed mode is implemented, it must be deterministic and `vm_mixed_pages` becomes mandatory.

This avoids inventing an OS/page-promotion policy that is outside current scope.

## Required semantics

For both 64KB and 2MB:
- correct VPN and page offset;
- `translation_key.page_size` participates in TLB identity;
- L1/L2 fill/probe/replacement remain page-size aware;
- radix-prefix PTE hierarchy and PWC prefix keys use the selected page-size class correctly;
- identity-like data mapping preserves `SimPA == SimVA`;
- one TLB entry covers exactly one configured page range;
- per-page-size observability is explicit;
- 56-bit generic mode remains default and 49-bit backend proof remains valid.

Do not add 4KB unless useful and low risk. Do not add target-paper sub-entry/coalescing.

## Required directed tests

At minimum:
1. `vm_64kb_offset`
2. `vm_2mb_offset`
3. 64KB TLB same-page hit / next-page miss behavior
4. 2MB TLB same-page hit / next-page miss behavior
5. 64KB radix/PWC identity remains correct
6. 2MB radix/PWC identity remains correct
7. no 64KB/2MB namespace collision
8. M2 original 64KB suite unchanged
9. if mixed mode exists: deterministic `vm_mixed_pages`

## Integrated validation

Run at least one available trace under 64KB and 2MB when both are semantically valid under the identity-like mapper. Report TLB/PTE/PWC/cycle differences as characterization, not as correctness expectations.

PASS only if all addressing, fill and range invariants are exact.

---

# Gate G3-4B — timing-realistic L1/L2 TLB lookup latency

## Why this gate is required

The accepted M2/G3-3 lookup path still performs a finite-port L1 probe and, on miss, a finite-port L2 probe in the same invocation. It models port limits but not non-zero TLB lookup service latency. M3 cannot close as a timing-realistic VM baseline until lookup service time is explicit.

## Required configurable timing

Add independent configurable lookup service latency for:
- L1 TLB
- L2 TLB

Generic baseline seed:
- L1 TLB lookup latency: 10 core cycles
- L2 TLB lookup latency: 80 core cycles

Evidence label: `REFERENCE_OTHER_PAPER` / generic `MODELING_DECISION`, not `SEGMENTATION_PAPER_KNOWN`.

Retain a zero-latency/legacy diagnostic setting only if useful for causality and regression. Formal generic M3 results must use the explicitly documented non-zero baseline unless the final parameter ledger gives a stronger justified value.

## Required request-state semantics

A translation lookup must have explicit in-flight state or an equivalent implementation that proves these semantics:

`NEW -> L1 lookup launch -> L1 service -> L1 result`

On L1 miss:

`L2 lookup launch -> L2 service -> L2 result`

On L2 miss:

`translation MSHR/PWQ/PTW`

Rules:
- a TLB lookup port is consumed once when that lookup is launched, not on every waiting cycle;
- the same lookup does not re-probe while service latency is pending;
- hit/miss/access counters increment exactly once per completed lookup;
- a registered MSHR waiter retry must preserve the accepted M2-RF pending-bypass semantics and must not relaunch L1/L2;
- a genuinely new waiter may perform its normal first lookup and then merge;
- L2 hit may fill L1 only after the modeled L2 lookup result becomes available;
- no data-cache request may issue before translation READY;
- stores/atomics remain exact-once.

## Required directed tests

At minimum:
1. exact L1 hit completion cycle
2. exact L1 miss -> L2 hit completion cycle
3. exact L1 miss -> L2 miss handoff to MSHR/PTW
4. finite-port launch contention
5. waiting lookup consumes no additional ports
6. waiting lookup generates no repeated probes/misses
7. pending-MSHR waiter does not relaunch TLB lookup
8. new waiter for same key retains first lookup then merge
9. L2-hit L1-fill timing
10. zero-latency diagnostic reproduces accepted functional counts where applicable
11. replay/store/atomic and conservation regressions

Reappearance of retry polling or repeated port consumption is a hard STOP.

---

# Gate G3-5A — translation latency decomposition

## Measurement contract

Do not create a misleading arithmetic sum across events that overlap or are shared by merged waiters.

Use two scopes.

### Per waiter/request scope

For each completed translation requester, make observable where applicable:
- entry into VM lookup path;
- L1 lookup queue/wait and service interval;
- L2 lookup queue/wait and service interval;
- time waiting as a merged/pending waiter;
- final translation READY time;
- total requester translation latency.

### Per translation-MSHR / walk scope

For each unique active translation key, make observable where applicable:
- MSHR allocation time;
- PWQ wait;
- walker start/end;
- PWC lookup service;
- PTE-memory wait interval(s);
- PTE L2-only vs DRAM outcomes;
- fill/wakeup interval;
- MSHR lifetime / unique-walk total latency.

Shared walk time must not be multiplied into a fake global sum merely because several waiters merge into one MSHR.

## Accounting rules

- timestamps are monotonic and non-negative;
- define queue wait separately from service;
- count each state interval once;
- where intervals overlap, document that they are critical-path/state intervals rather than additive components;
- retain existing MSHR lifetime/merge-depth/PWC statistics;
- add counts/total/max and preferably histogram or structured samples for final latency components;
- keep paper-facing TLB hit/miss counters separate from retry/backpressure events.

## Required exact tests

Create at least one deterministic analytical timing test with known cycle intervals covering:
- L1 hit;
- L2 hit;
- PTW path;
- PWC hit on an intermediate level;
- PTE memory response;
- merged waiter.

Expected-vs-actual timestamps/cycles must be machine-checkable.

PASS requires no unexplained double counting and no negative/non-monotonic interval.

---

# Gate G3-5B — causality and sensitivity closeout

Only start after all correctness/timing gates above PASS.

Use the currently available traces. If only LUD and BFS are available, use them and explicitly state that no third workload was evaluated. Do not fabricate a regular/memory/irregular trio claim.

## Required sweeps

At minimum:

1. L2 TLB capacity: three points around the 768-entry seed, e.g. `256 / 768 / 1536` (or a closely justified set)
2. translation MSHR entries: `8 / 32 / 64` or comparable
3. walkers: `1 / 4 / 16`
4. PWC: `OFF / FINITE-128 / IDEAL`
5. PTW implementation: M2 fixed-latency diagnostic vs M3 real-memory PTW
6. page size: 64KB vs 2MB on at least one valid trace
7. TLB lookup timing causality: zero-latency diagnostic vs generic non-zero timing on a bounded case

Do not require strictly monotonic IPC. Do require that every material trend is explainable using measured:
- L1/L2 TLB accesses/hits/misses/port stalls;
- lookup timing stalls;
- MSHR allocation/merge/full/occupancy/lifetime;
- PWQ/walker pressure;
- PWC accesses/hits/skips/evictions;
- PTE L2/DRAM traffic;
- translation latency decomposition;
- translation-blocked cycles;
- total cycles/IPC.

If a larger resource makes performance worse, investigate and explain it; do not hide the point or tune it away.

All sweep results must be structured TSV/CSV with exact Core SHA, Framework SHA, config identity, trace identity and status (`FORMAL`, `DIAGNOSTIC`, etc.).

---

# Parameter evidence boundary

Maintain/update `PARAMETER_EVIDENCE_LEDGER.md`.

At minimum distinguish:

## `SEGMENTATION_PAPER_KNOWN`
- 64KB paging baseline
- 32-entry fully-associative L1 TLB
- 768-entry, 16-way L2 TLB
- 16 page walkers
- other Table-I GPU parameters already recorded in the paper spec

Do not label TLB lookup latencies, PWC organization, page-table radix split, MSHR/PWQ sizes or synthetic-KV behavior as target-paper exact unless supported by new evidence.

## Generic/reference parameters
- 56-bit generic trace/backend width: project `MODELING_DECISION`
- balanced radix-prefix hierarchy: project `MODELING_DECISION`
- PWC intermediate-only semantics: project `MODELING_DECISION`
- PWC 128 entries: `REFERENCE_OTHER_PAPER`
- L1/L2 lookup seeds 10/80 cycles: `REFERENCE_OTHER_PAPER` / generic `MODELING_DECISION`

Paper-specific 49-bit mode remains separate from generic 56-bit mode.

---

# G3-CLOSEOUT acceptance

M3 PASS requires all of:
- G3-4A PASS
- G3-4B PASS
- G3-5A PASS
- G3-5B PASS
- all M1/M2/G3 directed regressions PASS
- VM-disabled transparency PASS
- PTE request/response conservation PASS
- zero recursive PTE translation
- zero response misassociation
- zero lost request/duplicate waiter wakeup/store/atomic side effect
- final MSHR/PWQ/walker quiescence
- clean build and `git diff --check`
- exact source/config/trace provenance
- worktrees clean after final commits

## M3 review pack

Complete `docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/` with standard files plus:
- `PARAMETER_EVIDENCE_LEDGER.md`
- complete directed expected-vs-actual matrix
- PTE request/response conservation report
- PWC closeout
- 64KB/2MB validation summary
- TLB lookup latency validation
- latency decomposition definition and analytical proof
- fixed-vs-real PTW causality summary
- structured sensitivity summary
- limitations / modeling decisions

---

# M1-M3 macro closeout

After M3 PASS, create:

`docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

It must independently establish:
- final Core/Framework SHAs;
- full request path from SimVA through TLB/MSHR/PWQ/walker/PWC/PTE memory to SimPA/data path;
- all frozen invariants;
- generic default configuration;
- parameter evidence classes;
- validation matrix;
- formal vs diagnostic results;
- known limitations;
- exactly what remains before target Segmentation reproduction.

Update:
- `docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`
- `docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Commit and push Core + Framework.

Then STOP.

## Final STOP boundary

Do NOT enter:
- M4B
- Segmentation implementation
- L2-TLB sub-entry/coalescing
- synthetic KV injection
- new AI-aware translation mechanism
- page fault/migration/UVM/MCM

without a new ChatGPT handoff.