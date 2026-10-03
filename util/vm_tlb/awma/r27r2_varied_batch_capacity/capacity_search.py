#!/usr/bin/env python3
"""Frozen natural-capacity search/confirmation for R27R2."""
import argparse,json,os,subprocess,time
from pathlib import Path
POLICIES=('c1','s2')
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
class Search:
 def __init__(self,a):
  if os.environ.get('R27R2_GPU_LOCK_HELD')!='1':raise RuntimeError('shared lock sentinel missing')
  self.a=a;self.root=Path(a.root);self.out=self.root/'raw/capacity_trials';self.logs=self.root/'logs/capacity_trials';self.out.mkdir(parents=True,exist_ok=True);self.logs.mkdir(parents=True,exist_ok=True);self.rows=[];self.serial=0
 def trial(self,p,b,kind,rep=0):
  self.serial+=1;stem=f'{self.serial:03d}_{kind}_{p}_B{b}_R{rep}';receipt=self.out/f'{stem}.json';log=self.logs/f'{stem}.log';cmd=[self.a.python,self.a.runner,'--mode','probe','--root',self.a.root,'--model',self.a.model,'--bank',self.a.bank,'--legacy-tokens',self.a.legacy_tokens,'--common',self.a.common,'--policy',p,'--batch',str(b),'--output',str(receipt)];start=time.time()
  try:
   with log.open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   rc=r.returncode
  except subprocess.TimeoutExpired:rc=124;dump(receipt,{'outcome':'UNKNOWN','status':'TIMEOUT','policy':p,'batch':b})
  if not receipt.exists():dump(receipt,{'outcome':'UNKNOWN','status':'MISSING_RECEIPT','policy':p,'batch':b,'exit_code':rc})
  v=json.loads(receipt.read_text());o=v.get('outcome','UNKNOWN');row={'serial':self.serial,'kind':kind,'rep':rep,'policy':p,'batch':b,'outcome':o,'exit_code':rc,'receipt':str(receipt),'log':str(log),'elapsed_seconds':time.time()-start,'oom_phase':v.get('oom_phase','')};self.rows.append(row);print(json.dumps({'capacity_trial':row},sort_keys=True),flush=True)
  if o not in ('PASS','OOM'):raise RuntimeError(f'UNKNOWN {row}')
  return o
 def search(self,p):
  a={};o=self.trial(p,64,'search');a[64]=o;low=high=None;censored=False
  if o=='PASS':
   low=64
   for b in (96,128):
    o=self.trial(p,b,'search');a[b]=o
    if o=='PASS':low=b
    else:high=b;break
   if low==128:censored=True
  else:
   high=64
   for b in (32,16,8,4,2,1):
    o=self.trial(p,b,'search');a[b]=o
    if o=='PASS':low=b;break
    high=b
   if low is None:raise RuntimeError(f'{p} B1 OOM')
  while not censored and high-low>1:
   if len(a)>=12:raise RuntimeError('distinct search ceiling')
   b=(low+high)//2;o=self.trial(p,b,'search');a[b]=o
   if o=='PASS':low=b
   else:high=b
  seen=False;mono=True
  for _,o in sorted(a.items()):
   if o=='OOM':seen=True
   elif seen:mono=False
  return {'policy':p,'largest_search_pass':low,'adjacent_oom':None if censored else high,'right_censored':censored,'attempted':a,'monotone':mono}
 def confirm(self,p,b,expect,kind):
  o=[self.trial(p,b,kind,r) for r in range(3)];return {'policy':p,'batch':b,'expected':expect,'outcomes':o,'qualified':o==[expect]*3}
 def alt(self,b,expect,kind):
  vals={p:[] for p in POLICIES}
  for r in range(3):
   for p in (POLICIES if r%2==0 else tuple(reversed(POLICIES))):vals[p].append(self.trial(p,b,kind,r))
  return [{'policy':p,'batch':b,'expected':expect[p],'outcomes':vals[p],'qualified':vals[p]==[expect[p]]*3} for p in POLICIES]
 def run(self):
  s={p:self.search(p) for p in POLICIES};c1,s2=s['c1'],s['s2'];conf=[]
  if not c1['monotone'] or not s2['monotone']:
   out={'decision':'R27R2_CAPACITY_BOUNDARY_UNSTABLE','searches':s,'confirmations':[],'all_trials':self.rows,'reason':'nonmonotone'};dump(self.root/'raw/CAPACITY_SEARCH_SUMMARY.json',out);print(json.dumps(out,indent=2));return
  if c1['largest_search_pass']==s2['largest_search_pass']:conf+=self.alt(c1['largest_search_pass'],{'c1':'PASS','s2':'PASS'},'confirm_pass')
  else:conf+=[self.confirm('c1',c1['largest_search_pass'],'PASS','confirm_pass'),self.confirm('s2',s2['largest_search_pass'],'PASS','confirm_pass')]
  if not c1['right_censored'] and not s2['right_censored'] and c1['adjacent_oom']==s2['adjacent_oom']:conf+=self.alt(c1['adjacent_oom'],{'c1':'OOM','s2':'OOM'},'confirm_oom')
  else:
   if not c1['right_censored']:conf.append(self.confirm('c1',c1['adjacent_oom'],'OOM','confirm_oom'))
   if not s2['right_censored']:conf.append(self.confirm('s2',s2['adjacent_oom'],'OOM','confirm_oom'))
  unstable=not all(x['qualified'] for x in conf);bcommon=min(c1['largest_search_pass'],s2['largest_search_pass']);w=None;reverse=False
  if not unstable and not c1['right_censored'] and c1['adjacent_oom']==c1['largest_search_pass']+1 and s2['largest_search_pass']>=c1['adjacent_oom']:w=c1['adjacent_oom']
  elif not unstable and not s2['right_censored'] and s2['adjacent_oom']==s2['largest_search_pass']+1 and c1['largest_search_pass']>=s2['adjacent_oom']:w=s2['adjacent_oom'];reverse=True
  def covered(p,b,e):return any(x['policy']==p and x['batch']==b and x['expected']==e and x['qualified'] for x in conf)
  wconf=[]
  if w is not None:
   exp={'c1':'PASS' if reverse else 'OOM','s2':'OOM' if reverse else 'PASS'}
   for p in POLICIES:
    if covered(p,w,exp[p]):wconf.append({'policy':p,'batch':w,'expected':exp[p],'qualified':True,'reused':True})
    else:x=self.confirm(p,w,exp[p],'confirm_witness');conf.append(x);wconf.append(x)
   unstable|=not all(x['qualified'] for x in wconf)
  if unstable:d='R27R2_CAPACITY_BOUNDARY_UNSTABLE'
  elif w is not None and not reverse:d='R27R2_FORWARD_WITNESS_5_STEP_SUPPORTED'
  elif w is not None:d='R27R2_S2_BATCH_CAPACITY_REGRESSION'
  elif c1['right_censored'] or s2['right_censored']:d='R27R2_CAPACITY_RIGHT_CENSORED'
  else:d='R27R2_NO_VARIED_BATCH_CAPACITY_EXTENSION'
  out={'decision':d,'searches':s,'confirmations':conf,'B_common':bcommon,'B_witness':w,'reverse':reverse,'witness_confirmations':wconf,'all_trials':self.rows,'unstable':unstable,'formal_timing':False};dump(self.root/'raw/CAPACITY_SEARCH_SUMMARY.json',out);print(json.dumps(out,indent=2,sort_keys=True))
def main():
 p=argparse.ArgumentParser()
 for n in ('root','python','runner','model','bank','legacy_tokens','common'):p.add_argument(f'--{n.replace("_","-")}',dest=n,required=True)
 Search(p.parse_args()).run()
if __name__=='__main__':main()
