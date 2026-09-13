# START — C16 Full-Authority Recovery V3 Goal

Use **Goal mode**.

## Goal

Finish the entire authoritative C16 Lane-G GPU/native/trace scope that remains after the accepted Llama S0 checkpoint, including all required model/scenario rows, rolling raw-artifact copyback to the local/control host, SHA closure, and final dataset publication.

Do not stop at ordinary engineering problems. Diagnose, repair, rerun the smallest affected gate, and continue.

## Read-only handoff branch

```text
hrl/vm-c16-g-retry570-chatgpt-handoff-v7
```

## Active partial checkpoint

```text
2c52c7aa79e5dc131ffefa29bedf5b0018fcdac3
```

## Accepted Llama S0 checkpoint

```text
2e955e007bcabcd3ec24a5f9d24768d27caaee27
manifest: 0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc
```

## Read in this order

```text
docs/vm_tlb/codex_handoff/c16/retry570/C16_FULL_AUTHORITY_RECOVERY_V3_MASTER_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md
docs/vm_tlb/specs/C16_FULL_AUTHORITY_RECOVERY_V3_MATRIX.json
docs/vm_tlb/codex_handoff/c16/retry570/C16_RECOVERY_V3_ASSET_TRANSFER_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/C16_RECOVERY_V3_NATIVE_CENSUS_TARGET_PLAN_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/C16_RECOVERY_V3_CAPTURE_COPYBACK_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/C16_RECOVERY_V3_FINAL_DATASET_CLOSEOUT_HANDOFF.md
```

Fetch/read without checkout/reset/merge:

```bash
git fetch origin hrl/vm-c16-g-retry570-chatgpt-handoff-v7
```

Then use:

```bash
git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v7:<path>
```

for every file above.

## Required execution order

```text
R0 authority/matrix reconciliation
 -> R1 exact identity + asset recovery
 -> R2 transfer/runtime preflight
 -> R3 native baseline + lightweight census
 -> R4 target-plan freeze
 -> R5 NVBit map/canary/repro
 -> R6 formal bounded capture
 -> R7 immediate local copyback/SHA closure
 -> R8 per-deployment publication
 -> repeat all rows
 -> R9 final cross-model dataset closeout
```

Prioritize Wave-1 first, publish a Wave-1 checkpoint, then complete Wave-2 and GLM extension.

## Full model roster

Wave-1:

```text
Llama-3.2-1B
Qwen2.5-0.5B-Instruct
Qwen2.5-7B-Instruct raw
Qwen2.5-7B-Instruct-AWQ
```

Wave-2:

```text
Qwen3-8B
Qwen3-30B-A3B
DeepSeek-V2-Lite
```

User extension:

```text
GLM historical project target — exact identity must be recovered, never guessed
```

## Scenario scope

Dense/smaller:

```text
S0 B1/T128/Decode4 canary
S1 B1/T256/Decode16
S2 B1/T2048/Decode32
S3 B1/T8192/Decode16
S4 B4/T2048/Decode16
```

Qwen3-30B-A3B and DeepSeek-V2-Lite minimum first-round:

```text
S1 B1/T256
S2 B1/T2048
```

Attempt additional scenarios only when identity/resource safety permits.

Do not rerun accepted Llama S0 solely for symmetry. Extend Llama through required S1-S4 work.

## Existing exact identities to reuse

```text
Qwen/Qwen2.5-0.5B-Instruct
@7ae557604adf67be50417f59c2c2f167def9a775

Qwen/Qwen2.5-7B-Instruct-AWQ
@b25037543e9394b818fdfca67ab2a00ecc7dd641
```

DeepSeek authoritative family is DeepSeek-V2-Lite. Verify the retained candidate revision rather than re-opening variant choice from scratch.

Recover exact revisions for Qwen2.5-7B raw / Qwen3-8B / Qwen3-30B-A3B / GLM from authoritative project evidence before execution.

## Critical engineering instruction

Do not treat fixable problems as terminal blockers.

### If GPU server cannot access upstream network

Do not stop.

Use the network-capable local/control host to:

1. download the exact immutable model revision;
2. build file/size/SHA manifest;
3. transfer via the existing SSH/rsync workflow;
4. rehash on GPU server;
5. continue R2/R3.

### If package/runtime fails

Repair the isolated environment without changing frozen scientific identity; add focused tests; rerun only the failed gate.

### If NVBit fails

