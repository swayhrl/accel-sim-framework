import datetime,hashlib,json,pathlib
import l2_config_generator as g
R=pathlib.Path(__file__).parent;ev=json.loads((R/'SOURCE_EVIDENCE.json').read_text());q=json.loads((R/'QUALIFICATION.json').read_text())
locations={
 'cache_parser':('src/gpgpu-sim/gpu-cache.h',578,586),
 'cache_guards':('src/gpgpu-sim/gpu-cache.h',715,760),
 'mshr_atom_address':('src/gpgpu-sim/gpu-cache.h',833,834),
 'mshr_construction':('src/gpgpu-sim/gpu-cache.h',1044,1058),
 'kernel_parameter_invariance':('src/gpgpu-sim/gpu-cache.h',1080,1087),
 'merge_capacity_semantics':('src/gpgpu-sim/gpu-cache.cc',581,595),
 'miss_queue_admission':('src/gpgpu-sim/gpu-cache.h',1493,1495),
 'option_registration_L2':('src/gpgpu-sim/gpu-sim.cc',260,264),
 'option_registration_FRFCFS':('src/gpgpu-sim/gpu-sim.cc',293,298),
 'separate_write_default':('src/gpgpu-sim/gpu-sim.cc',331,336),
 'FRFCFS_admission':('src/gpgpu-sim/dram_sched.cc',72,88),
 'credit_coupling':('src/gpgpu-sim/l2cache.cc',130,149)}
evidence={k:{'file':ev['sources'][p]['path'],'sha256':ev['sources'][p]['sha256'],'lines':[a,b]} for k,(p,a,b) in locations.items()}
profiles={}
for name,override in g.PROFILES.items():
 p=g.normalize(override);profiles[name]={'parameters':p,'logical_resource_cost':g.resource_cost(p),'factor_count_changed':sum(p[k]!=g.BASE[k] for k in g.BASE)}
contract={'schema':'DTC_L2_MLP_PARAMETER_CONTRACT_V1','status':'CPU_QUALIFIED_PENDING_COORDINATOR_REGISTRATION',
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'core_commit':ev['core_commit'],'framework_commit':ev['framework_commit'],
 'binary':{'path':'/root/data/dtc_failure_repair_20261025_v1/framework-build/accel-sim.out','sha256':'02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'},
 'core_library':{'path':'/root/data/dtc_failure_repair_20261025_v1/core-build/libcudart.so','sha256':'694f05ce97fe3e1552d94803c2202d8d037769c61624cde5f6a832622ed60c56'},
 'tracked_source_clean_observed':True,
 'baseline_L2':g.BASE_L2,'fixed_effective_options':g.FIXED,
 'fixed_geometry':{'cache_type':'SECTOR','sets_per_subpartition':128,'line_bytes':128,'ways':16,'controllers':20,'subpartitions_per_controller':2,'L2_data_bytes_total':10485760,'L2_set_mapping':'LINEAR','data_port_bytes':32,'result_FIFO_entries':0,'DRAM850MHz':True},
 'field_semantics':{'entries':'Maximum distinct 32-byte atom-address MSHR keys per L2 subpartition; not cache tags/data capacity.',
 'merge':'Maximum request-list length per existing MSHR key, INCLUDING the first request; baseline4 is not 4 additional merged requests.',
 'miss_queue':'Configured per-L2-subpartition miss/send queue bound; some admission paths reserve num_miss with >= test, others use size<bound, so configured slots are not a universal usable-occupancy guarantee.',
 'frfcfs':'FR-FCFS pending request window per DRAM/controller with write split disabled; ALSO increases shared memory-partition credits one-for-one.'},
 'credit_coupling':{'formula':'shared=frfcfs+return_queue-(subpartitions-1); private=1 per subpartition; add write queue only if separate writes enabled',
 'fixed_return_queue':192,'fixed_subpartitions':2,'fixed_write_split':0,
 'shared_limits':{'F64':255,'F128':319,'F256':447},
 'claim_boundary':'FRFCFS experiments are a coupled scheduling-window and partition-admission-credit factor, not an isolated L2-capacity intervention.'},
 'single_factor_profiles':profiles,'stage2_templates':g.stage2_templates(),
 'extension_policy':{'families':['entries','merge','miss_queue','frfcfs'],'next_doubling_examples':{'entries':1536,'merge':32,'miss_queue':256,'frfcfs':512},
 'configuration_limits':'Positive finite integers >= baseline; signed32 guard for all values; entries additionally <=1073741823 to avoid 2*entries constructor overflow. These are parser/integer guards, NOT realistic physical maxima.',
 'admission_rule':'Every extension needs source/option readback, independent scientific run identity and resource forecasts; scheduler can reject unsafe predicted memory/CPU even if parser-valid.',
 'no_zero_unlimited':'FRFCFS=0 forbidden; it changes finite-window semantics and has additional credit/unlimited behavior.',
 'uniformity':'One unified profile per complete workload-set comparison; never construct GM from per-program best choices.',
 'stop_basis':['whole-suite improvement saturation','performance regression','resource unrealizability','fixed scientific constraints','actual operational risk']},
 'logical_resource_formulas':{'MSHR_keys':'40*entries','request_references_upper_bound':'40*entries*merge','miss_queue_configured_slots':'40*miss_queue','FRFCFS_slots':'20*frfcfs','L2_data_bytes':'40*128*128*16 (fixed10MiB)',
 'area_bytes_status':'UNKNOWN; do not convert pointer/list/map software allocation or reference-slot counts into physical hardware area. Entries allocate a host container; merged lists/miss queues grow with occupancy.'},
 'API':{'module':'l2_config_generator.py','function':'generate(base_config_texts: list[str], profile: str|dict) -> (texts: list[str], manifest: dict)',
 'base_source':'Accepted downstream18 CH_P0 or DH_P0 ordered four config files. Preserve own cell and full input spec/expected population.',
 'only_mutated_options':[g.L2,g.FR],'P0_byte_identical':True,'all_non_target_effective_options_compared':True},
 'source_evidence':evidence,'qualification':{'path':'QUALIFICATION.json','sha256':hashlib.sha256((R/'QUALIFICATION.json').read_bytes()).hexdigest(),'invariants':q['local_invariant_checks'],'real_option_parser_cases':q['cpu']['cpu_fixture_cases'],'model_launches':0,'limitations':q['cpu']['limitations']},
 'remaining_runtime_qualification':'Coordinator performs minimal actual model qualification on distinct workload types with registered identities. Agent A did not start a simulator.',
 'source_package_no_historical_modifications':True}
