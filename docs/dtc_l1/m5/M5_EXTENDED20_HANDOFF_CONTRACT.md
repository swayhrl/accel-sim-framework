# M5 Extended-20 Handoff Contract

> For a trace payload, capture-side application correctness, trace identity,
> replay terminal status and replay accounting are separate evidence fields.

Status: **ACTIVE AFTER PORTFOLIO APPROVAL**

Authority:

- `M5_EXTENDED20_APPROVAL.md`
- `M5_EXTENDED20_FORMAL_MATRIX.md`
- `M5_PARALLEL_BATCH_POLICY.md`

Extended stages are quality gates, not ordinary human-approval pauses. After PASS, checkpoint/push and continue when dependencies are satisfied.

## 1. M5.E0 — Selection handoff

Reviewed source handoff:

- selection branch: `hrl/decoupled-l1-exp-m5-extended20-select-v0`
- reviewed commit: `d43b6eec93f68efa94057f34ffa699463b53e6a6`
- source status: `M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`
- researcher/ChatGPT disposition: **APPROVED** by `M5_EXTENDED20_APPROVAL.md`.

Do not redo the 52-candidate selection unless a primary workload later becomes ineligible and the five ranked alternates cannot preserve portfolio constraints.

## 2. Standard Extended handoff fields

Every E1-E3 handoff must record:

1. status;
2. input Core/Framework SHAs;
3. previous Paper/Extended handoff anchors;
4. selected portfolio version/approval SHA;
5. workload source/build/PTX/input/output-check identities;
6. config/parser/schema identities;
7. completed experiment IDs;
8. acceptance checklist;
9. issues and resolution IDs;
10. invalidated/obsolete results;
11. batch worker-pool settings and job-registry path;
12. compact result artifacts and raw-log index;
13. mechanism/generalization finding;
14. exact next executable scope;
15. do-not-redo list.

## 3. M5.E1 handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_E1_EXTENDED20_FORMALIZATION.md`

Must contain one row per approved workload:

`workload | suite | source commit | wrapper/build | executable SHA | PTX SHA | input SHA | output checker/reference | launch geometry | provenance status | formal-ready status`

Also require:

- corrected BlackScholes algorithm/domain metadata;
- explicit alternate substitutions, if any, with pre-performance reason and P1-P6 recheck;
- no unsupported feature hidden behind historical trace evidence;
- batch manifest template for 60 runs.

PASS state:

`M5_EXTENDED20_FORMALIZATION_READY`

If M5.2 is not yet PASS, wait without consuming long simulation resources; when M5.2 becomes available, revalidate common anchor hashes and continue E2.

## 4. M5.E2 handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_E2_EXTENDED20_FORMAL.md`

Review pack:

`docs/dtc_l1/review_packs/M5_E2_EXTENDED20_FORMAL/`

Must include all 20 triplets and at least:

- 60 primary job identities;
- output correctness status;
- Base/IO/OO cycles and dynamic operation identity;
- Base structural-stall evidence;
- common live-miss counters;
- PIB/MSHR/Tag/lower/traffic counters;
- IO/OO HOL/retirement/ref/reclaim evidence where relevant;
- accounting/drain checks;
- batch concurrency metadata;
- retry/obsolete mapping;
- parser/counter sanity.

Minimum review pack:

- `README.md`
- `SOURCE_ANCHORS.md`
- `WORKLOAD_PROVENANCE.md`
- `FORMAL_ANCHOR.md`
- `CONFIG_MANIFEST.md`
- `PARSER_SCHEMA.md`
- `BATCH_EXECUTION.md`
- `COUNTER_SANITY.md`
- `VALIDATION_SUMMARY.md`
- `RESULT_MANIFEST.tsv`
- `RAW_LOG_INDEX.tsv`
- `OPEN_ISSUES.md`
- `generated/` compact CSV/JSON

PASS state:

`M5_EXTENDED20_FORMAL_PASS`

PASS -> E3 immediately.

## 5. M5.E3 handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_E3_EXTENDED20_SYNTHESIS.md`

Must contain:

- one causal classification per workload;
- per-workload Base/IO/OO performance;
- live-miss relationship;
- Base bottleneck class;
- IO-vs-OO opportunity;
- downstream/traffic explanation;
- list and findings of any `DIAGNOSTIC_EXTENDED` follow-ups;
- `GM-EXTENDED20`;
- `GM-ALL-COMPUTE30` with exact membership;
- explicit preservation of negative/non-beneficiary results;
- statement that workload selection preceded DTC performance observation.

PASS state:

`M5_EXTENDED20_READY_FOR_COMPUTE_FREEZE`

## 6. Compute-freeze join rule

Extended E3 PASS alone does not freeze compute. Freeze requires:

- Paper M5.6 PASS;
- Extended E3 PASS;
- no unresolved correctness/fidelity issue;
- clean/pushed active compute branches.

Then write:

`docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md`

with:

- `COMPUTE_FREEZE_CORE_SHA`;
- `COMPUTE_FREEZE_FRAMEWORK_SHA`;
- Paper-10 review-pack path;
- Extended-20 review-pack path;
- formal config/parser anchors;
- list of reusable 30-workload primary results;
- explicit statement that later graphics code does not invalidate/rewrite compute FORMAL evidence.

## 7. Transition behavior

Do not stop for ordinary recoverable build/workload/assertion/timeout/performance problems. Apply the M5 issue lifecycle, regress, invalidate affected data, and continue.

Pause only for a genuine researcher-decision boundary or when a change would alter frozen DTC architecture/experiment meaning.
