# Current L2 results: traffic, blocking and performance association — V2

Agent D independent read-only snapshot: **2026-10-27 19:28:08 CST**. No model, registry, frozen consumer, original result or controller was modified. The background campaign continued.

This snapshot has 104 fresh accepted results plus six legal P0 references. Of accepted DH variants, **70 have a same-input DH-P0** across ten programs; seven accepted variants lack DH-P0 and are excluded from self-speedup comparisons. Agent A independently handles uniform-profile GM; no GM or per-program best selection is performed here.

## Raw-counter correction

The frozen strict proof does not extract L2 failure-reason fields, but the raw logs do print positive reasons. Targeted SHA-verified scans identify heartwall merge-entry failures 241/207/144 and vectorAdd miss-queue failures 5,486,196. See `RAW_REASON_ADDENDUM.md/.json` for the corrected evidence; V1 wording conflated unextracted with unprinted. Acceptance and cycles are unchanged.

## Facts

- **69/70 matched variants have exactly equal cycles to DH-P0.** The only nonzero case is heartwall M8: 8,551 → 8,587 cycles, +36 cycles / +0.4210%; DH self-speedup 0.995808.
- **All 70 pairs preserve L2 accepted read volume, read miss volume and DRAM read volume exactly.** 68/69 equal-cycle pairs also have identical complete traffic dictionaries. heartwall M16 is the one equal-cycle pair with changed hit/pending-hit/rejection distribution.
- heartwall M8 lowers L2 read reservation failures from 241 to 207 (−14.11%) while cycles worsen; M16 lowers them to 144 (−40.25%) with exactly unchanged cycles. Fewer rejected attempts do not establish faster application completion.
- Six of these ten paired programs issue zero DRAM read atoms: BlackScholes, dwt2d, gaussian, histogram, lud, mergeSort. The other four have 2, 443, 2 and 405 baseline atoms for heartwall, particlefilter_float, particlefilter_naive and sad respectively. These short completed inputs do not establish behavior of the long pending matrix programs.

## Baseline counter table, same-input DH-P0

| Program | Cycles | L2 accepted read sectors | Read miss sectors | Read reservation-fail attempts | DRAM read atoms | gpu_stall_dramfull | Last avg_mrq_latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| BlackScholes | 8971 | 37500 | 0 | 0 | 0 | 0 | MISSING |
| dwt2d | 73071 | 39144 | 0 | 0 | 0 | 0 | MISSING |
| gaussian | 740717 | 35308 | 0 | 0 | 0 | 0 | MISSING |
| heartwall | 8551 | 26900 | 2 | 241 | 2 | 0 | MISSING |
| histogram | 98202 | 499808 | 0 | 0 | 0 | 395635 | MISSING |
| lud | 478654 | 229832 | 0 | 0 | 0 | 0 | MISSING |
| mergeSort | 111917 | 12716 | 0 | 0 | 0 | 0 | MISSING |
| particlefilter_float | 2100874 | 1080156 | 443 | 0 | 443 | 0 | 9 |
| particlefilter_naive | 384601 | 12960 | 2 | 0 | 2 | 0 | 11 |
| sad | 114870 | 161980 | 405 | 0 | 405 | 0 | 63 |

L2 and DRAM atom size is 32B for these contracts. Reservation failures count rejected attempts, not distinct missing cache lines. Zero above means an available printed counter equals zero; MISSING is not converted to zero. Latency is only the last printed average and is not treated as a whole-application weighted value.

## heartwall: observed nonmonotonic behavior

| Counter | DH-P0 | DH-M8 | DH-M16 |
|---|---:|---:|---:|
| `cycles` | 8551 | 8587 | 8551 |
| `L2_accepted_read_32B_sectors` | 26900 | 26900 | 26900 |
| `L2_read_miss_32B_sectors` | 2 | 2 | 2 |
| `L2_read_reservation_fail_attempts` | 241 | 207 | 144 |
| `L2_pending_hits` | 6 | 14 | 30 |
| `DRAM_read_atoms` | 2 | 2 | 2 |
| `DRAM_read_bytes` | 64 | 64 | 64 |
| `gpu_stall_dramfull` | 0 | 0 | 0 |
| `DTC_OO_lower_issued` | 6725 | 6725 | 6725 |
| `DTC_OO_tag_evictions` | 0 | 0 | 0 |
| `DTC_OO_lower_create_queue_full_stalls` | 0 | 0 | 0 |
| `DTC_OO_ready_but_wb_blocked` | 712 | 700 | 705 |
| `service_ready_to_complete_sum` | 66515 | 67088 | 64281 |
| `service_ready_to_collect_sum` | 47444 | 47729 | 45296 |
| `service_collection_cycles` | 16776 | 16848 | 16839 |
| `service_wb_wait` | 2295 | 2511 | 2146 |
| `service_retired` | 12648 | 12648 | 12648 |

