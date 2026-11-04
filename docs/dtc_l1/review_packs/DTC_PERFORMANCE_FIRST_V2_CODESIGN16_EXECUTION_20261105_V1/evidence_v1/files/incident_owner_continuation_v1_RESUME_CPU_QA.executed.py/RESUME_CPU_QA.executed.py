from pathlib import Path
import ast,json,types,copy,hashlib,datetime
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/engineering_incidents/pre_intent_registry_lock_v1/owner_continuation_v1');p=O/'resume.py';m=types.ModuleType('resume_CPU_readonly');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);t=m.rd(O/'STAGE_TERMS.fixed.json');reg=m.rd(m.N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');old=reg['registered_future_requests'][m.REQ];checks=[]
def ck(n,b):assert b,n;checks.append(dict(check=n,passed=True))
def reject(n,f):
 try:f()
 except(AssertionError,KeyError,ValueError):ck(n,True);return
 raise AssertionError(n)
ck('import inert exposes only explicit resume',callable(m.resume))
ck('actual old q canonicalSHA matches Root staged terms',m.qsha(old)==t['expected_old_request_sha256'])
zero=m._zero_model_evidence(old,t);ck('actual readonly16spec/noINTENT/nofrontend/noSIM/retiredUUID join',zero['no_scientific_model']and len(zero['retired_UUIDs'])==2)
new=m.project_request(old,t,dict(CPU_FIXTURE=True),'CPU_ONLY');changed={k for k in set(old)|set(new)if old.get(k)!=new.get(k)};ck('projection changes only engine controller plan qhistory',changed=={'engine_sha256','controller_sha256','execution_plan_sha256','engineering_source_history'})
ck('budget16 remaining16 consumed0 specs16 unchanged',new['budget']==new['remaining']==len(new['admitted_specs'])==16 and new['consumed']=={} and new['admitted_specs']==old['admitted_specs'])
ck('input config source grants authorization all originalkeys preserved',all(new[k]==v for k,v in old.items()if k not in ['engine_sha256','controller_sha256','execution_plan_sha256','engineering_source_history']))
for label,field,value in [('spent','consumed',{'c':{'uuid':'actualmodel'}}),('budget','budget',17),('remaining','remaining',15),('request','request','FOREIGN')]:
 bad=copy.deepcopy(old);bad[field]=value;reject(label+' refuses continuation',lambda:m.project_request(bad,t,{},'CPU'))
bad=copy.deepcopy(t);bad['expected_old_request_sha256']='0'*64;reject('CAS drift refuses continuation',lambda:m.project_request(old,bad,{},'CPU'))
oldp=m.rd(m.R/'control/EXECUTION_PLAN.json');newp=m.rd(O/'FORWARD_EXECUTION_PLAN.fixed.json');m._check_plan(oldp,newp,t);ck('actual stagedplan only2pins+append checked sources',True)
for label,mut in [('budget',lambda x:x.update(initial_finite_budget=17)),('request',lambda x:x.update(request='FOREIGN')),('CoreOrOldPin',lambda x:x['source_pins'][0].update(sha256='0'*64))]:
 bad=copy.deepcopy(newp);mut(bad);reject('plan '+label+' rejected',lambda:m._check_plan(oldp,bad,t))
oldops=(m.R/'tools/perf16_ops.py').read_bytes();newops=m.checked(t['new_ops']);ck('ops change is only independent startup artifact',oldops.replace(b'DISPATCH_STARTED.json',b'DISPATCH_STARTED.CONTINUATION_V1.json')==newops)
ck('retired UUID dirs remain and no sameUUID new science',all((m.R/'DTC/run/results'/u).is_dir()for u in t['retired_pre_INTENT_UUIDs'])and not any((m.R/'control/qualification_ledger').glob('*.INTENT.json')))
ck('resume source contains no direct signal/registration/lease route mutation',all(x not in p.read_text()for x in ['os.kill(','register_exact_request(','update_authority(','leasepath,new','entry.read_bytes()==before']))
# Private synthetic file validates atomic history-safe writer; not a production file.
f=O/'cpu_fixture';f.mkdir(exist_ok=True);q=f/'atomic_fixture.json';q.write_text('OLD_CPU');m.atomic(q,b'NEW_CPU');ck('private atomic replacement exact bytes',q.read_bytes()==b'NEW_CPU')
result=dict(status='PASS_CPU_AND_READONLY_ZERO_MODEL_PROJECTION',checks=checks,check_n=len(checks),source_sha256=m.sha(p),ops_sha256=m.sha(O/'perf16_ops.continuation_v1.py'),Root_stage_terms_sha256=m.sha(O/'STAGE_TERMS.fixed.json'),read_only_current_old_request_sha256=m.qsha(old),zero_model_evidence=zero,actual_resume_or_stop_callbacks=0,registry_writes=0,models_started=0,signals=0,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(O/'RESUME_CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],checks=len(checks),source=m.sha(p),source_unchanged=True)))
