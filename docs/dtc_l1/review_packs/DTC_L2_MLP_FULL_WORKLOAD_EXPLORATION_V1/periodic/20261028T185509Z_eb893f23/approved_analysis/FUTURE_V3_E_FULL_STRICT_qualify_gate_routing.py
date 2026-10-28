"""New V3-only CPU gates and actual private consumer reference routing.
No actual native/model/authority writes. No successful physics stand-in is used.
"""
import copy,hashlib,importlib.util,json,pathlib,tempfile,threading,sys
from types import SimpleNamespace
P=pathlib.Path;D=P(__file__).parent
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
extra=load('E_new_V3_extra',D/'bpf_extra_strict.py');bridge=load('E_new_V3_consumer',D/'consumer_bridge.py')
root=P(tempfile.mkdtemp(prefix='CPU_GATE_ROUTING_',dir=D))
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
gate=root/'CPU_GATE.json';put(gate,{'schema':extra.GATE_SCHEMA,'kind':'CPU_ONLY_PREREQUISITE_STANDIN_NOT_ACTUAL_CANARY','qualification_only':True})
cfg={'schema':extra.ID,'overlay_id':extra.ID,'root':str(root),'request':extra.REQ,'qualification_only':True,'status':'ACTIVE_FUTURE_SCOPED',
 'source_paths':{'extra_strict':str(D/'bpf_extra_strict.py'),'consumer':str(D/'consumer_bridge.py')},
 'qualified_sources':{'extra_strict':extra.sha(D/'bpf_extra_strict.py'),'consumer':extra.sha(D/'consumer_bridge.py')},
 'canary4_prerequisite_path':str(gate),'canary4_prerequisite_sha256':extra.sha(gate)}
q={'qualification_only':True,'admitted_specs':{},'consumed':{},'request':extra.REQ}
checks=[]
def ok(n,fn):fn();checks.append({'name':n,'status':'PASS'})
def rejects(fn):
 try:fn()
 except Exception:return
 raise AssertionError('expected rejection')
