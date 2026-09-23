# CODEX 174 GOAL — RTX4080 / Ada Accel-Sim Platform Qualification V1

Date: 2026-09-23

Mode:

`GOAL MODE / LONG-RUN / SOLVE-AND-CONTINUE / PAPER-GRADE SUFFICIENCY`

Node:

`174-new`

Stage:

`AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1`

Read first, completely:

`docs/vm_tlb/chatgpt_handoff/awma/AWMA_PAPER_GRADE_PLATFORM_AND_MECHANISM_CALIBRATION_CONTEXT_2026-09-23.md`

The purpose is to establish a credible, bounded RTX4080/Ada simulator base platform for later AWMA research.

This is NOT an attempt to perfectly reverse-engineer RTX4080.

The success criterion is:

> major hardware scale and memory-hierarchy behavior are credible; validation error is bounded; no large qualitative mismatch remains; then freeze the platform and move on.

Do not spend unlimited time on infrastructure.

---

# Phase A — execution authority and clean branch

Create execution branch:

`hrl/awma-174-rtx4080-ada-platform-qualification-v1`

Use an isolated worktree/runtime root.

Record source anchors:

- current project prep:
  `a04085f73458c9d30537640c2f7daad4a3aa3dd7`
- exact Native control authority:
  `149af0566cc6720621fdfe88d3cd3ca9b32cba67`
- V1:
  `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
- V2R1:
  `dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`

Do not modify V1/V2R1 semantics in this Goal.

---

# Phase B — inspect existing Ada support; do not reinvent blindly

Inspect:

1. local repository history/configs for any SM89/Ada/RTX4080/RTX4090 support;
2. upstream Accel-Sim PR #548:
   `Add sm_89 (Ada) support and RTX 4060 Laptop config`
3. exact upstream PR head:
   `0c840b276bfecc6c7d1590efd7d5a22b8dff05f6`
4. the matching gpgpu-sim_distribution config/submodule authority referenced by that PR, if accessible.

The upstream PR is OPEN and UNMERGED.

Treat it as:

`UPSTREAM_ENGINEERING_REFERENCE_ONLY`

Do not blindly merge it.

Extract only the minimum relevant Ada support:

- SM89 binary version handling;
- opcode-map choice;
- trace config conventions;
- closest Ada hardware config scaffold.

Compare with our already-qualified SM89 opcode subset audit from:

`a04085f73458c9d30537640c2f7daad4a3aa3dd7`

If the upstream PR confirms that SM89 uses the Ampere opcode map for the relevant trace path, record that as supporting evidence.

Do not claim full Ada ISA fidelity.

---

# Phase C — create RTX4080 base config V0

Create a new config family, for example:

`SM89_RTX4080_AWMA_V1`

Do NOT overwrite RTX3070 or upstream configs.

Parameter provenance must be explicit.

For every nontrivial parameter classify it as one of:

- `PUBLIC_RTX4080_SPEC`
- `UPSTREAM_ADA_SCAFFOLD`
- `NEAREST_VALIDATED_INHERITANCE`
- `BOUNDED_CALIBRATION`
- `ASSUMED_LOW_SENSITIVITY`

## C1. Public-spec parameters

Use reliable NVIDIA/public hardware documentation for parameters such as:

- compute capability / SM89 identity;
- SM count;
- L2 capacity;
- memory bus width;
- memory data rate / bandwidth class;
- core/memory clock class;
- VRAM capacity if config requires it.

Do not guess silently.

Record source URLs/text in:

`RTX4080_PUBLIC_SPEC_AUTHORITY.md`

## C2. Ada scaffold parameters

For undocumented simulator fields, prefer the closest upstream Ada config/scaffold over RTX3070 inheritance.

Where the upstream Ada scaffold is not available or not applicable, inherit the nearest reasonable tested config and label the assumption.

Do not claim undocumented RTX4080 microarchitecture as fact.

## C3. Translation model exclusion

Do NOT use AWMA VM/TLB parameters to qualify the base GPU platform.

Platform qualification first uses the GPU base model without tuning:

- L1 TLB entries;
- L2 TLB entries;
- TLB lookup latency;
- PWC;
- walker count;
- PWQ/MSHR translation parameters.

The existing 10/80 VM overlay remains a research-model overlay and must not be used to tune the RTX4080 base config.

---

# Phase D — basic build / trace admission qualification

Build the simulator with the new SM89/RTX4080 config.

Use existing SM89 traces only as parser/execution sanity checks.

At minimum require:

- M0 trace parses;
- M1 trace parses;
- one AI trace parses if cheap;
- terminal execution under base platform path where applicable;
- no unsupported opcode in the exercised trace subset;
- instruction/CTA identity is plausible and stable.

If an SM89 parser issue is ordinary engineering:

solve-and-continue.

If an essential opcode semantic cannot be represented without a substantive simulator feature redesign:

STOP:

`ESSENTIAL_SM89_SEMANTIC_SUPPORT_MISSING`

Do not spend the Goal implementing broad Ada ISA support unrelated to the evaluated workload subset.

---

# Phase E — consume node109 platform-anchor bundle

Node109 parallel Goal will publish a bounded RTX4080 Native platform-anchor bundle on node164.

Search under:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/`

