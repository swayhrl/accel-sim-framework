#!/usr/bin/env python3
"""CPU-only binding of the independently published Lane8 STATIC_GATE."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from contracts import KS,footprint_rows

GATE_PATH='docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1/STATIC_GATE.json'
SOURCE_PATH='util/vm_tlb/c16/splitk_footprint_static_audit/footprint_audit.py'
def git(repo,*args,text=False):return subprocess.check_output(['git','-C',str(repo),*args],text=text)
def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def sha_file(path):return sha_bytes(Path(path).read_bytes())
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--gate-commit',required=True);p.add_argument('--pack',type=Path,required=True);a=p.parse_args();raw=git(a.repo,'show',f'{a.gate_commit}:{GATE_PATH}');gate=json.loads(raw)
 if gate['status']!='SUPPORTED_PROCEED_NATIVE_THRESHOLD_SCREEN' or gate['lane7_authorization']['only_K']!=list(KS):raise RuntimeError('unsupported or mismatched gate')
 if not gate['lane7_authorization']['native_threshold_screen_may_proceed']:raise RuntimeError('native authorization false')
 local={int(r['K']):r for r in footprint_rows()};rows=[]
 for k in KS:
  remote=gate['exact_footprint_bytes'][str(k)];row={'K':k,'full_w4_bytes':remote['split1'],'full_over_l2':remote['split1_over_64MiB'],'split8_static_bytes':remote['split8_each_split'],'split8_over_l2':remote['split8_over_64MiB']}
  if row['full_w4_bytes']!=local[k]['full_w4_bytes'] or row['split8_static_bytes']!=local[k]['candidate_split8_static_bytes']:raise RuntimeError(f'footprint mismatch {k}')
  rows.append(row)
 tree=git(a.repo,'rev-parse',f'{a.gate_commit}^{{tree}}',text=True).strip();source_blob=git(a.repo,'rev-parse',f'{a.gate_commit}:{SOURCE_PATH}',text=True).strip()
 binding={'status':'PASS_STATIC_GATE_BOUND','gate_status':gate['status'],'gate_branch':'hrl/c16-splitk-footprint-static-audit-174new-v1','gate_commit':a.gate_commit,'gate_tree':tree,'gate_path':GATE_PATH,'gate_file_sha256':sha_bytes(raw),'source_path':SOURCE_PATH,'source_blob':source_blob,'k_contract_sha256':canonical({'M':256,'N':49152,'group_size':128,'only_K':gate['lane7_authorization']['only_K'],'split':[1,8],'state':'WARM_SAME_ARM'}),'footprint_table_sha256':canonical(gate['exact_footprint_bytes']),'footprint_rows':rows,'scientific_boundary':gate['scientific_boundary'],'gpu_authorized':True}
 a.pack.mkdir(parents=True,exist_ok=True);(a.pack/'STATIC_GATE_BINDING.json').write_text(json.dumps(binding,indent=2,sort_keys=True)+'\n')
 manifest=json.loads((a.pack/'SOURCE_AND_RUN_MANIFEST.json').read_text());manifest.update({'status':'CPU_PREP_AND_STATIC_GATE_PASS_GPU_AUTHORIZED','gate_status':gate['status'],'static_gate_binding_sha256':sha_file(a.pack/'STATIC_GATE_BINDING.json')});q=Path(__file__);manifest['source_files'].append({'path':str(q.relative_to(a.repo)),'sha256':sha_file(q),'bytes':q.stat().st_size});(a.pack/'SOURCE_AND_RUN_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 receipt=json.loads((a.pack/'CPU_PREP_RECEIPT.json').read_text());receipt.update({'status':'CPU_PREP_AND_STATIC_GATE_PASS_GPU_AUTHORIZED','static_gate_binding_sha256':sha_file(a.pack/'STATIC_GATE_BINDING.json'),'cuda_imported':False,'gpu_lock_requested':False});(a.pack/'CPU_PREP_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':binding['status'],'gate_status':binding['gate_status'],'gate_commit':a.gate_commit,'gate_tree':tree},sort_keys=True))
if __name__=='__main__':main()
