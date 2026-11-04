#!/usr/bin/env python3
"""Pure successor Host-only binder. Writes only requested independent output; never registry/native install/start."""
import pathlib,json,hashlib,copy,argparse
P=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(pathlib.Path(p).resolve()),sha256=sha(p))
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
HOST_FIELDS={'host_common_ref','host_engine_ref','host_qualification_ref','helpers_ref','archive_module_ref','compact_module_ref','output_module_ref','postprocess_module_ref','validation_module_ref','resource_module_ref','resource_policy_ref','mode_contract_ref','pinned_files','native_entry_ref','validation_contract_ref'}
MODULES={'host_common_ref':'ep_perf_common_v2.py','host_engine_ref':'ep_perf_native_wv_modes_draft.py','archive_module_ref':'ep_perf_archive.py','postprocess_module_ref':'ep_perf_postprocess.py','validation_module_ref':'mode_aware_terminal.py','mode_contract_ref':'mode_contract.py'}
def bind(tag,bindings,out):
 out=pathlib.Path(out).resolve();assert out.is_relative_to(P),'candidate output must stay in private agent_b_native tree; Main installs separately'
 g=read(P/'RECOVERY_GROUPS.json')['groups'][tag];root=pathlib.Path(g['data_ROOT']);r=pathlib.Path(g['new_runtime_root']);old=pathlib.Path(g['old_runtime_root']);rows=[]
 qref=ref(bindings['host_qualification_path']);q=read(qref['path'])
 assert q['status']=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'and q['approved_by']=='EP-MAIN','requires actual Main-signed HostQ'
 for item in q['modules']:assert sha(item['path'])==item['sha256']
 native=read(P/tag/'NATIVE_ENTRY_ROUTE_RECOVERY_20261104_V1.json')['entry_ref']
 for case in g['unconsumed']:
  original=root/'cases'/case/'control/FROZEN_SPEC.json';a=read(original);assert sha(original)==g['original_admitted_specs'][case],'old unspent spec drift'
  b=copy.deepcopy(a)
  for k,f in MODULES.items():b[k]=ref(r/f)
  b['host_qualification_ref']=qref;b['native_entry_ref']=native
  for k in ['resource_module_ref','resource_policy_ref']:
   if k in bindings:b[k]=bindings[k];assert sha(b[k]['path'])==b[k]['sha256']
  # Keep every old pin incl. model argv/config dependencies, append new exact Host modules only.
  for p in r.rglob('*'):
   if p.is_file()and '__pycache__'not in str(p):b['pinned_files'][str(p)]=sha(p)
  for k in MODULES:b['pinned_files'][b[k]['path']]=b[k]['sha256']
  for k in ['resource_module_ref','resource_policy_ref']:b['pinned_files'][b[k]['path']]=b[k]['sha256']
  for item in bindings.get('additional_pinned_refs',[]):
   assert sha(item['path'])==item['sha256'];b['pinned_files'][item['path']]=item['sha256']
  delta=[k for k in a if a[k]!=b[k]];assert set(a)==set(b)and set(delta)<=HOST_FIELDS
  f=out/'specs'/case/'FROZEN_SPEC.json';write(f,b)
  rows.append(dict(cohort=case,request_id=g['goal'],original_spec_ref=ref(original),successor_spec_ref=ref(f),changed_fields=delta,same_gpu_source_input_282_argv_observer=True))
 result=dict(schema='EP_MAIN_RECOVERY_HOST_ONLY_SPEC_INDEX_V1',group=tag,request_id=g['goal'],runtime_root=str(r),entry_candidate_ref=ref(P/tag/'native_recovery_20261104_v1'),entry_target_ref=native,route_candidate_ref=ref(P/tag/'NATIVE_ENTRY_ROUTE_RECOVERY_20261104_V1.json'),route_target=str(root/'control/NATIVE_ENTRY_ROUTE_RECOVERY_20261104_V1.json'),host_qualification_ref=qref,rows=rows,consumed_original_preserved=g['consumed'],scientific_starts=0,installed=False)
 write(out/'SPEC_INDEX.json',result);return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--group',choices=['highclock','system'],required=True);a.add_argument('--bindings',required=True);a.add_argument('--out',required=True);v=a.parse_args();print(json.dumps(bind(v.group,read(v.bindings),pathlib.Path(v.out))))
