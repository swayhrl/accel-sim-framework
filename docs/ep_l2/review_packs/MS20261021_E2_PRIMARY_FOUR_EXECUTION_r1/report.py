"""Evidence publication and D delivery for only the user-approved PRIMARY FOUR."""
from pathlib import Path
import sys,json,time,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
spec=importlib.util.spec_from_file_location('pub',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def checkpoint(event,pair=None,extra=()):
 coord=c.Coordinator();s=coord.snapshot();base=read(P/'BASELINE.json');plan=read(P/'PLAN.json');data=read(c.SHARED/'RUN_REGISTRY.json');usage=c.output_usage()
 assert 32<=s['actual_starts']<=36 and s['t0_unix']==base['T0'] and s['reservations']==base['reservations'] and usage['old_bytes']==base['output_usage']['old_bytes']
 assert s['scientific_holds'].keys()>=base['scientific_holds'].keys()
 for a in base['prior_attempts']:
  current=next(x for x in s['attempts'] if x['attempt_id']==a['attempt_id'])
  assert all(current.get(k)==v for k,v in a.items())
  if a['receipt_path']:assert c.digest(a['receipt_path'])==a['receipt_sha256']
 paths=[]
 for a in s['attempts'][32:]:
  assert a['run_key'] in [r['run_key'] for r in plan['profiles']]
  if a.get('receipt_path'):
   src=Path(a['receipt_path']);assert c.digest(src)==a['receipt_sha256'];dst=P/(a['attempt_id']+'_RUN_STATUS.json');dst.write_bytes(src.read_bytes());paths.append(dst)
  for name in ['NATIVE_EXECUTION_READY.json','NATIVE_EXIT.json']:
   src=Path(a['result_directory'])/name
   if src.exists():dst=P/(a['attempt_id']+'_'+name);dst.write_bytes(src.read_bytes());paths.append(dst)
 endpoints={}
 if pair:
  assert pair['status']=='CURRENT_ACCEPTED' and pair['pair_id'] in [r['pair_id'] for r in plan['profiles']]
  for side,e in pair['endpoints'].items():
   assert c.digest(e['path'])==e['sha256'];r=read(e['path']);assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS'
   assert r['summary']['instructions']==s['input_selections'][r['selection_id']]['selection']['full_input_identity']['expected_full_instructions'] and r['summary']['slices']==64
   assert runner.validate_summary(r['summary'],r['identity'])['status']=='PASS';coord.require_no_hold(s,r['qualification_id'])
   n=r.get('native_exit_evidence')
   if n:assert n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None and n['native_process']==r['process']
   else:assert e['attempt_id'] in [x['attempt_id'] for x in base['prior_attempts']] and r['exit_code']==0
   endpoints[side]=dict(receipt=e,profile=r['profile'],labels=r['labels'],source_identity=r['source_identity'],cycles=r['summary']['cycles'],instructions=r['summary']['instructions'],slices=64,qualification_id=r['qualification_id'],native_exit=r.get('native_exit_evidence',dict(basis='REUSED_CURRENT_ACCEPTED_LEGACY_ANCHOR_RECEIPT',exit_code=r['exit_code'],wait_status='NOT_REINTERPRETED_OR_RECONSTRUCTED')),result_directory=next(a['result_directory'] for a in s['attempts'] if a['attempt_id']==e['attempt_id']),mechanism_metrics=r['mechanism_metrics'])
  ap=P/(pair['pair_id']+'_ACCEPTED_PAIR.json');c.write_json(ap,dict(accepted_pair=pair,endpoints=endpoints,interpretation='Exact approved comparison. L2_DATA_FREE remains diagnostic finite residual service, hardware-throughput-ineligible. DWT F versus F_MINUS_R is a conditional joint RO/state contrast, not additive critical stall attribution.'));paths.append(ap)
 rows=[]
 for row in plan['profiles']:
  matches=[a for a in s['attempts'][32:] if a['run_key']==row['run_key']];assert len(matches)<=1
  rows.append(dict(condition=row['condition_id'],profile=row['profile'],qualification=row['qualification'],pair_id=row['pair_id'],state=matches[0]['state'] if matches else 'NOT_STARTED',attempt_id=matches[0]['attempt_id'] if matches else None,receipt_path=matches[0].get('receipt_path') if matches else None,accepted=s['accepted_pairs'].get(row['pair_id'],{}).get('status')=='CURRENT_ACCEPTED'))
 buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']};assert buckets['contingency']==8
 report=dict(schema='E2_PRIMARY_FOUR_CHECKPOINT_V1',event=event,at_unix=time.time(),source_identity=s['final_source_identity'],T0=s['t0_unix'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],maximum=40,contingency_consumed=8,budget_buckets=buckets,controller=s['controller'],rows=rows,output_usage=usage,result_growth_since32_bytes=usage['new_bytes']-base['output_usage']['new_bytes'],remaining_new_generation_bytes=6*c.GIB-usage['new_bytes'],remaining_total_generation_bytes=20*c.GIB-usage['total_bytes'],resources=c.local_resources(),active_runs={k:v for k,v in data['runs'].items() if v['status'] in c.ACTIVE},active_leases={k:v for k,v in data['resource_leases'].items() if v['status'] in c.ACTIVE},accepted_main_pairs={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED' and k.startswith('V2_MAIN_')},accepted_controls={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED' and k.startswith('V2_CONTROL_')},scientific_holds=s['scientific_holds'],user_approval=ref(P/'USER_APPROVAL.json'),matrix=s['full_system_matrix'],next_conditions=[r['condition'] for r in rows if r['state']=='NOT_STARTED'],start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE,secondary_WB64_FWT_Btree_sensitivity_authorized=False,old_failures_preserved_and_charged=True)
 ep=P/(event+'.json');c.write_json(ep,report);paths.append(ep)
 hand=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';c.write_json(hand/'RECEIPT.json',report)
 text='# Lane E2 — PRIMARY FOUR / '+event+'\n\n'+f"Original174;T0={s['t0_unix']};actual{s['actual_starts']}/40,remaining{s['remaining_start_capacity']};contingency8/8 consumed. Controller{s['controller']['state']}. main61/Core d010/Framework9dd and original runtime/client source pin unchanged. Only PRIMARY FOUR approved; no WB64/FWT/Btree/sensitivity.\n\n"
 text+='| Authorized condition | Attempt | State | Pair accepted |\n|---|---|---|---|\n'
 for r in rows:text+=f"| {r['condition']} | {r['attempt_id']} | {r['state']} | {r['accepted']} |\n"
 text+='\n| CURRENT_ACCEPTED MAIN pair | S cycles | F cycles | S/F |\n|---|---:|---:|---:|\n'
 for k,v in report['accepted_main_pairs'].items():text+=f"| {k} | {v['cycles_left']} | {v['cycles_right']} | {v['ratio_left_over_right']:.9f} |\n"
 text+='\n| CURRENT_ACCEPTED control | Anchor cycles | Control cycles | Anchor/control |\n|---|---:|---:|---:|\n'
 for k,v in report['accepted_controls'].items():text+=f"| {k} | {v['cycles_left']} | {v['cycles_right']} | {v['ratio_left_over_right']:.9f} |\n"
 text+=f"\nNew generation{usage['new_bytes']}B/6GiB;old+new{usage['total_bytes']}B/20GiB;growth since32starts{report['result_growth_since32_bytes']}B. Everyendpoint384MiB stopguard; four1.5GiB; collector/metadata planningmargin32MiB preserved in prelaunch checks. Workspace5GiB floor+2GiB monitoring,64GiB RAMfloor,Share/CPU policy unchanged. Perendpoint10800s;Oct21BJT18:00 newstarts/22:00intake cutoff.\n\n"
 text+='All old32attempts/receipts/failedexit/HOLD remain immutable and charged. Original32+8 group limits unchanged; only exact FWT F_MINUS_W→DWT F_MINUS_R andBtreeF→VectorF retry rows replaced,originalmatrix retained. ExistingVectorS reused. DATA_FREE keeps diagnostic/oracle scope and finite residual obligations, never hardwareP1 speedup. No newnative/build, no secondcontroller, no validendpointreplay or auto-retry. Next authorized unstartedconditions: '+','.join(report['next_conditions'])+'. Seven-inputGM remainsUNKNOWN.\n'
 (hand/'STATUS.md').write_text(text);paths += [hand/'STATUS.md',hand/'RECEIPT.json',*extra]
 notice=None
 if pair:
  notice=dict(schema='E2_PRIMARY_FOUR_TO_D_CURRENT_ACCEPTED_V1',at_unix=time.time(),accepted_pair=pair,endpoints=endpoints,source_identity=s['final_source_identity'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],output_usage=usage,user_approval=ref(P/'USER_APPROVAL.json'),request='Incrementally analyze these exact CURRENT_ACCEPTED receipts now. Preserve old failed attempts/labels,full epoch,known-denominator and seven-inputGMUNKNOWN. Vector only adds its actual accepted MAIN pair; DWT R0 and L2_DATA_FREE stay controls; do not equate summed request waits to critical cycles.')
  nf=P/(pair['pair_id']+'_D_DELIVERY.json');c.write_json(nf,notice);paths.append(nf)
 rb=pub.publish('docs(ep-l2-e2): '+event,paths);c.write_json(P/(event+'_REMOTE_READBACK.json'),rb)
 if notice:
  notice['remote_publication']=rb['remote_commit']
  for channel in [c.HANDOFF/'events',c.HANDOFF/'inbox',Path('/workspace/ep_l2_ms20261019_shared')]:c.write_json(channel/('E2_TO_D_'+pair['pair_id']+'.json'),notice)
  c.write_json(P/(pair['pair_id']+'_D_DELIVERY_RECEIPT.json'),dict(status='DELIVERED_AFTER_REMOTE_READBACK',remote_publication=rb['remote_commit'],at_unix=time.time(),accepted_pair_id=pair['pair_id'],channels=['original events','original inbox','old shared root']))
 print(json.dumps(dict(event=event,actual=s['actual_starts'],remaining=s['remaining_start_capacity'],rows=rows,usage=usage,remote_commit=rb['remote_commit'])),flush=True)
 return report
