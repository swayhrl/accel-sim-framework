"""Independent publication and incremental D delivery for the approved main61 batch.

Only called by the ORIGINAL foreground controller at real terminal boundaries.
No simulation, polling, acceptance mutation, or remote-lane ACK is performed.
"""
from pathlib import Path
import contextlib,fcntl,importlib.util,io,json,sys,time
E=Path(__file__).resolve().parent;P=E.parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner,workload_policy as policy

def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v);return v

def collect(event,plan,pair=None):
 coord=c.Coordinator();s=coord.snapshot();assert policy.active(s)
 paths=[];endpoints={}
 if pair:
  assert pair['pair_id'] in {r['pair_id'] for r in plan['pairs']}
  assert pair['status']=='CURRENT_ACCEPTED' and pair==s['accepted_pairs'][pair['pair_id']]
  for side,endpoint in pair['endpoints'].items():
   assert c.digest(endpoint['path'])==endpoint['sha256'];r=read(endpoint['path']);directory=Path(endpoint['path']).parent
   assert r['attempt_id'] in {a['attempt_id'] for a in s['attempts'][46:]}
   assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS' and r['complete_input_verified']
   assert r['source_identity']==plan['source_identity'] and r['source_identity']['binary_sha256']==policy.MAIN61
   selection=s['input_selections'][r['selection_id']]['selection']['full_input_identity']
   assert r['summary']['instructions']==selection['expected_full_instructions'] and r['summary']['slices']==64
   n=r['native_exit_evidence'];assert n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None and n['native_process']==r['process']
   assert c.digest(directory/'NATIVE_EXIT.json')==r['native_exit_receipt_sha256'] and read(directory/'NATIVE_EXIT.json')==n
   coord.require_no_hold(s,r['qualification_id']);q=s['qualifications'][r['qualification_id']]
   assert c.digest(q['path'])==q['sha256']
   assert runner.validate_terminal_summary(r['summary'],read(directory/'input_spec.json'),q,r['input_audit'])==r['validation']
   endpoints[side]=dict(receipt=endpoint,source_identity=r['source_identity'],profile=r['profile'],labels=r['labels'],
    cycles=r['summary']['cycles'],instructions=r['summary']['instructions'],slices=64,qualification_id=r['qualification_id'],
    native_exit=n,result_directory=str(directory),mechanism_metrics=r.get('mechanism_metrics',{}),
    kernel_completion=r['summary'].get('kernel_completion'),raw=ref(directory/'raw.log'),terminal_summary=ref(directory/'terminal_summary.json'))
  assert endpoints['left']['source_identity']==endpoints['right']['source_identity']
  ap=E/(pair['pair_id']+'_ACCEPTED_PAIR.json');c.write_json(ap,dict(accepted_pair=pair,endpoints=endpoints,
   analysis_scope='FWT restores original finite main61 cohort; SGEMM is a separate preregistered exploratory control. Neither enters the new93a9 capacity cohort. Retain negatives and zero-admission/UNKNOWN distinctions.'))
  paths.append(ap)
 rows=[]
 for row in plan['conditions']:
  attempts=[a for a in s['attempts'][46:] if a.get('condition_id')==row['condition_id']];assert len(attempts)<=1
  a=attempts[0] if attempts else {};rows.append(dict(condition_id=row['condition_id'],qualification_id=row['qualification_id'],
    attempt_id=a.get('attempt_id'),state=a.get('state','NOT_STARTED'),receipt_path=a.get('receipt_path')))
  if a:
   for name in ['run_status.json','NATIVE_EXECUTION_READY.json','NATIVE_EXIT.json']:
    src=Path(a['result_directory'])/name
    if src.exists():dst=E/(a['attempt_id']+'_'+name);dst.write_bytes(src.read_bytes());paths.append(dst)
 usage=c.output_usage();data=read(c.SHARED/'RUN_REGISTRY.json')
 report=dict(schema='E2_APPROVED_MAIN61_WORKLOAD_CHECKPOINT_V1',event=event,at_unix=time.time(),T0=s['t0_unix'],
  actual_starts=s['actual_starts'],historical_starts_preserved=46,new_batch_actual_starts=s['actual_starts']-46,
  exact_new_starts_maximum=4,remaining_start_capacity=s['remaining_start_capacity'],contingency_consumed=8,
  original_reservations=s['reservations'],controller=s['controller'],rows=rows,source_identity=plan['source_identity'],
  accepted_pairs=[s['accepted_pairs'][r['pair_id']] for r in plan['pairs'] if r['pair_id'] in s['accepted_pairs']],
  output_usage=usage,remaining_new_generation_bytes=s['additional_results_max_bytes']-usage['new_bytes'],
  remaining_total_generation_bytes=s['old_plus_new_results_max_bytes']-usage['total_bytes'],resources=c.local_resources(),
  active_E_runs=[r for r in data['runs'].values() if r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN],
  active_E_leases=[r for r in data['resource_leases'].values() if r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN],
  no_automatic_retry_or_extra_scope=True,old_results_and_HOLD_preserved=True)
 rp=E/(event+'.json');c.write_json(rp,report);paths.append(rp)
 c.write_json(P/'RECEIPT.json',report);paths.append(P/'RECEIPT.json')
 status='# Lane E2 — approved main61 workload pipeline\n\n'
 status+=f"Event {event}; original T0 {s['t0_unix']}; actual {s['actual_starts']}; this batch {s['actual_starts']-46}/4; old46 retained. Original controller {s['controller']['state']}.\n\n"
 status+=f"Generated new {usage['new_bytes']}B / {s['additional_results_max_bytes']}B; total {usage['total_bytes']}B / {s['old_plus_new_results_max_bytes']}B. No migration reset.\n\n"
 status+='| Condition | Attempt | State |\n|---|---|---|\n'+''.join(f"|{r['condition_id']}|{r['attempt_id']}|{r['state']}|\n" for r in rows)
 (P/'STATUS.md').write_text(status);paths.append(P/'STATUS.md')
 hand=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e'
 c.write_json(hand/'RECEIPT.json',report);(hand/'STATUS.md').write_text(status);paths += [hand/'RECEIPT.json',hand/'STATUS.md']
 if pair:
  notice=dict(schema='E2_MAIN61_CURRENT_ACCEPTED_TO_D_V1',at_unix=time.time(),accepted_pair=pair,endpoints=endpoints,
    actual_starts=s['actual_starts'],output_usage=usage,analysis_request='Incrementally consume this exact main61 pair; FWT original-cohort restoration or SGEMM separate exploration, never capacity cohort. Retain negative/UNKNOWN results; no new experiment authorization.')
  path=E/(pair['pair_id']+'_D_DELIVERY.json');c.write_json(path,notice);paths.append(path)
 return report,paths