(R/'PARAMETER_CONTRACT.json').write_text(json.dumps(contract,indent=2),encoding='utf-8')
lines=['DTC L2 MLP parameter contract V1','',
 'Core '+ev['core_commit']+'; Framework '+ev['framework_commit']+'. Both tracked trees clean. Binary and library SHA independently re-read.',
 'Fixed effective L2: '+g.BASE_L2+'. 40 subpartitions, 256KiB each, total10MiB. DRAM850MHz; core/ICNT/L2 clocks1410MHz.',
 '', '|Profile|Entries/bank|Request-list max/key|Miss queue/bank|FRFCFS/controller|Total MSHR keys|Total request-reference bound|Shared credits/controller|',
 '|---|---:|---:|---:|---:|---:|---:|---:|']
for n,r in profiles.items():
 p=r['parameters'];c=r['logical_resource_cost'];lines.append(f"|{n}|{p['entries']}|{p['merge']}|{p['miss_queue']}|{p['frfcfs']}|{c['mshr_address_entries_total']}|{c['mshr_request_references_upper_bound']}|{c['shared_credit_limit_per_controller']}|")
lines += ['', 'Interpretation and boundaries', '',
 'MSHR merge includes the first request. Sector cache MSHR keys use32-byte atom alignment; a key count is not a cache-line count.',
 'FRFCFS is a coupled factor: shared credits=F+192−(2−1)=F+191; private credit limit remains1/subpartition. F64/128/256 gives255/319/447 shared credits/controller. Partition FIFOs remain64:64:64:64.',
 'Miss queue values are configured bounds. Admission paths differ (<size versus size+num_miss>=bound), so do not assert every operation may occupy exactly the configured count.',
 'Logical capacities do not establish physical area, queue latency, dynamic power, or fully allocated host RSS. Cache data capacity is fixed10MiB. High-resource profiles require explicit overhead disclosure.',
 '', 'CPU qualification', '',
 f"PASS: {q['local_invariant_checks']} mutation/invariant checks; {q['cpu']['cpu_fixture_cases']} isolated actual-Core option-parser cases; no simulator launches or model cycles.",
 'The fixture links only src/option_parser.cc. It uses the exact cache sscanf format/order plus fixed-geometry assertions; it does not instantiate a complete cache or simulator. Initial fixture token-count assertion was corrected from16 to15 before finalPASS; no scientific run identity was consumed.',
 'CH and DH P0 remain byte-identical. All variants differ only at the final effective L2/FRFCFS option. Old shadow definitions are retained. Every non-target effective option is compared.',
 '', 'Integration', '',
 'Use l2_config_generator.generate(texts, "E384") or generate(texts, {"entries":384,"merge":8}). Returns ordered config texts plus exact effective options, SHA, changes and slot costs. Only coordinator registers and dispatches.',
 'Templates support all eight one-factor profiles, nine evidence-gated combinations, and finite resource-qualified expansion (next examples E1536/M32/Q256/F512). These bounds are not stopping criteria or a launch budget.',
 'Avoid zero/unlimited windows. Do not modify finite service, DTC-L1, mapping, capacity, clocks or inputs. Same cell/input/build P0 proof is required for reuse.',
 '', 'Precise source evidence', '']
for k,e in evidence.items():lines.append(f"- {k}: {e['file']}:{e['lines'][0]}–{e['lines'][1]}, SHA256 {e['sha256']}")
(R/'PARAMETER_CONTRACT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'contract_sha256':hashlib.sha256((R/'PARAMETER_CONTRACT.json').read_bytes()).hexdigest(),'profiles':len(profiles),'runtime_models_started':0}))
