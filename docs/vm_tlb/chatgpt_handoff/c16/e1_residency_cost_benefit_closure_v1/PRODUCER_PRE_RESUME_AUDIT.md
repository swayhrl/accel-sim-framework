# Residency Cost/Benefit Producer Preliminary Audit Before 174 Resume

## Producer

`hrl/c16-e1-residency-cost-benefit-closure-109-v1@86ef7dcfb49241bd87ff4a8d59b4d950d53de0a5`

No node109 rerun is requested.

## Preliminary closure

The producer evidence is internally consistent with:

- four preregistered budgets:
  - 8 MiB
  - 16 MiB
  - 24 MiB
  - full-qweight request
- 7 CONTROL + 7 FAIR fresh processes per budget;
- exact all-28 up_proj policy windows;
- all 28 up_proj remain MATERIAL_LOCAL at every budget;
- no budget yields a positive whole-decode effect beyond dispersion;
- no budget reaches the 2% system gate;
- top-level semantic decomposition qualifies at every budget;
- median unexplained residual remains below 0.10 ms;
- stage label:
  `RESIDENCY_OFFSET_LOCALIZED`.

## Key measured decomposition

Representative medians:

### B8
- direct up saving: ~0.361 ms
- gate saving: ~-0.127 ms
- down saving: ~-0.201 ms
- self-attn saving: ~-0.029 ms
- whole decode saving: ~+0.053 ms
- whole-decode benefit median ~+0.31%, but not beyond dispersion

### B16
- direct up saving: ~0.364 ms
- gate: ~-0.300 ms
- down: ~-0.090 ms
- self-attn: ~-0.045 ms
- whole decode saving: ~-0.094 ms

### B24
- direct up saving: ~0.415 ms
- gate: ~-0.389 ms
- self-attn: ~-0.094 ms
- whole decode saving: ~-0.086 ms

### BFULL
- direct up saving: ~0.576 ms
- gate: ~-0.146 ms
- down: ~-0.030 ms
- self-attn: ~-0.534 ms
- norm: ~+0.074 ms
- whole decode saving: ~-0.028 ms
- unexplained residual: ~+0.006 ms

The previous ~0.36-0.44 ms unexplained accounting residual is therefore no longer unexplained at the top-level semantic accounting scale.

## Causal boundary

Do not translate semantic localization into a unique cache cause.

At full budget:
- aggregate 28-layer self-attention timing is slower;
- representative L0 self-attention NCU does **not** reproduce a comparable duration/traffic slowdown.

Therefore the supported statement is:

> the offset is localized to directly measured non-up semantic categories, with aggregate self-attention the largest full-budget component.

Unsupported:
- one particular self-attention kernel causes the offset;
- L2 hit-rate loss uniquely causes the offset;
- aggregate DRAM traffic uniquely causes the offset.

## Important architectural implication for later review

The CUDA persisting-L2 intervention demonstrates both:
- repeatable up_proj-local value;
- system-level interference/cost elsewhere.

This makes a later simulator counterfactual meaningful only if it explicitly tests a **cost-aware/elastic** policy rather than copying CUDA set-aside semantics.

The previously reviewed `M1_ELASTIC_PROTECTED_QUOTA` remains relevant because its purpose is to protect high-value lines while permitting ordinary traffic to use otherwise-unused capacity and preserving ordinary replacement fallback.

However, this producer alone does **not** authorize simulator implementation.
Independent 174 closure remains required.

## Producer raw packaging

Native files expose:
- condition/budget/mode;
- all 84 child occurrences;
- non-overlapping top-level occurrences;
- decode timing;
- complete policy receipt and ordered transitions;
- requested/actual set-aside;
- top-level/child call order.

NCU:
- exact 8-profile matrix;
- application replay;
- cache-control none;
- multi-pass receipt identity must close as in prior stages.

174 should normalize directly from raw evidence and preserve source SHA provenance.
