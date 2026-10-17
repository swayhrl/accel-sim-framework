"""Snapshot the one registry/current V2; count attempts, preserve source-specific anchors."""
import argparse,json,socket
from datetime import datetime,timezone
from pathlib import Path
from registry import Registry,ACTIVE,PARALLEL,R19,write_json,local_resources,process_identity,attempt_count
from acceptance import load_current_authority,current_manifest
from run import digest,tree_bytes,RESULT_ROOT,WORKSPACE_RESULT_ROOT

REPO=Path(__file__).resolve().parents[3]
H=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
 registry=Registry().snapshot();state=load_current_authority();manifest=current_manifest(state)
 ledger=json.loads((H/'PARALLEL_CAMPAIGN_LEDGER.json').read_text());accepted={v['run_key']:v for v in manifest['rows'] if v['scientific_acceptance']=='CURRENT_ACCEPTED'}
 assignment_path=H/'PARALLEL_SOURCE_ASSIGNMENT_r1.json';assignment=json.loads(assignment_path.read_text()) if assignment_path.exists() else {}
 new=[v for v in registry['runs'].values() if v.get('experiment_id')==PARALLEL];old=[v for v in registry['runs'].values() if v.get('experiment_id')==R19]
 for cell in ledger['cells']:
  own=[v for v in new if v.get('cell_id')==cell['cell_id']]
  cell.update(new_starts=sum(attempt_count(v) for v in own),actual_status='AWAITING_INDEPENDENT_QUALIFICATION',reuse_source=None,runs=own)
  cell['selected_source']=assignment.get('cells',{}).get(cell['cell_id'])
  if own:cell['actual_status']='CURRENT_ACCEPTED' if all(v['run_key'] in accepted for v in own) else own[-1]['status']
  # A historical source2309 anchor is available evidence, not completion of a new-source OFF cell.
  if cell['mode'] in ('B16_OFF','U_OFF'):
   mode='B16_BANKED' if cell['mode']=='B16_OFF' else 'U_WB16'
   rows=[v for v in accepted.values() if not v.get('experiment_id') and v['workload']==cell['workload_alias'] and v['mode']==mode and v['binary_sha256']=='23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee']
   cell['available_historical_anchors']=rows;cell['anchor_limit']='Available only for identical source/binary/config/input scope. Not a new-source matched OFF and not marked reused without a concrete matching comparison.'
  if not own and cell['condition'] in ('ROP40_H0','ICNT2_H0','WAD256_Q4'):
   matches=[v for v in manifest['launch_authorizations'] if v.get('regime')==cell['condition'] and v['status']=='CURRENT_QUALIFIED_FOR_LAUNCH']
   if matches:cell['actual_status']='CURRENT_QUALIFIED_AWAITING_RESOURCE_ADMISSION'
  if not own and cell['cell_id'] in ('I012','I013','I014'):cell['actual_status']='CURRENT_QUALIFIED_AWAITING_RESOURCE_ADMISSION'
  if not own and cell['condition']=='L1_32_H0':cell['actual_status']='PENDING_LANE1_OFFICIAL_RUNTIME_RELEASE_AND_INDEPENDENT_QUALIFICATION'
 active=[v for v in registry['runs'].values() if v['status'] in ACTIVE]
 for row in active:
  if row.get('process'):
   try:assert process_identity(row['process']['pid'])==row['process']
   except (AssertionError,FileNotFoundError,ProcessLookupError):row['snapshot_warning']='Live PID identity does not match; do not reclaim automatically'
 sizes={str(p.resolve()):tree_bytes(p) for p in (RESULT_ROOT,WORKSPACE_RESULT_ROOT)};policy=registry['hosts'][socket.gethostname()];boundary=sum(sizes.values())>=policy['max_result_bytes'];stamp=datetime.now(timezone.utc).isoformat()
 ledger.update(updated_at=stamp,new_starts=sum(attempt_count(v) for v in new),accepted_new=sum(v['run_key'] in accepted for v in new),reused=sum(v['reuse_source'] is not None for v in ledger['cells']),available_historical_anchor_cells=sum(bool(v.get('available_historical_anchors')) for v in ledger['cells']),running=sum(v['status'] in ACTIVE for v in new),failed=sum(a['status'] in ('FAILED','TIMEOUT','RESOURCE_LIMIT','INCOMPLETE') for v in new for a in v.get('attempt_history',[])+[v]),remaining_start_budget=72-sum(attempt_count(v) for v in new),current_V2_generation=manifest['generation'],active_runs=active,active_resource_leases=[v for v in registry['resource_leases'].values() if v['status'] in ACTIVE],output_tree_bytes=sizes,aggregate_output_bytes=sum(sizes.values()),max_result_bytes=policy['max_result_bytes'],new_application_admission='BLOCKED_OUTPUT_BUDGET_BOUNDARY' if boundary else 'REQUIRES_NORMAL_FULL_PREFLIGHT')
 write_json(H/'PARALLEL_CAMPAIGN_LEDGER.json',ledger)
 receipt={'at':stamp,'status':ledger['new_application_admission'],'resources':local_resources(),'current_scientific_pointer':json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())['scientific_acceptance'],'new_campaign':{k:ledger[k] for k in ['new_starts','accepted_new','reused','available_historical_anchor_cells','running','failed','remaining_start_budget','aggregate_output_bytes','max_result_bytes']},'new_campaign_registration':registry['campaigns'][PARALLEL],'r19':{'starts':sum(attempt_count(v) for v in old),'accepted':sum(v['run_key'] in accepted for v in old),'complete_unaccepted':sum(v['status']=='COMPLETE_VALID' and v['run_key'] not in accepted for v in old),'resource_stopped':sum(v['status']=='RESOURCE_LIMIT' for v in old),'cap':24,'deadline_unix':1792256956,'active':[v for v in old if v['status'] in ACTIVE]},'active_runs':active,'active_leases':ledger['active_resource_leases'],'no_background_watcher_created':True,'resume_entry':'Read this checkpoint, original deadlines and central registry; require output-budget authorization/resource recovery before any new/retry app; use same-key audited recovery, never reset attempts.'}
 write_json(args.out,receipt)
 main=json.loads((H/'RECEIPT.json').read_text());main.update(status=receipt['status'],latest_parallel_checkpoint=receipt,active_runs=active,current_V2=receipt['current_scientific_pointer']);write_json(H/'RECEIPT.json',main)
 (H/'STATUS.md').write_text('# Lane5 — rolling R19 and parallel execution\n\nSnapshot '+stamp+': '+str(len(active))+' active central sims; no extra watcher. R19 starts'+str(receipt['r19']['starts'])+'/24, accepted'+str(receipt['r19']['accepted'])+', complete but unpaired/unaccepted'+str(receipt['r19']['complete_unaccepted'])+', resource-stopped'+str(receipt['r19']['resource_stopped'])+'; original deadline2026-10-17 17:09:16UTC unchanged. New campaign attempts'+str(ledger['new_starts'])+'/72, accepted application rows'+str(ledger['accepted_new'])+', failed attempts'+str(ledger['failed'])+', remaining starts'+str(ledger['remaining_start_budget'])+'; frozen deadline'+datetime.fromtimestamp(registry['campaigns'][PARALLEL]['deadline_unix'],timezone.utc).isoformat()+'. No T0/count reset.\n\nCurrent V2 generation'+str(manifest['generation'])+' retains H0 ten accepted rows and all six old withdrawals. D2 both workloads accepted; group mean0.9979655384203753. ROP40 Convolution B290203/U291161 is accepted (negative). Local source37dc vectorAdd OFF73696/56000000 is accepted after parser-only revalidation; no simulator rerun. H0 five-workload mean1.0016002037656606 remains separate. Each accepted pair/endpoint has the existing Lane6 event; paper-side intake is not claimed.\n\nAggregate retained result bytes'+str(sum(sizes.values()))+'; effective total ceiling'+str(policy['max_result_bytes'])+'. New full applications: '+ledger['new_application_admission']+'. Prior8GiB resource-stop attempts remain immutable; current recovered attempts are listed by exact lease/PID. The12GiB amendment is authorized by20f1aab8df7c81a822b780172d8a3fa62bff3fb9; only this total output ceiling changed. Workspace48GiB/Share40GiB/availableRAM64GiB and4sim/8CPU/32GiB protections remain. No compiler/migration/deletion.\n\nWAD256 and ICNT2 are independently qualified/currently authorized for original source2309. Source37dc local ordinary profiles are qualified; future specs use frozen parser dependency wrapper. Unifiedfb source has49 independently executed affected positives plus11 native constructors and5 expected rejections, but no complete eleven-gate qualification/native OFF canary and no application authority. Pending source assignment is documented before ON outcomes; old2309 anchors are available evidence, never automatically counted as new-source matched anchors.\n')
 print(json.dumps({'status':receipt['status'],'active':len(active),'r19_starts':receipt['r19']['starts'],'new_attempts':ledger['new_starts'],'accepted_new':ledger['accepted_new'],'V2':manifest['generation']}))
if __name__=='__main__':main()
