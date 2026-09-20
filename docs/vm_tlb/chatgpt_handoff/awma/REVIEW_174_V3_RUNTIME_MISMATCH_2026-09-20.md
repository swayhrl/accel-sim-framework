# ChatGPT Review — 174 V3 Runtime Qualification Mismatch

Date: 2026-09-20

Reviewed execution:
`hrl/awma-repaired-hitpath-validity-174new-v3 @ 2ae0b7732881f29f5565d84ef1b76bae857a3501`

## Decision

V3 scientific sweep remains blocked, but the observed mismatch is reclassified as:

`RUNTIME_ACTIVATION_MISMATCH_ENGINEERING_DIAG_REQUIRED`

not as evidence that the repaired VM model itself failed.

Reasons:
- observed P34 cycles = `871,835`, exactly the historical legacy P34 result;
- required repaired result = `1,619,068`;
- no `AWMA_VM_COVERAGE` marker appeared;
- repaired source patch clearly contains the per-access guards and coverage marker string.

This strongly indicates that the rebuilt repaired core was not the code actually executing, or the rebuilt core artifact/load path was not the one proven in the runtime authority.

## Critical provenance gap

V3 runtime authority records the recovered patch, compiler, config and `libcudart_sha256`.

But the repaired source is in `shader.cc` and `vm_translation.cc`.

Therefore proving only libcudart is insufficient. The next stage must identify and hash the actual loaded simulator core artifact(s) containing these objects.

## Next action

Before any long P34 run:
1. discover the exact executable/shared-library chain;
2. prove which core artifact is loaded at runtime;
3. prove that loaded artifact contains the repair marker/code;
4. prove environment target UID/coverage variables are active;
5. only then launch repaired P34 qualification.

No architecture mechanism is authorized.
