# Codex Goal — Lane E / node174-new
## AWMA R22E C16/E1 existing-evidence kernel-family audit V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r22e-c16-e1-family-audit-174new-v1`

Planning parent:
`fc1351e9e62f2a1aa12c323823e24d30357a8a9d`

Stage:
`AWMA_R22E_C16_E1_FAMILY_AUDIT_174NEW_V1`

CPU-only.

Do NOT:
- run Accel-Sim/GPGPU-Sim
- run node109 GPU work
- stage large raw/trace onto 174 local disk
- scan all of node164
- rehash all model assets
- generate new traces
- implement hardware.

Read only the accepted reports/indexes/source needed for the two frozen categories below.

---

# 0. Methodology

Read:
- `origin/hrl/awma-chatgpt-literature-notes-v1@fc1351e9e62f2a1aa12c323823e24d30357a8a9d`
- `KERNEL_FAMILY_FIRST_REVIEW_V1.md`
- Round22 retrospective audit
- post-Round22 research plan.

Historical STOP labels remain unchanged.
This audit asks what was measured vs unmeasured at local-family scope.

UNKNOWN stays UNKNOWN.

---

# 1. Category A — cross-CTA low-bit conversion reuse

Locate the exact accepted C16 authorities referenced by Round22 / historical handoffs for:
- M32/M64 strict conversion duplication
- CTA-internal strong-kernel reuse
- natural SHARE3 up-projection timing weight
- encoded vs decoded representation sizes
- gate/up/down operator-family follow-up if available.

Build:
`CONVERSION_REUSE_EVIDENCE.tsv`

Per accepted shape/operator include:
- model/operator role
- M/shape
- dtype/representation
- logical duplicate ratio
- duplicate scope: lane/warp/CTA/cross-CTA
- whether strong kernel already removes intra-CTA duplication
- exact local operator timing available? YES/NO
- exact conversion-only timing available? YES/NO
- dynamic instruction evidence available? YES/NO
- cache/traffic evidence available? YES/NO
- expanded representation bytes
- natural workload time share where known
- source authority.

Do not infer time saved from duplicate-byte ratio.

Then write:
`CONVERSION_REUSE_GAP.md`

Answer:
1. Is local net performance of cross-CTA conversion reuse already measured?
2. If not, can one valid real-input counterfactual isolate it without changing GEMM math, output representation or consumer work?
3. What mandatory costs would such a counterfactual need:
   - decoded storage
   - publication
   - synchronization
   - fanout
   - extra reads/writes
   - lifetime/capacity.

If no clean counterfactual exists, say so.

Do not propose a dequant cache just because duplicate ratio is high.

---

# 2. Category B — E1 same-semantic linear operator shape/implementation boundary

Locate exact accepted E1 clean-baseline authorities for:
- q_proj / down_proj / up_proj
- RAW vs AWQ
- M1 / M256 and any accepted M1023/1024 transition facts
- Native timing if present
- NCU L1/TEX, L2, DRAM traffic if present
- operator-family consumer analysis.

Build:
`E1_FAMILY_MATRIX.tsv`

Each row:
- operator role
- M/shape
- RAW/AWQ
- implementation/kernel identity
- dtype/quantization
- complete local operator time if available
- traffic metrics
- whether comparison is same semantic work
- confounders: quantization, layout, dequant fusion, kernel selection, reduction
- evidence level.

Do not treat RAW/AWQ as a pure bitwidth intervention.

Compute only legal within-authority comparisons.
If timing is unavailable, do not use traffic ratio as speedup.

Identify whether any family shows:
- repeated positive local timing response
- repeated negative response
- only traffic response
- mixed/unknown.

---

# 3. Cross-category prioritization

Create:
`FAMILY_GAP_SCORECARD.md`

For Category A and B score descriptively, not numerically:
- real-input authority
- strong baseline quality
- local response already measured?
- mandatory implementation cost understood?
- nearest software capability
- one clean falsifiable next diagnostic available?
- likely need for simulator/hardware if software evidence survives?

Do not use application coverage alone to reject a family.
Do not ignore application coverage when discussing system value.

---

# 4. Final decision — at most ONE next diagnostic proposal

Allowed outcomes:

## A. One proposal
`R22E_ONE_LOCAL_DIAGNOSTIC_JUSTIFIED`

Choose exactly one category only if:
- real accepted input exists
- local response is genuinely unknown or mixed
- a clean same-semantic counterfactual exists
- mandatory costs can be included
- nearest software does not trivially close the gap.

Write:
`NEXT_LOCAL_DIAGNOSTIC_PROPOSAL.md`

Proposal must specify:
- exact input/shape/operator
- baseline
- one candidate/counterfactual
- numerical contract
- target family
- mandatory costs
- non-target observation
- stop rule.

Do NOT execute it.

## B. No proposal
`R22E_EXISTING_EVIDENCE_DOES_NOT_JUSTIFY_NEW_DIAGNOSTIC`

Explain which evidence closes each category.

Do not produce two follow-up experiments.

---

# 5. Data handling

Use node164 only through existing accepted paths/indexes.
Read the smallest required files.
Do not copy large traces/raw to 174.
If a needed historical path is missing but its compact Git report is sufficient, use the report.
If a scientific value exists only in unavailable raw, mark UNKNOWN rather than launching reconstruction.

---

# 6. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R22E_C16_E1_FAMILY_AUDIT_174NEW_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- AUTHORITY_INDEX.md
- CONVERSION_REUSE_EVIDENCE.tsv
- CONVERSION_REUSE_GAP.md
- E1_FAMILY_MATRIX.tsv
- FAMILY_GAP_SCORECARD.md
- NEXT_LOCAL_DIAGNOSTIC_PROPOSAL.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

CPU-only commit/push/fetch-back verify.
No GPU/simulator process from this Goal.
Worktree clean.
STOP.
