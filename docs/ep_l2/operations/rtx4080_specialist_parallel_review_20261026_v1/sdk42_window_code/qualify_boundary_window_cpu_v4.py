"""CPU-only policy and real Linux watchdog tests; no production control writes or GPU calls."""
import pathlib,json,hashlib,ast,subprocess,sys,copy,importlib.util
D=pathlib.Path(__file__).parent
def imp(n):
 spec=importlib.util.spec_from_file_location('private_'+n.replace('.','_'),D/n);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=imp('boundary_window_controller_candidate_v3.py')
F=D/'controller_cpu_fixture_v4';F.mkdir()
results=[]
def yes(name,f):f();results.append({'case':name,'status':'PASS'})
def no(name,f):
 try:f()
 except (AssertionError,FileExistsError,FileNotFoundError,RuntimeError,ValueError):results.append({'case':name,'status':'EXPECTED_REJECTION'});return
 raise AssertionError(name+' was accepted')
before=json.load(open(D/'BOUNDARY_BEFORE_V1.json'));q=copy.deepcopy(before['queue_baseline'])
phase,ds=m.frozen_modules()
rs={'__name__':'inert_resume','__file__':str(D/'dispatch_finite_resume33_candidate_v2.py')};exec(compile((D/'dispatch_finite_resume33_candidate_v2.py').read_text(),str(D/'dispatch_finite_resume33_candidate_v2.py'),'exec'),rs);ds=rs
no('unapproved_spec_no_execution',lambda:m.grant_gate({'approved':False},{}))
no('unfilled_spec_no_execution',lambda:m.grant_gate({'approved':True,'action':'SDK42_50K_MICROWINDOW_THEN_EXACT33_ONCE','GPU_window_max_seconds':900,'payload_max_bytes':1073741824},{}))
yes('original_running_job_unchanged',lambda:m.check_queue(q,before))
assert q==before['queue_baseline']
bad=copy.deepcopy(q);next(x for x in bad if x['id']==before['boundary_job']['id'])['status']='FAILED_RETAINED'
no('old_job_failure_does_not_advance',lambda:m.check_queue(bad,before))
bad=copy.deepcopy(q);next(x for x in bad if x['id']==before['resume_ids'][0])['worker_sha256']='bad'
no('original33_identity_drift_rejected',lambda:m.check_queue(bad,before))
stop=F/'STOP_AFTER_CURRENT';stop.write_bytes(b'FOREIGN_STOP')
no('foreign_stop_never_overwritten',lambda:m.stop_create_or_check(stop,b'OWN',phase));assert stop.read_bytes()==b'FOREIGN_STOP'
ownstop=F/'OWN_STOP';m.stop_create_or_check(ownstop,b'OWN',phase)
yes('own_stop_exact_reentry',lambda:m.stop_create_or_check(ownstop,b'OWN',phase))
beforebytes=ownstop.read_bytes()
phase['retire_stop'](ownstop,F/'RETIRED',b'OWN')
assert (F/'RETIRED').read_bytes()==beforebytes and not ownstop.exists();results.append({'case':'only_exact_own_stop_retired','status':'PASS'})
snap=json.load(open(D/'FROZEN_PENDING_33.json'));frozen={x['id']:x for x in snap['jobs']};selected=list(frozen)
pending=[{k:v for k,v in x.items()if k!='job_sha256'}for x in snap['jobs']]
first=selected[0];done=copy.deepcopy(pending);done[0]['status']='COMMITTED_VERIFIED'
assert first not in [x['id']for x in ds['scope_jobs'](done,frozen,selected)]
results.append({'case':'completed_original33_not_rerun','status':'PASS'})
drift=copy.deepcopy(pending);drift[0]['job_path']='/different'
no('resume_original33_jobpath_drift_rejected',lambda:ds['scope_jobs'](drift,frozen,selected))
assert len(ds['scope_jobs'](pending,frozen,selected))==33
clean={'status':'OWN_WINDOW_PROCESSES_ABSENT_AND_REMOTE_LEASES_IDLE'}
assert m.resume_allowed(True,True,clean,True)
assert not m.resume_allowed(True,True,{'status':'SSH_ERROR'},True)
assert not m.resume_allowed(False,True,clean,True)
assert not m.resume_allowed(True,False,clean,True)
assert not m.resume_allowed(True,True,clean,False)
results.append({'case':'window_failure_may_resume_only_with_independent_cleanup_and_old_closed','status':'PASS'})
m.one_shot_intent(F/'RESUME_INTENT.json',{'scope':'33'})
no('resume_launch_intent_once_only',lambda:m.one_shot_intent(F/'RESUME_INTENT.json',{'scope':'33'}))
# Fresh grant-only native entry rejection, before any attempt mkdir/lock/GPU query.
a=subprocess.run([sys.executable,'-B',str(D/'capture_sdk42_default50k_nas_candidate_v2.py'),str(D/'C8_SDK42_VECTOR_DEFAULT50000_SPECIALIST_A001.json')],capture_output=True,text=True,timeout=10)
assert a.returncode!=0 and 'ROOT_CAPTURE_APPROVAL_V1.json' in a.stderr
(F/'unapproved_worker.stderr.log').write_text(a.stderr)
results.append({'case':'real_worker_missing_Root_grant_rejected_before_side_effects','status':'PASS'})
# Frozen grant function accepts exactly task/limits and rejects mutations without running worker body.
s=(D/'capture_sdk42_default50k_nas_candidate_v2.py').read_text();tree=ast.parse(s);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='validate_root_grant')
ns={'json':json,'pathlib':pathlib,'sha':m.sha};exec(compile(ast.Module(body=[fn],type_ignores=[]),'grant_only','exec'),ns)
job=json.load(open(D/'C8_SDK42_VECTOR_DEFAULT50000_SPECIALIST_A001.json'));jp=F/'job.json';wp=F/'worker.py';wp.write_text('MOCK_BYTES');jp.write_text(json.dumps(job))
grant={'approved':True,'action':'SDK42_DEFAULT50000_C8_NAS_MICROWINDOW_ONCE','worker_sha256':m.sha(wp),'job_sha256':m.sha(jp),'GPU_window_max_seconds':900,'payload_max_bytes':1073741824};gp=F/'CPU_ONLY_MOCK_GRANT.json';gp.write_text(json.dumps(grant))
yes('exact_candidate_task_and_caps_grant_gate',lambda:ns['validate_root_grant'](jp,job,wp,gp))
bad=copy.deepcopy(job);bad['task']['argv'].append('--size=1024')
no('reduced_or_altered_argv_rejected',lambda:ns['validate_root_grant'](jp,bad,wp,gp))
bad=copy.deepcopy(job);bad['resource_limits']['capture_timeout_sec']=901
no('GPU_bound_increase_rejected',lambda:ns['validate_root_grant'](jp,bad,wp,gp))
bad=copy.deepcopy(job);bad['id']='DIFFERENT'
no('wrong_case_identity_rejected',lambda:ns['validate_root_grant'](jp,bad,wp,gp))
# Generate cleanup remote checker without executing it, and parse exact Python source.
a={'remote_window_worker':'/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/sdk42_default50k_microwindow_20261026_v1/capture_sdk42_default50k_nas_candidate_v2.py','remote_window_job':'/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/sdk42_default50k_microwindow_20261026_v1/C8_SDK42_VECTOR_DEFAULT50000_SPECIALIST_A001.json','remote_capture_approval':'/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/sdk42_default50k_microwindow_20261026_v1/ROOT_CAPTURE_APPROVAL_V1.json','window_worker_sha256':'a'*64,'window_job_sha256':'b'*64,'capture_approval_sha256':'c'*64}
import shlex
original=m.subprocess.run
def mock_run(argv,**kw):
 code=shlex.split(argv[-1])[-1];ast.parse(code);(F/'EXACT_REMOTE_CLEANUP_CHECK.py').write_text(code)
 return type('Result',(),{'returncode':0,'stdout':json.dumps(clean),'stderr':''})()
