# START — C16 full multi-model NVBit 1.7.5 trace campaign

Use **Goal mode**.

## Goal

Complete the entire required C16 Lane G AI-trace campaign across all required models using the already-qualified NVBit 1.7.5 runtime. Do not stop after Llama if later roster models can be safely attempted.

Qualified base checkpoint:

```text
d001a349156c51aa6de15f30b9aedaa70f534442
```

Read-only handoff branch:

```text
hrl/vm-c16-g-retry570-chatgpt-handoff-v4
```

Primary handoff:

```text
docs/vm_tlb/codex_handoff/c16/retry570/C16_MULTIMODEL_NVBIT175_FULL_TRACE_CAMPAIGN_HANDOFF.md
```

Machine-readable roster:

```text
docs/vm_tlb/specs/C16_MULTIMODEL_NVBIT175_FULL_TRACE_CAMPAIGN.json
```

## Start procedure

Do not checkout/reset/merge the handoff branch into the active worktree.

From the current `hrl/vm-c16-g-retry570-v0` worktree:

```bash
git fetch origin hrl/vm-c16-g-retry570-chatgpt-handoff-v4

git show \
  origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v4:docs/vm_tlb/codex_handoff/c16/retry570/C16_MULTIMODEL_NVBIT175_FULL_TRACE_CAMPAIGN_HANDOFF.md

git show \
  origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v4:docs/vm_tlb/specs/C16_MULTIMODEL_NVBIT175_FULL_TRACE_CAMPAIGN.json
```

Read both completely before execution.

## Goal-mode execution contract

Proceed continuously through:

```text
C0 campaign inventory/freeze
 -> Llama S0-S6
 -> Qwen-0.5 S0-S6
 -> Qwen-7B-AWQ S0-S6
 -> DeepSeek S0-S6
 -> GLM S0-S6
 -> C2 cross-model integrity audit
 -> C3 final campaign publication
```

For each model, continue through S0-S6 when the frozen asset exists. If one model is blocked, publish a precise blocker receipt and continue the remaining models instead of ending the entire goal.

Do not ask for confirmation at every normal stage. Make bounded, evidence-preserving fixes when implementation issues occur, rerun the smallest affected gate, and continue.

Stop the whole goal early only when a global invariant is threatened: runtime-profile drift, measurement-window contamination, raw-artifact integrity failure, or storage safety failure.

## Hard locks

```text
NVBit = 1.7.5
CUDA module loading = effective EAGER
CUDA/driver/PyTorch = frozen known-good matrix
no NVBit 1.8 re-debugging
no network model/tokenizer download
no silent model/variant/input substitution
prewarm before MEASUREMENT_ACTIVE
raw traces outside Git
remote SHA -> local copy -> local SHA required
```

“Full trace” means all required occurrences of each model's **requalified target memory instruction/range across its complete frozen workload window**, with prefill/decode attribution. It does not mean indiscriminate all-kernel/all-instruction tracing.

## First action

Before any model run, create the campaign ledger from the roster and reconcile every generic label with existing repository/local frozen evidence. Exact model identity must be known before a model enters S1.

## Final exit condition

Do not finish until every roster model is either:

```text
COMPLETE
```

with validated capture + SHA closure, or one of the explicit evidence-backed BLOCKED states defined in the campaign spec.

The final response must start with the required campaign/model fields from Section 11 of the main handoff and include final commit, manifest SHA256, blocked-model list, total raw trace bytes, and cleanup state.