**Association:** increasing merge capacity changes pending-hit counts, reservation rejection attempts and finite-completion-service timing, even though payload volume is unchanged. M8 has larger ready-to-complete and writeback-wait sums; M16 has smaller sums. These changes are consistent with timing/order interactions rather than a traffic-volume reduction.

**Not established:** which individual requests/warps or completion dependencies create the +36 critical-path cycles, whether a specific replacement/order policy is causal, or whether this small effect generalizes to other inputs. Cumulative service sums overlap across observations/SMs and cannot be equated to global application cycles. The source identity `ready_to_complete_sum = ready_to_collect_sum + collection_cycles + wb_wait` holds in all **140/140** available paired endpoint checks.

## The gpu_stall_dramfull name must not be interpreted literally

`gpu-sim.cc:1866` prints `gpu_stall_icnt2mem` under this label. At `gpu-sim.cc:2463–2467`, it increments when an ICNT packet is waiting while a memory subpartition is full. It is aggregated across subpartitions; it is not measured L2→DRAM queue latency or a count of nonoverlapping whole-application cycles.

**Concrete counterexample:** histogram DH-P0 has 395,635 reported gpu_stall_dramfull events versus 98,202 total cycles and zero issued DRAM read atoms. Its completed parameter variants preserve this counter and cycles. That supports an ICNT/L2 admission-pressure interpretation, not a DRAM-read-bandwidth conclusion.

Primary source: Core `9eedb3131937748f0492fa83aad37d3691118d70`, `/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-sim.cc`, SHA `8e159a05a385e2d29799363d5786dcabff6aff770675b8b4221864e6c4f0355c`. Source contexts and the service-counter definitions in shader.cc are preserved in `SOURCE_COUNTER_SCOPE_V2.json`.

## Priority workloads with no current matched variant

| Program | Full frozen input SHA | DH-P0 accepted | Accepted DH variants | Current interpretation |
|---|---|---|---|---|
| 3MM | `977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d` | False | NONE | No matched DH variant at snapshot |
| GEMM | `fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318` | False | NONE | No matched DH variant at snapshot |
| ATAX | `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950` | True | NONE | No matched DH variant at snapshot |
| MVT | `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079` | True | NONE | No matched DH variant at snapshot |
| BICG | `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef` | True | NONE | No matched DH variant at snapshot |

No current L2-parameter conclusion is made for 3MM/GEMM/ATAX/MVT/BICG. Prior PQ/PS or old-build results are not substituted.

## What remains unknown

- Frozen proof extraction omits L2 failure reasons. Targeted closed raw scans recover positive MSHR_MERGE_ENRTY_FAIL counts for heartwall P0/M8/M16 and MISS_QUEUE_FULL counts for vectorAdd DH-E384. Other unscanned or unprinted reasons remain None. No absence is filled with zero.
- Generic tag-conflict, PIB-full and lower-outstanding-peak fields are not printed for these DH-OO records; compatible OO lower-issue/eviction/service counters are retained separately, not silently aliased.
- Last-printed avg_mrq_latency is available only in a subset; it is neither a common whole-application metric nor evidence that missing cases have zero queue delay.
- The early completed subset is strongly short-job censored and has little DRAM-read demand. It cannot justify terminating the authorized full 35-input exploration or selecting a final uniform configuration.

## Every matched pair

All accepted read/miss/DRAM volume deltas below are exactly zero. Each complete endpoint counter table, full input SHA, source path/SHA, UUID, cohort and build identity is in `ANALYSIS_V2.json` under `pairs`.

