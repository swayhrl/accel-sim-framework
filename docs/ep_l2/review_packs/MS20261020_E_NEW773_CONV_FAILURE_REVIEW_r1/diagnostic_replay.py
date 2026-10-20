"""One explicitly authorized samebinary full-input forensic replay, original40 charged.

Normal application qualification gates remain unchanged. This named control
can only capture a failed exact773 execution, never accept a performance point.
Uses original singleton, central reservation/start journal and owned guards.
"""
import sys
from pathlib import Path
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import json,os,time,subprocess,ctypes,shutil,uuid,signal,resource
import coordinator as c
import run as legacy
from runner import disable_owned_core_dumps

PACK=Path(__file__).resolve().parent
CHECKPOINT=PACK/'DIAGNOSTIC_CHECKPOINT.json'
CONTROL_ID='E006_MAIN773_CONV_F_ABORT_FORENSIC_20261020_V1'


def reserve(coord,s,path):
 c.require(time.time()<c.START_DEADLINE,'originalstartcutoff')
 with coord.locked() as (data,item):
  c.counts(item);binding=item['forensic_controls'][CONTROL_ID]
  c.require(binding['checkpoint_path']==str(path.resolve()) and binding['checkpoint_sha256']==c.digest(path),'checkpoint binding changed')
  c.require(s['source_identity']==item['final_source_identity'] and s['campaign_id']==c.CAMPAIGN and s['prepared_by']=='E','wrongsource/campaign')
  c.require(s['source_identity']['binary_sha256']=='773271ac70f009dddcd4c522f66dcd37967e4f57ce1e5082d3fc5aea61f2f9f5','onlyfrozenfailedproducer')
  c.require(s['scientific_performance_endpoint'] is False and s['purpose']=='READ_ONLY_ABORT_STATE_NO_ACCEPTANCE','forensic-only, no scientificbypass')
  failed=next(a for a in item['attempts'] if a['attempt_id']==s['original_attempt_id'])
  c.require(failed['state']=='FAILED' and failed['actual_start'] and failed['profile']=='F' and failed['identity']==s['original_identity'],'exactoriginalfailedF only')
  c.require(not binding.get('attempt'),'one forensicreplay alreadyreserved; preserve/reconcile it')
  c.require(item['uncertain_start_intents']==0 and item['remaining_start_capacity']>0,'original40/unknownstart boundary')
  used=sum(c.policy_v2.charged_bucket(a,item['reservations'])=='contingency' and (a.get('actual_start') or a['state'] in ('RESERVED','START_INTENT_UNRECONCILED')) for a in item['attempts'])
  c.require(used<item['reservations']['contingency'],'originalcontingency8 exhausted')
  key=c.run_key(s['identity']);c.require(key==s['run_key'] and key not in data['runs'],'duplicate/wrongforensic runkey')
  c.require(s['maximum_result_bytes']==384*2**20 and s['memory_bytes']==8*c.GIB and s['CPU']==2,'fixed boundedforensicreserve')
  c.resource_gate(data,'simulation',2,s['memory_bytes'],s['maximum_result_bytes'],c.local_resources(),c.output_usage())
  aid=f'E{len(item["attempts"])+1:03d}_{uuid.uuid4().hex[:8]}'
  row=dict(attempt_id=aid,run_key=key,identity=s['identity'],selection_id='D_V1_convolutionSeparable',qualification_id='FORENSIC_ONLY_NO_SCIENTIFIC_QUALIFICATION_'+binding['checkpoint_sha256'],profile='F_ABORT_FORENSIC_REPLAY',comparison_group='DIAGNOSTIC_NOT_PERFORMANCE',budget_bucket='contingency',labels=dict(diagnostic=True,subset=None,oracle=True),state='RESERVED',actual_start=False,reserved_unix=time.time(),result_directory=str(c.OUTPUT/aid),maximum_result_bytes=s['maximum_result_bytes'],original_failed_attempt=s['original_attempt_id'],scientific_performance_endpoint=False,**c.disk_policy.lease_policy(item))
  item['attempts'].append(row);binding['attempt']=aid
  data['runs'][key]=dict(run_key=key,identity=s['identity'],owner='mechanism_E',host=item['host'],boot_id=item['boot_id'],lease_id=aid,status='RESERVED',cpu_units=2,memory_bytes=s['memory_bytes'],scan=False,result_directory=row['result_directory'],disk_growth_bytes=s['maximum_result_bytes'],experiment_id=c.CAMPAIGN,process=None,scientific_performance_endpoint=False,**c.disk_policy.lease_policy(item))
  return row


