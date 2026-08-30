# EP-L2 Codex Target Goal — M1 Elastic Substrate

## Goal

> Starting from the accepted D512 research baseline, implement the global payload-ID/handle + tag-sidecar substrate in a static-compatible form, prove exact parent behavior/timing equivalence, publish review-ready source/test evidence, and STOP before any functional resource borrowing or pending/TVD mechanism.

## Read first

```text
docs/ep_l2/project_spec/README.md
docs/ep_l2/project_spec/decisions/ADR-005-calibrated-research-baseline.md
docs/ep_l2/project_spec/decisions/ADR-006-unified-payload-opportunity-precondition.md
docs/ep_l2/project_spec/decisions/ADR-007-m1-substrate-is-infrastructure.md
docs/ep_l2/project_spec/EXPERIMENT_MODE_SWITCH_CONTRACT.md
docs/ep_l2/project_spec/MECHANISM_SEQUENCE_CURRENT.md
docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_CHATGPT_REVIEW.md
docs/ep_l2/chatgpt_handoff/M1_ELASTIC_SUBSTRATE_HANDOFF.md
docs/ep_l2/chatgpt_handoff/M1_ELASTIC_SUBSTRATE_ACCEPTANCE_CRITERIA.md
```

Also inspect the detailed Lane-F design pack on `hrl/ep-l2-mechanism-prep-v0`.

## Semantic parent

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

## Worktree

Prefer:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-m1/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-m1/
branch    hrl/ep-l2-m1-elastic-substrate-v0
results   /workspace/results/ep_l2_m1_equivalence/
```

## Execute autonomously

1. Re-audit exact source locations before editing; write a short source semantic map into the review pack.
2. Implement one global 1152-slot physical payload namespace, explicit role/owner/generation state, canonical payload handle and tag-index sidecar.
3. Preserve static resident mapping `tag_index -> payload_id=tag_index`; preserve directed bypass-model `1024+j` mapping; preserve bank modulo and arbitration.
4. Integrate allocation/rollback/fill/release paths without changing tag/MSHR/descriptor/WAD/lower semantics.
5. Implement/validate default static post-M1 mode under all functional mechanism bits OFF. Do not retain a long-term duplicate pre-M1 payload implementation merely for a substrate feature bit.
6. Add directed lifecycle/rollback/stale-fill/bank/terminal tests and config/provenance checks.
7. Release build + existing EP-L2 regressions.
8. Freeze source/config.
9. Run exact parent-vs-post-M1 equivalence on vectorAdd, convolution, cfd, sad and FWT7; launch independent rows in parallel where safe.
10. Self-repair only within M1 representation/plumbing scope. Any need for borrowing/new consumer/new capacity semantics is a hard stop.
11. Publish the review pack and report.

## Required status

```text
M1_ELASTIC_SUBSTRATE_REVIEW_READY
```

Then STOP for ChatGPT review.
