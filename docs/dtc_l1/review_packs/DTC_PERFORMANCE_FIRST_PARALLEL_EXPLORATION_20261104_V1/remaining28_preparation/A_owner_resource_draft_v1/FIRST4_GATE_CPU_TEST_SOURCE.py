from pathlib import Path
import sys,types,json,hashlib,copy
sys.dont_write_bytecode=True
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/agents/A_remaining28_owner_resource_v1');p=O/'perf28_resources.py';m=types.ModuleType('perf28_CPU_GATE_ONLY');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__)
F=O/'fixtures/first4_metadata_CPU_ONLY';F.mkdir(parents=True,exist_ok=True);m.FIRST4=F;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True)+'\n')
flags=dict(archive=True,live=False);peer=types.SimpleNamespace(archived=lambda root,c,row:flags['archive'],rss=lambda root,row:(0,flags['live']))
def reset():
 flags.update(archive=True,live=False);source=F/'source_CPU_ONLY.txt';source.write_text('CPU fixture, never simulator source\n');plan=F/'control/EXECUTION_PLAN.json';put(plan,dict(source_pins=[dict(path=str(source),sha256=sha(source))]));q=dict(request=m.FIRST4_REQ,budget=4,remaining=0,admitted_specs={},consumed={},execution_plan_sha256=sha(plan))
 for prog,c in zip(m.FIRST4_PROGRAMS,m.FIRST4_COHORTS):
  uid='CPU_ONLY_'+prog;sp=F/'control/specs'/(c+'.json');spec=dict(cohort=c,request=m.FIRST4_REQ,cell='DH',profile='PHYS768_TAG64x8',structure_variant='PHYS768_TAG64x8',downstream_profile='P0',program=prog,input_digest=m.FROZEN_PROGRAMS[prog]);put(sp,spec);q['admitted_specs'][c]=sha(sp)
  intent=F/'control/qualification_ledger'/(c+'.INTENT.json');put(intent,dict(schema='CPU_FIXTURE_NOT_SCIENCE',cohort=c,uuid=uid));receipt=dict(schema='CPU_FIXTURE_NOT_SCIENCE',cohort=c,uuid=uid,stop_reason=None,launcher_wait_returncode=0);put(intent.with_name(c+'.DONE.json'),receipt);put(F/'DTC/run/results'/uid/'NATIVE_EXIT.json',receipt);q['consumed'][c]=dict(uuid=uid,intent_sha256=sha(intent),execution_receipt=receipt)
  put(F/'control'/(c+'_ARCHIVE_RECEIPT.json'),dict(schema='CPU_FIXTURE_NOT_SCIENCE',not_actual_archive=True));put(F/'analysis'/(c+'.RESULT.json'),dict(schema='CPU_FIXTURE_NOT_SCIENCE',cohort=c,state='PASS_PERFFIRST4_DH_STRICT_ARCHIVE_NATIVE_RESTORE',uuid=uid,cycles=1,proof=dict(performance_accepted=True,cycles=1),input_digest=spec['input_digest'],profile='PHYS768_TAG64x8',structure_variant='PHYS768_TAG64x8'))
 return {'registered_future_requests':{m.FIRST4_REQ:q}}
def run(name,change=None,expected=False):
 reg=reset();q=reg['registered_future_requests'][m.FIRST4_REQ]
 if change:change(q)
 result=m.first4_completion_gate(reg,peer);assert result['pass']==expected,(name,result);checks.append(dict(name=name,PASS=True,observed_gate_pass=result['pass'],reasons=result['reasons']))
c=m.FIRST4_COHORTS[0];rp=F/'analysis'/(c+'.RESULT.json');sp=F/'control/specs'/(c+'.json');ip=F/'control/qualification_ledger'/(c+'.INTENT.json')
def change_json(path,key,value):j=json.loads(path.read_text());j[key]=value;put(path,j)
def change_receipt(q,k,v):
 row=q['consumed'][c];r=copy.deepcopy(row['execution_receipt']);r[k]=v;row['execution_receipt']=r;put(ip.with_name(c+'.DONE.json'),r);put(F/'DTC/run/results'/row['uuid']/'NATIVE_EXIT.json',r)
run('four_exact_synthetic_metadata_can_pass',expected=True)
run('first4_not_all_consumed',lambda q:q.update(remaining=1))
run('wrong_registered_budget',lambda q:q.update(budget=5))
run('wrong_cohort_membership',lambda q:q['admitted_specs'].pop(c))
run('duplicate_UUID_rejected',lambda q:q['consumed'][m.FIRST4_COHORTS[1]].update(uuid=q['consumed'][c]['uuid']))
run('sourcepin_drift',lambda q:(F/'source_CPU_ONLY.txt').write_text('changed'))
run('planpin_drift',lambda q:change_json(F/'control/EXECUTION_PLAN.json','unexpected',True))
run('specpin_drift',lambda q:change_json(sp,'unexpected',True))
run('intentpin_drift',lambda q:change_json(ip,'unexpected',True))
run('natural_stop_reason_rejected',lambda q:change_receipt(q,'stop_reason','CPU_INJECTED'))
run('nonzero_exit_rejected',lambda q:change_receipt(q,'launcher_wait_returncode',1))
run('archive_join_missing',lambda q:flags.update(archive=False))
run('prior_model_still_live',lambda q:flags.update(live=True))
run('strict_negative_not_promoted',lambda q:change_json(rp,'state','FAIL_PERFFIRST4_DH_ARCHIVED_NO_RETRY'))
run('zero_cycles_rejected',lambda q:change_json(rp,'cycles',0))
run('RESULT_uuid_mismatch',lambda q:change_json(rp,'uuid','wrong'))
run('RESULT_input_mismatch',lambda q:change_json(rp,'input_digest','wrong'))
run('strict_not_accepted_rejected',lambda q:change_json(rp,'proof',dict(performance_accepted=False,cycles=1)))
run('strict_cycles_mismatch',lambda q:change_json(rp,'proof',dict(performance_accepted=True,cycles=2)))
oldsha=m.TAG_C_REVIEW_SHA;m.TAG_C_REVIEW_SHA='wrong';run('independent_Tag16_review_pin_drift');m.TAG_C_REVIEW_SHA=oldsha
(O/'FIRST4_GATE_CPU_QUALIFICATION.json').write_text(json.dumps(dict(schema='PERF28_FIRST4_PREDECESSOR_METADATA_CPU_FIXTURE_V1',status='PASS_CPU_ONLY',source_sha256=sha(p),tests=checks,n=len(checks),positive_fixture_is_synthetic_metadata_not_science=True,actual_models_started=0,actual_registrations=0,actual_archives_or_results_fabricated=False,all_synthetic_files_under=str(F)),indent=2)+'\n');print('FIRST4_GATE_CPU',len(checks),'PASS')
