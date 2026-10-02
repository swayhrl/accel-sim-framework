# Codex Goal — Lane G / node109
## AWMA R22G R81 online dispatch CPU audit V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r22g-r81-dispatch-audit-109-v1`

Scientific parent:
`69e74fe74e18d1f3a71bfac0d097ce49234327a9`

Stage:
`AWMA_R22G_R81_DISPATCH_AUDIT_109_V1`

CPU-only.
Do not acquire the GPU campaign lock.
Do not run CUDA, compile GPU code, regenerate model outputs, train, profile or use node174.

Read-only methodology:
`origin/hrl/awma-chatgpt-literature-notes-v1@fc1351e9e62f2a1aa12c323823e24d30357a8a9d`

---

# 0. Frozen evidence

Use only accepted R81 artifacts from parent:
- C0/C1/H0 legal-set traces
- exact masks/legal IDs
- A0/A1/A2/A3 timing records
- complete-generation timing
- source capability map
- grammar compile/runtime receipts.

Do not relabel H0 as an unseen holdout; Round22 has already inspected it.

Known accepted facts:
- union<1% sparse stratum: A3 head-region reductions ~53.4%, 45.3%, 44.8% across C0/C1/H0
- union>50% broad states: A3 slower ~27.5%, 7.1%, 6.7%
- complete-generation no stable overall gain
- A0 strongest qualified known dense baseline
- A3 direct-index is a bounded software prototype
- Kestrel indexed head / FlashSampling / XGrammar are nearest capabilities.

---

# 1. Determine what information exists before head execution

Source-audit the exact R81/XGrammar path.

For every candidate dispatch signal determine:
- when it becomes available relative to LM-head start
- CPU or GPU residency
- whether obtaining it requires scanning the full mask
- whether it requires device-to-host synchronization
- whether exact legal IDs already exist or must be materialized
- whether identical-mask grouping is already known
- whether using A3 requires new metadata/H2D transfer.

At minimum audit:
- legal token count
- union size
- union fraction
- singleton status
- identical-mask group identity.

Write:
`ONLINE_SIGNAL_AVAILABILITY.md`

If the only useful predictor requires observing post-head timing or future information, it is not deployable.

---

# 2. Freeze exactly one rule before any retrospective dispatch arithmetic

Use the old pre-registered sparse stratum boundary only:

`IF legal_union_fraction < 0.01 THEN A3 ELSE A0`

This is not claimed optimal.
Do not scan thresholds.
Do not introduce a learned classifier.
Do not use per-step measured winner.

Call it:
`RULE_U01`.

If union fraction itself is not available before the head without a new full-mask scan or sync, still evaluate the rule as an oracle-like software diagnostic but mark its acquisition cost UNKNOWN / NONFREE.

---

# 3. Reconstruct cost ownership

For A0 and A3 determine from accepted source/timing boundaries which costs are already included:

- legal-set/mask generation
- legal ID materialization
- grouping
- metadata transfer
- weight/index gather
- LM-head compute
- token selection
- synchronization
- launch overhead.

Do not double charge costs already inside accepted head-region timing.

If a required RULE_U01/A3 cost was outside timing and no accepted measurement exists, mark it UNKNOWN.
Do not set it to zero.

Write:
`COST_OWNERSHIP.tsv`

---

# 4. Retrospective fixed-rule accounting

Using existing per-step accepted timing only, and without rerunning GPU work:

For each cohort C0/C1/H0:
- classify every retained timestep by RULE_U01
- report A0/A3 step counts
- compute the sum of the selected arm's accepted **head-region** time only where per-step matched data exists
- compare against all-A0 head-region timing
- preserve all steps
- separately report any mandatory cost that is UNKNOWN.

If exact matched per-step timings do not exist for both arms, do not synthesize them from cohort medians. Use only the strongest legal aggregate bound and mark exact hybrid estimate UNKNOWN.

Also compute:
- best-of(A0,A3) per-step oracle only as an explicitly nondeployable upper bound
- RULE_U01 gap to that oracle.

Do not call either number complete-generation speedup because arm switching/cache state was never executed in one live trajectory.

Write:
- `RULE_U01_RETROSPECTIVE.tsv`
- `BEST_OF_ORACLE.tsv`

---

# 5. Nearest-software capability audit

Using the accepted source capability map and pinned source:

For:
- XGrammar
- Kestrel indexed-head path
- FlashSampling-style fused selection
- A3 direct-index prototype

record:
- what online signal each consumes
- whether it already supports arbitrary dynamic legal sets
- where index/gather cost occurs
- whether dispatch between dense/indexed is already exposed.

Do not broaden into a new literature survey.

The question is whether RULE_U01 would merely be a small software dispatch policy over known primitives, or whether there is an unresolved expensive transition/publication step.

---

# 6. Decision

## If RULE_U01 uses already-available information and retrospective head-region accounting is consistently favorable
Decision:
`R22G_R81_SOFTWARE_DISPATCH_CANDIDATE_JUSTIFIED`

Produce one future GPU validation proposal:
- new validation inputs, not old H0
- fixed RULE_U01
- execute real mixed dispatch in one trajectory
- include all dispatch/index costs.

Do not run it here.

## If benefit depends on unmeasured expensive metadata/sync or retrospective result is not consistently favorable
Decision:
`R22G_R81_DISPATCH_NOT_JUSTIFIED_FROM_EXISTING_EVIDENCE`

State exactly which missing cost or negative state closes it.

## If exact per-step evidence is insufficient
Decision:
`R22G_R81_DISPATCH_EVIDENCE_INSUFFICIENT`

At most one minimal future measurement proposal.
No GPU run here.

No hardware mechanism is authorized in any case.

---

# 7. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R22G_R81_DISPATCH_AUDIT_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- ONLINE_SIGNAL_AVAILABILITY.md
- RULE_U01_CONTRACT.md
- COST_OWNERSHIP.tsv
- RULE_U01_RETROSPECTIVE.tsv
- BEST_OF_ORACLE.tsv
- SOFTWARE_CAPABILITY_DELTA.md
- NEXT_STEP_PROPOSAL.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

CPU-only commit/push/fetch-back verify.
Worktree clean.
STOP.
