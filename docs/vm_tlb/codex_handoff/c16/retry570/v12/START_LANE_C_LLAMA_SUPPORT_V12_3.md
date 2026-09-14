# START Lane C — Llama Support V12.3

You are CPU/code support for the single primary model: Llama-3.2-1B S0.

Read first:

```text
docs/vm_tlb/codex_handoff/c16/retry570/v12/V12_3_PRIMARY_MODEL_COMPLETION_MODE.md
```

Do not run GPU workloads. Do not expand other models.

## P0 — Q1 support

Current clean integration branch/commit:

```text
hrl/vm-c16-g-routeb-q1-integration-local-v0
ac36cbdcfaee44354a42ed952b010dcc7070475a
```

This is already a direct child of Lane A reviewed active HEAD and is the authoritative Q1 integration handoff.

Do not rewrite it unless Lane A reports a concrete Q1 failure. If Q1 fails, fix only the smallest proven issue and produce a new minimal direct-child integration commit based on Lane A's latest active HEAD.

Do not do unrelated refactors while Q1 is running.

## P1 — Q2 ready-to-integrate package

Current Q2 preparation authority:

```text
606a8d6414236362cf1b6e751956f6d794db9704
```

Prepare a minimal file list / patch plan that Lane A can transplant onto the post-Q1 active HEAD without broad branch merge.

Required Q2 assets include only the exact bridge tool/tests/handoff and any narrowly required shared producer support.

Q2 must remain independent of final representative selection.

## P2 — selection/cutlass support

Current selection disposition is fail-closed because the required >=70% duration prefixes include two owner-unresolved CUTLASS requests. Preserve full denominators and keep runnable final IDs empty until required owner evidence closes.

Do not weaken the threshold, remove failed rows, or substitute a nearby kernel.

While Lane A runs Q1/Q2, investigate CPU-side ownership evidence and prepare bounded observer ideas for the two unresolved CUTLASS functions. Do not trigger GPU probes yourself.

Each proposed owner retry must state what NEW evidence it obtains compared with the prior attempt.

## P3 — Route-B formal support

In parallel with Lane A's Q2, prepare:

- deterministic representative whitelist generation;
- deterministic partition manifests;
- canary validator;
- formal-capture parser/manifest generator;
- Route-C coverage analyzer;
- model-level closeout generator.

These must be CPU-only and must not delay Q1/Q2.

## Prohibition

Until Llama `MODEL_TRACE_COMPLETE`:

- do not start Qwen/AWQ/Qwen3/DeepSeek/GLM research expansion;
- do not spend time on publication polish;
- do not rewrite already-closed evidence;
- do not ask Lane A to wait for nonessential CPU work.

## Report only meaningful handoffs

```text
SUPPORT_COMMIT=
Q1_FIX_IF_ANY=
Q2_MINIMAL_PATCH_READY=
CUTLASS_NEW_EVIDENCE_PLAN=
ROUTEB_FORMAL_CPU_SUPPORT_READY=
ROUTEC_CPU_SUPPORT_READY=
PRIMARY_MODEL=Llama-3.2-1B
```
