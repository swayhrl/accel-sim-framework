from pathlib import Path
import sys,json,time,hashlib,shutil,fcntl,subprocess,importlib.util,contextlib,io,datetime
E=Path.cwd();P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1';A=P/'approved_four_r1';B=E/'docs/ep_l2/lane_collaboration_v1';sys.path.insert(0,str(E/'util/ep_l2/mechanism_e'));from coordinator import Coordinator,digest,local_resources,output_usage,process_identity,canonical
c=Coordinator();i=c.snapshot();assert i['actual_starts']>=52 and len(i['attempts'])>=52;tail=i['attempts'][51:];rows=[]
for a in tail:
 r=json.loads(json.dumps(a));D=Path(a['result_directory']);r['live_checks']={}
 for key in ['process','exit_collector_process']:
  if key in a:
   try:r['live_checks'][key]=process_identity(a[key]['pid'])==a[key]
   except (FileNotFoundError,ProcessLookupError):r['live_checks'][key]=False
 r['durable_exit_exists']=(D/'NATIVE_EXIT.json').exists();r['native_exit_not_inferred_from_process']=True;r['raw_bytes']=(D/'raw.log').stat().st_size if (D/'raw.log').exists() else 0;rows.append(r)
 dest=A/'execution';dest.mkdir(exist_ok=True)
 if a['actual_start']:
  ad=dest/a['attempt_id'];ad.mkdir(exist_ok=True)
  for name in ['input_audit.json','NATIVE_EXECUTION_REQUEST.json','NATIVE_EXECUTION_READY.json','NATIVE_EXECUTION_RELEASE.json']:
   if (D/name).exists() and not (ad/name).exists():shutil.copyfile(D/name,ad/name)
obs={'schema':'E2_APPROVED_FOUR_ACTUAL_RUNTIME_SNAPSHOT_V1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_starts':i['actual_starts'],'new_actual_starts':i['actual_starts']-51,'remaining_authorized_new_starts':4-(i['actual_starts']-51),'T0':i['t0_unix'],'controller':i['controller'],'new_tail':rows,'resources':local_resources(),'cumulative_result_generation':output_usage(),'fullGoal_complete':False,'native_exit_or_scientific_acceptance_not_inferred':True}
(dest/'LATEST_SNAPSHOT.json').write_text(json.dumps(obs,indent=2)+'\n')
for name in ['STATUS.json','RECEIPT.json']:
 p=P/name;d=json.loads(p.read_bytes());d.update(state='APPROVED_FOUR_ORIGINAL_CONTROLLER_RUNNING',status='APPROVED_FOUR_ORIGINAL_CONTROLLER_RUNNING',actual_starts=i['actual_starts'],controller=i['controller']['state'],at_utc=obs['at_utc'],current_runtime_snapshot='approved_four_r1/execution/LATEST_SNAPSHOT.json',current_scope_remaining_authorized_starts=obs['remaining_authorized_new_starts']);d['approved_successor_scope'].update(state='ACTUALLY_RUNNING_ORIGINAL_CONTROLLER',actual_new_full_app_starts=obs['new_actual_starts'],remaining_authorized_full_app_starts=obs['remaining_authorized_new_starts']);d['remaining_current_goal_authorized_app_starts']=obs['remaining_authorized_new_starts'];d['remaining_current_scope_authorized_starts']=obs['remaining_authorized_new_starts'];p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
p=B/'BOARD.md';s=p.read_text();s=s.replace('**E051 SGEMM 已完成补充科学接收并交 D；原唯一控制器 STOPPED，累计51次。**','**E051 SGEMM 已交 D；批准四端的 E052 CFD 已在原唯一中央控制器真实运行，当前累计52次、本批已启动1/4。**').replace('尚未启动或排队。','已完成逐条件新Q注册与原中央绑定；CFD运行，其他端随实际资源准入滚动。');p.write_text(s)
p=B/'NEXT_ACTIONS.json';n=json.loads(p.read_bytes());n['at_utc']=obs['at_utc'];f=n['detach_positive_RO_followup_approved_primary_four'];f.update(status='ACTUAL_ORIGINAL_CONTROLLER_RUNNING',actual_starts=i['actual_starts'],new_actual_starts=obs['new_actual_starts'],remaining_new_starts=obs['remaining_authorized_new_starts'],queued=True);p.write_text(json.dumps(n,indent=2,ensure_ascii=False)+'\n')
sys.path.insert(0,str(B));import coordination as co;client=co.Client(co.json_read(B/'CONTRACT.json'),'E2');st=client.status({'activity':'WORKING','current_task':'Approved fourr4 Fdiagnostics underoriginalcontroller: actualstarts '+str(i['actual_starts'])+', newtail '+','.join(a['attempt_id']+':'+a['state'] for a in tail)+'. Fullinput/source/Q verified beforestart; nativeexit/complete64/212/drain acceptance pending. Actualdisk allows single route now; resourceonlyrolling no countcap.','blocking_dependencies':[]},expected_sha=co.sha(client.path('status').read_bytes()))
paths=[p for p in dest.rglob('*') if p.is_file()]+[P/'STATUS.json',P/'RECEIPT.json',B/'BOARD.md',B/'NEXT_ACTIONS.json',client.path('status'),client.path('cursor'),client.path('events',event_id=st['projection']['last_emitted_event_id'])];shutil.copyfile('/tmp/e2_publish_four_runtime_snapshot.py',A/'engineering/publish_four_runtime_snapshot.py');paths.append(A/'engineering/publish_four_runtime_snapshot.py')
s=importlib.util.spec_from_file_location('pub',E/'docs/ep_l2/review_packs/MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(s);s.loader.exec_module(pub)
with open('/workspace/ep_l2_ms20261019_shared/E2_GIT_PUBLICATION.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not subprocess.check_output(['git','diff','--cached','--name-only']).strip()
 with contextlib.redirect_stdout(io.StringIO()):rr=pub.publish('ep-l2 E2: record actual approved CFD observer start52 and durable ownership',paths)
Path('/tmp/e2_four_runtime_latest_readback.json').write_text(json.dumps(rr,indent=2)+'\n');print(json.dumps({'remote_commit':rr['remote_commit'],'actual_starts':i['actual_starts'],'new_actual_starts':obs['new_actual_starts'],'tail':[(a['attempt_id'],a['state']) for a in tail]}))
