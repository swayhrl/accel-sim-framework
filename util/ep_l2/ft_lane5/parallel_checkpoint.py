"""Snapshot the existing registry and V2 into the additive 50-cell progress ledger."""
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from registry import Registry,ACTIVE,PARALLEL,R19,write_json,local_resources,process_identity,attempt_count
from acceptance import load_current_authority,current_manifest
from run import digest

REPO=Path(__file__).resolve().parents[3]
H=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'


def main():
 a=argparse.ArgumentParser();a.add_argument('--out',required=True,type=Path);args=a.parse_args()
 r=Registry().snapshot();state=load_current_authority();v=current_manifest(state);path=H/'PARALLEL_CAMPAIGN_LEDGER.json';ledger=json.loads(path.read_text());accepted={x['run_key']:x for x in v['rows'] if x['scientific_acceptance']=='CURRENT_ACCEPTED'}
 new=[x for x in r['runs'].values() if x.get('experiment_id')==PARALLEL];old=[x for x in r['runs'].values() if x.get('experiment_id')==R19]
 for cell in ledger['cells']:
  own=[x for x in new if x.get('cell_id')==cell['cell_id']]
  cell.update(new_starts=sum(attempt_count(v) for v in own),actual_status='AWAITING_INDEPENDENT_QUALIFICATION',reuse_source=None)
  if own:
   cell.update(actual_status='CURRENT_ACCEPTED' if all(x['run_key'] in accepted for x in own) else own[-1]['status'],runs=own)
  elif cell['mode'] in ('B16_OFF','U_OFF'):
   mode='B16_BANKED' if cell['mode']=='B16_OFF' else 'U_WB16'
   rows=[x for x in accepted.values() if not x.get('experiment_id') and x['workload']==cell['workload_alias'] and x['mode']==mode and x['binary_sha256']=='23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee']
   if len(rows)==1:cell.update(actual_status='REUSED_CURRENT_ACCEPTED_FROZEN_2309_ANCHOR',reuse_source=rows[0],reuse_limit='Only exact frozen2309 source/config/input scope; future different-binary ideal/structure comparisons require additional same-binary OFF anchors counted under72.')
 active=[x for x in r['runs'].values() if x['status'] in ACTIVE]
 for row in active:
  if row.get('process'):
   try:assert process_identity(row['process']['pid'])==row['process']
   except (AssertionError,FileNotFoundError,ProcessLookupError):row['snapshot_warning']='Registry live row does not match currently readable PID identity; do not reclaim automatically'
 stamp=datetime.now(timezone.utc).isoformat();ledger.update(updated_at=stamp,new_starts=sum(attempt_count(v) for v in new),accepted_new=sum(x['run_key'] in accepted for x in new),reused=sum(x['reuse_source'] is not None for x in ledger['cells']),running=sum(x['status'] in ACTIVE for x in new),failed=sum(a['status'] in ('FAILED','TIMEOUT','RESOURCE_LIMIT','INCOMPLETE') for x in new for a in x.get('attempt_history',[])+[x]),remaining_start_budget=72-sum(attempt_count(v) for v in new),current_V2_generation=v['generation'],active_runs=active,active_resource_leases=[x for x in r['resource_leases'].values() if x['status'] in ACTIVE])
 write_json(path,ledger)
 receipt={'at':stamp,'resources':local_resources(),'current_scientific_pointer':json.loads((rpath:=Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json')).read_text())['scientific_acceptance'],'new_campaign':{k:ledger[k] for k in ('new_starts','accepted_new','reused','running','failed','remaining_start_budget')},'new_campaign_registration':r['campaigns'][PARALLEL],'r19':{'starts':sum(attempt_count(v) for v in old),'accepted':sum(x['run_key'] in accepted for x in old),'cap':24,'deadline_unix':1792256956,'active':[x for x in old if x['status'] in ACTIVE]},'active_runs':active,'active_leases':ledger['active_resource_leases'],'no_background_watcher_created':True}
 write_json(args.out,receipt)
 main=json.loads((H/'RECEIPT.json').read_text());main.update(status='ACTIVE_PARALLEL_CONTINUE',latest_parallel_checkpoint=receipt);write_json(H/'RECEIPT.json',main)
 (H/'STATUS.md').write_text('# Lane5 — active R19 and parallel potential execution\n\nActual '+stamp+': '+str(len(active))+' central active sims; '+str(sum(x['cpu_units'] for x in active))+' CPU / '+str(sum(x['memory_bytes'] for x in active)//2**30)+'GiB reserved, plus separately recorded small leases. R19 starts'+str(len(old))+'/24, accepted'+str(receipt['r19']['accepted'])+', original deadline17:09:16UTC unchanged. New campaign starts'+str(len(new))+'/72, accepted'+str(ledger['accepted_new'])+', exact-source anchor reuse'+str(ledger['reused'])+' logical cells; new deadline'+datetime.fromtimestamp(r['campaigns'][PARALLEL]['deadline_unix'],timezone.utc).isoformat()+'. T0 not reset.\n\nCurrent V2generation'+str(v['generation'])+'; old10 H0 accepted,12 prior R19 accepted and sixwithdrawals retained. Existing two foreground pair controllers use the single central registry/lock; no extra watcher/GateWaiter. New output physical workspace. Original48GiB workspace/40GiB Share/64GiB availableRAM guards retained. D2/L25 independently qualified, ROP40 independently qualified for frozen2309 binary. Further ready categories are reviewed while these runs execute; no OFF anchor is assumed reusable across different binaries. Raw/trace/config/frozenpacks untouched.\n')
 print(json.dumps({'active':len(active),'r19':receipt['r19']['starts'],'new':len(new),'V2':v['generation']}))
if __name__=='__main__':main()
