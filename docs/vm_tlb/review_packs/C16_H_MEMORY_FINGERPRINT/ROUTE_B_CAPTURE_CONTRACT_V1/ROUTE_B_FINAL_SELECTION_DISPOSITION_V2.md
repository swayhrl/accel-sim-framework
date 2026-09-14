# Route-B final selection disposition V2

`SELECTION_NOT_ADMISSIBLE_DUE_TO_FAILED_CLOSED_COVERAGE`

This is a read-only normalization of active-G map evidence, not a rewrite of
`ROUTE_B_MAP_RESULTS_V2.json`.  The source request document is the historical
frozen V2 manifest at commit `424febe8b4f12eefb4169cc4cc4a1778ef0e660c`:

```text
request SHA-256 = 1a9d9f83b77bb1837f932d0e908e526a749c6811c5955cfb57c96b19b7360110
active map SHA-256 = cfb813f06ec4be0070769f62930e5d67a5f5354f8cb8f821e64ab4a589665d9b
derived selection SHA-256 = d77ceab77293d935d99c51e56e36c4cd964ad8fa36707d2c3f975bb74034e2d9
```

The freezer verifies the request SHA against active map `source_authority`
before it normalizes `full_mangled_function`, `global_mref_count`,
`actual_owning_code_object_sha256`, and `static_map_sha256`.  No missing owner
or MREF count is inferred.

| phase | full duration denominator | minimum >=70% prefix | coverage | failed required member | memory proxy | runnable IDs |
| --- | ---: | ---: | ---: | --- | --- | --- |
| PREFILL | 35,333,473 ns | 25,802,695 ns | 0.7302620662 | `LLAMA_S0_G1_V2_b7ce44b72eb0e85e` | `NOT_PROVABLE_FAILED_CLOSED` | `[]` |
| DECODE | 73,172,157 ns | 53,430,623 ns | 0.7302042907 | `LLAMA_S0_G1_V2_944c439ce7856ba1` | `NOT_PROVABLE_FAILED_CLOSED` | `[]` |

Both required members are `FAILED_CLOSED` with
`CODE_OBJECT_IDENTITY_UNRESOLVED`.  They remain in the full frozen duration
denominator and in the duration ranking.  The older map-authorized request
manifest does not contain per-geometry launch/duration allocations, so the
freezer records them as incomplete and never manufactures a memory proxy from
those aggregates.  This is separately sufficient to prohibit an 80% proxy
claim; it does not weaken the independent duration failure above.

Reproduce the compact result without editing active evidence:

```bash
git show 424febe8b4f12eefb4169cc4cc4a1778ef0e660c:docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/llama_s0_g1_campaign/ROUTE_B_MAP_REQUESTS_V2.json > "$RUN/requests.json"
git show origin/hrl/vm-c16-g-retry570-v0:docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/llama_s0_g1_campaign/ROUTE_B_MAP_RESULTS_V2.json > "$RUN/maps.json"
python3 util/vm_tlb/c16/lane_g/route_b_freeze_selection.py --requests "$RUN/requests.json" --active-map-results "$RUN/maps.json" --output "$RUN/final.json"
```
