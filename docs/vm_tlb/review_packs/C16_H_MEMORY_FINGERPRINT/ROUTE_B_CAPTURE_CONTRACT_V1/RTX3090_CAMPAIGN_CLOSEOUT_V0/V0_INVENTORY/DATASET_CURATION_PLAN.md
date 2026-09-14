# Dataset Curation Plan

V0 establishes a logical, not physical, layout:

```text
c16_rtx3090_campaign/{00_manifest,01_raw_authority,02_derived_authority,03_analysis_products,04_failed_and_debug,05_docs}
```

V1 may only proceed after review: copy (not move) receipt-bound `AUTHORITATIVE` raw files to an immutable manifest-backed dataset; retain `DERIVED` analysis separately; preserve `SUPERSEDED` diagnostics until a manifest proves replacement; and resolve every `UNKNOWN_REVIEW_REQUIRED` item. Never use RTX4080 material to fill RTX3090 gaps.
