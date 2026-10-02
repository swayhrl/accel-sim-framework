# Engineering attempts

Gate A initially reported expected-hash mismatches because four SHA constants were transcribed with duplicated characters at wrapped line boundaries. Direct 64-character values from `PARENT_AUTHORITY.json` were substituted; evidence bytes were unchanged, and the complete Gate A audit then passed.

The exact authorized parquet URL was attempted on node109, the local execution environment, and node164. All network paths timed out before receiving bytes. Bounded exact-size searches of known node109 and node164 Hugging Face/cache roots found no byte-identical cached copy. No alternate URL, corpus, split, model, tokenizer, or generated proxy was used.