def preflight(s):
 c.tooling_binding();client=json.loads((c.HANDOFF/'CLIENT_CONTRACT.json').read_text());b=client['forensic_controls'][CONTROL_ID]
 c.require(b['entry']==str(Path(__file__).resolve()) and b['entry_sha256']==c.digest(__file__) and b['checkpoint_sha256']==c.digest(CHECKPOINT),'exactpublishedforensicentry')
 for name,h in b['published_files'].items():
  import hashlib
  c.require(c.digest(PACK/name)==h and hashlib.sha256(subprocess.check_output(['git','show',b['publication_commit']+':'+b['git_directory']+'/'+name],cwd=client['execution_worktree'])).hexdigest()==h,'publishedforensicfilechanged')
 for asset in s['immutable_assets']:c.require(c.digest(asset['path'])==asset['sha256'],'immutableoriginalevidence changed')
 c.require(s['original_status']['exit_code']==-6 and s['original_status']['source_identity']==s['source_identity'],'actualoriginalabort required')
 c.require(s['source_identity']['binary_sha256']==c.digest(s['binary']),'frozenbinarychanged')
 c.require(legacy.asset_manifest(s['trace_files'])==s['trace_manifest'],'completeoriginaltracechanged')
 c.require(s['identity']['trace_content_sha256']==s['original_identity']['trace_content_sha256'] and s['identity']['runtime_config_sha256']==s['original_identity']['runtime_config_sha256'],'fullinput/config identitychanged')
 c.require(s['host_attach_control']['status']=='PASS' and c.digest(s['host_attach_control']['path'])==s['host_attach_control']['sha256'],'actualownedGDBhostcontrol required')
 return b


