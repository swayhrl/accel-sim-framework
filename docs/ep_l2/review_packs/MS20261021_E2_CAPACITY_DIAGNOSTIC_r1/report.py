"""E-owned capacity diagnostics: exact history checks, publication and immediate D handoff."""
from pathlib import Path
import contextlib,copy,hashlib,importlib.util,io,json,sys,time
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
sp=importlib.util.spec_from_file_location('pub',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(sp);sp.loader.exec_module(pub)
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def check_history(s):
 old=read(P/'BASELINE_REGISTRY.json')[c.FIELD]
 assert s['t0_unix']==old['t0_unix']==1792414193
 assert s['attempts'][:len(old['attempts'])]==old['attempts'],'Historical attempt mutation'
 assert all(s['accepted_results'][k]==v for k,v in old['accepted_results'].items()),'Historical endpoint mutation'
 assert all(s['accepted_pairs'][k]==v for k,v in old['accepted_pairs'].items()),'Historical pair mutation'
 assert s['full_system_matrix']==old['full_system_matrix'],'Original32 matrix changed'
 assert all(s['reservations'][k]==v for k,v in old['reservations'].items()),'Original bucket limits changed'
 for a in old['attempts']:
  if a.get('receipt_path'):assert c.digest(a['receipt_path'])==a['receipt_sha256'],'Historical receipt bytes changed'
 assert all(s.get('scientific_holds',{}).get(k)==v for k,v in old.get('scientific_holds',{}).items()),'Historical HOLD mutation'
 assert s['actual_starts']==sum(a.get('actual_start') is True for a in s['attempts'])
 assert 36<=s['actual_starts']<=46
 return old

def checkpoint(event,pair=None,extra=()):
 coord=c.Coordinator();s=coord.snapshot();old=check_history(s);data=read(c.SHARED/'RUN_REGISTRY.json');usage=c.output_usage();plan=read(P/'PLAN.json') if (P/'PLAN.json').exists() else None
 paths=[];endpoints={};accepted=[]
 if pair:
  assert plan and pair['pair_id'] in [r['pair_id'] for r in plan['pairs']]
  assert pair['status']=='CURRENT_ACCEPTED' and pair==s['accepted_pairs'][pair['pair_id']]
  newids={a['attempt_id'] for a in s['attempts'][len(old['attempts']):]}
  for side,e in pair['endpoints'].items():
   assert e['attempt_id'] in newids,'Old binary anchor reuse forbidden'
   assert c.digest(e['path'])==e['sha256'];r=read(e['path'])
   assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS' and r['complete_input_verified']
   assert r['summary']['instructions']==s['input_selections'][r['selection_id']]['selection']['full_input_identity']['expected_full_instructions'] and r['summary']['slices']==64
   n=r['native_exit_evidence'];assert n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None and n['native_process']==r['process']
   np=Path(e['path']).parent/'NATIVE_EXIT.json';assert c.digest(np)==r['native_exit_receipt_sha256'] and read(np)==n
   coord.require_no_hold(s,r['qualification_id']);q=s['qualifications'][r['qualification_id']];assert c.digest(q['path'])==q['sha256']
   original_spec=read(Path(e['path']).parent/'input_spec.json');assert runner.validate_terminal_summary(r['summary'],original_spec,q,r['input_audit'])==r['validation'],'Independent pair-publication terminal revalidation differs'
   assert r['source_identity']==plan['source_identity'] and r['source_identity']['binary_sha256']!='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
   endpoints[side]=dict(receipt=e,source_identity=r['source_identity'],profile=r['profile'],labels=r['labels'],cycles=r['summary']['cycles'],instructions=r['summary']['instructions'],slices=64,qualification_id=r['qualification_id'],native_exit=n,result_directory=str(Path(e['path']).parent),mechanism_metrics=r.get('mechanism_metrics',{}),capacity_diagnostic=r['summary'].get('capacity_diagnostic',{}))
  assert endpoints['left']['source_identity']==endpoints['right']['source_identity']
  ap=P/(pair['pair_id']+'_ACCEPTED_PAIR.json');c.write_json(ap,dict(accepted_pair=pair,endpoints=endpoints,analysis_scope='Separate five-input same-new-binary capacity/data-service diagnostic. Original MAIN denominator unchanged. ON never hardware P1 throughput eligible; near-unbounded requires complete covered zero refusals and highwater<=50%, otherwise large-finite/UNKNOWN. Preserve unfavorable outcomes.'));paths.append(ap)
 for a in s['attempts'][len(old['attempts']):]:
  for name in ['run_status.json','NATIVE_EXECUTION_READY.json','NATIVE_EXIT.json']:
   src=Path(a['result_directory'])/name
   if src.exists():dst=P/(a['attempt_id']+'_'+name);dst.write_bytes(src.read_bytes());paths.append(dst)
 for pid,row in s['accepted_pairs'].items():
  if pid not in old['accepted_pairs'] and row.get('status')=='CURRENT_ACCEPTED':accepted.append(row)
 rows=[]
 if plan:
  for r in plan['conditions']:
   matches=[a for a in s['attempts'][len(old['attempts']):] if a['run_key']==r['run_key']];assert len(matches)<=1,'Automatic retry forbidden'
   a=matches[0] if matches else {};rows.append(dict(condition=r['condition_id'],profile=r['profile'],pair_id=r['pair_id'],qualification_id=r['qualification_id'],state=a.get('state','NOT_STARTED'),attempt_id=a.get('attempt_id'),receipt_path=a.get('receipt_path')))
 else:
  import capacity_policy
  for r in capacity_policy.matrix()['conditions']:
   rows.append(dict(condition=r['condition_id'],profile=r['profile'],pair_id='CAPACITY_DIAGNOSTIC_'+r['workload']+'_OFF_ON_NEW_RUNTIME',qualification_id=None,state='PENDING_A2_FORMAL_PRODUCER_AND_NEW_E_QUALIFICATION',attempt_id=None,receipt_path=None))
 report=dict(schema='E2_CAPACITY_DIAGNOSTIC_CHECKPOINT_V1',event=event,at_unix=time.time(),approval=ref(P/'USER_APPROVAL.json'),authority_commit='49343880865edb22a17523790fc32dd55975966c',T0=s['t0_unix'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],maximum=s['maximum_actual_starts'],old_attempts_preserved=36,new_actual_starts=s['actual_starts']-36,new_actual_starts_limit=10,contingency_consumed=8,original_reservations=old['reservations'],controller=s['controller'],rows=rows,accepted_diagnostic_pairs=accepted,original_accepted_pairs_unchanged=True,output_usage=usage,result_growth_since36_bytes=usage['new_bytes']-read(P/'INDEPENDENT_INITIAL_ADMISSION.json')['result_usage']['new_bytes'],remaining_new_generation_bytes=s['additional_results_max_bytes']-usage['new_bytes'],remaining_total_generation_bytes=s['old_plus_new_results_max_bytes']-usage['total_bytes'],resources=c.local_resources(),active_runs=[r for r in data['runs'].values() if r['status'] in c.ACTIVE],active_leases=[r for r in data['resource_leases'].values() if r['status'] in c.ACTIVE],producer_pending=not bool(plan),central_amendment=s.get('capacity_diagnostic_amendment'),start_deadline=s['start_deadline_unix'],intake_deadline=s['result_intake_freeze'],intake_deadline_unix=s.get('intake_deadline_unix',c.INTAKE_DEADLINE),old_failed_incomplete_hold_preserved=True,no_automatic_retry_or_workload_replacement=True)
 ep=P/(event+'.json');c.write_json(ep,report);paths.append(ep)
 hand=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';c.write_json(hand/'RECEIPT.json',report)
 status=f"# Lane E2 — capacity diagnostic / {event}\n\nOriginal174; T0 {s['t0_unix']}; actual {s['actual_starts']}/{s['maximum_actual_starts']}, remaining {s['remaining_start_capacity']}; old36 immutable and charged, contingency8/8 preserved. Controller {s['controller']['state']}. New diagnostic accepted pairs {len(accepted)}/5. Original MAIN and control results unchanged.\n\n"
 status+=f"Result generation: new {usage['new_bytes']}B/{s['additional_results_max_bytes']}B; old+new {usage['total_bytes']}B/{s['old_plus_new_results_max_bytes']}B; growth since36 {report['result_growth_since36_bytes']}B. Workspace5GiB floor+2GiB monitor and Share/CPU/RAM controls unchanged. Authority4934388; no old-main61 eligibility or anchor reuse.\n\n"
 status+='| Condition | Attempt | State |\n|---|---|---|\n'
 for r in rows:status+=f"| {r['condition']} | {r['attempt_id']} | {r['state']} |\n"
 if not plan:status+='\nA2 formal producer pending; five complete-input pairs and independent new-runtime qualification are being prepared. No full application is authorized before exact new identities and gates pass.\n'
 else:status+='\nNext never-started authorized conditions: '+', '.join(r['condition'] for r in rows if r['state']=='NOT_STARTED')+'. No automatic retry.\n'
 (hand/'STATUS.md').write_text(status);(P/'STATUS.md').write_text(status);paths += [hand/'STATUS.md',hand/'RECEIPT.json',P/'STATUS.md',*extra]
 notice=None
 if pair:
  notice=dict(schema='E2_CAPACITY_DIAGNOSTIC_CURRENT_ACCEPTED_TO_D_V1',at_unix=time.time(),accepted_pair=pair,endpoints=endpoints,actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],output_usage=usage,analysis_request='Incrementally analyze exact same-new-binary OFF/ON pair now. Separate diagnostic aggregate; preserve original MAIN, unfavorable results and covered near-unbounded/large-finite/UNKNOWN distinctions. No hardware throughput claim or overlapping-wait stall sum.')
  nf=P/(pair['pair_id']+'_D_DELIVERY.json');c.write_json(nf,notice);paths.append(nf)
 with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('docs(ep-l2-e2): '+event,list(dict.fromkeys(paths)))
 c.write_json(P/(event+'_REMOTE_READBACK.json'),rb)
 if notice:
  notice['remote_publication']=rb['remote_commit'];channels=[c.HANDOFF/'events',c.HANDOFF/'inbox',Path('/workspace/ep_l2_ms20261019_shared')]
  for ch in channels:c.write_json(ch/('E2_TO_D_'+pair['pair_id']+'.json'),notice)
  c.write_json(P/(pair['pair_id']+'_D_DELIVERY_RECEIPT.json'),dict(status='DELIVERED_AFTER_REMOTE_READBACK_NOT_CONSUMPTION_CLAIM',remote_publication=rb['remote_commit'],at_unix=time.time(),pair_id=pair['pair_id'],channels=[str(x) for x in channels]))
 print(json.dumps(dict(event=event,actual=s['actual_starts'],remaining=s['remaining_start_capacity'],diagnostic_accepted=len(accepted),remote_commit=rb['remote_commit'])),flush=True)
 return report
