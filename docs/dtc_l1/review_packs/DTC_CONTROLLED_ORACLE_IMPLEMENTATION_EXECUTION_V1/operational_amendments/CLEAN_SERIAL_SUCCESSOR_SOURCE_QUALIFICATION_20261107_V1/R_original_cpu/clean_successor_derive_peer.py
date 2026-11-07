from pathlib import Path
import json,hashlib,ast
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');X=A/'agents/R_clean_successor_cpu_preparation_v1';X.mkdir(exist_ok=True)
p=A/'agents/P_resource_peer_adapter_v1/v5_cpu_draft_peer/oracle_peer_disk_adapter_v5.py';raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()=='1d93127340982e744c35763234e5cdcdef384c4346991cbf57869dc4491a5e10';s=raw.decode()
helper='''def _clean_cpu_resource_candidate(root,request):
 root=P(root);normal=root/'control/REGISTRY_REQUEST_CANDIDATE.json'
 if normal.exists():
  q=read(normal);require(q['request']==request,'CLEAN_FINAL_CANDIDATE_REQUEST');return q,{'kind':'NORMAL_UNREGISTERED_CLEAN_CANDIDATE','path':str(normal),'sha256':sha(normal),'scientific_authority_granted_by_adapter':False}
 require(request=='DTC_ORACLE_REMAINING24_20261106_V1','EXACT_CLEAN96_REQUEST')
 plan=read(root/'control/EXECUTION_PLAN.json');require(plan['preparation_phase']=='CPU_CLEAN_SUCCESSOR_DRAFT_NOT_REGISTERED'and plan['actual_execution_authorized']is False,'CLEAN_CPU_RESOURCE_PHASE')
 require(not(root/'control/SCIENCE_AUTHORIZATION.json').exists(),'NO_NORMAL_AUTH_IN_CLEAN_CPU_STAGE')
 m=root/'control/CLEAN_CPU_ARTIFACTS_MANIFEST.json';mp=read(m)
 require(mp['schema']=='DTC_CLEAN_SUCCESSOR_CPU_ARTIFACTS_MANIFEST_V1'and mp['request']==request and mp['registered']is False and mp['models_started']==0 and mp['scientific_UUIDs_allocated']==0,'CLEAN_CPU_MANIFEST_STATE')
 p=root/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json';q=read(p)
 require(mp['resource_candidate_sha256']==sha(p)and mp['plan_sha256']==sha(root/'control/EXECUTION_PLAN.json'),'CLEAN_CPU_RESOURCE_PINS')
 require(q['request']==request and q['budget']==q['remaining']==96 and not q['consumed']and not q.get('sealed')and q['ready_for_registration']is False and q['science_authority']is False,'CLEAN_CPU_NO_CONSUMPTION_OR_AUTHORITY')
 require(q['execution_plan_sha256']==sha(root/'control/EXECUTION_PLAN.json'),'CLEAN_CPU_PLAN_BINDING')
 require(not(root/'control/POOL_DISPATCH_RESERVATIONS.json').exists()or not read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'],'CLEAN_CPU_NO_CLAIMS')
 require(not any((root/'control/qualification_ledger').glob('*.INTENT.json'))and not any((root/'control/qualification_ledger').glob('*.DONE.json')),'CLEAN_CPU_NO_LIFECYCLE')
 require(not(root/'DTC/run/results').exists()or not any((root/'DTC/run/results').iterdir()),'CLEAN_CPU_NO_RESULT_UUID')
 return q,{'kind':'EXPLICIT_CLEAN_CPU_RESOURCE_EVIDENCE_ONLY','path':str(p),'sha256':sha(p),'science_ready':False,'consumption_permitted':False,'scientific_authority_granted_by_adapter':False}

'''
anchor='def _worker(spec,plan):';assert s.count(anchor)==1;s=s.replace(anchor,helper+anchor)
a="require(len(oracle_roots)==len(set(oracle_roots.values()))==2,'EXACT_TWO_ORACLE_STAGE_ROOTS_REQUIRED')";b="require(len(oracle_roots)==len(set(oracle_roots.values()))==1,'EXACT_ONE_CLEAN_NEW96_ROOT_REQUIRED')\n require(ownrequest=='DTC_ORACLE_REMAINING24_20261106_V1'and str(root)=='/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24','EXACT_CLEAN_SERIAL_SUCCESSOR_ROOT_SCOPE')";assert s.count(a)==1;s=s.replace(a,b)
a="else:q,stage_candidate_sources[request]=_resource_candidate(rp,request,allow_draft_peer=request!=ownrequest)";b="else:q,stage_candidate_sources[request]=_clean_cpu_resource_candidate(rp,request)";assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("'DTC_CONTROLLED_ORACLE_BOUNDED_NATIVE_PEER_ADAPTER_V5_CPU_DRAFT_PEER'","'DTC_CONTROLLED_ORACLE_BOUNDED_NATIVE_PEER_ADAPTER_CLEAN_SUCCESSOR_V1'")
compile(s,'<CLEAN_CPU_PEER_ADAPTER>','exec');p=X/'oracle_clean_peer_disk_adapter.py';assert not p.exists();p.write_text(s)
proof={'schema':'DTC_CLEAN_PEER_ADAPTER_EXACT_TRANSFORM_V1','original_path':str(A/'agents/P_resource_peer_adapter_v1/v5_cpu_draft_peer/oracle_peer_disk_adapter_v5.py'),'original_sha256':hashlib.sha256(raw).hexdigest(),'derived_sha256':hashlib.sha256(s.encode()).hexdigest(),'scope':'Exactly one new96 request root; explicit CPU-only resource candidate cannot register or consume; normal final/actual registry paths remain required for science. Original32 is external read-only peer, no old context attachment. All original bounded SH snapshot/peer/legacy/reservation accounting retained.','budget':96,'actual_scientific_models':0,'source_version':'PREPARATION_ONLY_PENDING_INDEPENDENT_REVIEW'};(X/'PEER_EXACT_TRANSFORM_PROOF.json').write_text(json.dumps(proof,sort_keys=True,indent=2)+'\n');print(json.dumps(proof))
