# EP-L2 Codex Target Goal — M0a + M1 Speculative Integration

## One-line goal

> Merge the exact frozen M1 substrate and M0a observability candidates into one isolated D512-based source family, prove M1 baseline equivalence and M0a timing neutrality on the integrated source, preserve explicit mode/provenance controls, optionally prepare observation-only M0b scaffolding, and stop at an interim review-ready state while final M0a/M1 promotion gates remain external dependencies.

## Read first

```text
docs/ep_l2/project_spec/README.md
docs/ep_l2/project_spec/MECHANISM_SEQUENCE_CURRENT.md
docs/ep_l2/project_spec/EXPERIMENT_MODE_SWITCH_CONTRACT.md

docs/ep_l2/chatgpt_handoff/M0A_INTERIM_CHATGPT_REVIEW.md
docs/ep_l2/chatgpt_handoff/M1_INTERIM_CHATGPT_REVIEW.md
docs/ep_l2/chatgpt_handoff/M0A_M1_SPECULATIVE_INTEGRATION_POLICY.md
docs/ep_l2/chatgpt_handoff/M0A_M1_INTEGRATION_HANDOFF.md
docs/ep_l2/chatgpt_handoff/M0A_M1_INTEGRATION_ACCEPTANCE_CRITERIA.md
```

Treat the handoff as executable scope and the acceptance criteria as mandatory self-gating.

## Exact source inputs

```text
M1 Core       955a50cbb5e8d928b6c7b0c78e1af062b835df44
M1 Framework  aae62b66685f15437cecf0193934f628e6fac6ae
M0a Core      666f0ba2d7b6a027f395346e274a934c19fdd3c1
M0a Framework 2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d
```

Create fresh integration worktrees/branch/result root as specified in the handoff.

## Autonomous execution order

1. Integrate exact frozen source deltas; do not merge moving branch tips.
2. Resolve only mechanical config/telemetry overlap.
3. Run Release build and full directed M1 + M0a integration tests.
4. Add explicit run-manifest mode/feature-vector provenance if missing.
5. Run compact natural BASE/M0a-ON equivalence checks.
6. Publish interim integration evidence with `SPECULATIVE_PENDING_GATE` maturity.
7. If all integration self-gates pass, prepare OFF-by-default M0b observation scaffolding only; do not run/promote a mechanism-opportunity campaign yet.

Do not wait for the live M0a scan to complete before performing steps 1-7.

## Hard boundary

Do not interrupt/restart M0a scan. Do not implement functional Unified, RO-pending, TVD, adaptive policy, or headroom. Do not change the calibrated D512 base resources.

## Required output

```text
docs/ep_l2/review_packs/M0A_M1_INTEGRATION_INTERIM_r1/
docs/ep_l2/codex_handoff/LANE_INT_LATEST.md
```

Final status for this target:

```text
M0A_M1_INTEGRATION_INTERIM_REVIEW_READY
```

Then STOP and request ChatGPT review.
