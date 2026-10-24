"""Actual small CPU process/failure fixtures; never reads raw trace or runs CUDA/SIM."""
import pathlib,hashlib,json,subprocess,os,time,shutil,importlib.util
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');Q=C.parent/'post_outer_v3_lock_cpu_qualification_A1';assert not Q.exists();Q.mkdir();OUTER=C/'supervise_stencil_post_native8_epoch3_v3.py';source=OUTER.read_text();ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('auth',C/'read_native_foreign_reserve_v1.py');auth=importlib.util.module_from_spec(spec);spec.loader.exec_module(auth);foreign=auth.snapshot();results=[]
cases=['runtime_deadline_own_twoPG_tree','late_COMMIT_receiver_receipt_present']
for case in cases:
 base=Q/case;ctl=base/'control';ctl.mkdir(parents=True);lib=base/'private_fake_library';(lib/'objects').mkdir(parents=True);(lib/'receipts').mkdir();savepath=ctl/'MARKER_CONTROLLER_EXECUTED'
 for name in ['post_app_parallel_v5.py','validate_app_hot_resume_v4r3.py','read_native_foreign_reserve_v1.py']:shutil.copyfile(C/name,ctl/name)
 (ctl/'QUEUE.json').write_text(json.dumps([{'id':ID,'status':'RUNNING_CPU_POST_NATIVE8'}]));(ctl/(ID+'_POST_EPOCH3_STATE.json')).write_text(json.dumps({'status':'FAKE_RUNNING_FOR_RESOURCE_FIXTURE'}))
 controller=ctl/'resume_stencil_native8_post_epoch3_v3.py'
 code="import pathlib,os,time,subprocess,json,hashlib\nC=pathlib.Path("+repr(str(ctl))+");B=pathlib.Path("+repr(str(lib))+");ID="+repr(ID)+"\n(C/'MARKER_CONTROLLER_EXECUTED').write_text('executed')\n"
 if case=='runtime_deadline_own_twoPG_tree':code+="p=subprocess.Popen(['sleep','30'],start_new_session=True)\n(C/'OWN_CHILD.json').write_text(json.dumps({'pid':p.pid,'ticks':pathlib.Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split()[19]}))\ntime.sleep(30)\n"
 elif case.startswith('late_COMMIT'):
  code+="root=B/'objects'/ID;root.mkdir();m=root/'MANIFEST.json';m.write_text(json.dumps({'asset_id':ID,'files':[]}));c={'asset_id':ID,'status':'COMMITTED_VERIFIED','manifest_sha256':hashlib.sha256(m.read_bytes()).hexdigest()};(root/'COMMIT.json').write_text(json.dumps(c));\n"
  if case.endswith('receipt_present'):code+="(B/'receipts'/(ID+'_RECEIVER_READBACK.json')).write_text(json.dumps(c))\n"
  code+="raise SystemExit(19)\n"
 else:code+="time.sleep(30)\n"
 controller.write_text(code)
 modified=source.replace(str(C),str(ctl)).replace('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1',str(lib))
 if case=='startup_journal_failure':modified=modified.replace("def save(p,o):","def save(p,o):\n if p.name.endswith('_SUPERVISOR.json'):raise PermissionError('isolated startup journal fault')")
 elif case=='immediate_proc_failure':modified=modified.replace("  immediate=proc.proc(p.pid);known[p.pid]=immediate","  raise PermissionError('isolated immediate proc handshake fault')")
 elif case=='Popen_failure':modified=modified.replace("p=subprocess.Popen([sys.executable,'-c',BOOTSTRAP", "p=subprocess.Popen(['/ABSENT_POST_GUARD_CPU_FIXTURE','-c',BOOTSTRAP")
 elif case=='runtime_deadline_own_twoPG_tree':modified=modified.replace('deadline=time.time()+48*3600','deadline=time.time()+2')
 outer=ctl/'fixture_outer.py';outer.write_text(modified)
 grant={'supervisor_sha256':sha(outer),'controller_sha256':sha(controller),'foreign_registry_sha256':foreign['registry_sha256'],'foreign_epoch_sha256':foreign['epoch_sha256'],'foreign_reserved_sum_bytes':foreign['sum_all_records_reserved_write_bytes']};g=ctl/'FAKE_CPU_ONLY_GRANT.json';g.write_text(json.dumps(grant))
 sentinel=subprocess.Popen(['sleep','120'],start_new_session=True);sentinel_tick=pathlib.Path('/proc',str(sentinel.pid),'stat').read_text().split(') ',1)[1].split()[19];start=time.time()
 try:
  with(base/'outer.log').open('x')as log:p=subprocess.run(['python3','-B',str(outer),str(g)],stdout=log,stderr=subprocess.STDOUT,timeout=30)
  assert p.returncode!=0,case;terminal=json.loads((ctl/(ID+'_POST_EPOCH3_SUPERVISOR_TERMINAL.json')).read_text());queue=json.loads((ctl/'QUEUE.json').read_text())[0];state=json.loads((ctl/(ID+'_POST_EPOCH3_STATE.json')).read_text())
  assert terminal['unresolved_exact_own_processes']==[]and sentinel.poll()is None and pathlib.Path('/proc',str(sentinel.pid),'stat').read_text().split(') ',1)[1].split()[19]==sentinel_tick
  if case in ['startup_journal_failure','immediate_proc_failure','Popen_failure']:assert not savepath.exists(),'controller sideeffect escaped gated startup'
  if case.startswith('late_COMMIT'):
   assert queue['status']in ['COMMIT_PRESENT_CLOSEOUT_PENDING','COMMITTED_VERIFIED']and state['status'].startswith('COMMIT_PRESENT')and terminal['status']=='COMMIT_PRESENT_CLOSEOUT_NOTE'
   assert (lib/'objects'/ID/'COMMIT.json').exists()
  else:assert queue['status']=='FAILED_RETAINED'and state['status']=='FAILED_RETAINED_CPU_POST_ONLY'
  childfile=ctl/'OWN_CHILD.json'
  if childfile.exists():
   child=json.loads(childfile.read_text());stat=pathlib.Path('/proc',str(child['pid']),'stat')
   if stat.exists():parts=stat.read_text().split(') ',1)[1].split();assert parts[19]!=child['ticks']or parts[0]=='Z'
  results.append({'case':case,'status':'CPU_GUARD_FIXTURE_PASS','seconds':time.time()-start,'returncode':p.returncode,'queue_status':queue['status'],'state_status':state['status'],'terminal_status':terminal['status'],'controller_executed':savepath.exists(),'unresolved':terminal['unresolved_exact_own_processes'],'foreign_sentinel_unchanged':True,'fixture_code_sha256':sha(outer),'fault_injection_scope':'Only isolated paths/controller and named fault; not producer/scientific qualification'})
 finally:
  if sentinel.poll()is None:sentinel.terminate();sentinel.wait(timeout=5)
 (Q/'PROGRESS.json').write_text(json.dumps({'rows':results},indent=2)+'\n')
(Q/'QUALIFICATION.json').write_text(json.dumps({'status':'ACTUAL_SMALL_CPU_GATED_START_FAILURE_OPERATIONAL_FAILURE_AND_COMMIT_PRESERVATION_PASS','production_outer_sha256':sha(OUTER),'rows':results,'real_raw_trace_reads':0,'GPU_or_SIM_runs':0,'real_queue_authority_or_library_modified':False},indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(results),'path':str(Q/'QUALIFICATION.json')}))