def execute():
 def interrupted(signum,frame):raise KeyboardInterrupt('owned forensiccontroller interrupted')
 signal.signal(signal.SIGTERM,interrupted)
 s=json.loads(CHECKPOINT.read_text());preflight(s);disable_owned_core_dumps();coord=c.Coordinator();proc=None;debug=None
 with coord.unique_controller():
  a=reserve(coord,s,CHECKPOINT);out=Path(a['result_directory']);out.mkdir(exist_ok=False);(out/'tmp').mkdir();(out/'cache').mkdir()
  c.write_json(out/'input_checkpoint.json',s);start=time.monotonic();status='FAILED';detail='Forensiclaunchincomplete';peak=0
  r=dict(attempt_id=a['attempt_id'],run_key=a['run_key'],identity=s['identity'],source_identity=s['source_identity'],original_failed_attempt=s['original_attempt_id'],scientific_performance_endpoint=False,independent_acceptance='NOT_A_PERFORMANCE_RESULT',profile=a['profile'],purpose=s['purpose'])
  try:
   shutil.copy2(s['binary'],out/'accel-sim.out');cmd=[str(out/'accel-sim.out')]
   for i,asset in enumerate(s['config_assets']):
    dst=out/f'config-{i}.config';shutil.copyfile(asset['path'],dst);c.require(c.digest(dst)==asset['sha256'],'configsnapshotchanged');cmd+=['-config',str(dst)]
   cmd+=['-trace',s['trace_entry']]
   env=dict(os.environ,**s['environment'],TMPDIR=str(out/'tmp'),TMP=str(out/'tmp'),TEMP=str(out/'tmp'),XDG_CACHE_HOME=str(out/'cache'))
   dbg_env={k:v for k,v in env.items() if k not in ['PYTHONHOME','PYTHONPATH']}
   with (out/'gdb.log').open('xb') as gdblog,(out/'raw.log').open('xb') as raw:
    debug=subprocess.Popen(['/usr/bin/gdb','-q','-nx','-batch','-x',str(PACK/'capture_abort.gdb')],stdout=gdblog,stderr=subprocess.STDOUT,cwd=out,env=dbg_env,start_new_session=True)
    debugid=c.process_identity(debug.pid);r['debugger_process']=debugid
    with coord.locked() as (data,item):
     data['runs'][a['run_key']]['debugger_process']=debugid
     next(x for x in item['attempts'] if x['attempt_id']==a['attempt_id'])['debugger_process']=debugid
    libc=ctypes.CDLL(None,use_errno=True);debug_pid=debug.pid
    def allow_own_debugger():
     if libc.prctl(0x59616d61,ctypes.c_ulong(debug_pid),0,0,0)!=0:raise OSError(ctypes.get_errno(),'owned PR_SET_PTRACER failed')
    def native_popen(command,**kw):return subprocess.Popen(command,preexec_fn=allow_own_debugger,**kw)
    proc=coord.start_application(a['attempt_id'],cmd,out,env,raw,native_popen);c.require(proc is not None,'nativeOSspawnfailed')
    identity=c.process_identity(proc.pid);r.update(process=identity,command=cmd,host_debug_scope='PR_SET_PTRACER allows onlyexactownedGDBpid; no globalsysctl change/no simulatedoptionchange')
    c.write_json(out/'NATIVE_STARTED.json',dict(process=identity,attempt_id=a['attempt_id'],binary_sha256=s['source_identity']['binary_sha256']))
    while proc.poll() is None:
     live=c.local_resources();usage=c.output_usage();peak=max(peak,legacy.process_tree_rss(proc.pid)+legacy.process_tree_rss(debug.pid))
     incident=c.disk_policy.stop_detail(live,a)
     if (incident or live['share_disk_free_bytes']<40*c.GIB or live['available_memory_bytes']<64*c.GIB or peak>s['memory_bytes'] or c.retained_tree_bytes(out)>=s['maximum_result_bytes'] or usage['new_bytes']>=6*c.GIB or usage['total_bytes']>=20*c.GIB):
      status='RESOURCE_LIMIT';detail='ownforensicresourceguard';r['resource_limit']=dict(incident or {},resources=live,output_usage=usage,attempt_id=a['attempt_id'],process=identity);c.write_json(out/'RESOURCE_LIMIT.json',r['resource_limit']);break
     if time.monotonic()-start>s['timeout_seconds'] or time.time()>=c.INTAKE_DEADLINE:status='TIMEOUT';detail='boundedforensiccutoff';break
     if debug.poll() is not None:
      # A debuggerstartup/capturefailure cannotleave an unmonitoredtarget.
      if proc.poll() is None:detail='debugger ended beforetarget';break
     time.sleep(a['monitor_interval_seconds'])
    if status not in ['RESOURCE_LIMIT','TIMEOUT']:
     if (out/'ABORT_STATE.json').exists():
      state=json.loads((out/'ABORT_STATE.json').read_text());c.require(state['inferior_pid']==proc.pid and state['start_ticks']==identity['start_ticks'] and state['boot_id']==identity['boot_id'],'capturedwronginferior')
      c.require(state['captured_sigabrt'] is True,'no actualSIGABRT captured')
      r['observed_abort']=state;detail='Actualsame773fullinputSIGABRTcaptured; GDBthenkillsownfailedinferior. Noperformance orcorrectnessPASS.'
     else:detail='Forensiccapturefailed; actualstartremainscharged; rawkept'
  except BaseException as error:detail=repr(error)
  finally:
   if proc:legacy.terminate_owned(proc)
   if debug:legacy.terminate_owned(debug)
   r.update(status=status,detail=detail,exit_code=proc.returncode if proc else None,debugger_exit=debug.returncode if debug else None,wall_seconds=time.monotonic()-start,peak_combined_rss_bytes=peak,raw_log_sha256=c.digest(out/'raw.log') if (out/'raw.log').exists() else None,gdb_log_sha256=c.digest(out/'gdb.log') if (out/'gdb.log').exists() else None)
   c.write_json(out/'run_status.json',r)
   with coord.locked() as (data,item):
    row=next(x for x in item['attempts'] if x['attempt_id']==a['attempt_id']);c.require(not proc or proc.poll() is not None,'ownnativechildstillalive');c.require(not debug or debug.poll() is not None,'owndebuggerstillalive')
    row.update(state=status if row['actual_start'] else 'CANCELLED_BEFORE_START',finished_unix=time.time(),receipt_path=str(out/'run_status.json'),receipt_sha256=c.digest(out/'run_status.json'))
    data['runs'][a['run_key']].update(status=row['state'],detail=detail,raw_log_sha256=r['raw_log_sha256'])
    item['forensic_controls'][CONTROL_ID]['result']=dict(path=str(out/'run_status.json'),sha256=c.digest(out/'run_status.json'))
   c.write_json(c.HANDOFF/'events/E_E006_SAME773_FORENSIC_RESULT_r1.json',r)
  print(json.dumps(dict(attempt_id=a['attempt_id'],status=status,detail=detail,actual_starts=coord.snapshot()['actual_starts'])),flush=True)
if __name__=='__main__':execute()
