# C16 Formal Campaign — Capture Execution and Acceptance V1

## 1. Code / evidence reconciliation before GPU work

Create a fresh execution branch/worktree from the formal-campaign coordination branch.

Do **not** replace the accepted Pipeline V1 implementation with the older pre-capture producer branch.

Use these sources as follows:

- current code base: Pipeline V1 integration `3c4847d2da818013dca6422194af36966136ab31` and this coordination branch;
- pre-capture evidence only: `55d11e6829bc89189d1c3fadf695c31078485421`;
- frozen matrix: `a5ab72e99976abb9f4592176c280defe8f75f9af`;
- analysis authority: `d07b7eb5d43b9a31474a6d298ec4e4f75292cc48`.

Recommended import pattern for pre-capture evidence:

```bash
git fetch origin
git checkout 55d11e6829bc89189d1c3fadf695c31078485421 -- \
  docs/vm_tlb/review_packs/C16_TRACE_CAMPAIGN_PRECAPTURE_109_V1
```

Do not wholesale-merge the pre-capture branch's older `util/vm_tlb/c16/data_plane` over the accepted integration implementation.

## 2. GPU serialization

Before each GPU operation, hold:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Confirm no unrelated compute process is consuming the RTX4080 while the lock is held.

CPU-only static-map parsing, report generation, hashing, and Git operations may run without the GPU lock.

## 3. Per-scenario preflight

Before expensive profiling/capture:

1. validate model revision + receipt;
2. validate exact frozen input binding receipt/hash;
3. start a fresh process;
4. record runtime versions/backend identity;
5. run a minimal native correctness smoke for that exact scenario;
6. record peak/allocated GPU memory when practical;
7. verify deterministic output/checksum enough to detect gross runtime drift;
8. only then perform NSYS/NCU/NVBit work.

A failed preflight is a recovery task. Follow the playbook. Do not silently alter the scenario.

## 4. Target readiness — useful standard, not procedural over-gating

A representative target is ready for formal address capture when the following evidence is sufficient to trust and analyze it:

- exact deployment/scenario/phase identity;
- exact dynamic function/launch selector revalidated;
- RTX4080-local exact function/code-object binding;
- static list of relevant GLOBAL memory references for that function;
- duration/population or other runtime evidence showing why the target matters;
- address-bearing canary with nonzero executing records;
- canary footprint is not obviously trivial for a target claimed representative;
- object-range map exists for known weights and, where relevant, AWQ metadata/KV cache; unknown ranges may remain UNKNOWN;
- no evidence of selector drift or data loss that would make interpretation unsafe.

NCU metrics are preferred for ranking but are not required for every exact target if NSYS + static map + address canary already establish the memory opportunity.

Exact high-duration GEMM semantic naming may remain unresolved; use an honest unresolved label rather than blocking or inventing a role.

## 5. Formal trace content

For representative kernel targets, capture **all relevant GLOBAL MREFs within the selected exact launch/window**.

The main bounding mechanism is the selected launch/step/window, not reducing the trace to one convenient PC.

Each formal bundle should preserve, directly or by referenced hash-closed control artifacts:

- run manifest;
- exact model/input/runtime binding;
- target/launch selector;
- static MREF map;
- object map;
- raw NVBit output;
- terminal/drop/overflow status;
- target canary/qualification receipt;
- stdout/stderr/CLI or exact argv;
- Pipeline V1 local close/transfer/ACK receipts.

## 6. Qwen2.5-0.5B campaign order

Recommended order:

1. S2_TEXT Prefill heavy GEMM;
2. S2_TEXT Prefill attention core;
3. S2_TEXT Decode early heavy target;
4. S2_TEXT Decode early memory/KV/attention target;
5. S2_TEXT Decode late version of the memory/KV-sensitive target when useful;
6. one audit/control target only after the representative set is healthy.

Then evaluate S1/S3/S4 and content variants with lightweight runtime comparison. Add only informative controls.

## 7. Qwen2.5-7B-AWQ campaign order

Use exact runtime identity `qwen25_7b_awq_autoawq_unfused`.

Recommended order:

1. S2_TEXT Prefill dominant quantized GEMM / weight-heavy target;
2. S2_TEXT Prefill quant/dequant or metadata-heavy target when runtime evidence proves a distinct useful class;
3. S2_TEXT Prefill attention core;
4. S2_TEXT Decode early dominant target;
5. S2_TEXT Decode early/late KV or attention-memory target;
6. optional context/batch controls selected by runtime evidence.

## 8. Scenario controls

### Context

Use S1/S2/S3 to study context scaling only where the implementation/shape or memory behavior makes the comparison useful.

At least one long-context S3 attention/KV-sensitive control is strongly preferred if S3 is resource-admitted.

### Batch

Use S4 as a batch control if admitted and if the implementation/shape differs materially from S2 structured.

### Input class

S2_CODE/S2_STRUCTURED/S2_TEXT should first be compared via native/NSYS signatures. If they are effectively the same implementation population, avoid redundant large NVBit traces.

## 9. Llama S0 supplement

After Qwen core coverage, collect a compact high-quality S0 set if time/resources allow:

- one heavy compute/memory target;
- one attention/KV-relevant target;
- early/late decode comparison if meaningful.

This is explicitly `S0_ONLY`; no context/batch generalization.

## 10. Capture bounds

Operational planning defaults:

