# CODEX NEXT STAGE — 174-new VM Per-Access Coverage Repair Qualification V1

Date: 2026-09-19

Status: ACTIVE MAINLINE — CORRECTNESS QUALIFICATION BEFORE ANY FURTHER TRANSLATION MECHANISM WORK.

Stage:

`AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_QUALIFICATION_174NEW_V1`

Node:

`174-new / port 2239`

## 0. Why this stage exists

The accepted global-access-determinism stage proved that the formal Q05 trace and generation-time GLOBAL coalescing are deterministic:

```text
P34 10/80 cycles = 871835
P34 0/80 cycles  = 748102

canonical GLOBAL instructions = 140672
all canonical records         = INPUT_SAME_OUTPUT_SAME
generation-time GLOBAL delta  = 0
```

It also exposed a much more serious coverage mismatch:

```text
generation-time GLOBAL mem_access_t objects = 2182656

prior accepted VM unique/READY count:
P34 10/80 = 776666
P34 0/80  = 864728
```

Therefore generation->VM conservation fails by construction.

Accepted source audit now shows a plausible correctness defect:

`ldst_unit::memory_cycle()`

checks/translates only the current `inst.accessq_back()` once, then calls the downstream access-queue path.

For positive L1D latency:

`process_memory_access_queue_l1cache()`

can iterate up to `l1_banks` times and pop multiple access-queue entries in the same cycle, without independently checking/applying VM translation to each newly exposed `accessq_back()`.

The bypass-L1D interconnect path can also pop multiple access entries per call.

Thus later accesses in the same coalesced access queue may enter L1D/ICNT without ever passing through the modeled TLB/PTW path.

Current accepted identity-like SimVA->SimPA means the lower functional address may accidentally remain numerically correct, but translation timing/state/telemetry can be skipped. Any future non-identity mapping would be even more sensitive.

This is a **scientific correctness gate**.

No previous accepted result is deleted in this stage. No repaired result becomes the new baseline automatically.

## 1. Coordination and execution parent

Read coordination:

`hrl/awma-vm-per-access-coverage-repair-handoff-v1`

Execution parent:

```text
hrl/awma-q05-global-access-determinism-174new-v1
be82faf264e93396b4b7d4fd72078c7e4491e3e4
```

Recommended execution branch:

`hrl/awma-vm-per-access-coverage-repair-174new-v1`

The independent 109 V2.1 campaign is complete at:

