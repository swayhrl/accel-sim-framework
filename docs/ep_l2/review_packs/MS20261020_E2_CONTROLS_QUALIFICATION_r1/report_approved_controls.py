"""Publication adapter for approved controls; original execution/acceptance code remains authoritative."""
from pathlib import Path
import sys,json,time,copy,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner,controller
spec=__import__('importlib.util',fromlist=['']).spec_from_file_location('pub',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py')
pub=__import__('importlib.util',fromlist=['']).module_from_spec(spec);spec.loader.exec_module(pub)
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def checkpoint(event,pair=None,extra=()):
 coord=c.Coordinator();s=coord.snapshot();data=read(c.SHARED/'RUN_REGISTRY.json');usage=c.output_usage();base=read(P/'BASELINE.json')
 buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']}
 assert buckets['contingency']==8 and s['t0_unix']==base['T0'] and usage['old_bytes']==base['output_usage']['old_bytes']
 paths=[];metrics={}
 for a in s['attempts'][20:]:
  if not a.get('receipt_path'):continue
  rp=Path(a['receipt_path']);assert c.digest(rp)==a['receipt_sha256'];r=read(rp);f=P/(a['attempt_id']+'_RUN_STATUS.json');f.write_bytes(rp.read_bytes());paths.append(f)
  for name in ['NATIVE_EXECUTION_READY.json','NATIVE_EXIT.json']:
   original=Path(a['result_directory'])/name
   if original.exists():
    if name=='NATIVE_EXIT.json':assert c.digest(original)==r['native_exit_receipt_sha256']
    f=P/(a['attempt_id']+'_'+name);f.write_bytes(original.read_bytes());paths.append(f)
 if pair:
  assert pair['status']=='CURRENT_ACCEPTED'
  for side,e in pair['endpoints'].items():
   assert c.digest(e['path'])==e['sha256'];r=read(e['path']);assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS'
   assert r['summary']['instructions']==s['input_selections'][r['selection_id']]['selection']['full_input_identity']['expected_full_instructions'] and r['summary']['slices']==64 and runner.validate_summary(r['summary'],r['identity'])['status']=='PASS'
   coord.require_no_hold(s,r['qualification_id'])
   if e['attempt_id'] in [a['attempt_id'] for a in s['attempts'][20:]]:
    n=r['native_exit_evidence'];assert n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None and n['native_process']==r['process']
   metrics[side]=dict(profile=r['profile'],labels=r['labels'],cycles=r['summary']['cycles'],instructions=r['summary']['instructions'],result_directory=next(a['result_directory'] for a in s['attempts'] if a['attempt_id']==e['attempt_id']),receipt=e,mechanism_metrics=r['mechanism_metrics'])
  f=P/(pair['pair_id']+'_ACCEPTED_CONTROL.json');c.write_json(f,dict(accepted_control=pair,endpoints=metrics,interpretation='Fixed predeclared control, not a new MAIN S/F pair. S_COPY_FREE is a diagnostic copy-service counterfactual, not hardware P1 throughput or full-scheme speedup. Other ablations retain physical P1.'));paths.append(f)
 report=dict(schema='E2_APPROVED_CONTROL_CHECKPOINT_V1',event=event,at_unix=time.time(),source_identity=s['final_source_identity'],T0=s['t0_unix'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],maximum=40,budget_buckets=buckets,contingency_remaining=0,output_usage=usage,result_growth_since_control_baseline_bytes=usage['new_bytes']-base['output_usage']['new_bytes'],resources=c.local_resources(),controller=s['controller'],active_runs={k:v for k,v in data['runs'].items() if v['status'] in c.ACTIVE},active_leases={k:v for k,v in data['resource_leases'].items() if v['status'] in c.ACTIVE},accepted_main_pairs={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED' and k.startswith('V2_MAIN_')},accepted_controls={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED' and k.startswith('V2_CONTROL_')},scientific_holds=s['scientific_holds'],next_original_controls=[r['profile'] for r in read(P/'ADMISSION_PLAN.json')['profiles'] if r['control_pair_id'] not in s['accepted_pairs']],next_approved_controls=[r['condition_id'] for r in read(P/'APPROVED_CONTROLS/PREPARATION_PLAN.json')['profiles'] if r['control_pair_id'] not in s['accepted_pairs']],DWT_CFD_reallocation=read(P/'APPROVED_CONTROLS/MATRIX_ADOPTION_RECEIPT.json'),FWT_Vector_Btree_retries=False,start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE)
 report['next_approved_controls']=[row['condition_id'] for row in read(P/'APPROVED_CONTROLS/PREPARATION_PLAN.json')['profiles'] if not any(a['run_key']==c.run_key(read(row['spec']['path'])['identity']) for a in s['attempts'])]
 report['unsuccessful_approved_attempts']=[dict(attempt_id=a['attempt_id'],profile=a['profile'],workload=a['identity']['workload'],state=a['state'],receipt_path=a.get('receipt_path'),receipt_sha256=a.get('receipt_sha256')) for a in s['attempts'][26:] if a['state'] not in c.ACTIVE and a['state']!='COMPLETE_VALID']
 report['DWT_replay_authorized']=False
 f=P/(event+'.json');c.write_json(f,report);paths.append(f)
 hand=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';c.write_json(hand/'RECEIPT.json',report)
 text='# Lane E2 — '+event+'\n\n'+f"Original174; originalT0={s['t0_unix']}; actual{s['actual_starts']}/40,remaining{s['remaining_start_capacity']},contingency8/8 consumed. main61/Core d010/Framework9dd unchanged. Controller {s['controller']['state']}; original unique registry/lock and maximum2.\n\n"
 text+='| Main S/F | S cycles | F cycles | S/F |\n|---|---:|---:|---:|\n'
 for k,v in report['accepted_main_pairs'].items():text+=f"| {k} | {v['cycles_left']} | {v['cycles_right']} | {v['ratio_left_over_right']:.9f} |\n"
 text+='\n| Independently accepted control | Anchor cycles | Control cycles | Anchor/control |\n|---|---:|---:|---:|\n'
 for k,v in report['accepted_controls'].items():text+=f"| {k} | {v['cycles_left']} | {v['cycles_right']} | {v['ratio_left_over_right']:.9f} |\n"
 text+=f"\nNew results{usage['new_bytes']}B, old+new{usage['total_bytes']}B; growth since20-start control baseline{report['result_growth_since_control_baseline_bytes']}B.6/20GiB and5GiB+2GiB monitoring reserves unchanged.\n\nRemaining original qualified controls: "+','.join(report['next_original_controls'])+'. DWT/CFD four-cell revision is user-approved and independently qualified; exact matrix adoption retained with original history. Remaining approved controls: '+','.join(report['next_approved_controls'])+'. FWT INCOMPLETE,Vector F RESOURCE_LIMIT/exit-15,Btree HOLD and all old receipts remain; no refunds,replay,newGoal,second controller or new migration. COPY_FREE remains diagnostic.\n'
 if report['unsuccessful_approved_attempts']:text+='\nAttempted unsuccessful approved conditions remain charged and are excluded from the unstarted queue: '+','.join(x['attempt_id']+':'+x['state'] for x in report['unsuccessful_approved_attempts'])+'. DWT replay is NOT authorized. A resource block is not a production correctness PASS or failure. Resume only never-started CFD conditions after a new real resource event and fresh original gates; no background watcher.\n'
 (hand/'STATUS.md').write_text(text);paths += [hand/'STATUS.md',hand/'RECEIPT.json',*extra]
 notice=None
 if pair:
  notice=dict(schema='E2_TO_D_INCREMENTAL_INDEPENDENT_CONTROL_V1',at_unix=time.time(),accepted_control=pair,endpoints=metrics,source_identity=s['final_source_identity'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],output_usage=usage,analysis_request='Analyze this exact predeclared independent control now. Preserve four MAIN S/F pairs,all labels and denominator; do not pool diagnostics into hardware results or sum overlapping request waits as GPU stall cycles.')
  nf=P/(pair['pair_id']+'_D_INCREMENTAL_NOTICE.json');c.write_json(nf,notice);paths.append(nf)
 rb=pub.publish('docs(ep-l2-e2): '+event,paths);c.write_json(P/(event+'_REMOTE_READBACK.json'),rb)
 if notice:
  notice['remote_publication']=rb['remote_commit']
  for channel in ['events','inbox']:c.write_json(c.HANDOFF/channel/('E2_TO_D_'+pair['pair_id']+'.json'),notice)
 print(json.dumps(dict(event=event,actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],accepted_controls=list(report['accepted_controls']),output_usage=usage,remote_commit=rb['remote_commit'])),flush=True)
 return report
