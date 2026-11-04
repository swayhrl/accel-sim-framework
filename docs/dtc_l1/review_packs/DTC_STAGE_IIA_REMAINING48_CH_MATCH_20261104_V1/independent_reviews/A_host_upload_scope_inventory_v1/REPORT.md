# CORE32 declared host-upload exposure inventory

Fixed population:32 inputs from contract9627c0fad4395ddf2414e958b897f8f4b73347cf29b70e31ca7f9fa912f0cc6b. All32 commandlist/input bindings and64 original P0 RESULT SHA/identities were checked;6 legal P0 wrapper/underlying cohort+UUID+proof links remain explicit. No simulator raw, trace bodies or live output was read. This is event/configuration scope only, not a safe/unsafe or numerical decision.

| Program | Kernels | Before first: copies / B | Between: copies / B | After last: copies / B |
|---|---:|---:|---:|---:|
| BlackScholes | 1 | 3 / 1200000 | 0 / 0 | 0 / 0 |
| convolutionSeparable | 2 | 2 / 37748804 | 0 / 0 | 0 / 0 |
| fastWalshTransform | 16 | 2 / 2105344 | 0 / 0 | 0 / 0 |
| histogram | 8 | 1 / 65536 | 0 / 0 | 0 / 0 |
| mergeSort | 13 | 2 / 65536 | 0 / 0 | 0 / 0 |
| scalarProd | 1 | 2 / 114032640 | 0 / 0 | 0 / 0 |
| scan | 33 | 1 / 27262976 | 0 / 0 | 0 / 0 |
| transpose | 24 | 1 / 1048576 | 0 / 0 | 0 / 0 |
| vectorAdd | 1 | 2 / 48000000 | 0 / 0 | 0 / 0 |
| bfs | 11 | 10 / 10258248 | 15 / 60 | 1 / 4 |
| cutcp | 11 | 3 / 632888 | 0 / 0 | 0 / 0 |
| histo | 80 | 1041 / 4143368 | 19 / 152 | 0 / 0 |
| mri-q | 4 | 2 / 24576 | 6 / 442368 | 0 / 0 |
| sad | 3 | 1 / 50688 | 0 / 0 | 0 / 0 |
| sgemm | 1 | 2 / 8253440 | 0 / 0 | 0 / 0 |
| stencil | 100 | 1 / 2097152 | 0 / 0 | 0 / 0 |
| 2DCONV | 1 | 1 / 67108864 | 0 / 0 | 0 / 0 |
| 3DCONV | 254 | 2 / 134217728 | 0 / 0 | 0 / 0 |
| 3MM | 3 | 7 / 7340032 | 0 / 0 | 0 / 0 |
| ATAX | 2 | 4 / 67158016 | 0 / 0 | 0 / 0 |
| BICG | 2 | 5 / 67174400 | 0 / 0 | 0 / 0 |
| GEMM | 1 | 3 / 3145728 | 0 / 0 | 0 / 0 |
| GESUMMV | 1 | 5 / 134266880 | 0 / 0 | 0 / 0 |
| MVT | 2 | 5 / 67174400 | 0 / 0 | 0 / 0 |
| dwt2d | 10 | 1 / 110592 | 0 / 0 | 0 / 0 |
| gaussian | 126 | 3 / 33024 | 0 / 0 | 0 / 0 |
| heartwall | 1 | 8 / 1961360 | 0 / 0 | 0 / 0 |
| lud | 46 | 1 / 262144 | 0 / 0 | 0 / 0 |
| myocyte | 5993 | 2 / 436 | 11984 / 2612512 | 0 / 0 |
| particlefilter_float | 36 | 6 / 192392 | 0 / 0 | 0 / 0 |
| particlefilter_naive | 9 | 6 / 48000 | 48 / 384000 | 0 / 0 |
| srad_v1 | 502 | 5 / 927344 | 0 / 0 | 0 / 0 |

Every input has pre-first HtoD. Five have declared interkernel HtoD: bfs15/60B,histo19/152B,mri-q6/442368B,myocyte11984/2612512B,particlefilter_naive48/384000B. bfs additionally has1post-last4B event. The other27 have only pre-first declared HtoD. Unknown commandlists:0; the parser keeps unbound format/order countsUNKNOWN rather than0. Positions are declared command order, not exact runtime hook timing. Addresses/bytecounts do not prove value changes or overlap with OO-read addresses.

All64 P0 proofs explicitly contain prefill1/flushL1=1/flushL2=0/invalidate_on_source_event=0; missing counts0. Source registration defaults at fixedCore9eed are1/0/0/0, with source path/lines/SHA in OPTION_DEFAULT_SOURCE.json. Actual missing fields would stayUNKNOWN even if a source default is known. A matching value does not prove it was inherited from that default; exact config/CLI precedence is not reconstructed. Six aliases preserve underlying P0 identities, not substituted new runs.

All64 also explicitly report n_clusters64,cores_per_cluster1,shader_core_pipeline2048:32, each missing0. This establishes64 simulatedSMs; together with the separately frozen10MiB L2 contract, report this as fixedSM70/V100-derived simulation configuration, not stock/native V100 hardware. No configuration was changed.

FIXED_SOURCE_ENTRY_POINTS.json reuses C myocyte72587 source facts and rechecks current fixed Git bytes: the shown idle-cluster flushL1 entry routes to ordinary m_L1D when source-event flag0; the shown prefill function updates L2 tag state. These selected callsites do not prove that OO state never resets elsewhere or that repeated uploads refresh OO numerical values. The event inventory establishes no stale-data bug or numerical safety. Absence of interkernel HtoD does not certify GPU stores, other host paths or coherence correctness. No input/accepted identity is downgraded or reselected.

Per-input fullSHA, commandlistSHA, P0 -trace pathSHA and source bindings are in CORE32_HTOD_INVENTORY.json. Per-event positions/addresses/bytes are in HTOD_EVENTS.json.gz;64 option/source/alias records in P0_EFFECTIVE_OPTIONS64.json. Candidate/source/trace/application identity limits remain intact. No new simulation, capture, GPU, service, owner/registry/pin/budget/waiter/final24/Git/v0.23 change occurred.
