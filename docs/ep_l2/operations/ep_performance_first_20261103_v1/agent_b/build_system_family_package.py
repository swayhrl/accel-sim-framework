import csv,copy,hashlib,json,datetime
from pathlib import Path
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
P=Path(__file__).resolve().parent
C=Path('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core')
CORE='78f4b59e865b136eede74df74c44c210f5b4ca04'
ELF='78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a'
def dump(name,x):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');return ref(p)
def ref(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
summary=J/'review/docs/ep_l2/operations/ep_full_workload_performance_20261027_v1/results_analysis/RESULTS_ANALYSIS_CURRENT.json'
x=json.loads(summary.read_text())
profiles={'D_DRAM_MHZ1020','D_LOWERFIFO256','U_L2MQ256','N_ICNT_BUFFERS1024','COMBO_G64W16_UD2','COMBO_ICNT_LOWER2','COMBO_G64W8_L1L2MQ2'}
reuse=[p for p in x['pairs'] if p['profile'] in profiles]
dump('EXISTING_SYSTEM_PAIRS_REUSE.json',dict(schema='EP_PF_EXISTING_SYSTEM_PAIR_METADATA_REUSE_V1',status='READ_EXISTING_ACCEPTED_SMALL_SUMMARY_NOT_NEW_ACCEPTANCE',summary_ref=ref(summary),pairs=reuse,trace_reads=0,raw_reads=0,model_starts=0))
with (P/'EXISTING_SYSTEM_PAIRS_REUSE.csv').open('w',newline='') as f:
 fields=['program','profile','S_cohort','F_cohort','S_cycles','F_cycles','speedup_S_over_treatment','S_absolute_REF_over_S','F_absolute_REF_over_F','relative_EP_ratio_change_vs_reference']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:p.get(k) for k in fields} for p in reuse)

def family(id,cls,options,stages,guard='SOURCE78_CONFIG_SUPPORTED_HOST_NATIVE_REBIND_REQUIRED',note=''):
 return dict(id=id,classification=cls,controlled_options=options,stages=stages,engineering_status=guard,note=note,new_performance_status='NOT_RUN_NOT_AUTHORIZED')