`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Do not modify node109 in this stage.

## 2. D0 — Freeze historical results as legacy-undercoverage evidence

Do not rewrite historical review packs.

Create a scope document classifying prior translation-dependent Q05 results as:

`LEGACY_VM_UNDERCOVERAGE_BASELINE_PENDING_REQUALIFICATION`

This applies at least to scientific claims based on the current VM timing path:

- isolated R0/I0 translation characterization;
- P2/M8 diagnostic characterization;
- full-kernel translation behavior;
- timeline/retry characterization;
- self-warm replay;
- contextual P1/P2/P4/P8/P16/P34 replay;
- target-only I0/context-effect decomposition;
- lookup-latency decomposition;
- lookup-model-validity stage.

Producer trace identity, native census, page-footprint capture, and trace-structure evidence remain valid unless separately contradicted.

The previous global-stream telemetry artifact is retired as a scientific access-count source.

## 3. D1 — Prove the coverage defect with source + read-only counters

Before modifying behavior, add disabled-by-default diagnostic counters to the legacy runtime.

At every downstream admission/pop point for VM-eligible GLOBAL/LOCAL/PARAM_LOCAL `mem_access_t`, count:

- total eligible generated/access-queue objects;
- admission/pops with `vm_translation_applied == true`;
- admission/pops with `vm_translation_applied == false`;
- translation telemetry outcome UNOBSERVED at L1D/ICNT admission;
- unique mem_access UID for each category.

Cover both:

1. L1D latency queue path;
2. L1D zero-latency path;
3. bypass-L1D / ICNT path.

Do not alter scheduling/timing in this diagnostic-only run.

Run:

- a minimal synthetic multi-access instruction reproducer if source-safe;
- formal P34 natural legacy control.

Required defect proof:

`UNTRANSLATED_DOWNSTREAM_ADMISSIONS > 0`

and source-localization showing exactly which loop/pop paths permit it.

If this cannot be demonstrated, STOP and reassess; do not patch speculatively.

## 4. D2 — Candidate repair contract

Implement a surgical candidate repair in an isolated diagnostic runtime.

Goal:

> Every VM-eligible coalesced `mem_access_t` must complete exactly one accepted VM translation before it may be admitted/popped into L1D or ICNT.

Preserve:

- accepted trace;
- coalescing;
- SimVA;
- mapping semantics;
- TLB capacities/associativity;
- TLB ports;
- lookup latencies;
- MSHR/PWQ/walker/PWC/PTE;
- L1D/L2/DRAM architecture;
- cache policies;
- CTA/warp scheduling policy.

Do not add pretranslation, batching, a new TLB port, or a mechanism.

Preferred implementation:

- factor the existing translation logic into one helper operating on the current `mem_access_t`;
- invoke/check it immediately before **each** downstream admission/pop of a VM-eligible access;
- if translation is pending or blocked, do not pop that access and stop/break the current downstream issue attempt with the existing VM stall semantics;
- only proceed to mem_fetch allocation/admission once that exact access has `vm_translation_applied=true`.

The helper must preserve:

- target source attribution;
- identity equality counters;
- object classification;
- translation telemetry outcome;
- one READY application per access.

Do not silently change L1D bank throughput except where the existing single-port translation model naturally prevents multiple new translations in the same cycle.

## 5. D3 — Coverage invariants for repaired runtime

Add qualification counters:

```text
vm_eligible_accesses_generated
vm_downstream_admissions
vm_translated_downstream_admissions
vm_untranslated_downstream_admissions
vm_unique_translated_access_uids
vm_translation_ready_applications
vm_post_ready_retranslation_attempts
```

Required repaired invariants at clean completion:

```text
vm_untranslated_downstream_admissions = 0
vm_post_ready_retranslation_attempts = 0

for every VM-eligible access admitted downstream:
  translation_applied == true
  translation outcome != UNOBSERVED
