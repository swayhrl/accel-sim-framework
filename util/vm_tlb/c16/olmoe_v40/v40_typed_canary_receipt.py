#!/usr/bin/env python3
import json
from pathlib import Path

LOG=Path('/data/c16/olmoe_v40/typed_sweep/ATTEMPTS.jsonl')
OUT=Path('/data/c16/olmoe_v40_publish_v1/re_audit/TYPED_CANARY_RECEIPT.json')
ROLES=('EXPERT_DOWN_WEIGHT','EXPERT_DOWN_INPUT','EXPERT_DOWN_OUTPUT')
def main():
 attempts=[json.loads(x) for x in LOG.read_text().splitlines() if x]
 found={}
 for item in attempts:
  if item.get('validator_status')!='PASS':continue
  for role,count in item.get('hits',{}).items():
   if role in ROLES and count and role not in found:found[role]={'static_index':item['static_index'],'hits':count,'attempt_root':item['attempt_root']}
 if set(found)!=set(ROLES):raise SystemExit('typed role closure')
 expected={'EXPERT_DOWN_WEIGHT':101,'EXPERT_DOWN_INPUT':103,'EXPERT_DOWN_OUTPUT':1085}
 if {role:value['static_index'] for role,value in found.items()}!=expected:raise SystemExit('typed anchor identity')
 OUT.write_text(json.dumps({'status':'PASS_TYPED_CANARY_CLOSURE','anchors':found,'all_attempts_validator_pass':len(attempts)==243},indent=2,sort_keys=True)+'\n')
 print(json.dumps(found,sort_keys=True))
if __name__=='__main__':main()