families=[
 family('DRAM_CLOCK','REALISTIC_ARCHITECTURAL_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_clock_domains':{'REF':'1132.0:1132.0:1132.0:850.0','screen':['1132.0:1132.0:1132.0:1020.0'],'diagnostic':['1132.0:1132.0:1132.0:1275.0','1132.0:1132.0:1132.0:1700.0']}},['first: FWT S/WV @1020, GEMM S/WV @1020','Vector4M S/F @1275 diagnostic','conditional @1700 or combine with surviving queue family'],note='DRAM cycle timing integers stay fixed: frequency changes ns service timings and bandwidth together. Not a bandwidth-only intervention. Legacy 1020 on Vector/Conv is reusable; do not repeat.'),
 family('L2_MISS_QUEUE','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_cache:dl2':{'REF':'S:32:128:8,L:B:m:L:P,A:128:1,128:0,32','screen':['S:32:128:8,L:B:m:L:P,A:128:1,256:0,32'],'diagnostic':['S:32:128:8,L:B:m:L:P,A:128:1,512:0,32']}},['reuse old 256 Conv/Vector/SGEMM first','conditional FWT/GEMM S/WV @256 only when reference exposes MissQ rejection','@512 only if accepted @256 remains full or gains >=2%'],note='Changes MissQ token only. Does not change line-MSHR128 or nominal merge1. D512 changes effective merge cap to32.'),
 family('L2_LOWER_FIFO','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_dram_partition_queues':{'REF':'64:128:64:64','screen':['64:256:64:64'],'diagnostic':['64:512:64:64']}},['reuse old LOWERFIFO256','conditional FWT or GEMM exact S/WV @256 if lower-full observed'],note='Tuple=ICNT->L2:L2->DRAM:DRAM->L2:L2->ICNT. Increasing FIFO does not directly change fixed latency.'),
 family('DRAM_SCHEDULER','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_frfcfs_dram_sched_queue_size':{'REF':'128','screen':['256'],'diagnostic':['512']}},['Vector4M S/F @256 only if c7e scheduler causal block or occupancy supports it','expand @512 only if @256 remains saturated'],note='Credit coupled by production formula: shared credit=FRFCFS+ReturnQ-(subpartitions-1), so 128/192 gives319,256/192 gives447. Not scheduler-only isolation.'),
 family('DRAM_RETURN_QUEUE','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_dram_return_queue_size':{'REF':'192','screen':['384'],'diagnostic':['768']}},['only if measured return blockage','same input S/F matched pair'],note='Also changes partition credit: 128/384 shared511. Credit, scheduler, and ReturnQ counters overlap; do not sum as exclusive stall cycles.'),
 family('ICNT_BUFFER','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-icnt_in_buffer_limit':{'REF':'512','screen':['1024'],'diagnostic':['2048']},'-icnt_out_buffer_limit':{'REF':'512','screen':['1024'],'diagnostic':['2048']}},['reuse all old1024 pairs; near-zero cases prune','new FWT/GEMM only if accepted injection or return stall evidence'],note='Active network_mode2 local crossbar, two subnets; limits represent local buffering, not BookSim mesh bandwidth.'),
 family('ICNT_CLOCK','DIAGNOSTIC_RELAXED_NOT_REAL_GPU',{'-gpgpu_clock_domains':{'REF':'1132.0:1132.0:1132.0:850.0','screen':['1132.0:1698.0:1132.0:850.0'],'diagnostic':['1132.0:2264.0:1132.0:850.0']}},['only when queue buffer family does not remove injection/return stall','same Source S/F pair; keep DRAM850 and L2/core1132'],note='Changes ICNT event cadence, not core, L2 or memory frequency. Physical crossbar implementation unqualified.'),
 family('FIXED_MEMORY_LATENCY','DIAGNOSTIC_RELAXED_NOT_REAL_GPU',{'-dram_latency':{'REF':'100','screen':['50'],'diagnostic':['0']}},['candidate only, not first default expansion','same input S/F or S/WV'],note='Delay deadline uses gpu_sim_cycle+gpu_tot_sim_cycle, not pure DRAM service latency. Reducing L100 is a sensitivity lineage. Preserve FIFO, credit, FRFCFS, bank timings and850MHz.'),
 family('L1_MISS_QUEUE','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_cache:dl1':{'REF':'S:4:128:128,L:T:m:L:L,A:512:8,16:0,32','screen':['S:4:128:128,L:T:m:L:L,A:512:8,32:0,32'],'diagnostic':['S:4:128:128,L:T:m:L:L,A:512:8,64:0,32']}},['reuse existing combo as context only, not isolated effect','conditional single-factor pair when L1 queue stalls measured'],note='Preserves L1 ways/capacity/MSHR/merge and policy. Existing L1L2MQ2 combo is not single-factor proof.'),
 family('UPSTREAM_RESPONSE','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_n_ldst_response_buffer_size':{'REF':'2','screen':['4'],'diagnostic':['8']}},['only if shader response-buffer backpressure observed','pair same S/F'],note='Do not alter core issue widths or unvalidated trace semantics.'),
 family('LINE_MSHR','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_cache:dl2':{'REF':'A:128:1','screen':['A:256:1'],'diagnostic':['A:512:1']}},['new Source explicit supported range; shared mshr_table/RO CPU tests; full new-ELF S/F references'],guard='NEW_SOURCE_REQUIRED_WV_F_AND_MS_OBSERVER_GUARD',note='gpu-cache.h3340/3347/3355/3373 pin128. Do not delete guards; qualify exact capacities and resource costs.'),
 family('DESCRIPTOR_AND_MERGE','FINITE_HARDWARE_CAPACITY_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_ep_l2_descriptor_pool_size':{'REF':'512','screen':['1024'],'diagnostic':['2048']},'-gpgpu_ep_l2_descriptor_per_line_cap':{'REF':'32','screen':['64'],'diagnostic':['128']}},['two separate single-factor subfamilies, no automatic simultaneous change','Agent C owns RO concurrency extension and CPU protection proof'],guard='NEW_SOURCE_REQUIRED_RO_CONSTRUCTOR_AND_MODE_GUARDS',note='ep-l2-ro-transactions.h86 exactD512; per-line source guard32. Nominal dl2 merge1 does not override shared descriptor cap32.'),
 family('PAYLOAD_BANK','FINITE_HARDWARE_THROUGHPUT_CANDIDATE_PPA_UNKNOWN',{'-gpgpu_ep_l2_bank_ops':{'REF':'1','screen':['2'],'diagnostic':[]},'-gpgpu_ep_l2_diag_l2_data_free':{'REF':'0','screen':[],'diagnostic':['1']}},['Agent A owns P2 WV/F exact mode extension','data-free bounded diagnostic separate from P2'],guard='P2_NEW_SOURCE_REQUIRED_WV_F_OBSERVER;DATA_FREE_EXISTING_SOURCE_REQUIRES_MODE_CPU_HOST',note='P2 option exists but WV/F and MS guardP1. Data-free removes payload bank contention while preserving capacity/pipelines/lower memory; not infinite L2 or real hardware.'),
]
dump('SYSTEM_PARAMETER_FAMILIES.json',dict(schema='EP_L2_PERFORMANCE_FIRST_SYSTEM_PARAMETER_FAMILIES_V1',status='CANDIDATES_NOT_SCIENCE_AUTHORIZED',source_identity=x['pairs'][0]['source_identity'],REF=dict(geometry='64slice32set8way',dram_mhz=850,dram_latency=100,bank_ops=1,physical_payload_slots_per_slice=1168,descriptor=512,line_mshr=128,descriptor_per_line=32,l2_missq=128,partition_queues='64:128:64:64',FRFCFS=128,DRAM_return=192,ICNT_in_out=512,network_mode=2),families=families,ideal_zero_queue_excluded='No unbounded queue0 in first range: production also makes partition credits unlimited. Require separate diagnostic design.',full_cartesian_product=False,accepted_pair_metadata_reuse=ref(P/'EXISTING_SYSTEM_PAIRS_REUSE.json')))
refs={
 'FWT':{'S':'EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1','EP':'EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1'},
 'GEMM':{'S':'EP_PERF_GEMM_140F6ED3_S_REF_V1','EP':'EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1'},
 'VECTOR4M':{'S':'EP_PERF_VECTOR4M_S_REF_V1','EP':'EP_PERF_VECTOR4M_F_REF_V1'},
}
def build_options(base,family_id,value):
 o=copy.deepcopy(base);f=next(f for f in families if f['id']==family_id)
 if family_id in ['LINE_MSHR','DESCRIPTOR_AND_MERGE','PAYLOAD_BANK']:raise ValueError('separate new source / mode qualification required')
 if len(f['controlled_options'])!=1:raise ValueError('multi-key family requires explicit subfamily contract')
 k,v=next(iter(f['controlled_options'].items()))
 if o.get(k)!=v['REF']:raise ValueError('reference mismatch')
 if value not in v['screen']+v['diagnostic']:raise ValueError('unapproved candidate value')
 o[k]=value
 if len(o)!=282:raise ValueError('Source78 option count changed')
 return o