| Program | Profile | P0 cycles | Variant cycles | DH self | Δ read reject attempts | Δ pending hits | Δ gpu_stall_dramfull | Variant UUID | Result SHA256 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| BlackScholes | E384 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `4c880a0d-9c42-4a7b-b381-d8c063f37f76` | `fcab3dbc375f37a164e30e134ca76182ff4ae831973e47220f59bf10f1d0489e` |
| BlackScholes | E768 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `8a509810-e7c1-4348-886a-7a6d892c0c2e` | `37d0c07e92556d4a997047ae8843e743ffa77824d842d22d342cf0cfceae5d9e` |
| BlackScholes | F128 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `8ff29c71-259a-4edb-a28a-9a36ec05de7c` | `9ef431a4a7c846f69781da71f019b3b1779198bc311ababb02ee9c65171b490e` |
| BlackScholes | F256 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `f2223a75-89ee-45fc-ae8a-d735b8ade457` | `0d42081b1fffe12d5c067057d328e2e80d9adfd291331576b536c0992e7c28e5` |
| BlackScholes | M16 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `44b99904-4f85-4a8c-a267-eeca30c8859e` | `705d01f88894e8730a8cdcd80bdca026f2adb3f1ad533a090ecb680c9682be9b` |
| BlackScholes | M8 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `f7108661-ea96-48d1-ba68-d205d3a1bf2e` | `9d2748cc43f3ea1072512f532982d35d5c4f71103e7aaf546427bd1326b31b27` |
| BlackScholes | Q128 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `65ce74a2-7a5e-45cf-bd8e-5d7d67500bf9` | `c6b60562429f8e7ff6507f336e8901fca0792491e5433bbf9636755d700d7c93` |
| BlackScholes | Q64 | 8971 | 8971 | 1.000000 | 0 | 0 | 0 | `4b9601f9-a0cb-48ec-b0aa-637aca3105b1` | `d2783bbebc8fd81b08a8049c26727a68f0514dd8433d88b066cacc99bee5f0fc` |
| dwt2d | E384 | 73071 | 73071 | 1.000000 | 0 | 0 | 0 | `fcf33ec3-c3e3-425f-a4fe-847684fa2a52` | `36e4d9a7eee2255ec91d4ac1b194a02a386e5d8f158202a01fdd9e85eacb46dc` |
| dwt2d | E768 | 73071 | 73071 | 1.000000 | 0 | 0 | 0 | `175808ab-a766-4a0d-a77c-41cb677708cb` | `f3a5be35a5f621a40f48f8011cde25e32662d44ff9061a25758b4c923250a217` |
| dwt2d | F128 | 73071 | 73071 | 1.000000 | 0 | 0 | 0 | `274522d3-50b4-4418-9ae6-5808c9fb50a2` | `2a8d105e93e1459bb3980b660922f962acc1dbc91a835daa0efb29130789e865` |
| dwt2d | F256 | 73071 | 73071 | 1.000000 | 0 | 0 | 0 | `bd6f7f0b-fc2d-4ce3-aa5d-6bdc0ab66f47` | `f415905433b4f04fee3ff6ed48fd05cd174228ac65aa4c128bab49758b335eea` |
| dwt2d | M16 | 73071 | 73071 | 1.000000 | 0 | 0 | 0 | `d7529f61-e508-49a6-ad7d-375d8eee99ed` | `29c3c4cbbca6e2311e6193ff1c6804e1f78a2c79355ae9a7c6161910ecfef032` |
| dwt2d | M8 | 73071 | 73071 | 1.000000 | 0 | 0 | 0 | `5130c2f5-d8f1-4d4a-9a84-003a04a5e74f` | `e7529011edff919fddc8981c042872a905812aaafcf859415883a86da1d3c742` |
| dwt2d | Q128 | 73071 | 73071 | 1.000000 | 0 | 0 | 0 | `0b0efef3-90d9-4203-aa9b-02857535b5d3` | `102533a84793924e1037396d310dca270cb22f4ba0945cc5fabd4d196245485a` |
| gaussian | E384 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `5ff7b749-0be0-43f8-bc6a-ea82940d12dd` | `a9e7ed76db118cca3029333924e2e3ee845fee38e52dfaff4e970de14b568d2c` |
| gaussian | E768 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `edf1d6e7-c487-45ce-ba1c-21898cd54ada` | `3e3f30656587d131f43c88b3be9c935fafef85e9f1075c3bd0e55642ab0fbffd` |
| gaussian | F128 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `ffcb4f63-3b80-49ca-9223-7cbcb1319666` | `e7964dd5510e66b49af5466fd28014eaf47fe8f4de3ad975e57989bad92518a4` |
| gaussian | F256 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `ba23377a-d47a-4700-a2ed-7dbdbdbcc093` | `7a7edec5116dfad431c404d3c2e9cd270d7340082af9c5a6aea490d16a4773a5` |
| gaussian | M16 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `996aa433-02bc-4643-ba47-2c51d8c3bf42` | `8b28c4df04f8d8be28f9413f931c35334da5c5fbb3b032c48ecaf187b8480a30` |
| gaussian | M8 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `6b173f11-8d8a-4818-b56e-e5ec72a0f23d` | `417a28bfdb99bfbee11913d3c314a3c25e657a85d1ed24ac1fa70895bb367197` |
| gaussian | Q128 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `21e13357-ef8f-40dd-bfb3-b8547b834773` | `4981842b129e232fc4e1c722c4e495eb5e0217cf2d154a95b8c933af4112762c` |
| gaussian | Q64 | 740717 | 740717 | 1.000000 | 0 | 0 | 0 | `86a0966c-a5b9-42af-89ba-e3821a6e8155` | `0720ef461ac3d1d5e29944962d8c35f5ba511ca8554119934c0a5c771b1f91d5` |
| heartwall | E384 | 8551 | 8551 | 1.000000 | 0 | 0 | 0 | `ebe55cb1-0693-49ec-8da5-e0267f368801` | `961861b3e4dc460f010b7e4cd110f91f4bde7e5211d6d47d7b06a890b3717915` |
| heartwall | E768 | 8551 | 8551 | 1.000000 | 0 | 0 | 0 | `a2ffbb3b-4e28-479e-a668-7a45b3220dac` | `cd28458caa0eaad99301fc352eaca685b1a496c6c202d3639328678e2c139d11` |
| heartwall | F128 | 8551 | 8551 | 1.000000 | 0 | 0 | 0 | `3017151c-781c-45bb-b3d0-1eb82e7a9b7d` | `bac564c2e5ec956dd2d102ae56d9d59b973ee991943825b18304cda8b5c628e7` |
| heartwall | F256 | 8551 | 8551 | 1.000000 | 0 | 0 | 0 | `51798f8e-1bbc-4da8-88f3-77c92fe6bde2` | `3b41bf77492e4f094d087df5c8432061f960f2816ed83ca01af8c1cd2b8a1204` |
| heartwall | M16 | 8551 | 8551 | 1.000000 | -97 | 24 | 0 | `dd53f8cf-a404-4d05-8e9b-447824c6e21f` | `72f024d3b566781a9ddd7ff421c687cb1a770390c8fefaa70da351812cfe5340` |
| heartwall | M8 | 8551 | 8587 | 0.995808 | -34 | 8 | 0 | `9fec6c9e-61c9-4886-8b38-60fcc1de07a0` | `22630143afd824132f99358bedee449304febf43cbd6291544ee3fb9c31cee2e` |
| heartwall | Q128 | 8551 | 8551 | 1.000000 | 0 | 0 | 0 | `e87f56e0-1d42-45ad-aa81-4becea002b68` | `e9f3af2abb33809e3bcd727498658273d5ffff4037f31db9e45ff59ea8514372` |
| heartwall | Q64 | 8551 | 8551 | 1.000000 | 0 | 0 | 0 | `fc37290d-942c-4739-9568-fbb7685a556b` | `0f576c39401cb1ad7795c08be30fabff9a06817850eaf4eaf360ada2544188f5` |
| histogram | E384 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `1f653870-6c3d-4da2-a31f-da9e5077d896` | `58e06b3b17fb2bd7832cf24e2213024e72bdf3c7f321f3dc3a00bcbd859f5d7b` |
| histogram | E768 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `f3f3b8db-857f-4718-b83d-329db8ad456d` | `bf3969bc7eff4c7fed284a3495884f4f98b5d8fdcbef78a58948d13b28546c70` |
| histogram | F128 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `4de8da3f-1f88-4e03-a032-b307481d2f78` | `073b90e208deec64e6bcd4180b6defb17c5bd6c6f10260027b5f8e0c9b87c1f8` |
| histogram | F256 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `388315f9-10ae-40bc-8b67-fe1a2a56e292` | `bb39980d28157a31dca321c34b2de830f354241e5bcd4cabb635b8bbf2800513` |
| histogram | M16 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `fc2b9fb7-f643-4094-8d56-e4af9c47c5ba` | `8c197c5065c0b20d2adf611b8b6cebd4a5592af826449ae3675d2708ee0c25bb` |
| histogram | M8 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `852e7c0a-501b-4b3d-9c5f-2597f747b61c` | `98cec0b1dc2173c1b033d9b6e17002ed2195c98bc04a5671895816c7817d4fa3` |
| histogram | Q128 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `a4c18dfe-203d-4b63-ad49-f473027e2efb` | `94226b61233b69d8e9ee5bd2478bfc6569f5ea45e288efce1a18391e0f86e321` |
| histogram | Q64 | 98202 | 98202 | 1.000000 | 0 | 0 | 0 | `30d1c54e-3aa3-4655-bbbd-6fe4377cda9b` | `40eff52291519d66800957000f32021415091b4bd6ab2957f188d903f9d3262f` |
| lud | E384 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `50017380-480e-4fdf-a9a4-f3bff9894441` | `c58484ace468797289347a8bcd891dd79ac56a9ab0535a02852514f56d5710c1` |
| lud | E768 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `d4838467-ce73-4cc8-b5ab-a0b1dc6cf136` | `ae6ac2b39a97a43b279333859eeb6bf33a153b4bbe7e9f38d20678d749b2a530` |
| lud | F128 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `22539e8c-5307-47c6-a56c-52a8f881c3ed` | `9b90df329e50b79842c9410f4e29ebab8645a793843e5a2a66a450ab5a582d1e` |
| lud | F256 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `61ccf22f-f73b-4d30-add8-af426a23d4ce` | `b2082a78e72e7862b18c0103595e9d36865519880c4e02bbf170fdefbc54744c` |
| lud | M16 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `1608e28a-5936-4c12-acfb-b40edfe20f71` | `b38b6f461cc130d8376995cd4cd99e5045b93cf8f0d36768985349855d7828b6` |
| lud | M8 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `a3ae87f6-5cda-435e-8323-5590e493fa38` | `ec469e2403623fdb9f329604dda098e3118ea9ea69392b810f487af2061244f7` |
| lud | Q128 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `8ae5dea1-e1c1-4d3d-a976-8fd3aa372cb5` | `742d2c28af90429aef2b1bf1ab24906707c97ec63f392dbc27d7d94be5da6060` |
| lud | Q64 | 478654 | 478654 | 1.000000 | 0 | 0 | 0 | `f5c4802f-317f-4cc6-b1ae-e2b6750e28e1` | `06adefe4f0e47bec96bca15f5259ec5b564b7ae143ba08e68e60c467c4c2f524` |
| mergeSort | E384 | 111917 | 111917 | 1.000000 | 0 | 0 | 0 | `a0ac99af-e5d5-4975-bc42-a8f702bcae60` | `b9a712871c2ae87440773783ce8b4d99402ab92d98e719de43a7224e784d32f7` |
| mergeSort | E768 | 111917 | 111917 | 1.000000 | 0 | 0 | 0 | `5d135da3-8dab-4f52-9e89-5aaf04ccedb5` | `68cf9711e89129e60617965a5d7edf16df80a2ff56a2a4713c4348bb1838ef59` |
| mergeSort | F128 | 111917 | 111917 | 1.000000 | 0 | 0 | 0 | `4a41e1ad-09f7-45df-a106-7d2f194fac33` | `2140165a8bcc92dd0bd86c6dac505ab7a20b1d5447f631446ce2e6d364df9d8e` |
| mergeSort | M16 | 111917 | 111917 | 1.000000 | 0 | 0 | 0 | `65d5f049-08e0-457e-a0af-761306443c99` | `5191b9364162487e41cbf3777a6938a53e740159db8b010413abbb7456741bfa` |
| mergeSort | Q128 | 111917 | 111917 | 1.000000 | 0 | 0 | 0 | `697e6f33-a26d-41da-af6a-cef73a26004e` | `4b4bf7f58a01a91cdf7683455b680103b347d7df185fc21e93dca12355b32898` |
| mergeSort | Q64 | 111917 | 111917 | 1.000000 | 0 | 0 | 0 | `7fce82d8-79f7-463b-bff6-58c950106b5c` | `b20b0c959f382c4e11d8f41ba51cba73a14d19cb72dd6ed3236b627906de3df5` |
| particlefilter_float | E384 | 2100874 | 2100874 | 1.000000 | 0 | 0 | 0 | `3f64980a-ee72-424b-a196-b47373336563` | `7095cf4f0585a01bc638e02eabfe3c670ba7e6230baea155570f4c2d9fc46183` |
| particlefilter_float | E768 | 2100874 | 2100874 | 1.000000 | 0 | 0 | 0 | `da19d00a-4538-4285-97df-fd2535b43a03` | `d66066528e806301a1435f5688ebae9e01fde21424027ba5eec23e0e091f87df` |
| particlefilter_float | F256 | 2100874 | 2100874 | 1.000000 | 0 | 0 | 0 | `a19a570f-a2db-4537-b68b-1cc7a86dc317` | `ff506a840abba7cdc917d809cd6db1c7ec8babab3ca632c1a378b7daecc08d4a` |
| particlefilter_float | M8 | 2100874 | 2100874 | 1.000000 | 0 | 0 | 0 | `49df1c91-8245-4c53-bc85-7d3721cb4a77` | `f6f5ae4463be20db3f82c255c43b87f778a6df530b0fd7a504ba761df51749a5` |
| particlefilter_float | Q128 | 2100874 | 2100874 | 1.000000 | 0 | 0 | 0 | `212a0e79-4b1d-483d-8b32-ee92f61af902` | `3369fe3b261bd0a9cb2ec1dc736172a84cb80bfa5337370def32966325828201` |
| particlefilter_naive | E384 | 384601 | 384601 | 1.000000 | 0 | 0 | 0 | `797194eb-8dd3-4815-a5c7-4de90fe64e74` | `d6bef57e13412fac315c5ca7307a1c039aa1837c772cbb521e626fe7c43ae6b5` |
| particlefilter_naive | E768 | 384601 | 384601 | 1.000000 | 0 | 0 | 0 | `20d87f47-1286-4a20-961a-ad7e66e5831c` | `a8199dc19f5a8b692ab760cf2d226ab477f6b3c8dfe73392d8ab2e66ab309afc` |
| particlefilter_naive | F256 | 384601 | 384601 | 1.000000 | 0 | 0 | 0 | `650ac5f8-f32c-47f3-bcc8-7d839e95988d` | `b1fad552d50ad2e3514472bbc42db8b42e38aaae3a397167ec23a95728c7e70c` |
| particlefilter_naive | M16 | 384601 | 384601 | 1.000000 | 0 | 0 | 0 | `187a17ae-a97f-43a5-bc34-5342bfc36105` | `3a970aa8ec612da4336cbac2588b72dbed64f9191298345a41864be5336d1912` |
| particlefilter_naive | M8 | 384601 | 384601 | 1.000000 | 0 | 0 | 0 | `69743f58-bcf9-4149-b3f8-95f366b48c14` | `f6efcddd6e9ec0867fad2f2b21c18d0d9dab85ee6deef03499339338e2b6a5d5` |
| particlefilter_naive | Q128 | 384601 | 384601 | 1.000000 | 0 | 0 | 0 | `d5bab8d1-6b5e-499c-bc0b-4ef9a2db4834` | `df2a58645512046c4391f8538575b6a08d13bf2713318e47343e52747b59dce4` |
| particlefilter_naive | Q64 | 384601 | 384601 | 1.000000 | 0 | 0 | 0 | `63b0cbca-11aa-4cdc-8142-b02e0217f054` | `5d77ac6559c0a7abcb54d29a7751065a739a965ef0cd8206f4d5787c6f4d40eb` |
| sad | E384 | 114870 | 114870 | 1.000000 | 0 | 0 | 0 | `4bdb5dc8-db80-4cd9-bb39-0efe33ebd90e` | `cee5074e6b59cf9c98cc5a19172473071b7c1a8191f639bc96694b8a20892eef` |
| sad | E768 | 114870 | 114870 | 1.000000 | 0 | 0 | 0 | `c7595a57-f34c-42b5-b7b7-474406db0057` | `5ec68dc08e8609aa6b304c773d00af34f77573887d15fad283ec0ff9bc88df3a` |
| sad | F128 | 114870 | 114870 | 1.000000 | 0 | 0 | 0 | `29e8274e-8485-4cfa-9d49-e63a6264f0ec` | `6d84087fab62e4962830c114ec563fc0592335b0f150f4b0b62178fc1837c234` |
| sad | M8 | 114870 | 114870 | 1.000000 | 0 | 0 | 0 | `6bed670e-0fb5-4914-b7ea-6b72d7fd5a2c` | `634a4623fb987fbeda60e85b0a8ab07d619456980d87b9e64b4c5ad4e5e2c818` |
| sad | Q128 | 114870 | 114870 | 1.000000 | 0 | 0 | 0 | `6202952f-7edb-4213-be7f-2f66c0087215` | `b14ddbb3ff0027cb473db1745d9e1e2632bbcbd1e5e3826ca45c60922a0bfcb9` |

