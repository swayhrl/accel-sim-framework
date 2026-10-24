"""Small CPU-only policy, pure-SHA and real process-guard fixtures."""
import pathlib,json,hashlib,importlib.util,subprocess,time,os,shutil
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent;I='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2'
Q=N/'stencil768_private_qualification_A3';assert not Q.exists();Q.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('actual768',C/'stencil768_common_v2.py');actual=importlib.util.module_from_spec(spec);spec.loader.exec_module(actual)
normal=actual.resources(True);checks=[]
for reserved in [1879048192,14763950080]:
 for used in [0,128*2**20,768*2**20]:
  p=actual.policy(2**60,reserved,used);edge=p['required'];assert actual.policy(edge,reserved,used)['PASS']and not actual.policy(edge-1,reserved,used)['PASS'];checks.append({'reserved':reserved,'used':used,'exact_free_boundary':edge,'edge_accept_short1_reject':True})
source=actual.B/'objects/QUAL_terminal_native_offload_positive_20261025_A1/tree/data'
core=actual.module(C/'postprocess_nas_sharded_v4.py','algorithm',actual.CORE_SHA)
assert actual.digest(source,expected_bytes=source.stat().st_size)==core.sha(source)
outer=C/'supervise_stencil_single768_epoch4_v2.py';source_outer=outer.read_text();rows=[]
for case in ['startup_journal_failure','dynamic_foreign_growth_own_twoPG','late_receiver_COMMIT','leader_reaped_leaves_child']:
 base=Q/case;ctl=base/'control';ctl.mkdir(parents=True);lib=base/'fake_library';(lib/'objects').mkdir(parents=True);(lib/'receipts').mkdir()
 for name in ['post_app_parallel_v5.py','validate_app_hot_resume_v4r3.py']:shutil.copyfile(C/name,ctl/name)
 (ctl/'QUEUE.json').write_text(json.dumps([{'id':I,'status':'RUNNING_CPU_POST_SINGLE768'}]))
 common=ctl/'stencil768_common_v2.py'
 common_code="import pathlib,json,importlib.util,os\nROOT=pathlib.Path("+repr(str(C))+" )\ns=importlib.util.spec_from_file_location('actual_common',ROOT/'stencil768_common_v2.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)\nSCAN=a.SCAN;LIMIT=a.LIMIT\nWORK=pathlib.Path("+repr(str(base/(I+'_post_epoch4_single768')))+")\nF=pathlib.Path("+repr(str(ctl/'FAKE_FOREIGN_GROWTH'))+")\ndef epoch_native_usage():\n return {'total_bytes':SCAN.tree_size_race_safe(WORK)if WORK.exists()else 0}\ndef resources(force=False,stage_budget=0,admission=False):\n reserved=14763950080+(2**30 if F.exists()else 0);free=5*2**30+14763950080+2**30+64*2**20+LIMIT+128*2**20;used=SCAN.tree_size_race_safe(WORK)if WORK.exists()else 0;p=a.policy(free,reserved,used,stage_budget,admission);assert p['PASS'],('injected_private_dynamic_floor',p);return {'policy':p,'Native_free':free,'authority':{'sum_all_records_reserved_write_bytes':reserved},'fixture_only':True}\n"
 common.write_text(common_code)
 controller=ctl/'resume_stencil_single768_epoch4_v2.py';marker=ctl/'CONTROLLER_EXECUTED'
 code="import pathlib,os,time,subprocess,json,hashlib\nC=pathlib.Path("+repr(str(ctl))+");B=pathlib.Path("+repr(str(lib))+");I="+repr(I)+";W=pathlib.Path("+repr(str(base/(I+'_post_epoch4_single768')))+");W.mkdir()\n(C/'CONTROLLER_EXECUTED').write_text('x')\n"
 if case=='dynamic_foreign_growth_own_twoPG':
  code+="p=subprocess.Popen(['sleep','30'],start_new_session=True);s=pathlib.Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split();(W/'CORE_PROCESS_START_99.json').write_text(json.dumps({'pid':p.pid,'ticks':s[19],'pgid':int(s[2]),'sid':int(s[3]),'start_floor_ticks':int(s[19]),'parent_pid':os.getpid()}));(C/'FAKE_FOREIGN_GROWTH').write_text('private fake only');time.sleep(30)\n"
 elif case=='leader_reaped_leaves_child':
  childproof=ctl/'ORPHAN_CHILD.json'
  leadercode="import os,sys,subprocess,pathlib,json;sys.stdin.buffer.read(1);p=subprocess.Popen(['sleep','30']);s=pathlib.Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split();pathlib.Path("+repr(str(childproof))+").write_text(json.dumps({'pid':p.pid,'ticks':s[19],'sid':int(s[3]),'pgid':int(s[2])}))"
  code+="p=subprocess.Popen(['python3','-c',"+repr(leadercode)+"],stdin=subprocess.PIPE,start_new_session=True);s=pathlib.Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split();(W/'CORE_PROCESS_START_99.json').write_text(json.dumps({'pid':p.pid,'ticks':s[19],'pgid':int(s[2]),'sid':int(s[3]),'start_floor_ticks':int(s[19]),'parent_pid':os.getpid()}));p.stdin.write(b'G');p.stdin.close();p.wait();(C/'LEADER_REAPED').write_text(str(p.pid));raise SystemExit(29)\n"
 elif case=='late_receiver_COMMIT':
  code+="d=B/'objects'/I;d.mkdir();m=d/'MANIFEST.json';m.write_text(json.dumps({'files':[]}));q={'asset_id':I,'status':'COMMITTED_VERIFIED','manifest_sha256':hashlib.sha256(m.read_bytes()).hexdigest()};(d/'COMMIT.json').write_text(json.dumps(q));(B/'receipts'/(I+'_RECEIVER_READBACK.json')).write_text(json.dumps(q));raise SystemExit(23)\n"
 else:code+="time.sleep(30)\n"
 controller.write_text(code)
 modified=source_outer.replace(str(C),str(ctl)).replace(str(actual.B),str(lib))
 if case=='startup_journal_failure':modified=modified.replace('def save(p,o):',"def save(p,o):\n if p.name.endswith('_SUPERVISOR.json'):raise PermissionError('private startup journal failure')")
 fixture=ctl/'fixture_outer.py';fixture.write_text(modified);grant=ctl/'FAKE_GRANT.json';grant.write_text(json.dumps({'supervisor_sha256':sha(fixture),'controller_sha256':sha(controller),'common_sha256':sha(common)}))
 sentinel=subprocess.Popen(['sleep','120'],start_new_session=True);tick=pathlib.Path('/proc',str(sentinel.pid),'stat').read_text().split(') ',1)[1].split()[19]
 try:
  with(base/'OUTER.log').open('x')as log:cp=subprocess.run(['python3','-B',str(fixture),str(grant)],stdout=log,stderr=subprocess.STDOUT,timeout=30)
  assert cp.returncode!=0;term=json.loads((ctl/(I+'_POST_EPOCH4_SUPERVISOR_TERMINAL.json')).read_text());q=json.loads((ctl/'QUEUE.json').read_text())[0]
  assert not term['unresolved_exact_own_processes']and sentinel.poll()is None and pathlib.Path('/proc',str(sentinel.pid),'stat').read_text().split(') ',1)[1].split()[19]==tick
  if case=='late_receiver_COMMIT':assert q['status']=='COMMITTED_VERIFIED'and term['status']=='COMMIT_PRESENT_CLOSEOUT_NOTE'
  else:assert q['status']=='FAILED_RETAINED'
  if case=='startup_journal_failure':assert not marker.exists()
  if case=='leader_reaped_leaves_child':
   orphan=json.loads((ctl/'ORPHAN_CHILD.json').read_text());entry=pathlib.Path('/proc',str(orphan['pid']),'stat')
   if entry.exists():parts=entry.read_text().rsplit(')',1)[1].split();assert parts[19]!=orphan['ticks']or parts[0]in ['Z','X','x']
   assert (ctl/'LEADER_REAPED').exists()
  rows.append({'case':case,'PASS':True,'queue':q['status'],'unresolved':term['unresolved_exact_own_processes'],'foreign_sentinel_unchanged':True,'fixture_outer_sha256':sha(fixture)})
 finally:
  if sentinel.poll()is None:sentinel.terminate();sentinel.wait(timeout=5)
out=Q/'QUALIFICATION.json';out.write_text(json.dumps({'status':'PRIVATE_SINGLE768_POLICY_SHA_AND_PROCESS_GUARDS_PASS','source_outer_sha256':sha(outer),'source_common_sha256':sha(C/'stencil768_common_v2.py'),'policy_boundaries':checks,'actual_pinned_V10_normal_resource_snapshot':normal,'pure_NAS_SHA_equals_frozen5d_SHA':True,'real_small_CPU_process_cases':rows,'production_WORK_created':actual.WORK.exists(),'production_or_registry_or_scientific_input_mutations':False,'GPU_109_SIM_or_scientific_record_validator_runs':0,'scope':'Fake controllers/resources exercise only actual outer/process/dynamic-policy code, not a producer/scientific positive'},indent=2)+'\n');assert not actual.WORK.exists();print(json.dumps({'path':str(out),'sha256':sha(out),'status':'PASS'}))
