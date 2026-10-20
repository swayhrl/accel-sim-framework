"""Publish actual rolling campaign state and D's incremental accepted-pair notice."""
from pathlib import Path
import sys,json,time,importlib.util
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;TAKE=P.parent/'MS20261020_E2_TAKEOVER_r1'
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));import coordinator as c
spec=importlib.util.spec_from_file_location('e2publish',TAKE/'publish.py');publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
def ref(p):return dict(path=str(p),sha256=c.digest(p))
def checkpoint(event,next_conditions,pair_ids=(),extra_paths=()):
 coord=c.Coordinator();s=coord.snapshot();data=json.loads((c.SHARED/'RUN_REGISTRY.json').read_text());usage=c.output_usage();baseline=json.loads((P/'CONTINUATION_BASELINE.json').read_text());buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']}
 for a in s['attempts'][:7]:
  if a.get('receipt_path'):assert c.digest(a['receipt_path'])==a['receipt_sha256']
 paired={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED'};paths=[];notices=[]
 for pairid in pair_ids:
  pair=paired[pairid]
  for endpoint in pair['endpoints'].values():assert c.digest(endpoint['path'])==endpoint['sha256'];coord.require_no_hold(s,endpoint['qualification_id'])
  f=P/(pairid+'_ACCEPTED_PAIR.json');c.write_json(f,pair);paths.append(f)
  notice=dict(schema='E2_TO_D_INCREMENTAL_ACCEPTED_PAIR_V1',at_unix=time.time(),campaign_id=c.CAMPAIGN,accepted_pair=pair,remaining_actual_starts=s['remaining_start_capacity'],actual_starts=s['actual_starts'],output_usage=usage,next_conditions=next_conditions,analysis_request='Analyze this newly accepted full pair now; do not wait for other inputs. Preserve missing/HOLD inputs and original denominator. Counters/overlapping waits are not disjoint stall cycles; no causal or numeric SASS claim beyond published scope.',source_identity=s['final_source_identity'],notification_transport='Existing central E_TO_D event/inbox contract and content-verified GitHub publication')
  nf=P/(pairid+'_D_INCREMENTAL_NOTICE.json');c.write_json(nf,notice);paths.append(nf);notices.append((pairid,notice,nf))
 retained={a['attempt_id']:c.retained_tree_bytes(Path(a['result_directory'])) for a in s['attempts']}
 failures=[]
 for a in s['attempts'][10:]:
  if a.get('receipt_path'):
   rp=Path(a['receipt_path']);assert c.digest(rp)==a['receipt_sha256'];record=json.loads(rp.read_text());f=P/(a['attempt_id']+'_RUN_STATUS.json');c.write_json(f,record);paths.append(f)
   if record['status']!='COMPLETE_VALID':
    evidence=dict(attempt_id=a['attempt_id'],state=a['state'],original_receipt=ref(rp),raw_sha256=record.get('raw_log_sha256'),detail=record.get('detail'),exit_code=record.get('exit_code'),execution_stage=record.get('execution_stage'))
    parser=Path(a['result_directory'])/'parser.log'
    if parser.exists():evidence['parser_log']=ref(parser);pf=P/(a['attempt_id']+'_PARSER.log');pf.write_bytes(parser.read_bytes());paths.append(pf)
    failures.append(evidence)
 report=dict(schema='E2_ROLLING_MAIN_RESULT_CHECKPOINT_V1',event=event,at_unix=time.time(),campaign_id=c.CAMPAIGN,source_identity=s['final_source_identity'],T0=s['t0_unix'],actual_starts=s['actual_starts'],maximum_actual_starts=40,remaining=s['remaining_start_capacity'],budget_buckets=buckets,contingency_remaining=8-buckets['contingency'],output_usage=usage,actual_new_root_growth_since_continuation=usage['new_bytes']-baseline['output_usage']['new_bytes'],retained_bytes_by_attempt=retained,controller=s['controller'],active_runs={k:v for k,v in data['runs'].items() if v['status'] in c.ACTIVE},active_leases={k:v for k,v in data['resource_leases'].items() if v['status'] in c.ACTIVE},resources=c.local_resources(),workspace_policy=coord.work_disk_policy(),accepted_pairs=paired,accepted_results=s['accepted_results'],failures=failures,scientific_holds=s['scientific_holds'],next_conditions=next_conditions,conditions_outside_ready_SF='No unsupported ablation, Btree or exploratory SGEMM launched',start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE)
 f=P/(event+'.json');c.write_json(f,report);paths.append(f);e=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';c.write_json(e/'RECEIPT.json',report)
 text='# Lane E2 — '+event+'\n\n'+f"Original174, original T0 {s['t0_unix']}. Actual starts {s['actual_starts']}/40, remaining{s['remaining_start_capacity']}, contingency{buckets['contingency']}/8. Core d010911e / Framework9dd1ee57 / main61aad385. Controller {s['controller']['state']}; default maximum2, live source/config/input/lease/RAM/CPU/disk/result guards at every launch.\n\n"
 text+='| Accepted pair | S cycles | F cycles | S/F |\n|---|---:|---:|---:|\n'
 for k,v in paired.items():text+=f"| {k} | {v['cycles_left']} | {v['cycles_right']} | {v['ratio_left_over_right']:.6f} |\n"
 text+=f"\nReal retained new results {usage['new_bytes']} B, old+new {usage['total_bytes']} B; new-root growth since this continuation {report['actual_new_root_growth_since_continuation']} B. Per-attempt retained sizes and exact raw/receipt identities in RECEIPT.\n\nNext concrete conditions: "+json.dumps(next_conditions,ensure_ascii=False)+'.\n\nOld raw/failures/withdrawals/hold history retained. Btree HOLD, SGEMM separately exploratory and not launchable; extra B/C joint fixture unqualified. No valid endpoint replay, new Goal, reset or second scheduler.\n'
 (e/'STATUS.md').write_text(text);paths += [e/'STATUS.md',e/'RECEIPT.json'];paths += list(extra_paths)
 readback=publisher.publish('docs(ep-l2-e2): '+event,paths);c.write_json(P/(event+'_REMOTE_READBACK.json'),readback)
 for pairid,notice,nf in notices:
  delivered=dict(notice,remote_publication=readback['remote_commit'],published_notice=ref(nf));c.write_json(c.HANDOFF/'events'/('E2_TO_D_INCREMENTAL_'+pairid+'.json'),delivered);c.write_json(c.HANDOFF/'inbox'/('E2_TO_D_INCREMENTAL_'+pairid+'.json'),delivered)
 print(json.dumps(dict(event=event,actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],output_usage=usage,accepted_pair_ids=list(paired),remote_commit=readback['remote_commit'])),flush=True)
 return report
if __name__=='__main__':checkpoint(sys.argv[1],json.loads(sys.argv[2]),sys.argv[3:])
