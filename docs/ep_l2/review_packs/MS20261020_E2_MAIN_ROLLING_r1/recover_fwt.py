"""Recover one dead E supervisor; never spawn/restart a native simulation.
Kernel zombie exit status is required, not inferred from a native log message.
All new admissions remain in the existing controller.step after terminal audit.
"""
from pathlib import Path
import os,sys,json,time,fcntl,subprocess,concurrent.futures
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
from publish_state import checkpoint
EXPECTED=('E011_618407f0','E012_63be0bb4')
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p),sha256=c.digest(p))
def proc(identity):
 try:
  raw=Path(f"/proc/{identity['pid']}/stat").read_text();f=raw[raw.rfind(')')+2:].split()
 except FileNotFoundError:return None
 assert c.process_identity(identity['pid'])==identity,'process identity changed'
 return dict(state=f[0],ppid=int(f[1]),start_ticks=int(f[19]),kernel_exit_status=int(f[49]),raw_stat=raw,observed_unix=time.time())
def owned_stop(identity,grace):
 import signal
 p=proc(identity)
 if p and p['state']!='Z':
  assert os.getpgid(identity['pid'])==identity['pid'];os.killpg(identity['pid'],signal.SIGTERM)
  until=time.time()+grace
  while time.time()<until:
   p=proc(identity)
   if p is None or p['state']=='Z':return
   time.sleep(.1)
  os.killpg(identity['pid'],signal.SIGKILL)
def finish_zombie(coord,a,result,death):
 # Pinned finish_application requires /proc disappearance. PID1 bash retains
 # zombies, so explicitly reconcile the proved exited kernel process under the
 # SAME registry lock. Original attempt/process/raw preserved; no retry/start.
 rp=Path(a['result_directory'])/'run_status.json';c.write_json(rp,result)
 with coord.locked() as (data,item):
  row=next(x for x in item['attempts'] if x['attempt_id']==a['attempt_id'])
  assert row['state']=='RUNNING' and row['process']==a['process'] and row['actual_start'] is True
  now=proc(a['process']);assert now and now['state']=='Z' and now['kernel_exit_status']==death['kernel_exit_status']
  assert result['attempt_id']==a['attempt_id'] and result['identity']==a['identity'] and c.digest(Path(a['result_directory'])/'raw.log')==result['raw_log_sha256']
  if result['status']=='COMPLETE_VALID':
   assert result['independent_acceptance']=='PASS' and result['complete_input_verified'] and result['validation']['status']=='PASS'
   coord.require_no_hold(item,result['qualification_id'])
   item['accepted_results'][a['attempt_id']]=dict(path=str(rp),sha256=c.digest(rp),run_key=a['run_key'],identity=a['identity'],qualification_id=a['qualification_id'])
  row.update(state=result['status'],finished_unix=time.time(),receipt_path=str(rp),receipt_sha256=c.digest(rp))
  live=data['runs'][a['run_key']];assert live['lease_id']==a['attempt_id'];live.update(status=result['status'],detail=result['detail'],raw_log_sha256=result['raw_log_sha256'],result_receipt_sha256=c.digest(rp),finished_unix=time.time())
  item.setdefault('orphan_terminal_reconciliation_history',[]).append(dict(attempt_id=a['attempt_id'],kernel_exit=death,receipt=ref(rp),reason='Confirmed zombie has exited; PID1 bash retains /proc. No native restart or start charge.',at_unix=time.time()))
 if result['status']=='FAILED':coord.place_scientific_hold(a['qualification_id'],a['attempt_id'],result['detail'],rp)
