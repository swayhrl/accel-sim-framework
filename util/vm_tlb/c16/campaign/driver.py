#!/usr/bin/env python3
"""C16 real fail-closed stage executor; no synthetic scientific PASS."""
import argparse,fcntl,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
from state import STAGES,canonical,receipt,sha
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def emit(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');os.replace(tmp,p)
def valid_chain(root,campaign):
 prev=None; out=[]
 for i,s in enumerate(STAGES):
  p=Path(root)/(f'{i:02d}_{s}.json')
  if not p.exists():break
  r=load(p)
  if r.get('status')!='PASS' or r.get('semantic_digest')!=digest(campaign.get('semantic_inputs',{})) or r.get('previous_receipt_sha256')!=prev:raise RuntimeError('STALE_OR_NONCONTIGUOUS_RECEIPT_CHAIN')
  prev=sha(p);out.append((i,p,r))
 return out
def main():
 a=argparse.ArgumentParser();a.add_argument('--campaign',type=Path,required=True);a.add_argument('--resume',action='store_true');x=a.parse_args();c=load(x.campaign);root=Path(c['state_root']);root.mkdir(parents=True,exist_ok=True)
 if c.get('mode') in {'FRAMEWORK_ONLY','PLAN_ONLY','DRY_RUN'}:raise SystemExit('FRAMEWORK_ONLY_SCIENTIFIC_PASS_FORBIDDEN')
 with (root/'campaign.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise SystemExit('CAMPAIGN_LOCK_BUSY')
  try:chain=valid_chain(root,c) if x.resume else []
  except RuntimeError as e:emit(root/'BLOCKED.json',{'gate':str(e),'status':'BLOCKED'});raise SystemExit(str(e))
  start=len(chain)
  for i,s in enumerate(STAGES[start:],start):
   h=c.get('handlers',{}).get(s)
   if not h:
    emit(root/'BLOCKED.json',{'schema':'C16_CAMPAIGN_BLOCKED_V2','status':'BLOCKED','gate':'BLOCKED_STAGE_EXECUTOR_MISSING_'+s,'attempted_methods':['registered handlers only']});print('BLOCKED');return
   attempt=root/'attempts'/f'{i:02d}_{s}_{int(time.time())}';attempt.mkdir(parents=True)
   running={'stage':s,'status':'RUNNING','semantic_digest':digest(c.get('semantic_inputs',{}))};emit(attempt/'RUNNING.json',running)
   p=subprocess.run(h,cwd=str(Path.cwd()),text=True,capture_output=True);(attempt/'stdout.log').write_text(p.stdout);(attempt/'stderr.log').write_text(p.stderr)
   if p.returncode!=0:
    emit(root/'BLOCKED.json',{'status':'BLOCKED','gate':'STAGE_COMMAND_FAILED_'+s,'argv':h,'attempt':str(attempt),'exit_code':p.returncode});print('BLOCKED');return
   artifact=attempt/'stdout.log';prev=sha(chain[-1][1]) if chain else None
   r=receipt(c,s,'PASS',{'semantic_digest':digest(c.get('semantic_inputs',{}))},{'artifact':str(artifact),'sha256':sha(artifact)},STAGES[i+1] if i+1<len(STAGES) else None,argv=h,deps=[]);r['semantic_digest']=digest(c.get('semantic_inputs',{}));r['previous_receipt_sha256']=prev;emit(root/(f'{i:02d}_{s}.json'),r);chain.append((i,root/(f'{i:02d}_{s}.json'),r))
  print('PASS')
if __name__=='__main__':main()