- per-target raw target size: about `<= 4 GiB`;
- per-target wall time: about `<= 20 min`;
- first-wave aggregate raw budget: about `<= 64 GiB`.

These are soft operational controls to keep the campaign moving.

If a target would exceed them, first reduce the number of complete selected launches/windows while keeping all relevant GLOBAL MREFs inside the retained window.

A truncated mid-launch trace is not promoted to formal merely to satisfy a size/time bound.

## 11. Failure / retry budget

Avoid infinite loops but do not give up after one failure.

General rule:

- first failure: diagnose + one direct retry when transient state is plausible;
- second failure: apply the best evidence-preserving recovery from the playbook;
- if the same root cause persists, reject/defer that target with evidence and continue to the next target/stratum.

Exceptions may use additional iterations when a concrete new root-cause hypothesis is being tested; do not repeat identical commands without new information.

## 12. Immediate post-capture checks

Before formal promotion, compute a fast local summary sufficient to catch a bad target before spending more hours:

- event/record count;
- executing-lane count/mask summary;
- load/store/atomic mix where represented;
- unique exact addresses;
- unique 128B lines;
- unique 4K and 64K pages;
- per-launch footprint;
- object-attribution coverage and UNKNOWN fraction;
- terminal/drop/overflow status.

Do not require a particular page/line count numerically across all kernels. Use it to detect obviously trivial or mis-selected representatives.

## 13. Pipeline V1 publication

For every accepted formal/control bundle:

```text
node109 staging
-> local finalize/hash/manifest
-> ready
-> content-copy to 164 inbox/<RUN_ID>.partial
-> 174-new independent verification
-> one-writer admit
-> immutable catalog entry
-> TRANSFER_ACK
-> node109 ACK verify
-> transferred
```

The known SSHFS limitation is accepted:

- directory `renameat2(RENAME_NOREPLACE)` may return EINVAL;
- receiver uses checked destination absence + same-mount rename fallback;
- formal admission writer concurrency remains one.

## 14. Optional concurrent analysis

The parser at analysis-prep commit `d07b7eb5...` passed exact RTX3090 Q2 regression.

After a run receives a valid destination ACK, it may be analyzed on 174-new immediately. This is useful but must not stall GPU capture if analysis is slower.

A parser failure does not invalidate a valid hash-closed raw capture; repair parser separately while continuing the GPU campaign.

## 15. Acceptance of individual runs

### `FORMAL_TRACE_ACCEPTED`

All of:

- exact model/input/runtime bound;
- exact target/launch identity;
- static GLOBAL MREF set bound;
- nontrivial address-bearing canary passed for representative claim;
- formal raw is complete for the selected bounded window;
- no unacceptable drops/overflow;
- object map available with UNKNOWN preserved;
- Pipeline V1 ACK closed;
- manifest/hash provenance complete.

### `FORMAL_CONTROL_ACCEPTED`

Same integrity requirements, but the run is explicitly a control/audit/context/batch measurement rather than a population representative.

### `BOUNDED_DIAGNOSTIC`

Useful evidence exists but completeness/selection/data-loss conditions do not support a formal representative claim.

### `REJECTED_WITH_EVIDENCE`

Target invalid, trivial, unresolvable, or repeatedly unstable; failure evidence retained.

## 16. Campaign-level acceptance

### `FORMAL_CAMPAIGN_PASS`

Expected when both admitted Qwen deployments have high-quality S2 portfolios covering their principal compute/memory and attention/KV behavior, including useful decode behavior, with Pipeline V1 closure.

This does **not** require every planned candidate row to succeed.

### `FORMAL_CAMPAIGN_PASS_WITH_DEFERRED_CONTROLS`

Core Qwen formal portfolios are complete, while some long-context/batch/audit/Llama/raw7B controls are deferred for clear resource/time/redundancy reasons.

### `FORMAL_CAMPAIGN_PARTIAL_WITH_ROOT_CAUSE`

At least one core deployment yields valid formal traces, but another core deployment cannot close a required representative stratum after evidence-backed recovery. Root cause and attempted repairs are explicit.

### `FORMAL_CAMPAIGN_FAIL`

Reserved for global integrity/authority/infrastructure failure or inability to produce a usable core formal set.

## 17. Required final review pack

Recommended:

```text
docs/vm_tlb/review_packs/C16_FORMAL_TRACE_CAMPAIGN_109_V1/
```

At minimum:

- `README.md`
- `FINAL_DECISION.json`
- `CAMPAIGN_STATE_FINAL.json`
- `SOURCE_ANCHORS.md`
- `DEPLOYMENT_SCENARIO_STATUS.tsv`
- `TARGET_READINESS_CLOSURE.tsv`
- `FORMAL_TRACE_INDEX.tsv`
- `CONTROL_TRACE_INDEX.tsv`
- `REJECTED_OR_DEFERRED.tsv`
- `OBJECT_MAP_INDEX.tsv`
- `STATIC_MREF_INDEX.tsv`
- `NCU_INDEX.tsv`
- `CANARY_QUALITY.tsv`
- `PIPELINE_ACK_INDEX.tsv`
- `TRACE_FOOTPRINT_QUICKCHECK.tsv`
- `RECOVERY_ACTIONS.tsv`
- `RAW_LOG_INDEX.tsv`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

The review pack must make it possible to answer: what was attempted, what recovered, what was captured formally, why each target was representative/control/rejected, and where every hash-closed raw bundle lives on node164.