def monitor(coord,a):
 directory=Path(a['result_directory']);spec=read(directory/'input_spec.json');old_audit=read(directory/'input_audit.json');audit=runner.inspect(spec,coord,launch_check=False);assert audit==old_audit
 assert c.digest(directory/'accel-sim.out')==a['identity']['binary_sha256']
 for i,x in enumerate(audit['configs']):assert c.digest(directory/f'config-{i}.config')==x['sha256']
 result=dict(attempt_id=a['attempt_id'],run_key=a['run_key'],identity=a['identity'],source_identity=coord.snapshot()['final_source_identity'],qualification_id=a['qualification_id'],selection_id=a['selection_id'],profile=a['profile'],labels=a['labels'],comparison_group=a['comparison_group'],comparison_invariants_sha256=audit['comparison_invariants_sha256'],input_audit=audit,status='RUNNING',independent_acceptance='NOT_ACCEPTED',complete_input_verified=False,process=a['process'],execution_stage='NATIVE_EXECUTION',supervisor_recovery=ref(P/'FWT_SUPERVISOR_RECOVERY.json'))
 status='RUNNING';detail='';peak=0;death=None;last_heartbeat=0
 while True:
  state=proc(a['process'])
  if state is None:
   status='INCOMPLETE';detail='Original orphan disappeared before kernel exit status could be collected; no exit inference from log';break
  if state['state']=='Z':death=state;break
  peak=max(peak,runner.legacy.process_tree_rss(a['process']['pid']));resources=c.local_resources();usage=c.output_usage();disk=runner.disk_policy.stop_detail(resources,a)
  if time.time()-a['started_unix']>spec['timeout_seconds'] or time.time()>=c.INTAKE_DEADLINE:status='TIMEOUT';detail='Original wall-time budget or intake cutoff; not reset by supervisor recovery'
  elif disk or resources['share_disk_free_bytes']<40*c.GIB or resources['available_memory_bytes']<64*c.GIB or peak>spec.get('memory_bytes',8*c.GIB) or c.retained_tree_bytes(directory)>=a['maximum_result_bytes'] or usage['new_bytes']>=6*c.GIB or usage['total_bytes']>=20*c.GIB:
   status='RESOURCE_LIMIT';detail='Original owned-run resource guard after supervisor recovery';result['resource_limit']=dict(disk or {},resources=resources,output_usage=usage,native_scientific_acceptance=False,stop_scope='OWNED_PROCESS_GROUP_ONLY');c.write_json(directory/'RESOURCE_LIMIT.json',result['resource_limit'])
  if status!='RUNNING':
   owned_stop(a['process'],a.get('termination_grace_seconds',3));time.sleep(.1);death=proc(a['process']);assert death and death['state']=='Z';break
  if time.time()-last_heartbeat>30:
   c.write_json(P/(a['attempt_id']+'_RECOVERY_HEARTBEAT.json'),dict(at_unix=time.time(),process=a['process'],state=state,resources=resources,output_usage=usage,elapsed_from_original_start=time.time()-a['started_unix']));last_heartbeat=time.time()
  time.sleep(a.get('monitor_interval_seconds',.2))
 result.update(peak_process_tree_rss_bytes_after_recovery=peak,wall_seconds=time.time()-a['started_unix'])
 if death:
  result.update(kernel_exit=death,exit_code=os.waitstatus_to_exitcode(death['kernel_exit_status']),exit_code_source='Linux /proc stat field52 of exact original zombie PID/start/boot; raw snapshot retained')
 try:
  if status=='RUNNING':
   assert result['exit_code']==0,'nonzero actual kernel exit'
   result['execution_stage']='TERMINAL_VALIDATION';native=runner.runtime_metrics(directory/'raw.log',audit['effective_options'])
   with (directory/'parser.log').open('xb') as log:r=subprocess.run([sys.executable,spec['parser']['path'],'--raw',str(directory/'raw.log'),'--out',str(directory/'terminal_summary.json')],cwd=directory,stdout=log,stderr=-2,timeout=120)
   assert r.returncode==0,'independent terminal parser failed'
   summary=read(directory/'terminal_summary.json');assert summary['cycles']==native['cycle'] and summary['instructions']==native['insn']==audit['expected_full_instructions']
   validation=runner.validate_summary(summary,a['identity']);assert runner.inspect(spec,coord,launch_check=False)==audit,'post-run identity changed'
   result.update(validation=validation,summary=summary,mechanism_metrics=summary.get('mechanism_metrics',{}),complete_input_verified=True,independent_acceptance='PASS');status='COMPLETE_VALID';detail='Independent original native kernel exit0, full input instruction closure, qualified source/config/input and hardware closure; no replay'
 except Exception as error:status='FAILED';detail=f'{type(error).__name__}: {error}'
 result.update(status=status,detail=detail,raw_log_sha256=c.digest(directory/'raw.log'))
 if death:finish_zombie(coord,a,result,death)
 else:
  rp=directory/'run_status.json';c.write_json(rp,result);coord.finish_application(a['attempt_id'],status,rp)
 print(json.dumps(dict(attempt_id=a['attempt_id'],status=status,detail=detail)),flush=True)
 return result

