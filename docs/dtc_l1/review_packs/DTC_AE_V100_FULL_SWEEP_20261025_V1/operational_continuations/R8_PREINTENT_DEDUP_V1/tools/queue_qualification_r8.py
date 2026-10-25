import pathlib,json,hashlib,importlib.util,copy,datetime,types,tempfile,ast
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('R8_queue_zero_model_qualification','revision8/sweep_controller.py');checks=[]
q={'admitted_specs':{c:'SHA' for c in ['A','B','C','D','E']},'consumed':{'B':{}},'sealed':['C']};running={'FUTURE':{'cell':'A','cpu':64}};claims={'A':{'host_cpu':64},'D':{'host_cpu':65}};cool={'E':101}
assert m.pending_cells(q,running,claims,cool,100)==[];checks.append('pre_INTENT_running_cell_excluded_before_registry_consumption')
assert m.pending_cells(q,{},claims,{},100)==['E'];checks.append('claimed_before_INTENT_cell_excluded_without_future_handle')
assert m.pending_cells(q,running,{},cool,102)==['D','E'];checks.append('consumed_and_sealed_excluded_cooldown_released_only_at_deadline')
test={'admitted_specs':{'A':'x'},'consumed':{},'sealed':[]};run={};claim={};selected=[]
for tick in range(20):
 for cell in m.pending_cells(test,run,claim,{},tick):
  selected.append(cell);claim[cell]={'host_cpu':64};run[cell]={'cell':cell,'cpu':64}
assert selected==['A'];checks.append('20_slow_prepare_dispatch_ticks_produce_one_pre_INTENT_submission')
with tempfile.TemporaryDirectory(prefix='dtc_R8_admission_no_model_') as tmp:
 root=P(tmp);(root/'control/qualification_ledger').mkdir(parents=True);oldT=m.T;m.T=root;fq={'consumed':{}};fake=types.SimpleNamespace(REQUEST=m.REQ,read_current_authority=lambda:({'registered_future_requests':{m.REQ:fq}},{}))
 assert m.prefork_resource_defer('A',fake,"RuntimeError('RESOURCE_HOLD_NO_START')");checks.append('recognized_prefork_resource_HOLD_is_zero_start_deferral')
 assert not m.prefork_resource_defer('A',fake,"RuntimeError('mapper identity changed')");checks.append('unknown_prefork_error_not_silently_deferred')
 fq['consumed']['A']={};assert not m.prefork_resource_defer('A',fake,"RuntimeError('RESOURCE_HOLD')");checks.append('consumed_cell_never_retried_even_on_resource_reason');fq['consumed'].clear()
 (root/'control/qualification_ledger/A.INTENT.json').write_text('{}');assert not m.prefork_resource_defer('A',fake,"RuntimeError('RESOURCE_HOLD')");checks.append('existing_INTENT_never_retried_even_before_registry_visibility');m.T=oldT
n=load('R8_qualification_current_authority','sweep_native_cap1m.py');actual=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];assert len(actual['consumed'])==139 and actual['budget']==356 and actual['state']=='RUNNING'
cell='E2-AEV100-1df9d5479504d9c7-CM';assert cell not in actual['consumed'] and not (T/'control/qualification_ledger'/(cell+'.INTENT.json')).exists();assert 'cohort has no serialized pre-fork resource reservation' in (T/'logs'/(cell+'.EXECUTION_R7.json')).read_text();checks.append('actual_R7_collision_refused_before_INTENT_no_scientific_start')
plan=read(T/'control/HOST_EXECUTION_PLAN_V1.json')
for r in plan['source_pins']+actual['shared_tool_pins']:assert sha(r['path'])==r['sha256']
checks.append('all_R7_host_adapter_and_old_scientific_sources_unchanged')
live=[]
for c,row in actual['consumed'].items():
 if 'execution_receipt' in row:continue
 out=T/'DTC/run/results'/row['uuid'];pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');assert m.live(pid);binding=read(T/'control/qualification_ledger'/(c+'.INTENT.json'))['host_execution_binding'];assert pid['host_execution_binding']==binding and pid['host_cpu_affinity_actual']==[binding['actual_host_cpu']];live.append({'cohort':c,'pid':pid['pid'],'start_ticks':pid['start_ticks'],'CPU':binding['actual_host_cpu']})
assert len(live)==len({r['CPU'] for r in live}) and len(live)>=1;checks.append('all_actual_live_models_have_distinct_verified_kernel_CPU_bindings')
ast.parse((T/'tools/revision8/sweep_controller.py').read_text());proof={'status':'PASS','controller_sha256':sha(T/'tools/revision8/sweep_controller.py'),'qualification_source_sha256':sha(T/'tools/queue_qualification_r8.py'),'checks':checks,'check_count':len(checks),'preserved_spent_count':139,'actual_live_host_bound_models':live,'unchanged_host_plan_sha256':sha(T/'control/HOST_EXECUTION_PLAN_V1.json'),'parent_retirement_transport_qualification_sha256':sha(T/'control/CONTINUATION_R7_ZERO_MODEL_QUALIFICATION.json'),'scientific_models_started':0,'model_signals':0,'admission_only_retries_not_model_retries':True,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
qualpath=T/'control/CONTINUATION_R8_ZERO_MODEL_QUALIFICATION.json'
if qualpath.exists():qualpath.rename(T/'control/draft_preimages/CONTINUATION_R8_QUAL_BEFORE_EXPLICIT_RECEIPT_SCIENCE_JOIN.json')
with qualpath.open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','checks':len(checks),'actual_live_models':len(live),'new_starts':0}))
