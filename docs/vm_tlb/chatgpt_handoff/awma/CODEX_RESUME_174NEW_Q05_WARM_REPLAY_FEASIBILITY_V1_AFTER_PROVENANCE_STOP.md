# CODEX RESUME — 174-new Q05 Warm-Replay Feasibility V1 after provenance STOP

Status: **ACTIVE MAINLINE RESUME**

This file supersedes only the **Start point / provenance gate** in:

`CODEX_NEXT_STAGE_174NEW_Q05_WARM_REPLAY_FEASIBILITY_V1.md`

All scientific objectives, frozen identities, STOP boundaries and deliverables in the original specification remain unchanged.

## Why this resume exists

The prior attempt correctly stopped at:

`STOP_FOR_ENGINEERING_PROVENANCE_REVIEW`

because `origin` could not resolve the reported previous-stage execution branch/commit:

```text
hrl/awma-q05-translation-timeline-174new-v1
reported commit 6319020c4d22311711ee7a090933fefc9830e036
```

The coordination handoff itself is remotely resolvable:

`hrl/awma-q05-context-warmup-handoff-v1`

This is an engineering provenance defect, not a scientific-contract change.

The warm-replay feasibility stage does not scientifically require the previous timeline instrumentation source tree as its code parent. The previous timeline numbers remain comparison/context evidence; the warm-replay stage must independently audit kernel-boundary state from source and independently qualify any new diagnostic instrumentation it adds.

## Authorized recovery routes

Execute Route P1 first. If P1 cannot be proven, use Route P2. Do not invent a third route.

### Route P1 — restore the exact previous execution commit to origin

On 174-new, inspect the local Git object database/worktrees without modifying scientific files.

If and only if the exact object:

`6319020c4d22311711ee7a090933fefc9830e036`

exists locally, prove all of the following:

1. `git cat-file -e <sha>^{commit}` succeeds;
2. the commit is a descendant of the accepted previous source/result anchor `6415d3f1` (or document the exact ancestry if the full SHA of that short commit resolves locally);
3. its tree contains the reported timeline report/review-pack paths or the commit history clearly identifies the reported timeline stage;
4. no rewriting/recommit is needed.

Then push the **same exact commit object** to origin as:

`hrl/awma-q05-translation-timeline-174new-v1`

Do not amend, cherry-pick, squash, reconstruct or create a replacement commit with similar contents.

After push, independently verify from origin that:

```text
origin/hrl/awma-q05-translation-timeline-174new-v1
== 6319020c4d22311711ee7a090933fefc9830e036
```

Record the recovery in:

`PROVENANCE_RECOVERY_RECEIPT.md`

Then create the warm-replay feasibility execution branch from that exact commit and continue D0-D7 from the original specification.

### Route P2 — use the last remotely verifiable accepted source anchor

Use this route only if the exact `6319020c...` commit object is unavailable locally or cannot be safely proven/pushed unchanged.

The authorized parent becomes the remotely verifiable previous Q05 full-translation result:

```text
hrl/awma-q05-full-translation-174new-v1
6415d3f1
```

Verify this parent from origin before creating the worktree.

Create:

`hrl/awma-q05-warm-replay-feasibility-174new-v1`

from that remote-verifiable parent.

Scientific treatment under Route P2:

- the reported timeline results (19/104/240 keys, 106/374/393 merges, etc.) may be cited only as **previous reported diagnostic evidence**, not as source-tree authority for this new stage;
- do not depend on diagnostic code that existed only in the missing commit;
- independently re-audit kernel-boundary state from the accepted source/core;
- if this stage needs new observability/counter instrumentation, implement it independently as disabled-by-default diagnostic code and run the neutrality gate required by the original warm-replay specification;
- existing large timeline raw on node164 may be read as prior evidence if its provenance/hash can be closed, but it does not make `6319020c...` a source ancestor;
- D1B page-key reconciliation may use the durable prior outputs when provenance is adequate; otherwise reproduce only the bounded analysis needed from accepted Q05 trace/simulation evidence.

Route P2 is scientifically valid because this stage asks what state survives kernel boundaries and how to measure Q05 after a warm prefix; it does not require carrying forward the previous timeline instrumentation implementation.

Record:

`PROVENANCE_RECOVERY_RECEIPT.md`

with:

```text
route = P2_REMOTE_ACCEPTED_PARENT
missing_reported_commit = 6319020c4d22311711ee7a090933fefc9830e036
actual_parent = 6415d3f1...
scientific_identity_change = NO
previous_timeline_source_authority_inherited = NO
```

Then continue D0-D7 from the original warm-replay feasibility specification.

## Hard prohibitions during provenance recovery

Do not:

- fabricate a new commit and label it `6319020c...`;
- silently use a local-only branch as scientific authority;
- force-push unrelated history onto an accepted branch;
- modify accepted Q05 SIM_INPUT/baseline/run/evidence identities;
- treat the provenance repair as permission to begin the real predecessor warmup experiment;
- begin any TLB/PTW/cache mechanism experiment.

## Engineering policy

Missing remote branch, stale ref, local object inspection, exact-object push and worktree recreation are solve-and-continue under this resume specification.

Stop again only if:

- neither P1 nor P2 can establish a remotely verifiable parent;
- `6415d3f1` is no longer remotely verifiable;
- local evidence contradicts the reported scientific identity;
- continuing would require changing the frozen Q05/SIM_INPUT/scientific contract.

## Completion

After provenance recovery, continue the original stage normally and finish with the original expected marker:

`AWMA_Q05_WARM_REPLAY_FEASIBILITY_174NEW_V1_COMPLETE_WITH_SCOPE`

The final report must state whether Route P1 or Route P2 was used.