def main():
 coord=c.Coordinator();snap=coord.snapshot();before=snap['actual_starts'];old=snap['controller'];assert old['state']=='ACTIVE' and old['process']['pid']==1665599
 assert not Path('/proc/1665599').exists(),'old supervisor is still present'
 # Acquire the original singleton lock before clearing its dead owner; no overlap.
 with (c.HANDOFF/'CONTROLLER.lock').open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  active=[a for a in snap['attempts'] if a['state']=='RUNNING'];assert tuple(a['attempt_id'] for a in active)==EXPECTED
  for a in active:assert proc(a['process'])['ppid']==1
  event=dict(schema='E2_DEAD_SUPERVISOR_RECOVERY_NO_NATIVE_RESTART_V1',at_unix=time.time(),old_controller=old,old_exec_session_exit=143,old_pid_absent=True,original_controller_lock_exclusively_acquired=True,original_live_attempts=active,recovery_process=c.process_identity(os.getpid()),resources=c.local_resources(),output_usage=c.output_usage(),actual_starts=before,remaining=snap['remaining_start_capacity'],T0=snap['t0_unix'],monitor_gap='Old supervisor exited outside native processes. Exact monitor-gap onset unavailable; no claim of continuous observation across that gap. Current physical guards checked before recovery and every0.2s afterwards.',native_restart=False,native_build=False,new_budget_charge=0,kernel_exit_requirement='Zombie wait status from exact PID/start/boot. If unavailable endpoint INCOMPLETE, never inferred PASS from process disappearance or log.')
  c.write_json(P/'FWT_SUPERVISOR_RECOVERY.json',event)
  with coord.locked() as (data,item):
   assert item['controller']==old;item.setdefault('controller_recovery_history',[]).append(event);item['controller']=dict(state='ACTIVE',process=c.process_identity(os.getpid()),recovered_from=old['process'])
  try:
   with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda a:monitor(coord,a),active))
  finally:
   with coord.locked() as (data,item):item['controller']=dict(state='STOPPED',process=c.process_identity(os.getpid()),stopped_unix=time.time())
 # Original pair-acceptance code independently requires same source/config/input.
 assert coord.snapshot()['actual_starts']==before==12
 pairid='V2_MAIN_FWT_7_21_S_F_MAIN61';accepted=all(r['status']=='COMPLETE_VALID' for r in results)
 pair=runner.accept_pair(coord,EXPECTED[0],EXPECTED[1],pairid,'MAIN_S_VS_F') if accepted else None
 audit=dict(schema='E2_FWT_INDEPENDENT_TERMINAL_AUDIT_V1',at_unix=time.time(),may_continue_original_main=accepted,pair=pair,source_identity=coord.snapshot()['final_source_identity'],expected_full_instructions=791609344,original_native_processes_preserved=True,actual_starts=12,remaining=28,contingency_remaining=0,source_binary_config_input_rehashed=True,exit0_and_native_full_input_and_all_scientific_closure_required=True,monitor_recovery=ref(P/'FWT_SUPERVISOR_RECOVERY.json'),endpoints=[dict(receipt=ref(Path(a['result_directory'])/'run_status.json'),raw=ref(Path(a['result_directory'])/'raw.log'),status=r['status'],validation=r.get('validation'),cycles=r.get('summary',{}).get('cycles'),instructions=r.get('summary',{}).get('instructions'),kernel_exit=r.get('kernel_exit')) for a,r in zip(active,results)],output_usage=c.output_usage())
 c.write_json(P/'FWT_INDEPENDENT_TERMINAL_AUDIT.json',audit)
 plan=read(P/'PLAN.json');next_conditions=plan['conditions'] if accepted else ['Review exact FWT failed/incomplete receipt before any further admission']
 checkpoint('FWT_PAIR_CURRENT_ACCEPTED' if accepted else 'FWT_EXACT_RESULT_NOT_ACCEPTED',next_conditions,[pairid] if accepted else [],[P/'FWT_SUPERVISOR_RECOVERY.json',P/'FWT_INDEPENDENT_TERMINAL_AUDIT.json',P/'PRELAUNCH_REMOTE_READBACK.json'])
 if accepted:
  import rolling_main;rolling_main.main()
if __name__=='__main__':main()
