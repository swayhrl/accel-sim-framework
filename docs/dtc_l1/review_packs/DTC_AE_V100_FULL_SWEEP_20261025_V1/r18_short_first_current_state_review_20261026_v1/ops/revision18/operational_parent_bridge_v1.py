"""Explicit R16 science-source lineage to real R18 operational-parent bridge.

Private module adapters only. Never changes frozen scientific sources/specs/plans,
returns a fake lease, starts an already consumed point, or supplies a wait result.
"""
import pathlib,json,hashlib,importlib.util,copy,os
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision18';T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
ORIGINAL='DTC_AE_V100_FULL_SWEEP_20261025_V1';OLD='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';LAVA='DTC_AE_LAVAMEM_REPAIR_20261026_V2';LATE='DTC_AE_LATE_FAILURE_REPAIR_20261026_V1';MANIFEST=D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json'
ROOTS={LAVA:F/'validation_lava_memory_v2',LATE:F/'validation_late_failure_v1'}
NATIVE={LAVA:'lavamem_native_v2.py',LATE:'late_native_v1.py'};OPS={LAVA:'lavamem_ops_v2.py',LATE:'late_ops_v1.py'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def manifest():
 m=read(MANIFEST);assert m['schema']=='EXPLICIT_R16_SCIENCE_TO_REAL_R18_OPERATIONAL_PARENT_BRIDGE_V1' and m['bridge_path']==str(P(__file__).resolve()) and m['bridge_sha256']==sha(__file__)
 assert m['scientific_parent_lineage_sha256']=='32ebd671924d4e23eda7960c5957708e5a71f225ceb0887edcbe3249f25f65d3'
 assert sha(m['actual_parent_path'])==m['actual_parent_sha256'] and 'revision18/sweep_controller.py' in m['actual_parent_path']
 for pin in m['source_pins']:assert sha(pin['path'])==pin['sha256'],('continuation source drift',pin['path'])
 return m
def continuation_record(q,m):
 matches=[r for r in q.get('operational_parent_continuations',[]) if r.get('manifest_sha256')==sha(MANIFEST) and r.get('bridge_sha256')==sha(__file__) and r.get('actual_parent_sha256')==m['actual_parent_sha256']]
 assert len(matches)==1,'missing or ambiguous registered operational-parent continuation'
 return matches[0]
def scientific_base(request):
 assert request in ROOTS;m=manifest();p=m['requests'][request];root=ROOTS[request];engine=load('r18_private_frozen_'+request,root/'tools'/NATIVE[request]);reg,epoch,q,plan=engine.registered()
 assert sha(root/'tools'/NATIVE[request])==p['frozen_engine_sha256']==q['engine_sha256'] and q['execution_plan_sha256']==p['frozen_execution_plan_sha256'] and q['spec_request_sha256']==p['frozen_request_sha256']
 assert plan['parent_controller_sha256']==m['scientific_parent_lineage_sha256'] and sha(plan['parent_controller_path'])==m['scientific_parent_lineage_sha256']
 record=continuation_record(q,m);assert set(record['effective_future_cohorts'])<=set(p['authorized_future_cohorts']) and not set(record['consumed_prefix_UUIDs'])&set(record['effective_future_cohorts'])
 return engine,m,p,record
def actual_parent(request,engine,m,record):
 # The frozen original predicate verifies real PID/start, qualification FD/flock,
 # native host/namespace and ancestry. Its actual lease is never rewritten.
 lease=engine.original_native().assert_batch_lease();reg,epoch,q,plan=engine.registered()
 assert epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE' and epoch['holder']==os.uname().nodename
 assert lease['controller_sha256']==m['actual_parent_sha256'] and {OLD,LAVA,LATE}<=set(lease.get('additional_requests',[]))
 assert all(reg['registered_future_requests'][k]['orchestrator_sha256']==m['actual_parent_sha256'] for k in [ORIGINAL,LAVA,LATE])
 assert continuation_record(q,m)==record
 assert (lease['pid'],lease['start_ticks'],lease['fd'])==(record['actual_parent_pid'],record['actual_parent_start_ticks'],record['actual_parent_qualification_fd']),'actual lease differs from explicitly registered R18 generation'
 return lease
def binding_for(request,cell,engine,m,record):
 assert cell in record['effective_future_cohorts'] and cell in m['requests'][request]['authorized_future_cohorts']
 lease=actual_parent(request,engine,m,record)
 return {'schema':'ACTUAL_R18_OPERATIONAL_PARENT_WITH_UNMODIFIED_R16_SCIENCE_LINEAGE_V1','request':request,'cohort':cell,'manifest_path':str(MANIFEST),'manifest_sha256':sha(MANIFEST),'operational_bridge_path':str(P(__file__).resolve()),'operational_bridge_sha256':sha(__file__),'actual_controller_path':m['actual_parent_path'],'actual_controller_sha256':m['actual_parent_sha256'],'actual_lease_pid':lease['pid'],'actual_lease_start_ticks':lease['start_ticks'],'actual_lease_fd':lease['fd'],'scientific_plan_parent_sha256':m['scientific_parent_lineage_sha256'],'frozen_scientific_engine_sha256':m['requests'][request]['frozen_engine_sha256'],'frozen_scientific_execution_plan_sha256':m['requests'][request]['frozen_execution_plan_sha256'],'frozen_scientific_request_sha256':m['requests'][request]['frozen_request_sha256'],'base_repair_execution_overlay_semantics':'Actual frozen base engine/source/plan identity; current operational adapter and controller are independently identified here.','lease_returned_unchanged':True,'scientific_model_options_or_trace_or_geometry_changed':False,'model_retries':0}
def adapted(request):
 engine,m,p,record=scientific_base(request);old_prepare=engine.prepare
 engine.assert_parent_lease=lambda:actual_parent(request,engine,m,record)
 def prepare(cell):
  proof=old_prepare(cell);proof['operational_parent_continuation_binding']=binding_for(request,cell,engine,m,record);return proof
 engine.prepare=prepare
 return engine,m,record
def prepare(request,cell):return adapted(request)[0].prepare(cell)
def run_native(request,cell):
 engine,m,record=adapted(request);native=engine.engine();old_exclusive=native.exclusive
 def exclusive(path,obj):
  path=P(path)
  if path.name.endswith('.INTENT.json') or path.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
   obj=dict(obj,operational_parent_continuation_binding=binding_for(request,cell,engine,m,record))
  return old_exclusive(path,obj)
 native.exclusive=exclusive
 return native.finish_cell(cell)
def inspect_operational_receipts(request,cell):
 engine,m,p,record=scientific_base(request);reg,epoch,q,plan=engine.registered();row=q['consumed'][cell];root=ROOTS[request];ip=root/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(ip);out=P(intent['output']);assert sha(ip)==row['intent_sha256'] and intent['uuid']==row['uuid'] and out==root/'DTC/run/results'/row['uuid']
 entries=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')]
 if cell in record['consumed_prefix_UUIDs']:
  assert row['uuid']==record['consumed_prefix_UUIDs'][cell]
  if any('operational_parent_continuation_binding' in x for x in entries):
   # Validate a real prior R17 generation with its original published bridge;
   # no historical launch binding is rewritten for the new metadata parent.
   legacy=load('r18_prior_r17_receipt_review',F/'ops/revision17/operational_parent_bridge_v1.py')
   prior_m=legacy.manifest();prior_p=prior_m['requests'][request];assert prior_p==p
   prior_record=legacy.continuation_record(q,prior_m)
   legacy.ROOTS=dict(legacy.ROOTS,**{request:ROOTS[request]})
   old_scientific_base=legacy.scientific_base
   legacy.scientific_base=lambda req:(engine,prior_m,prior_p,prior_record) if req==request else old_scientific_base(req)
   proof=legacy.inspect_operational_receipts(request,cell)
   return dict(status='PRESERVED_AND_VERIFIED_PRIOR_R17_OPERATIONAL_RECEIPTS',cohort=cell,uuid=row['uuid'],prior_R17_proof=proof)
  assert all('operational_parent_continuation_binding' not in x for x in entries)
  return {'status':'PRESERVED_ORIGINAL_R16_LAUNCH_OPERATIONAL_FIELDS_UNMODIFIED','cohort':cell,'uuid':row['uuid']}
 assert cell in record['effective_future_cohorts'];bindings=[x['operational_parent_continuation_binding'] for x in entries];assert bindings[0]==bindings[1]==bindings[2];b=bindings[0]
 assert b['request']==request and b['cohort']==cell and b['manifest_path']==str(MANIFEST) and b['manifest_sha256']==sha(MANIFEST) and b['operational_bridge_path']==str(P(__file__).resolve()) and b['operational_bridge_sha256']==sha(__file__)
 assert b['actual_controller_path']==m['actual_parent_path'] and b['actual_controller_sha256']==m['actual_parent_sha256'] and b['scientific_plan_parent_sha256']==m['scientific_parent_lineage_sha256']
 assert (b['actual_lease_pid'],b['actual_lease_start_ticks'],b['actual_lease_fd'])==(record['actual_parent_pid'],record['actual_parent_start_ticks'],record['actual_parent_qualification_fd']),'historical operational lease identity changed'
 assert b['frozen_scientific_engine_sha256']==p['frozen_engine_sha256'] and b['frozen_scientific_execution_plan_sha256']==p['frozen_execution_plan_sha256'] and b['frozen_scientific_request_sha256']==p['frozen_request_sha256'] and b['lease_returned_unchanged'] is True and b['scientific_model_options_or_trace_or_geometry_changed'] is False
 return {'status':'REAL_R18_OPERATIONAL_PARENT_RECEIPTS_AND_UNMODIFIED_R16_SCIENCE_LINEAGE_VERIFIED','cohort':cell,'uuid':row['uuid'],'manifest_sha256':sha(MANIFEST),'bridge_sha256':sha(__file__),'binding':b,'accepted_cycles':None,'science_terminal_still_requires_original_full_strict':True}
def finish_evidence(request,cell):
 proof=inspect_operational_receipts(request,cell);result=load('r18_frozen_finish_'+request,ROOTS[request]/'tools'/OPS[request]).finish_evidence(cell)
 target=ROOTS[request]/'analysis/r18_operational_parent_review'/(cell+'.json');target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert read(target)==proof
 else:
  with target.open('x') as f:json.dump(proof,f,sort_keys=True,indent=2);f.write('\n')
 return result
def run_cell(request,cell):
 # Reuse exact pinned worker command path; its only new launch route is this
 # explicitly identified bridge installed at the native frontend.
 engine,m,record=adapted(request);actual_parent(request,engine,m,record)
 assert cell in record['effective_future_cohorts'] and cell not in engine.registered()[2]['consumed']
 ops=load('r18_frozen_worker_'+request,ROOTS[request]/'tools'/OPS[request]);ops.finish_evidence=lambda c:finish_evidence(request,c)
 lease_engine=adapted(request)[0];old_load=ops.load
 def worker_load(name,file):return lease_engine if file==NATIVE[request] else old_load(name,file)
 ops.load=worker_load
 return ops.run_cell(cell)