for the new platform-anchor bundle whose receipt declares:

`RTX4080_PLATFORM_ANCHORS_109_V1`

The bundle should contain:

- calibration anchors;
- held-out validation anchors;
- uninstrumented Native timing;
- corresponding simulator-native traces;
- exact command/source/binary/GPU authority;
- node164 manifest verification.

Do not substitute M0–M3 or T0/T1/T2 as tuning data.

If the bundle has not appeared yet:

- continue all independent phases;
- at final dependency point, poll/wait only for a bounded period;
- if still absent, STOP with:
  `WAITING_FOR_RTX4080_PLATFORM_ANCHOR_BUNDLE`

Do not fabricate or infer Native anchor values.

---

# Phase F — bounded calibration pass 0

Run the platform **calibration-anchor** traces on RTX4080 config V0.

Focus on broad base-platform behavior:

- L1-class hit behavior;
- L2-class hit behavior;
- DRAM latency class;
- DRAM streaming bandwidth;
- optional basic arithmetic throughput if provided.

For every anchor record:

- Native metric;
- simulator metric;
- relative error;
- qualitative direction/trend;
- exact config/binary/trace SHA.

Do not use AWMA research probes for tuning.

---

# Phase G — maximum two bounded tuning passes

This Goal permits at most:

`TUNING_PASS_1`

and:

`TUNING_PASS_2`

after V0.

Every parameter change must have a documented causal reason tied to:

1. public RTX4080 specification; or
2. one dedicated calibration anchor.

Examples of acceptable changes:

- SM count / partition count correction;
- L2 size correction;
- memory bandwidth / DRAM timing adjustment;
- cache latency adjustment;
- clock-domain adjustment;
- clearly relevant pipeline throughput from the Ada scaffold.

Examples of prohibited tuning:

- change a parameter because M1/M2 Native result would look better;
- change TLB latency to make translation sensitivity match;
- tune specifically to T0/T1/T2;
- tweak undocumented knobs one by one until all kernels fit.

After at most two passes:

FREEZE the best defensible config.

Do not start a third tuning loop.

Publish a tuning ledger:

`PLATFORM_TUNING_LEDGER.tsv`

with:

- pass;
- parameter;
- old/new value;
- justification;
- evidence anchor;
- effect.

---

# Phase H — held-out platform validation

Use only anchors/kernels explicitly marked held-out by node109.

Do not tune after looking at held-out results.

Require at least 3 held-out points covering:

- cache-friendly memory behavior;
- streaming/bandwidth behavior;
- compute or mixed behavior.

For each report:

- Native runtime / metric;
- simulator runtime / metric;
- absolute relative error;
- ranking/trend.

Compute:

- median absolute error;
- mean absolute error;
- worst-case error;
- optional Pearson/Spearman only if enough points exist.

Do not overinterpret correlation with only 3 points.

---

# Phase I — predeclared platform qualification decision

Use these thresholds exactly.

## PASS