m.subprocess.run=mock_run
try:assert m.remote_check(a,before,True,{'gpu_compute':[],'exact_sdk_argv':[]})==clean
finally:m.subprocess.run=original
results.append({'case':'independent_remote_cleanup_checker_source_parses_no_GPU_no_signal','status':'PASS'})
baseline={'gpu_compute':[[338712,'343978668']],'exact_sdk_argv':[]}
yes('baseline_ComfyUI_identity_preserved_allowed',lambda:m.independent_identity_gate(baseline,copy.deepcopy(baseline)))
observed=copy.deepcopy(baseline);observed['exact_sdk_argv']=[[999990,'100001']]
no('missing_marker_bare_SDK_alive_rejected',lambda:m.independent_identity_gate(baseline,observed))
observed_gpu=copy.deepcopy(baseline);observed_gpu['gpu_compute'].append([999991,'100002'])
no('foreign_new_GPU_compute_identity_hold_no_signal',lambda:m.independent_identity_gate(baseline,observed_gpu))
observed_reused={'gpu_compute':[[338712,'DIFFERENT_TICKS']],'exact_sdk_argv':[]}
no('reused_GPU_PID_different_ticks_rejected',lambda:m.independent_identity_gate(baseline,observed_reused))
no('missing_preGPU_baseline_rejected',lambda:m.independent_identity_gate({},baseline))
report={'status':'CONTROLLER_CPU_POLICY_GATES_PASS','cases':results,'GPU_started':False,'production_STOP_or_QUEUE_writes':False,'source_KEEP':True}
(D/'CONTROLLER_CPU_FIXTURE_RESULT_V4.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'status':report['status'],'cases':len(results)}))