Verify the pinned known-good NVBit 1.7.5/EAGER/preflight path. Never switch back to NVBit 1.8.

### If trace is zero

First prove whether the selected target launched. Requalify phase-specific targets where needed. Zero does not mean no memory traffic.

### If remote disk pressure appears

Immediately copy already-complete raw data back locally, verify SHA, index it, then delete only the verified remote copy to free space. Continue.

### If a model OOMs

Try all identity-preserving remedies first. Never silently change batch/context/dtype/quantization/model or enable CPU fallback just to make it pass. If the frozen row truly cannot fit the RTX3090, mark only that row `SKIPPED_RESOURCE` with evidence and continue every other row.

## Do not interrupt the user for normal issues

Do not ask the user after each failed command, download, build, timeout, or target mismatch.

Use Goal-mode problem solving:

```text
observe
 -> narrow cause
 -> apply bounded evidence-preserving fix
 -> focused validation
 -> continue
```

Only true external/user-action conditions may remain unresolved:

- gated credentials unavailable;
- exact identity impossible to reconstruct after authoritative search;
- physical GPU resource impossibility under frozen identity;
- no available authorized host/transfer route.

Even then, continue every independent row first and report the exact action needed only in the final exception table.

## Copyback is mandatory

This Goal is not complete while required raw artifacts exist only on the GPU server.

For every successful/partial raw trace or required large census payload:

```text
remote SHA
 -> local/control-host copy
 -> local SHA
 -> equality PASS
 -> local artifact index
```

Use rolling copyback throughout the campaign, not one giant end-of-run copy.

Raw traces must not enter Git.

Final required invariant:

```text
REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0
```

## Frozen runtime

```text
GPU=RTX3090/SM86
Driver=570.124.04
CUDA=12.4
PyTorch=2.5.1+cu124
NVBit=1.7.5
effective CUDA module loading=EAGER
```

NCU permission failure on this instance is already known; do not spend time repeating equivalent NCU permission probes.

## Target-plan policy

Use a valid existing C-lane `NVBIT_TARGET_PLAN` if exact deployment/scenario identity matches.

If none exists, generate and freeze a deterministic `RECOVERY_V3_TARGET_PLAN` from native census using C16 strata/special-semantics rules before capture.

Do not select by naked ordinal. Do not reuse static ranges across models. Do not force one target across prefill/decode.

## Stage acceptance

Do not advance by intuition. Enforce every R0-R9 gate in:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md
```

A failed gate triggers recovery work; it does not trigger a user-facing stop unless a true external condition remains after all safe recovery attempts.

## Publication cadence

- Publish Wave-1 fixed checkpoint as soon as Wave-1 is closed.
- Continue Wave-2 without waiting for manual approval.
- Publish per-deployment/scenario compact packs.
- Finish with one recovery-v3 cross-model dataset publication.

## Preferred terminal status

```text
C16_FULL_AUTHORITY_RECOVERY_V3_DATASET_COMPLETE
```

If true external exceptions remain:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_DATASET_COMPLETE_WITH_EXTERNAL_EXCEPTIONS
```

Do not use generic `BLOCKED_MODELS` for a fixable network/download/build/transfer problem.

## Final response must lead with

```text
RECOVERY_V3_STATUS=
RECOVERY_V3_COMMIT=
PUBLISH_MANIFEST_SHA256=
WAVE1_STATUS=
WAVE2_STATUS=
GLM_EXTENSION_STATUS=
TOTAL_DEPLOYMENTS_COMPLETE=
TOTAL_SCENARIO_ROWS_COMPLETE=
TOTAL_BOUNDED_PARTIAL_ROWS=
TOTAL_RESOURCE_SKIPS=
TOTAL_USER_ACTION_EXCEPTIONS=
ALL_SUCCESSFUL_RAW_LOCAL_SHA_CLOSED=
REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=
TOTAL_LOCAL_RAW_BYTES=
ACTIVE_GPU_PROCESS_COUNT=
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_CAMPAIGN=
```

Then provide one section per deployment with:

```text
exact identity/revision
asset source + hash closure
scenario coverage
native/census status
target-plan ID/SHA
prefill/decode target classes
static ranges/opcodes
formal capture coverage
record/address counts
local raw bytes/path/SHA closure
resource skip or external exception if any
```

Do not finish the Goal until the R9 final dataset pack is committed/pushed and all required successful raw artifacts are locally present and SHA closed.
