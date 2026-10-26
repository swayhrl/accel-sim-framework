"""No model/COPY authority actions: fakeRoot actual-finish tests plus read-only pins."""
import pathlib,json,hashlib,importlib.util,tempfile,types,copy,ast,fcntl,datetime
P=pathlib.Path;O=P('/root/data/dtc_failure_repair_20261025_v1/ops');SOURCE=O/'repair_completion_adopter_v1.py';OPS=O.parent/'validation/tools/repair_ops_v1.py'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v))
def load(name,path):s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
checks=[]
def checked(name,fn):fn();checks.append({'case':name,'status':'PASS'})
def reject(fn):
 try:fn()
 except (AssertionError,KeyError,FileNotFoundError,json.JSONDecodeError):return
 raise AssertionError('negative accepted')
tree=ast.parse(SOURCE.read_text());calls=[ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n,ast.Call)]
assert not any(x.endswith(('.run_cell','.run_native','.prepare','.finish_cell','.update_authority','.Popen','.kill','.killpg','.system','.run')) for x in calls);checks.append({'case':'AST_no_scientific_start_subprocess_signal_or_authority_API','status':'PASS'})
with tempfile.TemporaryDirectory(prefix='finite4_metadata_adopter_cpu_') as td:
 m=load('adopter_cpu',SOURCE);m.R=P(td)/'R';m.O=P(td)/'ops';m.O.mkdir();m.BINDING=m.O/'binding.json';m.CELLS=['cpu-ordinary'];cell=m.CELLS[0];uid='actual-fakeRoot-only';out=m.R/'DTC/run/results'/uid;out.mkdir(parents=True);sp=m.R/'control/specs'/(cell+'.json');ip=m.R/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');rp=m.R/'analysis'/(cell+'.RESULT.json');ap=m.R/'control'/(cell+'_ARCHIVE_RECEIPT.json');qp=m.R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')
 spec={'cohort':cell,'request':m.REQ};intent={'cohort':cell,'uuid':uid,'output':str(out)};launch={'launcher_pid':420001};pid={'pid':420002,'start_ticks':123};done={'cohort':cell,'uuid':uid,'output':str(out),'stop_reason':None,'launcher_wait_returncode':0,'native_simulator_observed':True,'actual_simulator_wait_and_file_evidence':True,'launcher_is_strace_parent_of_native_simulator':True}
 for p,v in [(sp,spec),(ip,intent),(dp,done),(out/'NATIVE_EXIT.json',done),(out/'NATIVE_LAUNCH.json',launch),(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',pid)]:put(p,v)
 (m.R/'DTC/control').mkdir(parents=True)
 q={'admitted_specs':{cell:sha(sp)},'consumed':{cell:{'uuid':uid,'intent_sha256':sha(ip),'execution_receipt':done}}};point={'spec_sha256':sha(sp),'intent_sha256':sha(ip),'uuid':uid,'launch_sha256':sha(out/'NATIVE_LAUNCH.json'),'pid_receipt_sha256':sha(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'),'model_pid':pid['pid'],'model_start_ticks':pid['start_ticks'],'launcher_pid':launch['launcher_pid']};binding={'points':{cell:point}}
 engine=types.SimpleNamespace(registered=lambda:(None,None,q,None));m.model_state=lambda *a:'RECORDED_GENERATION_GONE';m.launcher_absent=lambda *a:True
 proof={'cohort':cell,'uuid':uid,'status':'REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE','accepted_cycles':None,'correctness_validation_passed':True,'strict_overlay_sha256':'fake-pinned-strict'};strict=types.SimpleNamespace(terminal=lambda c:copy.deepcopy(proof));archive={'receipt':{'cohort':cell,'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'},'independently_verified_restored_entries':5};events=[]
 def verify(c):events.append('verify');return copy.deepcopy(archive)
 def archive_fn(c):events.append('COPY_fakeRoot');put(ap,archive['receipt'])
 outbox=types.SimpleNamespace(verify=verify,archive=archive_fn)
 assert m.context(cell,binding,engine)['state']=='CLOSED_NATIVE_EVIDENCE_READY';checks.append({'case':'complete_closed_native_evidence_gate','status':'PASS'})
 def missing_receipt():
  saved=q['consumed'][cell].pop('execution_receipt');assert m.context(cell,binding,engine)['state']=='WAIT_REAL_DONE_AND_EXECUTION_RECEIPT';q['consumed'][cell]['execution_receipt']=saved
 checked('missing_real_wait_receipt_waits_no_synthesis',missing_receipt)
 def missing_done():
  b=dp.read_bytes();dp.unlink();assert m.context(cell,binding,engine)['state']=='WAIT_REAL_DONE_AND_EXECUTION_RECEIPT';dp.write_bytes(b)
 checked('missing_DONE_waits_no_synthesis',missing_done)
 for key,value in [('uuid','wrong'),('intent_sha256','wrong')]:
  original=q['consumed'][cell][key];q['consumed'][cell][key]=value;checked('wrong_'+key+'_rejected',lambda:reject(lambda:m.context(cell,binding,engine)));q['consumed'][cell][key]=original
 original=q['consumed'][cell]['execution_receipt'];q['consumed'][cell]['execution_receipt']={'wrong':True};checked('DONE_q_receipt_mismatch_rejected',lambda:reject(lambda:m.context(cell,binding,engine)));q['consumed'][cell]['execution_receipt']=original
 for key,value in [('launcher_wait_returncode',-15),('stop_reason','OOM'),('native_simulator_observed',False),('actual_simulator_wait_and_file_evidence',False),('launcher_is_strace_parent_of_native_simulator',False),('output','/wrong')]:
  changed=dict(done,**{key:value});put(dp,changed);put(out/'NATIVE_EXIT.json',changed);q['consumed'][cell]['execution_receipt']=changed;checked(key+'_negative_rejected',lambda:reject(lambda:m.context(cell,binding,engine)))
 put(dp,done);put(out/'NATIVE_EXIT.json',done);q['consumed'][cell]['execution_receipt']=done
 changed=dict(spec,validation_kind='COMPONENT_SENTINEL_NOT_FORMAL');put(sp,changed);checked('sentinel_rejected_even_if_scope_name_forged',lambda:reject(lambda:m.context(cell,binding,engine)));put(sp,spec)
 checked('not_in_finite4_rejected',lambda:reject(lambda:m.context('not-allowed',binding,engine)))
 m.model_state=lambda *a:'RECORDED_GENERATION_ALIVE_OR_ZOMBIE';assert m.context(cell,binding,engine)['state']=='WAIT_MODEL_AND_STRACE_LAUNCHER_EXIT';m.model_state=lambda *a:'RECORDED_GENERATION_GONE';checks.append({'case':'live_or_zombie_recorded_model_generation_waits','status':'PASS'})
 m.launcher_absent=lambda *a:False;assert m.context(cell,binding,engine)['state']=='WAIT_MODEL_AND_STRACE_LAUNCHER_EXIT';m.launcher_absent=lambda *a:True;checks.append({'case':'launcher_PID_present_without_start_capture_waits_conservatively','status':'PASS'})
 # Invoke the actual frozen finish_evidence body only on fakeRoot; model
 # execution endpoints throw, and its strict/outbox imports are private stubs.
 ops=load('original_frozen_ops_cpu',OPS);ops.R=m.R;ops.run_cell=m.forbidden;ops.load=lambda name,file:strict if file=='repair_strict_v1.py' else outbox if file=='repair_outbox_v1.py' else (_ for _ in ()).throw(AssertionError('unexpected dependency'))
 fake_strict=m.R/'tools/repair_strict_v1.py';fake_strict.parent.mkdir();fake_strict.write_text('fake strict identity');(m.R/'tools/repair_ops_v1.py').write_bytes(OPS.read_bytes());proof['strict_overlay_sha256']=sha(fake_strict)
 put(m.BINDING,{'fake-only':True})
 before=copy.deepcopy(q);item=m.inspect(cell,binding,engine,outbox,strict,True);assert 'readonly_full_frozen_strict_proof'in item and not events and not rp.exists() and not ap.exists();checks.append({'case':'full_readonly_review_no_copy_or_RESULT','status':'PASS'})
 lockpath=m.R/'analysis/postprocess_v2'/(cell+'.METADATA_CONSUMER.lock');lockpath.parent.mkdir(parents=True)
 with lockpath.open('a+b') as held:
  fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);assert m.execute_point(cell,binding,engine,outbox,strict,ops)['state']=='WAIT_SHARED_V2_POINT_LOCK' and not events
 checks.append({'case':'exact_shared_V2_point_lock_contention_waits_without_error','status':'PASS'})
 def strict_failure(c):raise AssertionError('whole-population/runtime/source/BA strict negative fixture')
 original_terminal=strict.terminal;strict.terminal=strict_failure;checked('any_full_strict_failure_propagates_before_proof_archive_RESULT',lambda:reject(lambda:m.execute_point(cell,binding,engine,outbox,strict,ops)));assert not events and not rp.exists() and not ap.exists() and not (out/'REPAIR_STRICT.json').exists();strict.terminal=original_terminal
 result=m.execute_point(cell,binding,engine,outbox,strict,ops);assert result['state']=='EXISTING_FROZEN_FINISH_RESULT_AND_ARCHIVE_VERIFIED' and events.count('COPY_fakeRoot')==1 and read(rp)['proof']==proof and q==before and m.adoption_path(cell).exists();checks.append({'case':'actual_frozen_finish_body_full_success_only_metadata_and_standard_archive','status':'PASS'})
 original_result=rp.read_bytes();original_out={str(p):sha(p) for p in out.rglob('*') if p.is_file()};m.execute_point(cell,binding,engine,outbox,strict,ops);assert rp.read_bytes()==original_result and original_out=={str(p):sha(p) for p in out.rglob('*') if p.is_file()} and events.count('COPY_fakeRoot')==1;checks.append({'case':'existing_finished_result_idempotent_verify_no_copy_no_out_append','status':'PASS'})
 rp.write_text('{');checked('partial_canonical_RESULT_rejected_no_overwrite',lambda:reject(lambda:m.inspect(cell,binding,engine,outbox,strict)));rp.write_bytes(original_result)
 bad=read(rp);bad['uuid']='wrong';put(rp,bad);checked('conflicting_canonical_RESULT_rejected_no_overwrite',lambda:reject(lambda:m.inspect(cell,binding,engine,outbox,strict)));rp.write_bytes(original_result)
 rp.unlink();proofbytes=(out/'REPAIR_STRICT.json').read_bytes();(out/'REPAIR_STRICT.json').unlink();checked('archive_without_original_strict_proof_rejected_no_append',lambda:reject(lambda:m.inspect(cell,binding,engine,outbox,strict)));(out/'REPAIR_STRICT.json').write_bytes(proofbytes)
 # Existing archive+proof+qualification permits actual finish to recreate only
 # absent RESULT; it must not add to the already archived out or repeat COPY.
 m.adoption_path(cell).unlink();result=m.execute_point(cell,binding,engine,outbox,strict,ops);assert original_out=={str(p):sha(p) for p in out.rglob('*') if p.is_file()} and events.count('COPY_fakeRoot')==1;checks.append({'case':'archive_existing_exact_proofs_absent_RESULT_recreated_by_frozen_finish_without_out_mutation','status':'PASS'})
# This script never invokes finish_evidence against a real R. Actual live
# terminal review is the separately executed source-pinned independent proof.
m=load('adopter_real_readonly',SOURCE);binding,engine,outbox,strict,ops=m.bound(False);live=[m.inspect(c,binding,engine,outbox,strict,False) for c in m.CELLS];independent=O/'REPAIR_COMPLETION_ADOPTER_READONLY_STRICT_REVIEW_V1.json';review=read(independent);assert review['status']=='PASS' and review['scientific_model_starts']==0
assert {r['cohort'] for r in review['points']}==set(m.CELLS[:2]);assert all(r['status']=='PASS_READONLY_REGISTERED_STRICT_V1_FULL_REPLAY' and r['strict_proof']['correctness_validation_passed'] and r['out_inventory_unchanged'] and r['target_consumed_row_unchanged'] for r in review['points'])
assert all(x['state']=='READY_FROZEN_METADATA_FINISH_ONLY' for x in live[:2]) and all(x['state'] in ['WAIT_REAL_DONE_AND_EXECUTION_RECEIPT','WAIT_MODEL_AND_STRACE_LAUNCHER_EXIT','READY_FROZEN_METADATA_FINISH_ONLY'] for x in live[2:])
result={'schema':'FINITE4_METADATA_COMPLETION_ADOPTER_CPU_AND_INDEPENDENT_READONLY_STRICT_QUALIFICATION_V1','status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wrapper_path':str(SOURCE),'wrapper_sha256':sha(SOURCE),'binding_sha256':sha(m.BINDING),'driver_path':str(P(__file__).resolve()),'driver_sha256':sha(__file__),'checks':checks,'check_count':len(checks),'readonly_live_gate_results':live,'independent_full_strict_review_path':str(independent),'independent_full_strict_review_sha256':sha(independent),'old_original_ops_sha256':sha(OPS),'scientific_model_starts':0,'real_COPY164_calls':0,'real_authority_changes':0,'real_canonical_RESULT_or_out_changes':0,'live_consumer_restarts':0}
p=O/'REPAIR_COMPLETION_ADOPTER_CPU_QUALIFICATION_V1.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'qualification':str(p),'sha256':sha(p)}))
