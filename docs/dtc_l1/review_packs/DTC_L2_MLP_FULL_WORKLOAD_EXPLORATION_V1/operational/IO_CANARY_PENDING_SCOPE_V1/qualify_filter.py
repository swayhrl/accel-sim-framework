from pathlib import Path as P
import json,types,tempfile,sys,importlib.util,hashlib
B=P(__file__).parent;sp=importlib.util.spec_from_file_location('canary_filter_fixture',B/'single_canary_filter.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
def ck(n,v):assert v,n;checks.append(n)
def denied(fn):
 try:fn()
 except AssertionError:return True
 return False
with tempfile.TemporaryDirectory()as td:
 r=P(td);(r/'control/qualification_ledger').mkdir(parents=True);disk=r/'control/POOL_DISPATCH_RESERVATIONS.json';disk.write_text('{"claims":{}}');q={'admitted_specs':{'CANARY':'x','OTHER':'y'},'consumed':{}};claims={};e=types.SimpleNamespace(registered=lambda:(None,None,q,None));calls=[];gate={'allow':True}
 def original(p,s,c,h,prev,policy,index):calls.append((p,s,c,h,prev,policy,index));return{'cohort':p[0]['cohort']}if p and gate['allow']else None
 res=types.SimpleNamespace(choose_dispatch=original);pool=object();frame=types.SimpleNamespace(f_locals=dict(res=res,engine=e,claims=claims,pool=pool));proof=m.install_on_frame(frame,'CANARY',r);pending=[{'cohort':'OTHER'},{'cohort':'CANARY'}];sample={};history={};policy={};selected=res.choose_dispatch(pending,sample,claims,history,None,policy,7);ck('only_canary_narrowed_pending_original_unchanged',selected['cohort']=='CANARY'and pending==[{'cohort':'OTHER'},{'cohort':'CANARY'}]and calls[-1][0]==[{'cohort':'CANARY'}]);ck('all_resource_gate_inputs_same_identity',calls[-1][1]is sample and calls[-1][2]is claims and calls[-1][3]is history and calls[-1][5]is policy and calls[-1][6]==7 and proof['pool_object_id']==id(pool))
 gate['allow']=False;ck('original_resource_HOLD_never_bypassed',res.choose_dispatch(pending,sample,claims,history)is None);gate['allow']=True
 q['consumed']['CANARY']={};n=len(calls);ck('consumed_canary_cannot_launch_or_refill_other',res.choose_dispatch(pending,sample,claims,history)is None and len(calls)==n);q['consumed']={}
 ck('idempotent_same_target_existing_instance',m.install_on_frame(frame,'CANARY',r)['idempotent']);m.restore_in_owner();bad=[]
 bad.append(denied(lambda:m.install_on_frame(frame,'UNKNOWN',r)));claims['CANARY']={};bad.append(denied(lambda:m.install_on_frame(frame,'CANARY',r)));claims.clear();disk.write_text('{"claims":{"CANARY":{}}}');bad.append(denied(lambda:m.install_on_frame(frame,'CANARY',r)));disk.write_text('{"claims":{}}');intent=r/'control/qualification_ledger/CANARY.INTENT.json';intent.write_text('{}');bad.append(denied(lambda:m.install_on_frame(frame,'CANARY',r)));intent.unlink();ck('unregistered_inmemory_claim_diskclaim_INTENT_rejected',all(bad))
 m.install_on_frame(frame,'CANARY',r);scoped=res.choose_dispatch
 def newer(*a,**k):return scoped(*a,**k)
 res.choose_dispatch=newer;restored=m.restore_in_owner();selected=res.choose_dispatch(pending,sample,claims,history);ck('restore_disables_scope_without_clobbering_newer_outer',restored['newer_outer_wrapper_preserved']and res.choose_dispatch is newer and selected['cohort']=='OTHER');delattr(sys.modules['__main__'],m.MARKER)
qa=dict(status='PASS',schema='SINGLE_CANARY_PENDING_SCOPE_CPU_QUALIFICATION_V1',checks=checks,total_checks=len(checks),source_sha256=hashlib.sha256((B/'single_canary_filter.py').read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),production_parent_attached=False,production_mutations=0,model_starts=0,model_signals=0)
(B/'CPU_QUALIFICATION.json').write_text(json.dumps(qa,sort_keys=True,indent=2)+'\n');print(json.dumps(qa))
