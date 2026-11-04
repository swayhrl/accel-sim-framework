import pathlib,json,hashlib,datetime
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');D=V/'agents/D_independent_review_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 p=D/name
 if p.exists():raise RuntimeError('Immutable file exists '+str(p))
 p.write_text(value if isinstance(value,str) else json.dumps(value,indent=2,ensure_ascii=False)+'\n')
checks=[]
for p in sorted(D.glob('*.json')):
 j=json.loads(p.read_text())
 if isinstance(j,dict) and isinstance(j.get('checks'),list):
  assert all(x.get('pass') is True for x in j['checks']),p
  checks.append({'name':p.name,'sha256':sha(p),'checks':len(j['checks']),'all_PASS':True})
assert any(x['name']=='INDEPENDENT_C_MATRIX_AND_CPU_REPLAY_REVIEW.json' for x in checks),'C review not complete'
rootfinal=V/'root_completion_check_v1/MANIFEST.json';assert sha(rootfinal)=='588cac2fd5d6ea4b2bd8412e3149abeddc3a8d841bce1547ad25787fb19996a1'
for x in json.loads(rootfinal.read_text())['files']:
 p=rootfinal.parent/x.get('path',x.get('relative_path',x.get('name')));assert sha(p)==x['sha256']
C=json.loads((D/'INDEPENDENT_C_MATRIX_AND_CPU_REPLAY_REVIEW.json').read_text());A=json.loads((D/'INDEPENDENT_A_SOURCE_AND_CPU_REPLAY_REVIEW.json').read_text());count=sum(x['checks'] for x in checks)
write('SCIENTIFIC_REVIEW_CHECK_INDEX.json',{'schema':'DTC_V2_D_INDEPENDENT_CPU_REVIEW_INDEX_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_CPU_PREPARATION_WITH_DECLARED_HOLDS','mechanical_checks':count,'check_reports':checks,'A_CPU_case_executions':sum(x['case_count'] for x in A['runs']),'C_CPU_positive_case_executions':len(C['CPU_replayed_positive_cases']),'C_CPU_expected_abort_cases':len(C['CPU_replayed_negative_assertion_cases']),'scientific_execution_approved':False,'new_scientific_models':0,'new_GPU_jobs':0,'new_science_request_or_budget_or_UUID':0,'A2_production_and_science':'HOLD','original16_Tag_safety_HOLD':'PRESERVED_NOT_PERFORMANCE_NEGATIVES','Root_completion_metadata_manifest':{'path':str(rootfinal),'sha256':sha(rootfinal)},'full_universal_liveness_numeric_coherence_RTL_PPA_certification':False})
table='\n'.join('| '+x['name']+' | '+str(x['checks'])+' | '+x['sha256']+' |' for x in checks)
report=f'''# Independent scientific review — Performance-First V2 CPU preparation

**PASS for the documented CPU-only preparation and proposed fixed-Core16-cell contract, with explicit scientific HOLD boundaries. This is not approval to run any V2 scientific simulation.**

Independent Agent D performed {count} recorded mechanical checks, replayed46 directed A fixture case executions (22 original-header and24 isolated-prototype), and independently recompiled/replayed C's19 original-header cases plus2 expected assertion deaths. PASS includes expected no-progress/HOLD and expected assertion-rejection classes. The count is a reproducibility index, not a universal safety theorem.

## Identity and review population

- Core `9eedb3131937748f0492fa83aad37d3691118d70`; Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`.
- Actual simulator SHA `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`; actual libcudart SHA `694f05ce97fe3e1552d94803c2202d8d037769c61624cde5f6a832622ed60c56` independently hashed. C pins their actual paths and both original build receipts.
- Platform remains64SM,10MiB L2,DRAM850MHz; fixed DH-P0 is reused. The eight exact input digests and16 legal CH/DH-P0 references remain the frozen `INPUT_AUTHORITY.fixed.json` SHA `0b9cd6dfe3c397e32ce286ef068717ac4dd563b65855dd245a4fceb08fdadfa1` population.
- B and C preserve their11-accepted/21-awaiting V1 capture. Root's later15-accepted/17-awaiting check is separately pinned completion metadata, not a substituted performance dataset. The16 original larger-Tag safety-HOLD rows stay outside performance GM.
- Stage I `361fa6fa0700825bb9cda43e25b9fd1f60e0b262`, First16 `5f67b4d6b94568a9f1acc80c3e56736bd81e4753`, completed Core32 source `b665d5ea77b5ae022a86cd03c6c464f5b11cb15e`, V1 publication `018d6440c17265205d7b1eab31d9bfa4ee51690d` retain their original roles.

## A: liveness, reachable states and new-mechanism boundary

The unchanged original header independently reproduces both1024-Tag/pool640 counterexamples:640 completed, retired, idle valid mappings remain in the physical pool while a requested set has an invalid way; the next miss repeatedly returns NO_FREE_LINE. Existing target-set Ref0 victim reclamation, live-Ref temporary blocking and this cross-set idle starvation are distinct classes. Neither original HOLD configuration is replaced, retried or classified as a performance regression.

A1's128×4 and32×16 keep512 Tags and pool640. All16 proposed rows retain the fixed eight inputs, accepted DH-P0 sources, binding/config SHA and exact270-option expectation with only logical sets/ways changed. They alter Hash row mapping and associativity together. These are separately proposed parameter experiments; the main combination approval would not release them.

The conditional headroom argument is source-supported: the unchanged single LDST dispatch retains an incomplete load, and retirement requires `next_reference==references.size()`. After fair return/collect/writeback/legal retirement of other fully registered entries, at most512 mapped identities plusN−1 partially registered references remain. The preserved declared-body qualification receipts report N≤32; their parser counts start and last-byte128B lines, and the fixed Core coalescer also handles end-byte segment crossing. Thus the conditional bound is543<640 on this declared-trace domain. Scan's439,384 unaligned addresses are explicitly preserved; natural alignment is not assumed. Unknown future inputs, permanently blocked fences/external dependencies or changed dispatch semantics are outside this argument.

The multiple-partial-PIB API-only adversarial counterexample remains a tested HOLD class. It is not asserted reachable in the unchanged production LDST, and cannot be used to claim a measured production deadlock or to justify prematurely retiring incomplete instructions.

A2's global-idle-LRU prototype reclaims only allocated, ready, matching-generation valid mappings withRef0, no waiter and no same-generation queued return. It clears one selected mapping and uses the lifetime helper; the original Lane X source-event invalidation function is byte-identical. Private-member exposure is confined to directed CPU observation/fault injection. The independent replay reproduces all46 classifications, including expected rejection of stale generations, duplicate returns/releases, live-reference release and bad waiter identity.

**A2 remains PRODUCTION_AND_SCIENCE_HOLD.** Global search/victim policy and whole-instruction reservation change the mechanism. A one-reclaim-per-cycle quota does not model a whole-directory search completing in one cycle. Required next work includes independently versioned Core/binary, real LDST admission/token integration, finite search/Tag-write arbitration/timing, observability, and fresh lifecycle/order regressions. Reservation alone does not fix idle mapped starvation; its conservative32-reference budget admits only20 entries at pool640 and may reduce MLP. No idealized prototype can replace V1's frozen Core or16 safety-HOLD outcomes.

## C: ready proposal, pending scientific execution

The main proposal has exactly16 PLAN cells: physical768+OO PIB192 and physical1024+OO PIB192, each on all eight frozen inputs. Independent review verifies every source/reference/binding/config SHA, all16 distinct identities, actual binary/libcudart bytes, and exact270-option maps. Only `-gpgpu_dtc_l1_physical_lines` and `-gpgpu_dtc_l1_oo_pib_entries` differ from the same-input DH-P0. The PIB option also changes lower-create depth128→192; it is not a pure PIB expansion. Tag64×8, Hash, bank quotas, allocation and finite completion/downstream limits stay fixed.

All new combination cycles, S, CH ratio andJ are null. No native request, UUID or scientific budget has been registered; proposed cohort strings are plans. C's strict template admits only these exact shapes and changes the original legacy parser's640×64 terminal physical gauge bound to the configured768×64 or1024×64 bound. Inverse replacement restores every other legacy parser byte. Terminal conservation/population checks must still run. Runtime270 echo, actual natural terminal, strict conservation and full true164/native-restore qualification remain future scientific obligations; CPU configuration PASS does not claim these have occurred.

The independent C replay covers640/768/1024×PIB128/192, finite wakeup/collection/service limits, merges/de-duplication, generations, legal old-entry retirement under a full pool and new-entry progress, plus duplicate-return/stale-generation assertion rejection. Per-identity Ref is bounded by the192 UID owners because references are de-duplicated per entry;192×32=6144 is a separate conservative aggregate-reference bound, not a single-line observation. Missing runtime PIB/physical pressure or peak counters remain missing; no saturation measurement is invented.

The fixed16-budget future contract correctly leaves whole-family STOP rows deferred/unconsumed without shrinking, refunding or resetting the budget. The earlier ambiguous approved-subset phrase was removed before Root document freeze. There is no hidden canary, baseline rerun, replacement input or additional dispatcher. Root owns any future registration/publication; present authority remains CPU-only.

## B: independently checked measured facts and limits

Before reading data, D verifies accepted source proof, natural EXIT0, source and uncompressed raw SHA. Exactly four already closed DH-P0/physical768 MVT/BICG raw streams are independently parsed; no active raw is read. D additionally checks B's frozen37 public files,22 literal source excerpts against their fixed Git blobs, and four closed CSV/resource members against accepted archive manifests.

| Program | DH-P0 | Physical768 | DH self speedup | CH-P0 / candidate | Main kernel change |
| --- | ---: | ---: | ---: | ---: | --- |
| MVT |34687540|30609855|1.133214777|0.868386178|K1 −4076476; K2 −1209 |
| BICG |28685812|30892841|0.928558562|0.851287779|K1 exact0; K2 +2207029 |

MVT OO misses/lower requests fall43.98% and DRAM reads2.83%; BICG OO misses/lower requests fall37.10% while DRAM reads rise16.44%. More retained physical identities are not more address-searchable logical Tags. BICG K2's explicit40-L2-subpartition CSV entry-limit retries increase142533205→179225930, miss-queue retries15514452→34133834 and merge retries14509→59229. Those are same-run K2-end minusK1-end counters, including actual printed zeros, not relabeled final cumulative totals.

BICG K2 overall miss-count populationCV decreases0.946292→0.924976 across40 L2 subpartitions. This rejects the specific claim of increased whole-phase relative L2-count imbalance; it does not rule out larger absolute load, short hotspots or DRAM-bank contention. Retry events, occupancy means, endpoint allocated gauges and overlapping completion sums are not critical-path blocking time. WB-wait falls in both programs although their cycle responses have opposite signs. Existing evidence supports testable timing/filtering/lifetime hypotheses, not a unique causal attribution. Exact-zero controls and BICG's accepted performance regression remain included.

## Statistics and hardware/correctness costs

D independently recomputes all64 profile rows on the same32-program six-cell intersection from integer cycles: GM(CH-P0/DH-P0)=1.1000721938790632; F128/F256 interaction GM=.9968295092319233/.9985232961680061. Root separately verifies192 RESULT SHA/cycles; D does not claim to have rerun their raw/strict acceptance. The exploratory8 inputs/32 structural cells never become32 exploratory programs or a best-per-program stitched GM.

For each future uniform combination report S_combo=DH0/combo and R_combo=CH0/combo. J=S_combo/(S_physical×S_PIB) requires accepted DH0, physical-only, PIB-only and combo on the same input; the absolute traditional comparison additionally needs its legal CH0. Missing terms makeJ unavailable, not zero. Compare profiles only on a common accepted input intersection and retain every planned row, suite, regression, zero, negative, HOLD and missing reason.

640/768/1024 physical identities represent128B model-accounting grain:80/96/128KiB per SM.768 adds20%,1024 adds60%. The C++ physical-line structure stores lifecycle metadata and has no128B payload array. Neither those nominal bytes nor C++ sizeof/RSS proves functional data SRAM, RTL area, latency, frequency or energy.512 Tags name at most512 lookup mappings; nominal64KiB accounting is not a contiguous span, unique historical-generation set or proof all physical slots are searchable. A historical cost-table phrase `addressspan` is interpreted only in this corrected sense and is not copied into a new scientific claim.

PIB192 and lower-create192 each add50% depth. CH uses actual96KiB geometry/768 Tags, commonPIB256 and traditionalMSHR512:8; selected DH OO uses512 Tags and activePIB128 or192, with separate pending physical identities. Its ordinary fallback/store/atomic cache structure remains present. These are different active structures and timing pipelines, not equal-area hardware. Additional SRAM/metadata, comparators, search, arbitration, ports and wiring are not free; no PPA/numerical result is manufactured.

Preserve existing HtoD/source-event history and source/capture-ELF limitations. The original qualification explicitly says `NOT_NEWLY_CERTIFIED;whole_declared_trace_only` and numerical correctness `UNPROVEN`. CPU liveness/configuration tests cannot certify complete native capture, functional payload, application numeric equivalence or coherence. English v0.23 remains frozen.

## Final reviewed status and authorization boundary

The CPU-only preparation contract passes independent review with all above HOLDs and missing observables declared. No scientific retry, reset, old UUID reuse, V1 configuration/result edit, competing owner/controller, GPU/capture job or manuscript change was performed. Selected consumed identities/budgets/specs and charges are independently checked unchanged while natural terminal metadata may evolve. Root's final completion check is separately pinned at `{sha(rootfinal)}`.

The next scientifically executable proposal is the fixed-Core16-combination contract **only after separate user approval naming the immutable final preparation commit and exact matrix**. The optional16 Tag512 organization proposal requires its own explicit approval. A2 new-mechanism execution remains HOLD and is included in neither batch. This review and CPU PASS grant no native execution permission. Stop at the current authorization boundary.

## Reproducibility index

All paths below are relative to this D packet. Private CPU executables/temp trees and all raw/trace data are excluded from the public manifest. Each check report pins its actual external sources and explicitly states its review scope.

| Check report | Mechanical checks | SHA256 |
| --- | ---: | --- |
{table}

See `REPRODUCE.md`, `SCIENTIFIC_REVIEW_CHECK_INDEX.json` and `MANIFEST.json` for scripts, exact dependencies and qualified outcomes.
'''
write('D_INDEPENDENT_SCIENTIFIC_REVIEW.md',report)
write('REPRODUCE.md','''# Reproduce the independent CPU review

This packet runs on the preserved174-new environment with the fixed true164 packets, input bindings, closed native results and production source/binary paths recorded in the JSON reports. It does not capture new traces, run a simulator/GPU, register requests or alter V1. The old raw streams and CSV/resource files are read only after their accepted receipt/EXIT/hash gates.

The included `dtc_v2_d_*.py` scripts are the exact executed review sources. Every script refuses to overwrite its output report. To replay them, use a fresh private copy with only its D output-directory constant redirected to a new exclusive true164 directory. Keep all scientific source paths and SHA constants unchanged, run scripts in the order listed below, and preserve original frozen outputs. The source bridge reads the preceding fixed8 bound report. These scripts are separate review checks, not scientific experiments.

1. `dtc_v2_d_initial_audit.py`; `dtc_v2_d_cost_review.py`; `dtc_v2_d_root_math.py`.
2. `dtc_v2_d_b_closed_check.py`; `dtc_v2_d_b_csv_review.py`; `dtc_v2_d_v1_preservation.py`.
3. `dtc_v2_d_fixed8_bound.py`; `dtc_v2_d_parser_bridge.py`; `dtc_v2_d_b_source_root_contract.py`.
4. `dtc_v2_d_a_replay_review.py`; `dtc_v2_d_a1_matrix_review.py`; `dtc_v2_d_c_final_review.py`.

Use `python3 -B` for Python. The A/C independent replays themselves compile one fixture at a time with nice19 on CPU132,2GiB address-space,60s subprocess and zero-core-dump limits. Verify CPU132 is still legally free from protected jobs before any later replay; a different safeCPU only changes host execution placement, not scientific configuration. Initial legacy fixture compilation used nice15 with no concurrency and no model. CPU binaries stay private; their SHA and argv are recorded in reports.

Expected A outcomes are22 original and24 isolated-prototype cases, including intentional HOLD/assertion classes. Expected C outcomes are19 original-header cases plus2 deliberate SIGABRT cases. None establishes a universal liveness theorem or replaces future strict270-option/lifecycle/archive/native-restore acceptance. Present CPU-only authorization does not permit the16 planned simulations.
''')
public=[]
for p in sorted(D.iterdir()):
 if p.is_file() and p.suffix in ['.json','.md','.py','.cpp'] and p.name!='MANIFEST.json':public.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
write('MANIFEST.json',{'schema':'DTC_V2_D_INDEPENDENT_SCIENTIFIC_REVIEW_PUBLIC_MANIFEST_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':public,'mechanical_checks':count,'bounded_case_executions':{'A':46,'C_positive':19,'C_expected_abort':2},'status':'PASS_CPU_PREPARATION_WITH_DECLARED_HOLDS','scientific_execution_approved':False,'new_scientific_models':0,'new_request_or_UUID_or_budget':0,'raw_trace_simulator_and_CPU_executables_published':False,'source_or_V1_or_manuscript_modified':False})
print(json.dumps({'manifest_sha256':sha(D/'MANIFEST.json'),'report_sha256':sha(D/'D_INDEPENDENT_SCIENTIFIC_REVIEW.md'),'public_files':len(public),'checks':count,'public_bytes':sum(x['bytes'] for x in public)}))
