from pathlib import Path
import hashlib,json,datetime,difflib
O=Path(__file__).parent
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');B=A/'agents/B/strace_bpf_future_entry_v3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
 with(O/n).open('xb')as f:f.write(b)
 return hashlib.sha256(b).hexdigest()
assert sha(O/'bpf_extra_strict.py')=='702a0a3e27645ece6cf15a68c598bce4067b69132a74c1fb1e3cfde03a621c3b'
assert sha(O/'consumer_bridge.py')=='de70cede8876fca5bf909f5b8d685b74da43a6ca08880e18e09d59e924c0225b'
expected={'producer':'06e52cd8e359791a912ba081b9e3cb16d7e23baae1d7a8511eefa8d74528c675','frontend':'c1557a219ada13fb0478830209f137036324048d8387cdffaa850f3744a5e8d2','entry':'2a21ba7d62ea9094dd1dc6de7c4d0c699c9baf491e07467228f1b307d60c8792'}
for key,path in [('producer',B/'strace_entry.py'),('frontend',B/'bpf_frontend.py'),('entry',B/'native-entry/bin/experiment')]:assert sha(path)==expected[key]
qa=read(O/'CPU_PREFIX_CONSUMER_QUALIFICATION.json');g=read(O/'CPU_GATE_ROUTING_QUALIFICATION.json')
assert qa['count']==28 and g['count']==15 and qa['status']==g['status']=='PASS'
assert qa['sources']['extra']==g['source_sha256']['extra']==sha(O/'bpf_extra_strict.py')
assert qa['sources']['consumer']==g['source_sha256']['consumer']==sha(O/'consumer_bridge.py')
for key in expected:assert qa['sources'][key]==expected[key]
# Recover exact prior qualification source only as an additional labelled
# preimage, never replace current frozen source or old QA documents.
current=(O/'consumer_bridge.py').read_text();previous=current
previous=previous.replace("    rp=m['bridge']['result_path'](c)\n    require(c in q['consumed']and rp.exists()and m['consumer'].accepted(read(rp))and read(rp)['proof'].get(EXTRA,{}).get('schema')==ID,'Preserve mandatory V3 route for admitted unused/unresolved claim; Main disposition required')", "    require(c in q['consumed']and m['bridge']['result_path'](c).exists(),'Preserve mandatory V3 route for admitted unused/unresolved claim; Main disposition required')")
previous=previous.replace("   rp=m['bridge']['result_path'](c)\n   require(not m['bridge']['selected'](c)or(rp.exists()and m['consumer'].accepted(read(rp))and read(rp)['proof'].get(EXTRA,{}).get('schema')==ID),'Cannot remove mandatory route from unresolved spent identity')", "   require(not m['bridge']['selected'](c)or m['bridge']['result_path'](c).exists(),'Cannot remove mandatory route from unresolved spent identity')")
ph=hashlib.sha256(previous.encode()).hexdigest();assert ph.startswith('cf114279'),ph
with(O/'consumer.PRE_ACCEPTED_RESTORE_CF114.py').open('x')as f:f.write(previous)
with(O/'CF114_TO_FINAL_DE70_RESTORE_ONLY.diff').open('x')as f:f.write(''.join(difflib.unified_diff(previous.splitlines(True),current.splitlines(True),fromfile='consumer_cf114.py',tofile='consumer_de70.py')))
contract=read(A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json')
rows=[]
for c in contract['scope_cohorts']:
 p=R/'analysis'/(c+'.RESULT.json');row={'cohort':c,'RESULT_exists':p.exists()}
 if p.exists():row.update(RESULT_sha256=sha(p),state=read(p).get('state'))
 rows.append(row)
put('PRODUCTION_RELEASE_STATUS.json',{'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'NOT_ELIGIBLE_NOT_INSTALLED','actual_models_qualified':False,'actual_V2_full_four_replay_receipt_captured_by_this_package':False,'observed_results':rows,'production_changes':0,'new_grants':0,'models_started':0})
put('INTERFACE.json',{'schema':'DTC_BPF_V3_EXTRA_CONSUMER_CANDIDATE_INTERFACE','ID':'DTC_STRACE_FUTURE_ENTRY_V3','source_roles':['entry','frontend','producer','extra_strict','consumer'],
 'extra_sha256':sha(O/'bpf_extra_strict.py'),'consumer_sha256':sha(O/'consumer_bridge.py'),'B_runtime_sources':expected,
 'policy_source_sha256':'389be2e9dc01e071bc4c3edae10f8fa67ba1555c357840225b4a9687b8622b91',
 'APIs':{'extra.normalize_contract':'(cfg,root,source_sha256=None,qualification_only=False)','extra.terminal':'(c,base_proof,root,contract,authority,readonly=False)','extra.verify_archive':'(c,archive,root,contract)','extra.capture_release_prerequisite':'(actual_frame,actual_main,path) explicit Main-only real4 full replay receipt writer','extra.verify_release_prerequisite':'(cfg,q) -> ACTUAL_CANARY4_GATE_VERIFIED or private CPU_ONLY_GATE_QUALIFIED_NOT_PRODUCTION_RELEASE; raises HOLD on all missing/invalid cases','consumer.make_private_consumer':'(consumer,contract,extra,authority_provider)','consumer.install_on_frame':'(frame,cfg_path,owner_assert,main=None,qualification_loader_sha256=None)','consumer.consumer_check':'(frame,cfg)','consumer.restore_in_owner':'(owner_assert,main=None)'},
 'markers':{'consumer':'DTC_STRACE_BPF_PRIVATE_CONSUMER_V3','Bdispatcher':'DTC_STRACE_FUTURE_DISPATCH_V3'},
 'install_order':['Real4 V2 fullchain qualification and source-bound capture','Main official source/QA/readback and required q/memory/scope amendments','E V3 actual frame-private consumer outer route','B V3 same-owner private dispatcher','Main explicit activation'],
 'restore_order':'B V3 before E V3; admitted dangling routeclaim/unresolved spent identity retains mandatory route and requires Main disposition',
 'current_status':'NOT_ELIGIBLE_NOT_INSTALLED','production_ready':False,'actual_models_qualified':False,
 'CPU_qualification':{'gate_routing':{'count':15,'sha256':sha(O/'CPU_GATE_ROUTING_QUALIFICATION.json')},'actual_prefix_consumer':{'count':28,'sha256':sha(O/'CPU_PREFIX_CONSUMER_QUALIFICATION.json')}},
 'physics_and_archive_transport':'Explicit CPU stand-ins; no real simulation/true164 transport qualified by these fixtures',
 'prior_A_joint_preimage_sha256':ph,'primary350_unchanged':True,'IR_statistical_union_authorized':False})
names=['bpf_extra_strict.py','consumer_bridge.py','build_extra.py','gate_functions.py','qualify_gate_routing.py','qualify_prefix_consumer.py','freeze_package.py','README.md','INTERFACE.json','PRODUCTION_RELEASE_STATUS.json','CPU_GATE_ROUTING_QUALIFICATION.json','CPU_PREFIX_CONSUMER_QUALIFICATION.json','consumer.PRE_ACCEPTED_RESTORE_CF114.py','CF114_TO_FINAL_DE70_RESTORE_ONLY.diff']
h=put('MANIFEST.json',{'schema':'DTC_E_FUTURE_BPF_V3_FULL_STRICT_CONSUMER_CANDIDATE_MANIFEST','status':'FROZEN_CPU_QUALIFIED_PRODUCTION_RELEASE_HOLD','files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in names],'models_started':0,'new_grants':0,'production_changes':0})
print(json.dumps({'manifest_sha256':h,'extra_sha256':sha(O/'bpf_extra_strict.py'),'consumer_sha256':sha(O/'consumer_bridge.py'),'gate15_QA_sha256':sha(O/'CPU_GATE_ROUTING_QUALIFICATION.json'),'prefix28_QA_sha256':sha(O/'CPU_PREFIX_CONSUMER_QUALIFICATION.json'),'cf114_preimage_sha256':ph}))