Classify:

`RTX4080_ADA_PLATFORM_QUALIFIED`

if:

- median held-out absolute error <= 25%;
- key L1/L2/DRAM trend directions are correct;
- no essential held-out point is >2× wrong;
- no essential parser/trace semantic gap exists.

## Scoped PASS

Classify:

`RTX4080_ADA_PLATFORM_QUALIFIED_WITH_SCOPE`

if:

- 25% < median error <= 35%;
- trend directions remain credible;
- no systematic gross mismatch;
- any large outlier has a concrete unsupported-feature/scope explanation.

A scoped PASS is sufficient for the next AWMA relative-mechanism stage.

Do NOT continue tuning merely to turn scoped PASS into PASS.

## FAIL

Classify:

`RTX4080_ADA_PLATFORM_NOT_QUALIFIED`

if:

- median held-out error >35%; or
- major memory-hierarchy direction is wrong; or
- multiple essential held-out points are >2× wrong; or
- SM89 trace execution requires unsupported semantics that materially affect evaluated workloads.

After FAIL, STOP for review.

Do not launch a third tuning campaign.

---

# Phase J — freeze publication baseline

If PASS or scoped PASS:

create a frozen base config authority:

`RTX4080_ADA_ACCELSIM_BASE_V1`

Freeze:

- base config files;
- trace config;
- parser patch;
- source commit;
- binary SHA;
- public-spec provenance;
- tuning ledger;
- calibration results;
- held-out validation results.

Important:

This is a **GPU platform baseline only**.

Do not yet declare:

`RTX4080_AWMA_TRANSLATION_BASELINE`

because translation-model external calibration still comes next.

---

# Phase K — lightweight AWMA compatibility smoke test

After platform qualification only, do a minimal smoke test to verify the existing AWMA VM overlay can be layered without engineering failure.

Use at most:

- M0 one point;
- M1 one point;

with existing 10/80 overlay.

Requirements:

- terminal;
- full translation coverage where emitted;
- quiescent;
- no crash/config incompatibility.

Do NOT analyze Native alignment here.

Do NOT tune platform or VM from these points.

This is an integration smoke test only.

---

# Phase L — report / review pack

Report:

`docs/vm_tlb/codex_handoff/awma/RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/`

Required files:

```text
README.md
SOURCE_ANCHORS.md
UPSTREAM_ADA_REFERENCE.md
RTX4080_PUBLIC_SPEC_AUTHORITY.md
PARAMETER_PROVENANCE.tsv
RTX4080_BASE_CONFIG_V0/
FINAL_RTX4080_BASE_CONFIG/
SM89_SUBSET_QUALIFICATION.tsv
PLATFORM_ANCHOR_AUTHORITY.tsv
CALIBRATION_RESULTS.tsv
PLATFORM_TUNING_LEDGER.tsv
HELDOUT_VALIDATION_RESULTS.tsv
QUALIFICATION_DECISION.md
AWMA_VM_OVERLAY_SMOKE.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Directories may contain multiple config files; hash every published member.

No accidental zero-byte placeholders.

---

# Phase M — publication contract

Close exactly:

```text
qualification closure
→ report/review pack
→ SHA256SUMS
→ commit
→ push
→ fetch-back
→ remote HEAD == local HEAD
→ inspect fetched remote tree
→ every promised file exists/non-empty as applicable
→ sha256sum -c
→ clean worktree
→ STOP
```

Do not start exact M0–M3 contextual cross-calibration in this same Goal.

Do not start mechanism evaluation.

---

# Global solve-and-continue policy

Ordinary engineering issues:

`solve-and-continue`

Examples:

- config path mismatch;
- build errors;
- missing derived runner index;
- trace wrapper;
- PR patch adaptation;
- parser plumbing;
- Git transport;
- node164 path discovery.

STOP only for:

- essential SM89 semantic incompatibility;
- platform anchor P1 evidence missing/corrupt with no recovery path;
- qualification FAIL after bounded two-pass policy;
- a required architecture assumption would materially change the paper claim.

The infrastructure goal is to become **credible enough**, not perfect.
