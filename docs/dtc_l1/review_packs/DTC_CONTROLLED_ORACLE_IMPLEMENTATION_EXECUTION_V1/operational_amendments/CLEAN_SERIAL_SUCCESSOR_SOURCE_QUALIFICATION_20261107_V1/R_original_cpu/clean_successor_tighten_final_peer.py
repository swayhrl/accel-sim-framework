from pathlib import Path
import hashlib,json,os
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');X=A/'agents/R_clean_successor_cpu_preparation_v1';R=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24');p=X/'oracle_clean_peer_disk_adapter.py';s=p.read_text();old=s;anchor="q=read(normal);require(q['request']==request,'CLEAN_FINAL_CANDIDATE_REQUEST');return q,{'kind':'NORMAL_UNREGISTERED_CLEAN_CANDIDATE','path':str(normal),'sha256':sha(normal),'scientific_authority_granted_by_adapter':False}"
replacement="""q=read(normal);plan=read(root/'control/EXECUTION_PLAN.json');auth=read(root/'control/SCIENCE_AUTHORIZATION.json')
  require(q['request']==request and q['ready_for_registration']is True,'CLEAN_FINAL_CANDIDATE_REQUEST_AND_READY')
  require(plan['preparation_phase']=='SCIENCE_FINAL_FROZEN'and plan['actual_execution_authorized']is True and q['execution_plan_sha256']==sha(root/'control/EXECUTION_PLAN.json'),'CLEAN_FINAL_PLAN_REQUIRED')
  require(auth['schema']=='DTC_ORACLE_SCIENCE_AUTHORIZATION_V1'and auth['ready_for_registration']is True and auth['owner_bindings_ratified']is True and auth['target_resource_policy_ratified']is True,'CLEAN_FINAL_AUTH_REQUIRED')
  return q,{'kind':'NORMAL_UNREGISTERED_CLEAN_CANDIDATE','path':str(normal),'sha256':sha(normal),'scientific_authority_granted_by_adapter':False}"""
assert s.count(anchor)==1;s=s.replace(anchor,replacement);compile(s,'<CLEAN_PEER_FINAL_METADATA_GUARD>','exec');(X/'oracle_clean_peer_disk_adapter.PREP0.py').write_text(old);p.write_text(s);(R/'tools/oracle_clean_peer_disk_adapter.py').write_text(s)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();enc=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode();rd=lambda p:json.loads(Path(p).read_bytes())
# Explicitly preserve each prior CPU metadata image. No registered science exists.
for name in['EXECUTION_PLAN.json','RESOURCE_REQUEST_CANDIDATE.CPU.json','CLEAN_CPU_ARTIFACTS_MANIFEST.json']:
 pp=R/'control'/name;(X/(name+'.CPU_PREIMAGE.v1')).write_bytes(pp.read_bytes())
pl=rd(R/'control/EXECUTION_PLAN.json');pl['peer_disk_adapter']['sha256']=sha(p)
for pin in pl['source_pins']:
 if pin['path']==str(R/'tools/oracle_clean_peer_disk_adapter.py'):pin['sha256']=sha(p)
(R/'control/EXECUTION_PLAN.json').write_bytes(enc(pl));q=rd(R/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json');q['execution_plan_sha256']=sha(R/'control/EXECUTION_PLAN.json');(R/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json').write_bytes(enc(q));mf=rd(R/'control/CLEAN_CPU_ARTIFACTS_MANIFEST.json');mf.update(plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),resource_candidate_sha256=sha(R/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json'),CPU_metadata_forward_revision={'reason':'Tighten finalnormalcandidate guard to require genuine final phase/auth; CPU resource evidence cannot be renamed as science authority. No exec/science projection changes.','previous_manifest_path':str(X/'CLEAN_CPU_ARTIFACTS_MANIFEST.json.CPU_PREIMAGE.v1'),'previous_manifest_sha256':sha(X/'CLEAN_CPU_ARTIFACTS_MANIFEST.json.CPU_PREIMAGE.v1')})
for f in mf['files']:
 if f['path']in['control/EXECUTION_PLAN.json','control/RESOURCE_REQUEST_CANDIDATE.CPU.json']:f['sha256']=sha(R/f['path'])
(R/'control/CLEAN_CPU_ARTIFACTS_MANIFEST.json').write_bytes(enc(mf));print(json.dumps({'new_peer_sha256':sha(p),'newplan':sha(R/'control/EXECUTION_PLAN.json'),'newmanifest':sha(R/'control/CLEAN_CPU_ARTIFACTS_MANIFEST.json'),'layout_unchanged':sha(R/'control/LAUNCHER_LAYOUT.fixed.json')},indent=2))
