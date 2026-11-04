# Fixed Physical × PIB combination resource accounting

| Per-SM model resource | DH-P0 | Physical768 + PIB192 | Physical1024 + PIB192 |
| --- | ---: | ---: | ---: |
| Physical lifetime/address slots | 640 | 768 (+20%) | 1024 (+60%) |
| Declared 128B-line accounting | 80 KiB | 96 KiB | 128 KiB |
| Active OO instruction PIB entries | 128 | 192 (+50%) | 192 (+50%) |
| Lower-create candidate bound | 128 | 192 (+50%) | 192 (+50%) |
| Lookup Tag mappings | 512 | 512 | 512 |
| Allocation quota per cycle | 4 | 4 | 4 |
| Tag quota: banks × per-bank / total | 4 × 1 / 4 | 4 × 1 / 4 | 4 × 1 / 4 |
| Finite create / inject / retire width | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |

These are declared model counts and address/dependency accounting. They do not demonstrate implemented data payload, RTL area/power/latency, physical timing closure or equal cost. Pool expansion retains more physical lifetimes/generations; Tag512 still supplies only512 lookup mappings, nominally64KiB when counted at128B granularity, not a continuous address span or a larger lookup cache. PIB and lower-create expand together; throughput widths remain fixed. C++ sizeof and process RSS are not hardware area.

COST_DATA.json pins the exact16 frozen candidate options and prior independently reviewed cost package. COST_SOURCE_EVIDENCE.json verifies fixed Core9eed Git bytes and source lines: common.h26/516–556/571–589/637–663/1013–1040; shader.cc3374–3390,3430–3445,3460–3519,3593–3616; shader.h2151–2161; DTC_L1_SPEC.md75–90. All16 declared configs keep64SM,10MiBL2,850MHzDRAM, Tag64×8, four Tag banks, allocation4 and finite service. Runtime actual option echoes remain a strict-result requirement, not inferred from this static table.

The CH-P0 comparison is an absolute cycle ratio to the original CH design; it is not a matched-area hardware comparison. Previously disclosed CH/commonPIB256 and DH/OO admission, compatibility-cache routing, unequal timing, host-upload/invalidation and numerical-coherence limits remain unchanged. No Tag/A2 model or new mechanism is included here.