```

Close conservation separately for GLOBAL and LOCAL.

If source-defined exclusions exist, enumerate them explicitly.

## 6. D4 — Unit and synthetic regression

Create tests covering:

1. one memory instruction with one coalesced access;
2. one instruction with multiple coalesced accesses landing in different L1 banks;
3. bank conflict;
4. L1D bypass path;
5. translation hit;
6. translation miss + MSHR/PTW;
7. store;
8. local memory;
9. identity mapping;
10. non-identity test backend if already source-safe and isolated.

Verify that every access must translate before downstream admission.

Also verify no duplicate translation after READY.

No test may weaken the actual accepted runtime contract.

## 7. D5 — Minimal real-Q05 qualification matrix

Do not launch a full historical replay campaign yet.

Use the same formal P34 context bundle and F0 config.

### Legacy control

Reproduce once with unmodified accepted binary:

`P34_LEGACY_R0`

Expected:

`871835 cycles`

and undercoverage counters should show skipped accesses when diagnostic instrumentation is enabled without changing behavior.

### Repaired natural

Run:

`P34_REPAIRED_R0`

Report:

- cycles;
- active-thread instructions;
- CTA;
- generated VM-eligible GLOBAL/LOCAL accesses;
- translated coverage;
- L1/L2 TLB accesses/hits/misses;
- MSHR;
- walks;
- PWC/PTE;
- requester latency;
- L2 data accesses/misses;
- DRAM counters.

### Repaired target-I0 diagnostic

Only if the target-only I0 path can be adapted without ambiguity to apply to **every** Q05 VM-eligible access:

`P34_REPAIRED_Q05_I0`

Every predecessor remains repaired natural R0.

If target-I0 cannot be made per-access cleanly in this stage, mark:

`REPAIRED_TARGET_I0_DEFERRED`

and do not approximate.

### Optional isolated smoke

If runtime is manageable and source-safe:

`FORMAL_ISOLATED_REPAIRED_R0`

only as a supporting contrast.

## 8. D6 — Required impact report

Create a before/after table:

```text
metric                         legacy P34       repaired P34
cycles
GLOBAL generated accesses
LOCAL generated accesses
translated access coverage
L1 TLB accesses
L1 hits/misses
L2 accesses/hits/misses
MSHR alloc/merge
walks
PWC/PTE
L2 data misses
DRAM
```

Report legacy translation coverage:

```text
P34 10/80 legacy VM READY / generation-time GLOBAL
= 776666 / 2182656 ~= 35.6%
```

Do not call that the total exact VM-eligible coverage until GLOBAL+LOCAL accounting is reconciled.

The purpose is to establish whether the repair materially changes scientific conclusions.

## 9. D7 — Scientific decision

Allowed decisions:

### `PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_QUALIFIED`

Use only if:

- legacy downstream untranslated admission is directly observed;
- source path is closed;
- repaired invariant reaches zero untranslated admissions;
- real Q05 repaired run completes naturally.

This decision **does not automatically accept the repaired runtime as the new research baseline**.

### `PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_NOT_YET_QUALIFIED`

Defect proven, repair not fully qualified.

### `UNDERCOVERAGE_NOT_REPRODUCED`

Only if direct downstream evidence contradicts the current source hypothesis.

### `STOP_FOR_SCIENTIFIC_REVIEW`

Required if the minimal repaired Q05 run materially changes accepted scientific claims, which is expected to be possible.

## 10. Rebaseline boundary

Do not automatically rerun all prior experiments.

If the repair qualifies, stop after producing a proposed requalification plan:

`VM_BASELINE_REQUALIFICATION_PLAN.md`

The plan should identify the minimum results that must be replayed:

likely:

1. formal isolated R0/I0;
2. P34 natural R0;
3. P34 target-only I0;
4. P8 screening control if still desired;
5. translation telemetry/timeline sanity;
6. only after these, representative-family expansion.

Do not replay P1/P2/P4/P16 or old P2/M8 mechanism-like diagnostics unless they are still scientifically necessary.

## 11. Integrate 109 final evidence only as context

Reference but do not alter:

`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Accepted side-lane conclusions to carry:

- Decode Flash Primary-1/2 temporal and requested 2D capture coverage are complete;
- Primary-1 memory footprint changes only modestly through Decode32 and is much more stable across within-step occurrence;
- Primary-2 is structurally tiny and highly stable;
- default native pointer-chase knees are heavily data-cache-policy confounded;
- targeted `cg` surface is largely flat across location count at each stride and does not provide a clean pure-TLB latency calibration;
- 10/80 therefore remain generic simulator parameters.

Do not use native recon to patch lookup constants.

## 12. Forbidden

No architecture mechanism:

- no new TLB design;
- no capacity/port optimization;
- no PTW/PWC mechanism;
- no segmentation/page-size mechanism;
- no prefetch/speculation;
- no cache redesign.

Do not silently promote repaired runtime.

Do not delete or rewrite legacy result packs.

## 13. Durable output

Large repaired-run logs:

`/root/share/mnt164/huangrulin/awma_vm_per_access_coverage_repair_v1/`

## 14. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
LEGACY_RESULT_SCOPE_ADDENDUM.md
LEGACY_UNTRANSLATED_ADMISSION_EVIDENCE.tsv
VM_ACCESS_COVERAGE_SOURCE_CONTRACT.md
CANDIDATE_REPAIR.patch
REPAIR_SEMANTIC_CONTRACT.md
UNIT_REGRESSION_RESULTS.tsv
COVERAGE_INVARIANTS.tsv
P34_REPAIR_IMPACT_MATRIX.tsv
OPTIONAL_ISOLATED_REPAIR_SMOKE.tsv
REPAIRED_TARGET_I0_STATUS.md
VM_BASELINE_REQUALIFICATION_PLAN.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1_COMPLETE_WITH_SCOPE`

If defect/repair changes scientific interpretation, also emit:

`STOP_FOR_SCIENTIFIC_REVIEW`

Then report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