points=[]
for workload,value in [('FWT','1132.0:1132.0:1132.0:1020.0'),('GEMM','1132.0:1132.0:1132.0:1020.0'),('VECTOR4M','1132.0:1132.0:1132.0:1275.0')]:
 for arm,cohort in refs[workload].items():
  source=J/'cases'/cohort/'control/FROZEN_SPEC.json';s=json.loads(source.read_text())
  assert s['source_identity']['core_source_commit']==CORE and s['source_identity']['binary_sha256']==ELF
  opts=build_options(s['expected_effective_options'],'DRAM_CLOCK',value)
  p=dict(schema='EP_PF_OPTION_PREVIEW_NOT_FROZEN_SPEC_V1',status='NEEDS_MAIN_HOST_NATIVE_QUALIFICATION_AND_USER_RANGE_AUTHORIZATION',id=f'PF_{workload}_{s["mode"]}_DRAM{value.split(":")[-1]}',family='DRAM_CLOCK',classification='DIAGNOSTIC_RELAXED_NOT_REAL_GPU' if workload=='VECTOR4M' else 'ARCHITECTURAL_CANDIDATE_PPA_UNKNOWN',reference_spec=ref(source),source_identity=s['source_identity'],mode=s['mode'],M=s['M'],T=s['T'],input_identity_sha256=s['input_identity_sha256'],geometry=s['geometry'],observer_env=s['observer_env'],expected_effective_options=opts,changed_options={'-gpgpu_clock_domains':{'before':s['expected_effective_options']['-gpgpu_clock_domains'],'after':value}},estimated_wall_seconds_parent_forecast_not_current_measurement=s['estimated_wall_seconds'],estimated_RAM_bytes_parent_forecast=s['estimated_peak_RAM_bytes'],science_start_permission=False)
  pr=dump('option_previews/'+p['id']+'.json',p);points.append(dict(id=p['id'],ref=pr,mode=p['mode'],input_identity_sha256=p['input_identity_sha256']))
dump('FIRST_SCREEN_OPTION_PREVIEWS.json',dict(status='NOT_HOST_QUALIFIED_NOT_FROZEN_NO_BUDGET',points=points,proposed_primary_starts=6,no_extra_REF_starts_if_exact_source_observer_input_geometry_reused=True))
# Test the actual offline builder and refusal behavior, not a simulator.
tests=[]
def check(label,fun,reject=False):
 try:
  fun();ok=not reject
 except (ValueError,AssertionError,KeyError):ok=reject
 tests.append(dict(label=label,passed=ok))
