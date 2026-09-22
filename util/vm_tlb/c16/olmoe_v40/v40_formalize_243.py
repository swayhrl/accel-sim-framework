#!/usr/bin/env python3
"""Fail-closed CPU re-admission of immutable V40 shards."""
import csv, hashlib, json, os, subprocess
from pathlib import Path

REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v40-publish-109-v1')
ROOT=Path('/data/c16/olmoe_v40/typed_sweep')
LOG=ROOT/'ATTEMPTS.jsonl'; SELECTOR=Path('/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv')
AUTH=Path('/data/c16/olmoe_v40_publish_v1/selector_authority/SELECTOR_AUTHORITY_REPAIR_V1.json')
VALIDATOR=REPO/'util/vm_tlb/c16/olmoe_v40/c16warp1_v40_validator.py'
OUT=Path('/data/c16/olmoe_v40_publish_v1/re_audit')

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def atomic(path,obj):
 t=path.with_name(path.name+'.tmp');t.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');os.replace(t,path)
def only(values,name):
 if len(values)!=1 or None in values or '' in values:raise ValueError('identity '+name)
 return next(iter(values))

def main():
 if OUT.exists():raise SystemExit('refusing to overwrite re-audit')
 authority=json.loads(AUTH.read_text())
 if authority.get('status')!='PASS_PROVENANCE_REPAIR' or authority.get('selector_raw_tsv_sha256')!=sha(SELECTOR):raise SystemExit('selector raw authority')
 canonical=Path(authority['canonical_selector_path'])
 if not canonical.is_file() or authority.get('selector_canonical_v1_sha256')!=sha(canonical):raise SystemExit('selector canonical authority')
 rows=list(csv.DictReader(SELECTOR.open(),delimiter='\t')); wanted={int(r['static_index']) for r in rows}
 attempts=[json.loads(x) for x in LOG.read_text().splitlines() if x]
 if len(rows)!=243 or len(wanted)!=243 or len(attempts)!=243 or {x['static_index'] for x in attempts}!=wanted:raise SystemExit('243 membership')
 OUT.mkdir(parents=True); shards=[];tools=set();replays=set();functions=set()
 for item in sorted(attempts,key=lambda x:x['static_index']):
  root=Path(item['attempt_root']); receipt=json.loads((root/'SUPERVISOR_RECEIPT.json').read_text()); result=json.loads((root/'result.json').read_text())
  validation=root/'C16WARP1_REAUDIT_VALIDATOR_RECEIPT.json'
  run=subprocess.run(['/usr/bin/python3',str(VALIDATOR),'--trace',str(root/'trace.bin'),'--stdout',str(root/'stdout.log'),'--static-index',str(item['static_index']),'--occurrence','0','--receipt',str(validation)],capture_output=True,text=True)
  verdict=json.loads(validation.read_text()) if validation.exists() else {'status':'REJECT'}
  residual=result.get('residual_process_check',{})
  clean=result.get('phase')=='CLEAN_EXIT' and result.get('timed_out') is False and residual.get('no_target_residual_process') is True
  accepted=run.returncode==0 and verdict.get('status')=='PASS' and clean and receipt.get('selected_static')==item['static_index']
  kind='EXECUTED' if accepted and verdict.get('record_count',0)>0 else 'ZERO_EXECUTION_PROVEN' if accepted else 'FAILED_EXCLUDED'
  shards.append({'static_index':item['static_index'],'attempt_root':str(root),'classification':kind,'record_count':verdict.get('record_count'),'validator_receipt':str(validation),'hits':item.get('hits',{})})
  tools.add(receipt.get('tool_sha256'));replays.add(receipt.get('canonical_replay_sha256'));functions.add(receipt.get('function_identity_sha256'))
 tool,replay,function=only(tools,'tool_sha256'),only(replays,'replay_sha256'),only(functions,'function_identity_sha256')
 if any(x['classification']=='FAILED_EXCLUDED' for x in shards):raise SystemExit('failed shard')
 if sum(x['classification']=='EXECUTED' for x in shards)+sum(x['classification']=='ZERO_EXECUTION_PROVEN' for x in shards)!=243:raise SystemExit('partition')
 (OUT/'FORMAL_243_SHARDS.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in shards))
 summary={'status':'PASS','selector_authority_receipt':str(AUTH),'selector_raw_tsv_sha256':sha(SELECTOR),'selector_canonical_v1_sha256':sha(canonical),'historical_selector_checksum':'9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33','historical_checksum_status':'OPAQUE_HISTORICAL_CHECKSUM_SERIALIZATION_NOT_DURABLY_RETAINED','total_selected':243,'executed_count':sum(x['classification']=='EXECUTED' for x in shards),'zero_count':sum(x['classification']=='ZERO_EXECUTION_PROVEN' for x in shards),'failed_excluded_count':0,'dynamic_warp_records':sum(x['record_count'] or 0 for x in shards),'tool_sha256':tool,'replay_sha256':replay,'function_identity_sha256':function,'shards_jsonl':str(OUT/'FORMAL_243_SHARDS.jsonl')}
 atomic(OUT/'FORMAL_243_SUMMARY.json',summary);print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