def _checkpoint_locked(event,plan,pair=None,extra=()):
 report,paths=collect(event,plan,pair)
 pub=load('e2_exact_publisher',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py')
 with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('docs(ep-l2-e2): '+event,list(dict.fromkeys(paths+list(extra))))
 c.write_json(E/(event+'_REMOTE_READBACK.json'),rb)
 if pair:
  notice=read(E/(pair['pair_id']+'_D_DELIVERY.json'));notice['remote_publication']=rb['remote_commit']
  channels=[c.HANDOFF/'events',c.HANDOFF/'inbox',Path('/workspace/ep_l2_ms20261019_shared')]
  for ch in channels:c.write_json(ch/('E2_TO_D_'+pair['pair_id']+'.json'),notice)
  receipt=E/(pair['pair_id']+'_D_DELIVERY_RECEIPT.json');c.write_json(receipt,dict(status='DELIVERED_AFTER_REMOTE_READBACK_NOT_CONSUMPTION_CLAIM',
   pair_id=pair['pair_id'],remote_publication=rb['remote_commit'],at_unix=time.time(),channels=[str(x) for x in channels]))
  # Publish a real immutable collaboration event, then its own receipt; no peer ACK.
  coop=load('e2_exact_collaboration',ROOT/'docs/ep_l2/lane_collaboration_v1/coordination.py')
  client=coop.Client(coop.json_read(ROOT/'docs/ep_l2/lane_collaboration_v1/CONTRACT.json',65536),'E2',str(ROOT))
  ap=E/(pair['pair_id']+'_ACCEPTED_PAIR.json');reference=dict(repo='swayhrl/accel-sim-framework',commit=rb['remote_commit'],path=ap.relative_to(ROOT).as_posix(),sha256=c.digest(ap),role='CURRENT_ACCEPTED exact main61 pair')
  emitted=client.emit('DELIVERY',['D'],pair['pair_id']+' CURRENT_ACCEPTED',dict(task_id='D-WORKLOAD-INCREMENTAL-'+pair['pair_id'],dependency_met=True,request=notice['analysis_request']),[reference],
   'E2:CURRENT_ACCEPTED:'+pair['pair_id'])
  ep=ROOT/'docs/ep_l2/lane_collaboration_v1/events/E2'/(emitted['event']['event_id']+'.json')
  with contextlib.redirect_stdout(io.StringIO()):delivery_rb=pub.publish('docs(ep-l2-e2): deliver '+pair['pair_id']+' to D',[receipt,ep])
  c.write_json(E/(pair['pair_id']+'_D_DELIVERY_REMOTE_READBACK.json'),delivery_rb)
 print(json.dumps(dict(event=event,actual_starts=report['actual_starts'],accepted_pairs=len(report['accepted_pairs']),remote_commit=rb['remote_commit'])),flush=True)
 return report


def checkpoint(event,plan,pair=None,extra=()):
 # Cross-process Git/metadata publication serialization only; no simulation
 # control or scientific authority, and never a second controller.
 lock_path=Path('/workspace/ep_l2_ms20261019_shared/E2_GIT_PUBLICATION.lock')
 with lock_path.open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  return _checkpoint_locked(event,plan,pair,extra)
