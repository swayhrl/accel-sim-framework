# C16 model/deployment selection freeze

This is a selection-before-results freeze.  The model roles, immutable model
and tokenizer revisions, deployment variants, initial analysis role, and
scenario eligibility in `MODEL_MATRIX.tsv` are fixed before any C16 GPU run,
native timing, counter, trace, cache, or TLB result.  No candidate speedup,
cycle, cache/TLB-miss, or other outcome informed selection.

- Wave 1 retains the historical Llama bridge only to connect prior operator
  knowledge; it does not authorize a restart of the old full-ROI sweep.
- Qwen2.5-0.5B is the low-cost native canary anchor.  Qwen2.5-7B raw and AWQ
  remain separate deployments; any later pair interpretation requires matching
  runtime backend, KV representation, dtype, inputs, and scenario evidence.
- Wave 2 starts only after Wave 1 can publish independently.  Qwen3-8B is a
  dense bridge, while Qwen3-30B-A3B and DeepSeek-V2-Lite are structural MoE/MLA
  holds rather than presumed performance observations.
- The C15 MoE limit is retained: recorded `intermediate_size` values do not
  describe the full routed/shared-expert widths.  They are not valid input to a
  later MoE clustering decision without new direct runtime evidence.

Unavailable local full weights are deliberately retained as explicit gaps, not
silently replaced by another model or revision.
