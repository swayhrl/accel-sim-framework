# START — Llama first, then finish all remaining multi-model traces

Use **Goal mode**.

## Goal

1. Complete the formal Llama NVBit 1.7.5 target capture first, starting from the already-qualified S0/S1/S2 evidence.
2. Then recover/freeze/acquire the exact remaining model assets and complete Qwen-0.5, Qwen-7B-AWQ, DeepSeek, and GLM.
3. Finish with a cross-model recovery publication.

Do not stop at another legacy-budget blocker.

## Read-only handoff

```text
branch:
hrl/vm-c16-g-retry570-chatgpt-handoff-v5

main handoff:
docs/vm_tlb/codex_handoff/c16/retry570/C16_NVBIT175_RECOVERY_LLAMA_FIRST_THEN_MULTIMODEL_HANDOFF.md

machine spec:
docs/vm_tlb/specs/C16_NVBIT175_MULTIMODEL_RECOVERY_V2.json
```

Active worktree remains:

```text
hrl/vm-c16-g-retry570-v0
```

Do not checkout/reset/merge the handoff branch.

## Start commands

```bash
git fetch origin hrl/vm-c16-g-retry570-chatgpt-handoff-v5

git show \
  origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v5:docs/vm_tlb/codex_handoff/c16/retry570/C16_NVBIT175_RECOVERY_LLAMA_FIRST_THEN_MULTIMODEL_HANDOFF.md

git show \
  origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v5:docs/vm_tlb/specs/C16_NVBIT175_MULTIMODEL_RECOVERY_V2.json
```

Read both completely.

## Critical interpretation

The historical six-window ledger under:

```text
c16_llama32_1b_frozen_compatible
```

is immutable historical evidence, but it is **not** a permanent ban on the newly authorized recovery campaign.

Do not reset or alter it.

Instead create a new campaign/deployment namespace exactly as directed by the handoff, and ledger new capture windows there.

The user explicitly authorizes up to 8 new NVBit capture windows for Llama S3-S5 under the new recovery scope, and up to 8 per later model after S0-S2 qualification.

## Immediate order

```text
L0 revalidate prior Llama S0/S1/S2 hashes
 -> L1 create new recovery budget namespace
 -> L2 S3 narrow capture
 -> L3 S4 independent reproducibility
 -> L4 S5 complete prefill + decode1..decode4 capture
 -> L5 Llama closeout
```

Do not continue to other models until Llama is either:

```text
LLAMA_FULL_TARGET_TRACE_COMPLETE
```

or a new genuine technical/global blocker exists.

Legacy budget exhaustion is no longer an allowed blocker.

After Llama success:

```text
R0 broad metadata-only model/identity recovery
 -> R1 exact-asset acquisition when identity is authoritative but asset is absent
 -> Qwen-0.5 S0-S6
 -> Qwen-7B-AWQ S0-S6
 -> DeepSeek S0-S6
 -> GLM S0-S6
 -> cross-model final publication
```

## Asset recovery correction

Do not repeat the old limited search rooted only at `/root/autodl-tmp/c16_retry570`.

Inspect existing metadata under all relevant existing roots listed in the spec, plus repository/current Git history and retained manifests/receipts.

If an exact model identity/revision is recovered but the asset is missing locally, controlled network acquisition of that **exact** model/revision is now permitted.

No variant guessing, no smaller substitute, no silent quantization/dtype change.

If identity itself remains unresolved after the bounded recovery pass, report `BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER` for that model and continue the others.

## Llama target is already requalified

Unless contradictory evidence appears, use the accepted NVBit1.7.5 S2 target:

```text
function: full mangled indexSelectLargeIndex
static range: [101,102)
opcode: LDG.E.U16
historical 34: forbidden
historical 348: not reused
```

Full Llama capture must cover:

```text
PREFILL
DECODE1
DECODE2
DECODE3
DECODE4
```

Do not declare completion after only one decode step.

## Fixed global runtime

```text
NVBit = 1.7.5
CUDA = 12.4
driver = 570.124.04
PyTorch = 2.5.1+cu124
effective CUDA module loading = EAGER
```

Do not reopen NVBit1.8 diagnosis.

## Goal-mode behavior

For ordinary implementation problems:

- investigate;
- attempt bounded fixes;
- rerun only the smallest affected gate;
- continue.

Do not stop at the first recoverable issue.

For one later model that remains blocked after the expanded asset/identity recovery, publish a precise blocker and continue remaining models.

Stop the whole goal only if a global invariant fails: measurement contamination, runtime-profile drift, storage safety, or raw-artifact integrity.

## Final report

Use the exact lead fields required by the main handoff, beginning with Llama S3/S4/S5 results and then every remaining model.
