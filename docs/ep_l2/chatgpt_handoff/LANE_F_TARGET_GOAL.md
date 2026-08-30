# EP-L2 Codex Target Goal — Lane F Mechanism Implementation Prep

## One-line goal

> Independently audit the current EP-L2 source and convert the staged mechanism roadmap into exact source/state-machine/allocator/lifecycle modification plans for M0/M1/M2, with M3/M4 dependency maps, so functional implementation can begin immediately after baseline-decision review without changing simulator behavior in this lane.

## Start location

```text
/workspace/worktrees/accel-sim-ep-l2/
branch hrl/ep-l2-exp-v0
```

Fetch/pull latest.

## Read first

```text
docs/ep_l2/project_spec/README.md
docs/ep_l2/project_spec/RESEARCH_CHARTER.md
docs/ep_l2/project_spec/ARCHITECTURE_BLUEPRINT.md
docs/ep_l2/project_spec/EVIDENCE_AND_CLAIM_MODEL.md
docs/ep_l2/project_spec/WORKLOAD_CHARACTERIZATION_SCHEMA.md
docs/ep_l2/project_spec/WORKLOAD_ARCHETYPES_PRELIMINARY.md
docs/ep_l2/project_spec/MECHANISM_IMPLEMENTATION_PLAN.md

docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_ACCEPTANCE_CRITERIA.md
```

Treat the handoff and acceptance criteria as the complete target-mode contract.

## Worktree

Create a new **read-only-analysis-oriented** source worktree if useful, for example:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-mechanism-prep/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-mechanism-prep/
branch    hrl/ep-l2-mechanism-prep-v0
```

Do not modify Lane A/B/C/D/E active/frozen worktrees.

## Source parents to inspect

```text
Formal C7e Core       ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Formal C7e Framework  f08d2ce857972fad73c4e1ab7162ba94c6336507

D512 Core             878f80869ce212e779df20b6421e4dc7f987825d
D512 Framework        aae62b66685f15437cecf0193934f628e6fac6ae
```

## Execute

Audit exact source/state transitions and produce the review pack required by `LANE_F_MECHANISM_PREP_HANDOFF.md`.

Prioritize M0/M1/M2 depth over speculative M3/M4 implementation detail:

```text
1. exact payload lifecycle/source map
2. static role-partition enforcement points
3. behavior-preserving M1 allocator/substrate refactor
4. safe M2 shared-pool allocation design
5. exact M0 telemetry producer points
6. RO/WAD/TVD dependency maps
```

No functional mechanism code or simulator experiment is authorized.

## Completion

Publish:

```text
docs/ep_l2/codex_handoff/LANE_F_LATEST.md
docs/ep_l2/review_packs/MECHANISM_IMPLEMENTATION_PREP_r1/
```

Status:

```text
MECHANISM_IMPLEMENTATION_PREP_REVIEW_READY
```

Push documentation/design-only artifacts and STOP for ChatGPT review.
