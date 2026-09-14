# Open issues and boundaries

- The parser outputs label any reuse/order conclusion as
  `OBSERVED_CALLBACK_ORDER_ONLY`; they do not claim global shared-L2 reuse or
  an MRC.
- The R5 reconciliation establishes artifact and authority closure only.  It
  does not make a scientific or cross-model conclusion.
- The N1 vector-add report is retained solely as an NCU parser fixture.  It is
  never combined with R5 metrics.
- Qwen3-8B and DeepSeek-V2-Lite remain `NO_HISTORICAL_FROZEN_BINDING`; no
  input was inferred, tokenized, or created.
- Future formal bundles require a catalog entry, source-manifest verification,
  and the one-writer Pipeline V1 admission rule before `analyze-run` is used.