b=json.loads((J/'cases/EP_PERF_VECTOR4M_F_REF_V1/control/FROZEN_SPEC.json').read_text())['expected_effective_options']
check('clock1020_exact_one_key',lambda: (lambda o: (_ for _ in ()).throw(AssertionError()) if sum(o[k]!=b[k] for k in b)!=1 else None)(build_options(b,'DRAM_CLOCK','1132.0:1132.0:1132.0:1020.0')))
check('clock1275_diagnostic_supported',lambda:build_options(b,'DRAM_CLOCK','1132.0:1132.0:1132.0:1275.0'))
check('missq256_preserves_mshr_merge',lambda:build_options(b,'L2_MISS_QUEUE','S:32:128:8,L:B:m:L:P,A:128:1,256:0,32'))
check('lowerFIFO256_tuple',lambda:build_options(b,'L2_LOWER_FIFO','64:256:64:64'))
check('unknown_clock_refused',lambda:build_options(b,'DRAM_CLOCK','1132:1132:1132:9999'),True)
check('MSHR_guard_not_bypassed',lambda:build_options(b,'LINE_MSHR','A:256:1'),True)
check('descriptor_guard_not_bypassed',lambda:build_options(b,'DESCRIPTOR_AND_MERGE','1024'),True)
check('P2_guard_not_bypassed',lambda:build_options(b,'PAYLOAD_BANK','2'),True)
check('multi_key_ICNT_requires_contract',lambda:build_options(b,'ICNT_BUFFER','1024'),True)
check('wrong_REF_clock_refused',lambda:build_options(dict(b,**{'-gpgpu_clock_domains':'1132:1132:1132:1020'}),'DRAM_CLOCK','1132.0:1132.0:1132.0:1700.0'),True)
check('extra_option_refused',lambda:build_options(dict(b,**{'-bogus':'1'}),'DRAM_CLOCK','1132.0:1132.0:1132.0:1020.0'),True)
check('reference_unchanged',lambda:None if b==json.loads((J/'cases/EP_PERF_VECTOR4M_F_REF_V1/control/FROZEN_SPEC.json').read_text())['expected_effective_options'] else (_ for _ in ()).throw(AssertionError()))
assert all(t['passed'] for t in tests)
dump('OFFLINE_CONFIGURATION_CPU_RECEIPT.json',dict(schema='EP_PF_OFFLINE_CONFIG_COMPILER_CPU_TESTS_V1',status='PASS_OFFLINE_ONLY_NOT_PRODUCTION_CPU_OR_NATIVE_APPLICATION',tests=tests,tests_passed=len(tests),models_started=0,real_registry_mutations=0,source_mutations=0,trace_reads=0,script_ref=ref(Path(__file__))))
# Pin the reviewed small exact source files; no trace/content rehash.
source_refs=[ref(C/'src/gpgpu-sim'/n) for n in ['gpu-cache.h','gpu-cache.cc','gpu-sim.cc','l2cache.cc','ep-l2-ro-transactions.h','icnt_wrapper.cc']]
dump('ENGINEERING_QUALIFICATION.json',dict(schema='EP_PF_SYSTEM_PARAMETER_ENGINEERING_QUALIFICATION_V1',status='PARTIAL_CONFIG_PREPARATION_ONLY',reviewed_source_commit=CORE,reviewed_ELF_SHA256=ELF,source_refs=source_refs,existing_accepted_summary=ref(summary),existing_accepted_pair_reuse_count=len(reuse),offline_CPU=ref(P/'OFFLINE_CONFIGURATION_CPU_RECEIPT.json'),source_code_config_support='PASS_FOR_EXACT_SOURCE78_QUEUE_CLOCK_LATENCY_OPTIONS_ONLY',production_CPU_constructor_and_drain='NOT_EXECUTED_NEW_VALUES_THIS_TASK',host_qualification='NOT_QUALIFIED_NEW_PROFILE_REQUIRED',native_qualification='NOT_QUALIFIED_NEW_REQUEST_AND_EXACT_RANGE_REQUIRED',application_NI='NO_NEW_OBSERVER; EXISTING_MODE_NI_SCOPE_DOES_NOT_AUTOMATICALLY_QUALIFY_NEW_SOURCE',new_source_required=['WV/F MSHR !=128','RO descriptor !=512','RO per-address cap !=32','WV/F bank_ops !=1'],science_budget_created=0,models_started=0,accepted_source_or_ELF_modified=False,Main_required_actions=['Review and freeze family-specific complete282/283 option contracts and fairS/EP pairs','CPU mode constructors + finite backpressure/drain tests at exact selected values','Host parser and native admissible profile contracts must explicitly authorize changed background, cannot bypass old REF guard','New user-approved scoped family budget before any application start','Same new ELF referenceS/EP if source changes; do not splice Source78 and P1-corrected Source1e07'],physical_PPA='UNKNOWN'))
print(json.dumps(dict(reused_pairs=len(reuse),families=len(families),option_previews=len(points),offline_tests=len(tests),models_started=0)))
