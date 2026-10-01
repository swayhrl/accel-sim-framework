# Matched-template comparison, not a lineage attribution

| Item | DeepSeek-V2-Lite selected expert4 down_proj | OLMoE selected expert58 down_proj |
|---|---:|---:|
| Natural replay input (M,K), BF16 | (1,1408) | (1,1024) |
| Weight (N,K), BF16 | (2048,1408) | (2048,1024) |
| Output (M,N), BF16 | (1,2048) | (1,2048) |
| Kernel family | cuBLAS `internal::gemvx` template-6 | same demangled template-6 |
| Selected static global MREFs | 243 | 243 |
| Executed / zero selected MREFs | 169 / 74 | 129 / 114 |
| Selected static offset+opcode+SASS match | 243/243 | 243/243 |
| CTA x IDs observed in selected traces | 0..511 (512) | 0..511 (512) |
| Warp identities observed per CTA | 2 | 2 |
| Declared launch grid/block | UNKNOWN in accepted legacy log; trace establishes only observed CTA/warp coverage | `512,1,1` / `16,4,1` from accepted shard stdout launch line |
| Weight line visits / unique 128B line | 2.0 record visits; 1 distinct warp | 1.0 record visit; 1 distinct warp |
| Same-CTA / cross-CTA duplicate 32B sector visits | 180,224 / 0 | 0 / 0 |
| Exact duplicate BF16 bytes | 5,767,168 | 0 |

Sources: DeepSeek `REPLAY.json` and `STATIC_MREF_MAP.tsv`, plus its hash-checked C16WARP1 shards; OLMoE shard `ADDRESS_CONTEXT.json`, canonical selector and `shards/static_654/stdout.log` line 13, plus its hash-checked shards. `TRAFFIC_ORACLE.json` records the source-map SHA256 values. The OLMoE launch line is not silently substituted as DeepSeek's launch declaration. Both trace sets show 512 CTA IDs and 1024 distinct `(CTA,warp)` identities at every executed weight MREF, but this does not prove no additional unobserved CTA or warp existed in the launch.

The exact same selected SASS addresses are executed twice per DeepSeek warp and once per OLMoE warp. This closes the *observed* work-assignment difference at the warp/static instruction level. K and effective static coverage differ; N, M, observed CTA and warp coverage do not. The payload has record order but no explicit loop-iteration label, source-level branch decision, or DeepSeek launch dimensions. Thus the evidence supports a `gemvx` shape/work-decomposition classification but not a unique K threshold, precise loop cause, or hardware cache-policy conclusion. It cannot establish a DeepSeek lineage effect. Q30 uses template-7 and was already part of discovery, not a matched holdout.
