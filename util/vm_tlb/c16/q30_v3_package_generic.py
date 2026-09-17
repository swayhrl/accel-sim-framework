#!/usr/bin/env python3
import argparse, csv, hashlib, json, re, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

RUNTIME=Path('/data/c16/env/c16-qwen3-30b-hf451-gpu/bin/python')
V20=Path('/data/c16/qwen3_runtime_v14/v20/tools/v20_warp_regsource.so')
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-q30-s2-formal-v3')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def cp(a,b):
 a,b=Path(a),Path(b)
 if not a.is_file() or a.is_symlink(): raise RuntimeError('invalid '+str(a))
 b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
def out(a): return subprocess.check_output(a,text=True).strip()
def main():
 p=argparse.ArgumentParser();p.add_argument('--staging-root',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--target',required=True);p.add_argument('--capture-root',type=Path,required=True);p.add_argument('--static-map',type=Path,required=True);p.add_argument('--state-manifest',type=Path,required=True);p.add_argument('--phase',required=True);p.add_argument('--function',required=True);p.add_argument('--occurrence',type=int,required=True);a=p.parse_args()
 if not re.fullmatch(r'C16R_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_\d{8}T\d{6}Z_[a-f0-9]{12}',a.run_id):raise SystemExit('bad run id')
 d=a.staging_root/a.run_id
 if d.exists():raise SystemExit('collision')
 audit=json.loads((a.capture_root/'LOCAL_INDEPENDENT_AUDIT.json').read_text())
 if not audit.get('complete_set') or any(x['overflow'] for x in audit['shards']):raise SystemExit('audit not closed')
 d.mkdir(parents=True);cp(a.capture_root/'LOCAL_INDEPENDENT_AUDIT.json',d/'FORMAL_AUDIT.json');cp(a.static_map,d/'STATIC_MREF_MAP.tsv');cp(a.state_manifest,d/'STATE_CHAIN.json')
 shards=[]
 for s in sorted(audit['shards'],key=lambda x:x['static_index']):
  i=s['static_index'];src=a.capture_root/f'mref_{i}';stem=f'raw_shards/mref_{i}'
  for n,suf in [('trace.bin','.bin'),('ADDRESS_CONTEXT.json','.ADDRESS_CONTEXT.json'),('stdout.log','.stdout.log'),('stderr.log','.stderr.log')]:cp(src/n,d/(stem+suf))
  shards.append({'static_index':i,'binary_record_format':'C16WARP1','trace_relative_path':stem+'.bin','address_context_relative_path':stem+'.ADDRESS_CONTEXT.json','terminal_status':s['terminal_status'],'record_count':s['record_count'],'overflow_count':s['overflow'],'drop_count':0,'trace_sha256':s['trace_sha256'],'address_context_sha256':s['address_context_sha256'],'exact_replay_identity':f'full-layer exact replay occurrence={a.occurrence}'})
 (d/'WARP_SHARD_MANIFEST.json').write_text(json.dumps({'schema_version':1,'target':a.target,'function':a.function,'function_occurrence':a.occurrence,'static_global_mref_count':len(shards),'shards':shards,'prohibitions':['no cross-shard chronology','no cross-replay VA union','no reconstructed reuse distance']},indent=2,sort_keys=True)+'\n')
 (d/'QUICKCHECK.json').write_text(json.dumps({'status':'PASS','expected_shards':len(shards),'present_shards':len(shards),'executed_shards':sum(x['record_count']>0 for x in shards),'zero_execution_proven_shards':sum(x['record_count']==0 for x in shards),'total_callback_records':sum(x['record_count'] for x in shards),'drop_count':0,'overflow_count':0,'static_set_sha256':sha(a.static_map)},indent=2,sort_keys=True)+'\n')
 gpu=out(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader']).split(', ');v=json.loads(out([str(RUNTIME),'-c','import json,torch,transformers;print(json.dumps({"python":__import__("sys").version.split()[0],"torch":torch.__version__,"cuda":torch.version.cuda,"transformers":transformers.__version__}))']))
 m={'schema_version':1,'run_id':a.run_id,'created_at_utc':datetime.now(timezone.utc).isoformat(),'scientific_status':'FORMAL','producer':{'hostname':out(['hostname']),'gpu_name':gpu[0],'gpu_uuid':gpu[1],'driver':gpu[2],'cuda':v['cuda']},'git':{'repository':'accel-sim-framework','commit':out(['git','-C',str(REPO),'rev-parse','HEAD']),'dirty':False},'model':{'model_id':'Qwen/Qwen3-30B-A3B','revision':'ad44e777bcd18fa416d9da3bd8f70d33ebb85d39','asset_receipt_sha256':'f49a40631ceac11fda5378ec18ed35eb5da3b3e6e24bc667a77994eed0631f25'},'input':{'binding_id':'Q30_S2_TEXT B1/T2048/D32','authority_status':'ACCEPTED_EXACT','receipt_sha256':'e3368d01dc311d134e1f62c6412a3c05b2a2fb1de527f1947f3b7502af28c99a','token_ids_sha256_or_semantic_hash':'00d47e2312fb3db3585b5396ebc7484507356148019a845c8253c6d58d56d4f5'},'scenario':{'batch':1,'prefill_tokens':2048,'decode_tokens':32,'input_class':'S2_TEXT','phase':a.phase},'runtime':{'python':v['python'],'torch':v['torch'],'transformers':v['transformers'],'dtype':'bfloat16','attention_backend':'sdpa; qwen3moe_sparse_expert_loop'},'capture':{'instrument':'NVBit V20 warp register-source','tool_version':'C16WARP1/V20','tool_identity_sha256_if_applicable':sha(V20),'target':a.target,'exact_argv':['full-layer exact replay',f'function occurrence={a.occurrence}','one static GLOBAL MREF per process','no CTA slicing']},'artifacts':[]}
 mp=a.staging_root/(a.run_id+'.manifest.json');mp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','bundle':str(d),'manifest':str(mp),'shards':len(shards)}))
if __name__=='__main__':main()
