#!/usr/bin/env python3
"""Version the pre-registration EXT1 Spec after bounded stale-RAM diagnosis."""
import hashlib,json,os
from pathlib import Path
P=Path
R=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
C='EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1'
H=R/'runtime/host_stencil_ext1_bound_v1'
S=R/'cases'/C/'control/FROZEN_SPEC.json'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def enc(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def once(p,b):
 if p.exists():assert p.read_bytes()==b,str(p)
 else:
  with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def main():
 reg=json.loads((N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes())['registered_future_requests']
 assert 'EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1' not in reg
 assert json.loads((R/'control/DISPATCH_CLAIMS.json').read_bytes())['claims']=={}
 s=json.loads(S.read_bytes());once(S.with_name('FROZEN_SPEC.version1.json'),S.read_bytes())
 oldq=P(s['host_qualification_ref']['path']);q=json.loads(oldq.read_bytes())
 v1=H/'resources_ext1.py';pin=sha(v1)
 body='''"""Bounded correction of terminal legacy RAM metadata for EXT1 admission."""\nimport hashlib,importlib.util,json\nfrom pathlib import Path\nP=Path\nBASE=P("'''+str(v1)+'''")\nPIN="'''+pin+'''"\nREG=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')\nEP_CLOSED=('EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1','EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1','EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1','EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1','EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1','EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1','EP_L2_UMT1_SCAN_CF8D1C4D_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1','EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104')\nDTC_TERMINAL=('DTC_ORACLE_INITIAL8_20261106_V1','DTC_ORACLE_REMAINING24_20261106_V1','DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1','DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1','DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1','DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1')\ndef impl():\n assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PIN\n x=importlib.util.spec_from_file_location('ext1_v1_resources',BASE);m=importlib.util.module_from_spec(x);x.loader.exec_module(m);return m\ndef snapshot():\n s=impl().snapshot()\n if s['actual_loader_aware_models']:return s\n raw=REG.read_bytes()\n if hashlib.sha256(raw).hexdigest()!=s['registry_sha256']:s['foreign_metadata_errors'].append('registry changed during EXT1 terminal audit');return s\n rows=json.loads(raw)['registered_future_requests'];clear=[]\n for req in EP_CLOSED+DTC_TERMINAL:\n  q=rows[req];cs=q.get('consumed')\n  if not(isinstance(cs,dict) and q.get('remaining')==0 and len(cs)==q.get('budget')):return s\n  if req in EP_CLOSED:\n   if not(q.get('state')=='CLOSED_COMPLETED' and q.get('reserved_write_bytes')==0 and all(r.get('state') in ('CLOSED_ACCEPTED','CLOSED_UNACCEPTED') for r in cs.values())):return s\n  else:\n   if not(q.get('state')=='RUNNING' and all(isinstance(r.get('execution_receipt'),dict) and r.get('charged')==1 for r in cs.values())):return s\n  clear.append('unmapped active foreign RAM owner '+req)\n if not set(clear).issubset(set(s['foreign_metadata_errors'])):return s\n s['foreign_metadata_errors']=[e for e in s['foreign_metadata_errors'] if e not in clear]\n s['ext1_legacy_terminal_reconciliation']={'cleared_errors':clear,'registry_sha256':s['registry_sha256'],'no_live_models':True,'foreign_write_commitments_retained':True}\n return s\ndef admit(s,additional,writes,policy):return impl().admit(s,additional,writes,policy)\n'''
 v2=H/'resources_ext1_v2.py';once(v2,body.encode())
 q['modules'].append(ref(v2));qp=R/'documents/HOST_QUALIFICATION_EXT1_STENCIL_V2.json';once(qp,enc(q))
 b={'schema':'EP_L2_EXT1_MAIN_ENGINEERING_BINDING_V2','authorization_ref':s['Main_scientific_launch_authorization'],'host_qualification_ref':ref(qp),'old_ext2_spec_ref':ref(R/'cases/EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1/control/FROZEN_SPEC.json'),'source_keep':True,'models_started':False,'reason':'versioned pre-registration legacy terminal RAM diagnostic correction'}
 bp=R/'documents/MAIN_ENGINEERING_BINDING_EXT1_V2.json';once(bp,enc(b))
 s['resource_module_ref']=ref(v2);s['host_qualification_ref']=ref(qp);s['Main_engineering_binding_ref']=ref(bp);s['pinned_files'][str(v2)]=sha(v2)
 new=enc(s)
 with S.with_name('.FROZEN_SPEC.ext1_v2.tmp').open('wb') as f:f.write(new);f.flush();os.fsync(f.fileno())
 os.replace(S.with_name('.FROZEN_SPEC.ext1_v2.tmp'),S)
 print(json.dumps({'status':'EXT1_PRE_REGISTRATION_SPEC_V2','spec_ref':ref(S),'resource_ref':ref(v2)}))
if __name__=='__main__':main()
