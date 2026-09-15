#!/usr/bin/env python3
"""Plan/resume driver; formal capture requires external hash-bound authorization."""
import argparse,json,fcntl
from pathlib import Path
from state import STAGES,last_valid,receipt,write_new,sha
def main():
 a=argparse.ArgumentParser();a.add_argument('--campaign',type=Path,required=True);a.add_argument('--resume',action='store_true');a.add_argument('--dry-run',action='store_true');x=a.parse_args();c=json.loads(x.campaign.read_text());root=Path(c['state_root']);root.mkdir(parents=True,exist_ok=True)
 with (root/'campaign.lock').open('w') as l:
  fcntl.flock(l,fcntl.LOCK_EX|fcntl.LOCK_NB); prior=last_valid(root) if x.resume else None;start=prior[0]+1 if prior else 0
  for s in STAGES[start:]:
   if s=='FORMAL_CAPTURE':
    auth=Path(c.get('execution_authorization',''))
    if not auth.is_file():write_new(root/'BLOCKED.json',{'schema':'C16_CAMPAIGN_BLOCKED_V1','gate':'QWEN3_EXECUTION_AUTHORIZATION','attempted_methods':['PLAN_ONLY'],'evidence':[str(x.campaign)],'unblock':'174-new hash-bound authorization'});print('BLOCKED');return
   r=receipt(c,s,'SKIPPED' if x.dry_run else 'PASS',{'campaign_sha256':sha(x.campaign)},{'mode':'DRY_RUN' if x.dry_run else 'FRAMEWORK_ONLY'},STAGES[STAGES.index(s)+1] if s!=STAGES[-1] else None,argv=[]);write_new(root/(s+'.json'),r)
  print('PASS')
if __name__=='__main__':main()
