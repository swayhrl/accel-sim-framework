"""Independent whole-input correctness validation of a new repaired binary pair.

Never promotes repaired runs into the original performance matrix.
"""
import pathlib,json,hashlib,importlib.util,gzip,types
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_remaining_failure_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def terminal(cell):
 engine=load('repair_independent_engine',R/'tools/remaining_native_v1.py');reg,epoch,q,plan=engine.registered();assert q['strict_sha256']==sha(__file__);s=engine.spec_for(cell);ip=R/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');intent=read(ip);done=read(dp);out=P(intent['output']);row=q['consumed'][cell]
 assert sha(ip)==row['intent_sha256'] and done==row['execution_receipt']==read(out/'NATIVE_EXIT.json') and done['uuid']==intent['uuid']==row['uuid'] and out==R/'DTC/run/results'/row['uuid'];assert done['stop_reason'] is None and done['launcher_wait_returncode']==0 and done['native_simulator_observed']
 assert sha(out/'raw.log.gz')==done['raw_sha256']
 with gzip.open(out/'raw.log.gz','rb') as stream:rawbytes=stream.read()
 assert hashlib.sha256(rawbytes).hexdigest()==done['raw_uncompressed_sha256'] and len(rawbytes)==done['raw_uncompressed_bytes'];raw=rawbytes.decode();trace=(out/'actual_file_process_network.log').read_text();assert 'connect(' not in trace and '"/usr/bin/ssh"' not in trace and '"/bin/ssh"' not in trace
 old=load('repair_pinned_whole_input_population',T/'tools/sweep_strict_cap1m.py');binding=P(s.get('input_binding_path',str(T/'control/input_bindings'/(s['input_digest']+'.json'))));assert sha(binding)==s['input_binding_sha256'];domain=read(binding)['qualification'];engine.check_input(s)
 assert all(r['path'] in trace for r in domain['rows']);assert s['framework_commit'] in raw and s['core_commit'][:7] in raw
 launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');assert launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv'] and s['native_simulator_argv'][0] in pid['maps'] and pid['mnt_namespace']==s['execution_mnt_namespace'] and launch['host']['hostname']=='huangrulin-sshfs-174'
 overlays=[x['repair_execution_overlay'] for x in [intent,launch,pid]];assert overlays[0]==overlays[1]==overlays[2] and overlays[0]['engine_sha256']==q['engine_sha256'] and overlays[0]['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN_V1.json') and overlays[0]['observer_overlay_sha256']==plan['observer_overlay']['sha256']
 resource=plan['resource_accounting_overlay'];assert sha(resource['path'])==resource['sha256'];shared=load('remaining_strict_exact_resource_source',resource['path']);expected_resource=shared.future_engine_install(types.SimpleNamespace(exclusive=lambda path,obj:None))._R19_FUTURE_RESOURCE_BINDING;resource_bindings=[x['resource_accounting_binding_R19'] for x in [intent,launch,pid]];assert resource_bindings[0]==resource_bindings[1]==resource_bindings[2]==expected_resource
 observer_bindings=[x['observer_exit_race_binding'] for x in [intent,launch,pid]];assert observer_bindings[0]==observer_bindings[1]==observer_bindings[2];observed=observer_bindings[0];observer=load('repair_independent_observer_source',plan['observer_overlay']['path']);code,counts=observer.transformed((T/'tools/sweep_native_cap1m.py').read_text());assert observed['profile']=='OBSERVER_PROC_EXIT_RACE_V1' and observed['adapter_path']==plan['observer_overlay']['path'] and observed['adapter_sha256']==plan['observer_overlay']['sha256']==sha(plan['observer_overlay']['path']) and observed['base_native_source_path']==str(T/'tools/sweep_native_cap1m.py') and observed['base_native_source_sha256']==sha(T/'tools/sweep_native_cap1m.py') and observed['transformed_run_native_source_sha256']==hashlib.sha256(code.encode()).hexdigest() and observed['transformation_counts']==counts and observed['identity_snapshots_synthesized'] is False and observed['telemetry_or_scientific_completion_rules_changed'] is False
 for name,source in [('REPAIR_FROZEN_SPEC.json',R/'control/specs'/(cell+'.json')),('REPAIR_INTENT_SNAPSHOT.json',ip),('REPAIR_EXECUTION_PLAN.json',R/'control/EXECUTION_PLAN_V1.json'),('REPAIR_APPROVAL_REQUEST.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('REPAIR_BUILD_PROFILE.json',R/'control/REMAINING_BUILD_PROFILE_V1.json'),('REPAIR_OPERATIONAL_OUTPUT_CAP.json',R/'control'/('OPERATIONAL_OUTPUT_CAP_'+cell+'.json'))]:assert sha(out/name)==sha(source)
 assert launch['effective_result_cap_bytes']==engine.output_cap(s) and launch['frozen_upper_result_cap_bytes']==s['limits']['max_result_directory_bytes']
 expected_cpu=launch['prepared']['selected_host_cpu'];assert pid['host_cpu_affinity_actual']==[expected_cpu]
 for item in s['runtime_files']:assert sha(item['actual_realpath'])==item['sha256']
 result=old.population(raw,s,domain,old.legacy());diagnostic_cycles=result.pop('cycles');count=0;last=None
 with gzip.open(out/'progress.jsonl.gz','rt') as stream:
  for line in stream:
   p=json.loads(line);count+=1;assert p['seq']==count and (p['pid'],p['start_ticks'],p['generation'])==(pid['pid'],pid['start_ticks'],done['uuid']) and p['input']==s['original_environment']['DTC_AG7_INPUT_SHA'] and p['roi']==s['original_environment']['DTC_AG7_ROI_SHA']
   if last is not None:assert p['mono_ns']>last['mono_ns'] and p['completed']>=last['completed']
   last=p
 assert last and last['end']=='NATURAL' and last['completed']==s['expected']['instructions'];decisions=0;resources=0
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as stream:
  for line in stream:
   p=json.loads(line)
   if 'DTC_exact_original_policy' in p:assert p['DTC_exact_original_policy']['decision']['decision']!='STOP';decisions+=1
   if 'physical_RAM_pass' in p:
    assert p['physical_RAM_pass'] and p['physical_disk_pass'] and p['process_tree_observed_rss_bytes']<=s['limits']['max_process_tree_rss_bytes'];resources+=1
 assert decisions and resources
 return dict(result,schema='DTC_REMAINING_FAILURE_WHOLE_INPUT_CORRECTNESS_STRICT_V1',status='REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE',cohort=cell,uuid=done['uuid'],prior_original_point=s.get('prior_original_point'),validation_kind=s.get('validation_kind','REPAIR_FAILED_OR_ENGINEERING_POINT'),source_kind=s.get('source_kind','ORIGINAL_CAPTURED_FULL_INPUT_REPAIR'),diagnostic_cycles=diagnostic_cycles,accepted_cycles=None,performance_accepted=False,correctness_validation_passed=True,full_input_native_values='UNPROVEN',whole_input_model_trace_population_and_lifecycle_validated=True,progress_records=count,original_BA_decisions=decisions,resource_samples=resources,core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],engine_overlay_sha256=q['engine_sha256'],strict_overlay_sha256=sha(__file__),population_source_sha256=sha(T/'tools/sweep_strict_cap1m.py'),repair_points_never_merge_into_original288=True,AS_and_RSS_hard_cap_bytes=s['limits']['max_process_tree_rss_bytes'],estimated_peak_model_RAM_bytes=s['estimated_peak_model_RAM_bytes'],source_physics_and_270_options_unchanged=True,resource_accounting_binding_R19=expected_resource,resource_accounting_source_sha256=resource['sha256'],SOURCE_KEEP=True)
