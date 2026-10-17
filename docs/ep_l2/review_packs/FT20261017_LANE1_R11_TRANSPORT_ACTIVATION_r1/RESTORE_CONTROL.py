import datetime,fcntl,hashlib,json,os,pathlib,subprocess,time
repo=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r1');shared=pathlib.Path('/workspace/ep_l2_ft20261016_shared');out=pathlib.Path(__file__).resolve().parent
request=shared/'pilot_requests/EP_L2_R0_1_ENGINEERING_20261017_L1_P01/r3/LOW_SPACE_PILOT_REQUEST.json';old=json.loads((shared/'LANE1_GATEWAITER_STATUS.json').read_text());deadline=1792343848.8041663
assert old['status']=='WAITER_STOPPED_FAIL_CLOSED' and old['invocations']==0 and 'CalledProcessError(128' in old['error'] and old['deadline_unix']<=deadline
assert not pathlib.Path('/proc/1585205').exists() and not pathlib.Path('/proc/1585258').exists()
assert hashlib.sha256(request.read_bytes()).hexdigest()=='1b6ab366fea69c54706e0d4ad9a389ba83fc696e8c3570a2ad3606ac6e236b1a'
assert hashlib.sha256((repo/'util/ep_l2/ft_lane1/gate_waiter.py').read_bytes()).hexdigest()=='75b511456763dd35bb5125fed364f3a090306b02e081dcd6cd991ba9a1d624ed'
assert hashlib.sha256((repo/'util/ep_l2/ft_lane1/engineering_pilot.py').read_bytes()).hexdigest()=='f5e660913649adb614a06baacecaf5a0640693f7969ce2976f75f08ec42ba527'
for n in ['LANE1_GATEWAITER.lock','LANE1_OUTCOME_PUBLISHER.lock','LANE1_BUILD_EXECUTION.lock']:
 p=shared/n
 if p.exists():
  with p.open() as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with (shared/'REGISTRY.lock').open() as f:
 fcntl.flock(f,fcntl.LOCK_SH);d=json.loads((shared/'RUN_REGISTRY.json').read_text());assert not any(v['status'] in ['RUNNING','RESERVED'] for k in ['runs','resource_leases'] for v in d[k].values());assert not d.get('engineering_pilots')
assert subprocess.check_output(['git','status','--porcelain'],cwd=repo)==b''
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_TERMINAL_PROMPT='0',GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf',GIT_CONFIG_VALUE_0='git@github.com:',GIT_CONFIG_KEY_1='credential.helper',GIT_CONFIG_VALUE_1='!gh auth git-credential')
remaining=int(deadline-time.time());assert 0<remaining<=172800
command=['python3','-u','util/ep_l2/ft_lane1/gate_waiter.py','--request',str(request),'--watch','--execute-authorized','--max-seconds',str(remaining),'--output',str(out/'gate_waiter_r4')]
(out/'RESTORE_AUDIT.json').write_text(json.dumps({'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'RESTORE_GUARDED_TRANSPORT_NO_STALE_AUTHORITY_HTTPS_VERIFIED','old_state':old,'old_publisher_receipt':json.loads(pathlib.Path('/workspace/results/ep_l2_ft20261016/lane1/review_r11/network_recovery_r2/outcome_publisher_r3/PUBLISHER_STATE.json').read_text()),'original_deadline_unix':deadline,'requested_remaining_seconds':remaining,'request_unchanged':True,'driver_unchanged':True,'registry_active':False,'locks_free':True,'no_build_or_lease_was_executed':True,'transport':'HTTPS github.com using existing gh credential helper, ephemeral process environment only; guarded transport source248191e3 and r3 hash rebind; all resource/science/source inputs unchanged'},indent=2)+'\n')
with (out/'GATEWAITER_CONSOLE.log').open('x') as log:subprocess.run(command,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
