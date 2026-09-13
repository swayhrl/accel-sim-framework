# Retry570 NVBit-native static-map closeout

Status: `NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED`.

This diagnostic used an NVBit 1.8 mapper based directly on `nvbit_get_instrs(ctx, f)`, `Instr::getIdx()`, `getOffset()`, `getOpcode()`, and `getSass()`. It requires exact equality with the full mangled `indexSelectLargeIndex` identity; it has no kernel-name-substring fallback.

`348` is retained only as `HISTORICAL_CANDIDATE_ORDINAL`; `34` is retained only as `SASS_TEXT_LINE_COUNTER`. Neither is an NVBit static index. The bounded same-binding Llama S0 map-only run reached model load but timed out at 180 seconds before a model forward, target function launch, or map payload. No `LLAMA_INDEXSELECT_NVBIT_STATIC_MAP.tsv` was produced.

Accordingly no target instruction, exact-memory trace, C16 tracer, Qwen0.5 run, or C frozen target is authorized. This is not a disambiguated zero-record NO-GO and not a model/NVBit incompatibility claim. Retained logs and ledger/marker reconciliation artifacts are dual-endpoint hash closed; raw payloads remain outside Git.