ok('CPU_stub_is_explicitly_not_production_release',lambda:extra.require(extra.verify_release_prerequisite(cfg,q)['production_release_eligible']is False,'production'))
qq=copy.deepcopy(q);qq.pop('qualification_only')
ok('CPU_stub_rejected_without_private_authority_flag',lambda:rejects(lambda:extra.verify_release_prerequisite(cfg,qq)))
cc=copy.deepcopy(cfg);cc['root']=str(extra.PRODUCTION_ROOT)
ok('CPU_stub_rejected_at_real_root_even_with_two_flags',lambda:rejects(lambda:extra.verify_release_prerequisite(cc,q)))
cc=copy.deepcopy(cfg);cc['qualification_only']=False
ok('CPU_stub_rejected_without_config_flag',lambda:rejects(lambda:extra.verify_release_prerequisite(cc,q)))
cc=copy.deepcopy(cfg);cc['canary4_prerequisite_sha256']='0'*64
ok('gate_bytes_drift_rejected',lambda:rejects(lambda:extra.verify_release_prerequisite(cc,q)))
consumer=load('E_private_actual_original_consumer',extra.PRODUCTION_ROOT/'tools/l2_results.py')
delegated=[];sentinel=object()
def oldsafe(c):delegated.append(c);return sentinel
def qualification_loader(n,f):raise AssertionError('No physics leaf may execute in routing qualification')
consumer.safe_finish=oldsafe;consumer.load=qualification_loader
contract=extra.normalize_contract(cfg,root,qualification_only=True);contract['qualification_loader_sha256']=extra.sha(__file__)
api=bridge.make_private_consumer(consumer,contract,extra,lambda:q)
old4='EXACT_V2_ENGINEERING_CPU_ONLY';out=root/'DTC/run/results/OLD_V2_PRIVATE'
put(root/'control/qualification_ledger'/(old4+'.INTENT.json'),{'output':str(out),extra.FIELD:{'schema':'DTC_STRACE_FUTURE_ENTRY_V2'}})
ok('old_engineer4_binding_exact_delegate_no_new_gate_or_physics',lambda:extra.require(api['safe_finish'](old4)is sentinel and delegated[-1]==old4,'oldV2'))
ok('unknown_old_cohort_exact_delegate_same_value',lambda:extra.require(api['safe_finish']('OLD_UNSELECTED_NO_INTENT')is sentinel,'old'))
new='CPU_V3_CLAIMED_NO_BINDING'
put(root/'control/strace_bpf_v3_route_claims'/(new+'.json'),{'schema':'STRACE_BPF_V3_FUTURE_ROUTE_CLAIM_V1','overlay_id':extra.ID,'cohort':new})
count=len(delegated);value=api['safe_finish'](new)
ok('new_route_claim_missing_all_bindings_HOLD_never_old_acceptance',lambda:extra.require(value['state']=='STRACE_V3_OBSERVATION_HOLD_PRESERVE'and len(delegated)==count and not api['result_path'](new).exists(),'claim'))
unknown='CPU_UNKNOWN_OBSERVATION_GENERATION'
put(root/'control/qualification_ledger'/(unknown+'.INTENT.json'),{'output':str(root/'DTC/run/results/UNKNOWN'),extra.FIELD:{'schema':'UNQUALIFIED_V99'}})
count=len(delegated);value=api['safe_finish'](unknown)
ok('unknown_generation_HOLD_without_old_delegation',lambda:extra.require(value['state']=='STRACE_V3_OBSERVATION_HOLD_PRESERVE'and len(delegated)==count,'unknown'))
cfgp=root/'ACTIVE_FIXTURE.json';put(cfgp,cfg)
aging=SimpleNamespace(lock=threading.RLock())
engine=SimpleNamespace(registered=lambda:(None,None,q,None))
frame=SimpleNamespace(f_locals={'consumer':consumer,'engine':engine,'res':SimpleNamespace(DTC_LARGE_JOB_AGING_INSTALLED=aging)})
main=sys.modules['__main__'];before=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed,consumer.safe_finish)
receipt=bridge.install_on_frame(frame,cfgp,lambda:None,qualification_loader_sha256=extra.sha(__file__))
ok('actual_private_safe_attribute_installed_other_refs_unchanged',lambda:extra.require(before[:4]==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)and consumer.safe_finish is not before[4],'install'))
ok('actual_frame_consumer_readiness_points_to_installed_wrapper',lambda:extra.require(bridge.consumer_check(frame,cfg)is True,'ready'))
ok('installed_outer_preserves_V2_delegate',lambda:extra.require(consumer.safe_finish(old4)is sentinel,'outer'))
q['admitted_specs'][new]='CPU_ONLY_UNSPENT_CLAIM'
ok('restore_refuses_registered_unused_routeclaim_without_removing_safe',lambda:rejects(lambda:bridge.restore_in_owner(lambda:None)))
ok('failed_restore_preserves_same_mandatory_wrapper',lambda:extra.require(consumer.safe_finish is getattr(main,bridge.MARKER)['wrapper'],'preserve'))
q['admitted_specs'].pop(new) # private fixture-only authority; no production mutation
bridge.restore_in_owner(lambda:None)
ok('restore_exact_previous_V2_safe_and_all_refs',lambda:extra.require(before==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed,consumer.safe_finish)and not hasattr(main,bridge.MARKER),'restore'))
result={'schema':'DTC_BPF_V3_GATE_ROUTING_CPU_QUALIFICATION','status':'PASS','checks':checks,'count':len(checks),
 'source_sha256':{'extra':extra.sha(D/'bpf_extra_strict.py'),'consumer':extra.sha(D/'consumer_bridge.py')},'driver_sha256':extra.sha(__file__),
 'scope':'Actual new gate and private consumer code with explicit private authority/lease fixture. No native/physics/archive terminal leaf executed.',
 'production_release_qualified':False,'actual_models_qualified':False,'models_started':0,'grants_added':0,'production_changes':0}
put(D/'CPU_GATE_ROUTING_QUALIFICATION.json',result)
print(json.dumps({'status':'PASS','checks':len(checks)}))
