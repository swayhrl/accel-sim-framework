import datetime,fcntl,hashlib,json,os,pathlib,subprocess,time
repo=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r1');shared=pathlib.Path('/workspace/ep_l2_ft20261016_shared');out=pathlib.Path(__file__).resolve().parent
request=shared/'pilot_requests/EP_L2_R0_1_ENGINEERING_20261017_L1_P01/r2/LOW_SPACE_PILOT_REQUEST.json';old=json.loads((shared/'LANE1_GATEWAITER_STATUS.json').read_text());deadline=1792343848.8041663
assert old['status']=='WAITER_STOPPED_FAIL_CLOSED' and old['invocations']==0 and 'TimeoutExpired' in old['error'] and old['deadline_unix']==deadline
assert not pathlib.Path('/proc/1156558').exists() and not pathlib.Path('/proc/1156581').exists()
assert hashlib.sha256(request.read_bytes()).hexdigest()=='f992a65187ea46413cec85623af16cdd39e180b817e23f9002419d03cbf7129e'
assert hashlib.sha256((repo/'util/ep_l2/ft_lane1/gate_waiter.py').read_bytes()).hexdigest()=='58a44e056414d1ca947c51263f929279ba12d56e4c679275836c05b381497795'
assert hashlib.sha256((repo/'util/ep_l2/ft_lane1/engineering_pilot.py').read_bytes()).hexdigest()=='f5e660913649adb614a06baacecaf5a0640693f7969ce2976f75f08ec42ba527'
for n in ['LANE1_GATEWAITER.lock','LANE1_OUTCOME_PUBLISHER.lock','LANE1_BUILD_EXECUTION.lock']:
 p=shared/n
 if p.exists():
  with p.open() as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with (shared/'REGISTRY.lock').open() as f:
 fcntl.flock(f,fcntl.LOCK_SH);d=json.loads((shared/'RUN_REGISTRY.json').read_text());assert not any(v['status'] in ['RUNNING','RESERVED'] for k in ['runs','resource_leases'] for v in d[k].values());assert not d.get('engineering_pilots')
assert subprocess.check_output(['git','status','--porcelain'],cwd=repo)==b''
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o HostName=140.82.112.4 -o HostKeyAlias=github.com')
remaining=int(deadline-time.time());assert 0<remaining<=172800
command=['python3','-u','util/ep_l2/ft_lane1/gate_waiter.py','--request',str(request),'--watch','--execute-authorized','--max-seconds',str(remaining),'--output',str(out/'gate_waiter_r3')]
(out/'RESTORE_AUDIT.json').write_text(json.dumps({'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'RESTORE_AFTER_READONLY_GITHUB_FETCH_TIMEOUT','old_state':old,'old_publisher_receipt':json.loads(pathlib.Path('/workspace/results/ep_l2_ft20261016/lane1/review_r8/outcome_publisher_r2/PUBLISHER_STATE.json').read_text()),'original_deadline_unix':deadline,'requested_remaining_seconds':remaining,'request_unchanged':True,'driver_unchanged':True,'registry_active':False,'locks_free':True,'no_build_or_lease_was_executed':True,'transport':'Authenticated github.com known-host alias; bounded SSH transport timeout; no source or admission change'},indent=2)+'\n')
with (out/'GATEWAITER_CONSOLE.log').open('x') as log:subprocess.run(command,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
