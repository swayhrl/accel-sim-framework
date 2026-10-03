#!/usr/bin/env python3
"""Bounded parent and exact-seed qualification for R27R2 Gate A."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import torch
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(memoryview(t.detach().contiguous().cpu().view(torch.uint8).numpy())).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--pack',required=True);ap.add_argument('--common',required=True);ap.add_argument('--model',required=True);ap.add_argument('--model-receipt',required=True);ap.add_argument('--seed',required=True);ap.add_argument('--admission',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();repo,pack,common,model,seed=map(Path,(a.repo,a.pack,a.common,a.model,a.seed));errors=[]
 commit='254d66f69ec81bf932add705f721f36255feef2c';tree='ebefec69e9ba153adfaf5d1f7860a956964d09cb';got_tree=subprocess.check_output(['git','-C',str(repo),'rev-parse',f'{commit}^{{tree}}'],text=True).strip()
 if got_tree!=tree:errors.append('closed R27R1 commit/tree')
 pe=[]
 for line in (pack/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);g=sha(pack/n)
  if h!=g:pe.append((n,h,g))
 if pe:errors.append('R27R1 pack hashes')
 d=json.loads((pack/'FINAL_DECISION.json').read_text());p=json.loads((pack/'PARENT_IDENTITY_RECHECK.json').read_text())
 if d['decision']!='R27R1_INPUT_OR_SOURCE_NOT_QUALIFIED' or not p['qualified'] or p['status']!='R27R1_PARENT_AUTHORITY_QUALIFIED':errors.append('accepted R27R1 state')
 s=torch.load(common,map_location='cpu',weights_only=False);ci={'path':str(common),'bytes':common.stat().st_size,'sha256':sha(common),'logical_step':s.get('step'),'schema':s.get('schema'),'weight_sha256':tsha(s['weight']),'m_sha256':tsha(s['m']),'v_sha256':tsha(s['v']),'cpu_rng_sha256':tsha(s['cpu_rng']),'cuda_rng_sha256':tsha(s['cuda_rng']),'all_cpu':all(x.device.type=='cpu' for x in s.values() if isinstance(x,torch.Tensor)),'identity':s.get('identity')}
 exp=p['consumed_common_checkpoint']
 if ci['bytes']!=2626691315 or ci['sha256']!='09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55' or ci['logical_step']!=1 or not ci['all_cpu']:errors.append('common file/state')
 for n in ('weight','m','v'):
  if ci[f'{n}_sha256']!=exp[f'{n}_sha256']:errors.append(f'common {n}')
 source=[]
 for x in p['R26_frozen_source']:
  q=repo/'util/vm_tlb/awma/r26_tied_weight_production_capacity'/Path(x['path']).name;g=sha(q);source.append({'path':str(q),'sha256':g,'expected':x['expected'],'qualified':g==x['expected']})
 if not all(x['qualified'] for x in source):errors.append('R26 source')
 receipt=json.loads(Path(a.model_receipt).read_text());payload=[];total=0
 for x in receipt['payloads']:
  q=model/x['filename'];z=q.stat().st_size;g=sha(q);total+=z;payload.append({'filename':x['filename'],'bytes':z,'sha256':g,'qualified':z==x['size_bytes'] and g==x['sha256']})
 if sha(a.model_receipt)!='7694c95442cc7ff1d3fc8ed1104d5c0d6a50c3a17f779f402ef90669edeb7b47' or total!=2480783094 or not all(x['qualified'] for x in payload):errors.append('model payload')
 cce=[]
 for rel,e in [('cut_cross_entropy/cce_backward.py','e5402a590ef019692d8341805d3adf18ed95d3062c59236b364322c296b42d36'),('cut_cross_entropy/tl_utils.py','e117b70a0fdc2ec4313fd7d9ba5a7e1d78b30fb478760c3c661f9d717cc65ea4'),('cut_cross_entropy/tl_autotune.py','445745f6c20efcd5bcfb2fbc784361c3b4a3a0e8f2089242fde6d4362a977a20')]:
  q=Path('/data/c16/awma/r26_tied_weight_production_capacity_109_v1_20261002/source/cce')/rel;g=sha(q);cce.append({'path':str(q),'sha256':g,'expected':e,'qualified':g==e})
 if not all(x['qualified'] for x in cce):errors.append('CCE source')
 adm=json.loads(Path(a.admission).read_text());si={'path':str(seed),'bytes':seed.stat().st_size,'sha256':sha(seed),'mtime':seed.stat().st_mtime,'node164':adm['node164']}
 if si['bytes']!=6357543 or si['sha256']!='e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7' or adm['status']!='R27R2_EXACT_INPUT_ADMITTED' or not adm['node164']['readback_passed']:errors.append('seed admission')
 out={'schema':'R27R2_GATE_A_PARENT_SEED_QUALIFICATION_V1','status':'R27R2_PARENT_AND_SEED_QUALIFIED' if not errors else 'R27R2_PARENT_OR_SEED_NOT_QUALIFIED','qualified':not errors,'closed_R27R1':{'commit':commit,'tree':got_tree,'pack_entries':len((pack/'SHA256SUMS').read_text().splitlines()),'pack_errors':pe,'decision':d['decision'],'parent_status':p['status']},'common':ci,'R26_source':source,'CCE':cce,'model':{'path':str(model),'payload_total_bytes':total,'payloads':payload},'seed':si,'admission_receipt':{'path':a.admission,'sha256':sha(a.admission)},'historical_207_audit_rerun':False,'network_attempts':0,'CUDA_JIT_operations':0,'GPU_lock_acquisitions':0,'errors':errors}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'errors':errors},sort_keys=True));raise SystemExit(0 if not errors else 2)
if __name__=='__main__':main()
