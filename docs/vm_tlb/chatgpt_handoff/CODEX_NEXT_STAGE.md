# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION` has been reviewed by ChatGPT: **PASS**.

Execute **M2 and M3 as one continuous Codex target-mode macro task** with internal acceptance gates. Do not pause for human review between M2 and M3 when M2 fully passes; do not continue when any gate fails.

Execution order:

1. read `stage_specs/M2_M3_TARGET_MODE.md`;
2. execute `stage_specs/M2_FUNCTIONAL_TRANSLATION.md` through all M2 gates;
3. if and only if M2 closeout is PASS, continue automatically into `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`;
4. create `review_packs/M1_M3_VM_BASELINE_CLOSEOUT/` after M3 PASS;
5. push, report, and STOP before M4B / Segmentation / synthetic-KV / new AI-aware mechanisms.

Do not modify `chatgpt_handoff/*`.

## Mandatory read order

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. repository-root `AGENTS.md`
4. `stage_specs/M2_M3_TARGET_MODE.md`
5. `stage_specs/M2_FUNCTIONAL_TRANSLATION.md`
6. `stage_specs/M3_REFERENCE_MATERIALS.md`
7. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
8. M1 review pack; at M3 entry, completed M2 review pack
9. long-lived VM specs under `docs/vm_tlb/specs/`

## Source anchors

Continue from the current pushed Track-A heads:

- Core branch: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- M1 Core commit: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- Framework branch: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Use the existing isolated Track-A worktrees. Fetch/pull the latest Framework handoff commit before implementation, then verify Core/Framework branch and worktree cleanliness.

## Target-mode monitoring

Maintain the Codex-owned checkpoint file:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

Follow all goal/gate IDs in `M2_M3_TARGET_MODE.md`. Update the progress file after each gate so the long task is restartable and externally auditable.

A gate may advance only when its required tests/evidence are PASS. On FAIL/BLOCKED:

- stop implementation beyond that gate;
- update `TARGET_PROGRESS.md` and `LATEST_REPORT.md`;
- create/update the relevant review pack;
- commit/push review evidence when safe;
- STOP.

## M2 review emphasis

In addition to the M2 stage spec:

- `SimPA` is not semantically valid merely because it contains an initialized numeric value; completion/validity must gate downstream use.
- untranslated requests must not enter the real data-cache path.
- replay must not retranslate completed requests or duplicate load/store/atomic side effects.
- one `(ASID, VPN, page-size-class)` has at most one active walk.
- translation-MSHR merge is not a TLB hit.
- finite lookup throughput/resources, MSHR, PWQ and walkers must affect behavior, not only statistics.
- directed tests must assert expected counts and conservation.

## M2 -> M3 automatic transition gate

Codex may enter M3 without waiting for ChatGPT only when all M2 acceptance criteria are PASS and the M2 review pack contains:

- expected-vs-actual directed-test table;
- invariant/conservation report;
- structured TLB/MSHR/PWQ/walker statistics;
- integrated workload smoke;
- VM-disabled transparency regression;
- exact Core/Framework SHAs and clean provenance.

Any unresolved functional failure blocks M3.

## M3 implementation emphasis

M3 must build a reusable **generic timing-realistic** page-walk substrate, not silently claim exact Segmentation-paper PTW behavior.

Required principles:

- PTE requests are explicit physical requests and never recursively translate.
- PTE reads must consume actual intended L2/lower-memory resources and walkers must wait for real responses.
- multiple outstanding PTE responses must be associated with the correct walk/request.
- PWC must be finite/configurable with zero-capacity and optional ideal diagnostic modes.
- 64KB and 2MB semantics must be validated; target-paper sub-entry stays out of M3.
- timing components require explicit timestamp ownership and double-counting checks.
- retain M2 fixed-latency PTW as a diagnostic causal comparison through M3 closeout where practical.
- every parameter must be labeled according to evidence (`PAPER_SPEC`, `MODELING_DECISION`, `REFERENCE_OTHER_PAPER`, `DIAGNOSTIC`, `UNKNOWN`).

Use `M3_REFERENCE_MATERIALS.md` to distinguish target-paper facts, CLAP reference values, legacy `dev-uvm` reference code, and project modeling choices.

## Reporting

Active Track-A report:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Target progress:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

Review packs:

- `docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/`
- `docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/`
- `docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

Update report/progress at least at M2 closeout, M3 major gates, and final macro closeout.

## STOP conditions

STOP immediately on:

- any correctness invariant failure;
- baseline-transparency regression;
- request loss;
- duplicate wakeup;
- duplicate store/atomic effect;
- recursive PTE translation;
- PTE response misassociation;
- deadlock or unexplained nondeterminism;
- a material semantic ambiguity requiring a new modeling decision not already authorized;
- source/provenance uncertainty.

Do not weaken tests or convert a paper-specific unknown into `PAPER_EXACT` to continue.

## Final STOP boundary

After M3 PASS and `M1_M3_VM_BASELINE_CLOSEOUT`:

- push Core and Framework Track-A branches;
- update `LATEST_REPORT.md` and `TARGET_PROGRESS.md`;
- provide final SHAs and review-pack entry points;
- STOP.

**STOP BEFORE M4B / Segmentation implementation / synthetic-KV simulator injection / new AI-aware TLB mechanism.**
