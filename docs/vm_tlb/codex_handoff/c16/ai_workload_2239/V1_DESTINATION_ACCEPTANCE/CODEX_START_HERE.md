# Codex Start Here — 2239 Destination Acceptance V1

## Branch

```text
hrl/c16-ai-workload-2239-destination-acceptance-v1
```

## Required handoff

Read completely before doing any work:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V1_DESTINATION_ACCEPTANCE/HANDOFF.md
```

Also read all V0 source-export records under:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/
```

## Execute V1 only

Primary objective:

> Admit the destination Docker as the future AI-workload execution environment by recording its actual storage, model/input identity, runtime/toolchain, and already-present authority-bound artifacts. Do not start a new broad workload campaign.

### First checks

1. verify branch and HEAD;
2. inspect `git status` and `git worktree list`;
3. read the V1 handoff and V0 source-export completely;
4. inventory destination-visible storage mounts non-destructively;
5. identify whether any GPU workload is currently active;
6. do not disturb any existing process.

### Required scientific boundaries

```text
RTX4080 R5 authority: b75f26674a09705659e770ab2134351414aa3c93
R5 status: READY_FOR_MULTIMODEL_REVIEW
R4: mechanism-only / non-authoritative
RTX3090 closeout: 649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9
3090 and 4080 remain separate authorities
```

### Destination admission tasks

- bind and record the actual external-storage mount;
- create only a tiny scratch read/write/hash test on the chosen external mount, then remove that test file;
- prove or fail-close exact Llama revision `4e20de362430cd3b72f300e6b0f18e50e7166e08`;
- prove or fail-close the frozen four-hash input bundle without tokenization;
- record Python/PyTorch/CUDA/transformers/GPU/toolchain identity;
- verify NVBit 1.7.5/tracer identity if present, otherwise classify rebuild/verify required;
- record NCU version/identity and permission state without broad profiling;
- read-only reconcile known N1/U8 artifacts if visible;
- do not infer R5 U5/U6/U9 raw authority from filenames or PASS summaries;
- prepare long-term destination storage namespaces but do not bulk-copy source data.

### GPU rule

A GPU diagnostic is optional, not required.

If any unrelated/current workload is active, record:

```text
GPU_DIAGNOSTIC_DEFERRED_ACTIVE_WORKLOAD
```

and do not run a fixture.

Never kill or reset another process. Never attach a profiler/tracer to an existing workload.

### Required outputs

Write only new V1 result files under:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V1_DESTINATION_ACCEPTANCE/RESULTS/
```

Required files:

```text
DESTINATION_STATE.md
DESTINATION_RECEIPT.json
STORAGE_ADMISSION.json
MODEL_ADMISSION.json
FROZEN_INPUT_ADMISSION.json
RUNTIME_TOOLCHAIN_ADMISSION.md
ARTIFACT_RECONCILIATION.tsv
OPEN_ISSUES.md
V1_DECISION.json
```

### Hard constraints

```text
NO source evidence deletion/move/rewrite.
NO bulk data migration.
NO 3090 recovery-root copy.
NO broad Llama rerun.
NO broad NVBit capture.
NO broad NCU profiling.
NO tokenizer regeneration.
NO silent model redownload/update.
NO process killing/reset.
NO large data in Git.
NO secrets/private keys/tokens/passwords in Git.
NO unnecessary private network inventory in Git.
NO UNKNOWN_PROVENANCE promotion without exact receipt/path/hash evidence.
```

### Finish

1. self-review all V1 outputs;
2. verify no existing scientific evidence was modified;
3. commit;
4. push current branch;
5. stop;
6. report branch, final commit, decision, storage mount admission, model/input admission, runtime/toolchain state, reconciled artifacts, open issues, and whether any GPU diagnostic was run.

Do not proceed to storage import or a new workload campaign after V1.