## Frozen identities and baseline provenance

| Program | Input SHA256 | DH-P0 UUID | DH-P0 result SHA256 |
|---|---|---|---|
| BlackScholes | `b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0` | `8af29f6f-8c8c-4c3f-b541-c86b50798e2b` | `81ccd85d831c67931d22f939897247d66b805cf7dcd67050bb6093adafb8ffb0` |
| dwt2d | `e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008` | `8d91167e-f749-4c2e-90a4-caa6220e2949` | `6c6e3c0a1f09ac958c730914cc9301c18f06c57fd848b86a58827085601e08c7` |
| gaussian | `16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3` | `4e0b7234-d5bc-40a6-8d71-0c7b85be7475` | `2d4cd72fe067dcc235562f095f29bd11a721487f0771775af013d5d08e2b12ea` |
| heartwall | `731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980` | `8c03a83b-0ea4-4b90-8dab-e82ffeb73949` | `5c18b6dd2ce866c6042db1588632a1862e1315b95f2a9635e6aad8ff600d651d` |
| histogram | `3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58` | `cbc3c4d9-9506-4738-b669-91bd49465214` | `3ef7b9b076636a9d839c298ce2365f69632da7a8c6736b3656118953dd0e5bc0` |
| lud | `b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8` | `e62295c7-b5a9-41aa-813c-4f1631d2ee84` | `4fe4f49e527be4294fd324edfb0e30fcee097791e8e987fffb8c23b6406b8fd7` |
| mergeSort | `dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48` | `7b7d633d-f431-4f67-80fb-a468dfd96981` | `7ff810be923c6f06c3f9e746991419e5aa97aa7540d2df800f550c4620658e27` |
| particlefilter_float | `b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4` | `ea290deb-69d7-4fb5-b333-afd53ef84e36` | `9fed62c4c4f877139d1b021b5ab1de913ab766aca34338ed78017ea1aeb0191b` |
| particlefilter_naive | `3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e` | `a661a364-ca9c-4e89-b5eb-3b5fec052b5c` | `aff055d8d21fd4443c6dcbd19441ec7fdc39f6e196dc42dd7b2ed304fee311da` |
| sad | `db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9` | `13d289c8-b23c-470c-9d7f-8e1ea7499348` | `527a707de22bcdb7bba0631728c636093d648014a53247d1e1fe53a3f48fae1b` |

Result source paths are `/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/<cohort>.RESULT.json`; full cohort/path are in every JSON endpoint identity. All rows use Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary SHA `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`.

The immutable raw JSON snapshot is compressed in `SNAPSHOT.json.gz`; the uncompressed SHA is `107add6fda4ad38a61cd35d130f9113ec67a10333746936ede746d79c2dccfee`. The input stream scope proof is `agents/D/report_v1/input_stream_scope.json`, SHA `55b4603466a6ccec914a4898c937c749b2d0a58086a4482c3ef0a58c60eee186`: all 35 inputs are single-stream across 7,368 qualified headers. Last-printed L2 buckets therefore cover each declared trace, separately from numerical correctness of the whole source application. English v0.23 remains unchanged.
