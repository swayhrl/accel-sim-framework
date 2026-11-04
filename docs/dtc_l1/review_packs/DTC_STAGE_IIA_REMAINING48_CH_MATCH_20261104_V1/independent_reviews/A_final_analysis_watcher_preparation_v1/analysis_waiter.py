#!/usr/bin/env python3
"""One-shot CPU analysis waiter; no scientific dispatcher, native CLI, signals or Git."""
import argparse,datetime,fcntl,gzip,hashlib,json,os,pathlib,secrets,subprocess,sys,time,traceback
sys.dont_write_bytecode=True
P=pathlib.Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
PREP=A/'agents/A_final_analysis_watcher_preparation_v1'
STATE=PREP/'state'
OFFICIAL=A/'agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json'
REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
CPREP=A/'agents/C_final48_review_preparation_v1';BPREP=A/'agents/B_final24_consumption_preparation_v1'
PYTHON=P('/usr/bin/python3')
PLOT_PYTHON=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/A_figures_v1/plot-venv/bin/python')
STAGE_PINS=[
 (CPREP/'MANIFEST.json','98363f73eb985a7089b236a91300e77b2cb170d99081555c703659ca7543fc59'),
 (CPREP/'final48_readonly_audit.py','69fc696dd05e05c33be3560021b1fa5f479246d075ac93a846e4fafbcdd44bf8'),
 (BPREP/'MANIFEST.json','450cfdb615975f80da6dd4a48fd3de8853235efcf10052f158dc2d431e30d997'),
 (BPREP/'consume_final24.py','5537173bf3f955b021e7bd7bb65c75ea18e23c22a8f89cc51ef8dcf1e525d84c'),
 (A/'root_cycle_statistics_audit.py','a9f881775a6780237470104b286e82abad2e9d51f7b4f696767439bfce5595df'),
 (A/'root_figures_v2/plot_core32.py','30cfe1f0e5c3d08a095c011961c98580ae3a86e155c76e4e0c0d18f77ca92313'),
 (A/'agents/A_resource_config_v1/RESOURCE_SPEC_FIELDS.json','5af631a81ad583bab34e53e5bfb09d40d5833407b503fc4354b65e9ea40267d1')]
QUAL_SHA='ff7555aff68156598df69ef83a1d48750b29884383ba8362f91f04c6ab5a16ea'
ADAPTER_SHA='0383daa67804db3b92779f2520cbbc0978c195c759e27357938319c942442e1c'
PLAN_SHA='9f257eeea3ebe81610a88cef8ad37512b54bdb50728f965e8d73ccf5dd89a4b3'
PASS='PASS_STAGEII48_CH_STRICT_ARCHIVE_NATIVE_RESTORE';NEG='FAIL_STAGEII48_CH_ARCHIVED_NO_RETRY'

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def rd(p):return json.loads(P(p).read_bytes())
def jsonbytes(x):return(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def exclusive(p,x):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(jsonbytes(x));f.flush();os.fsync(f.fileno())
def atomic(p,x):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name('.'+p.name+'.'+secrets.token_hex(4));exclusive(q,x);os.replace(q,p)
def safe_relative(p):
 p=P(p);assert not p.is_absolute()and'..'not in p.parts,'UNSAFE_RELATIVE_PATH';return p
def checked(p,want):
 b=P(p).read_bytes();assert digest(b)==want,('SOURCE_OR_FILE_SHA_DRIFT',str(p));return b
def verify_manifest(path,want=None):
 path=P(path);b=checked(path,want)if want else path.read_bytes();m=json.loads(b)
 for x in m['files']:
  q=(path.parent/safe_relative(x['path'])).resolve();assert q.is_relative_to(path.parent.resolve()),'MANIFEST_PATH_ESCAPE';checked(q,x['sha256'])
 return m

def verify_source_contract(preparation_manifest_sha=None):
 if preparation_manifest_sha:verify_manifest(PREP/'MANIFEST.json',preparation_manifest_sha)
 for p,want in STAGE_PINS:checked(p,want)
 for p,want in [STAGE_PINS[0],STAGE_PINS[2]]:verify_manifest(p,want)
 assert PYTHON.is_file()and PLOT_PYTHON.is_file(),'MISSING_CPU_PYTHON'
 return dict(status='SOURCE_CONTRACT_PINS_PASS',pins=[dict(path=str(p),sha256=h)for p,h in STAGE_PINS],Python=str(PYTHON),plot_Python=str(PLOT_PYTHON))

def light_gate(p):
 assert p.get('schema')=='DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1'and p.get('request')==REQ,'WRONG_OFFICIAL_PROVIDER_IDENTITY'
 s=p.get('summary',{});reasons=[]
 if p.get('source_qualified')is not True or s.get('source_qualified')is not True:reasons.append('SOURCE_NOT_QUALIFIED')
 for k in ['expected_CH','registered_consumed','registered_remaining','accepted_CH','archived_negative_CH','verification_hold','await_result']:
  if type(s.get(k))is not int:reasons.append('MISSING_OR_NONINTEGER_'+k)
 if reasons:return dict(ready=False,reasons=reasons)
 if s['expected_CH']!=48:raise ValueError('EXPECTED_BUDGET_NOT_FIXED48')
 if s['registered_consumed']<0 or s['registered_remaining']<0 or s['registered_consumed']+s['registered_remaining']!=48:raise ValueError('REGISTERED_BUDGET_NOT48_BY_CONSUMED_REMAINING')
 if s['registered_consumed']!=48 or s['registered_remaining']!=0:reasons.append('NOT48CONSUMED_REM0')
 if s['accepted_CH']<0 or s['archived_negative_CH']<0 or s['accepted_CH']+s['archived_negative_CH']!=48:reasons.append('ACCEPTED_PLUS_ARCHIVED_NEGATIVE_NOT48')
 if s['verification_hold']!=0 or s['await_result']!=0:reasons.append('HOLD_OR_PENDING')
 if p.get('all_registered48_terminal_verified')is not True or s.get('all_registered48_terminal_verified')is not True:reasons.append('NOT_ALL48_TERMINAL_VERIFIED')
 if s.get('request')!=REQ or s.get('core32_fixed_input_n')!=32 or s.get('expected_six_source_slots')!=192:raise ValueError('WRONG_SCIENTIFIC_SCOPE')
 return dict(ready=not reasons,reasons=reasons,budget_expected=48,registered_consumed=s['registered_consumed'],registered_remaining=s['registered_remaining'],accepted=s['accepted_CH'],archived_negative=s['archived_negative_CH'])

def full_gate(raw):
 p=json.loads(raw);g=light_gate(p);assert g['ready'],'FULL_GATE_CALLED_EARLY'
 snap=P(p['snapshot']).resolve();assert snap.is_relative_to((OFFICIAL.parent/'snapshots').resolve()),'NOT_OFFICIAL_B_SNAPSHOT_NAMESPACE'
 assert P(p['manifest']['path']).resolve().parent==snap,'SNAPSHOT_MANIFEST_ESCAPE'
 assert all(P(x['path']).resolve().parent==snap for x in p['files']),'SNAPSHOT_MEMBER_ESCAPE'
 assert p['qualification_manifest']['sha256']==QUAL_SHA;verify_manifest(p['qualification_manifest']['path'],QUAL_SHA)
 mf=json.loads(checked(p['manifest']['path'],p['manifest']['sha256']));assert mf['source_qualified']is True and mf['schema']=='DTC_REMAINING48_READONLY_ANALYSIS_SNAPSHOT_V1';assert mf['adapter']['sha256']==ADAPTER_SHA and mf['runtime_plan']['sha256']==PLAN_SHA
 mp={x['path']:x['sha256']for x in mf['files']};loaded={}
 for x in p['files']:
  assert mp[x['path']]==x['sha256'];b=checked(x['path'],x['sha256'])
  if P(x['path']).name in ['SUMMARY.json.gz','OBSERVATIONS.json.gz','CORE32_RESULTS.json.gz']:loaded[P(x['path']).name]=json.loads(gzip.decompress(b))
 s=loaded['SUMMARY.json.gz'];obs=loaded['OBSERVATIONS.json.gz'];assert s==p['summary']and s['observed_utc']==p['observed_utc'];assert obs['source_qualified']is True and obs['registration_granted']is True and obs['registered_consumed']==48 and obs['registered_remaining']==0 and obs['request']==REQ
 expected=rd(STAGE_PINS[-1][0])['points'];byid={x['cohort']:x for x in expected};rows=obs['observations'];assert len(byid)==len(rows)==48 and {x['cohort']for x in rows}==set(byid);uuids=[];ac=ng=0
 for r in rows:
  e=byid[r['cohort']];assert r['input_digest']==e['input_digest']and r['profile']==e['profile']and r['design']=='CH';assert r['status']in [PASS,NEG];assert isinstance(r.get('uuid'),str)and r['uuid'];uuids.append(r['uuid'])
  if r['status']==PASS:assert r['accepted']is True and type(r.get('cycles'))is int and r['cycles']>0;ac+=1
  else:assert r['accepted']is False and r.get('cycles')is None;ng+=1
 assert len(set(uuids))==48 and(ac,ng)==(s['accepted_CH'],s['archived_negative_CH'])
 return p,dict(g,source_manifest=p['manifest'],official_provider_sha256=digest(raw),unique_UUIDs=48,qualified_B_adapter_asserts_actual_budget48=True,C_next_rechecks_actual_registry_and_live_generations=True)

def verify_true164(path):
 q=P(path).resolve();assert q.is_relative_to(A.resolve()),'OUTPUT_NOT_IN_APPROVED_TRUE164_ROOT'
 probe=q
 while not probe.exists():probe=probe.parent
 m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(probe)],text=True))['filesystems'][0]
 assert m['fstype']=='fuse.sshfs'and m['source']=='admin-wcx@10.208.130.164:/home/shared','NOT_GENUINE164_OUTPUT'
 return m

def own_identity():
 pid=os.getpid();f=P('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split();return dict(pid=pid,start_ticks=int(f[19]),boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip(),utc=utc())
def acquire_lock(path):
 f=P(path).open('a+b')
 try:fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:f.close();return None
 return f

def claim_attempt(path,value):exclusive(path,value)
def hold(state,reason,detail=None):
 p=P(state)/'ANALYSIS_HOLD.json'
 if not p.exists():exclusive(p,dict(status='ANALYSIS_HOLD_NO_AUTO_CPU_OR_MODEL_RETRY',utc=utc(),reason=reason,detail=detail,model_actions=0,Root_manual_review_required=True))
 atomic(P(state)/'STATUS.json',dict(status='ANALYSIS_HOLD',utc=utc(),reason=reason));return 2

def make_plan(tag,frozen_provider):
 c=A/'agents/C_final48_independent_audits_v1'/tag;b=BPREP/'updates'/tag;m=A/'root_independent_cycle_statistics_v1'/tag;fig=A/'agents/A_figures_v1/snapshots'/tag
 assert not any(p.exists()for p in [c,b,m,fig]),'ANALYSIS_OUTPUT_ALREADY_EXISTS'
 return [dict(name='C_FINAL48',argv=[str(PYTHON),'-B',str(STAGE_PINS[1][0]),'--mode','final','--provider',str(frozen_provider),'--output-dir',str(c)],output=str(c)),dict(name='B_FINAL24',argv=[str(PYTHON),'-B',str(STAGE_PINS[3][0]),'--provider',str(frozen_provider),'--output-dir',str(b)],output=str(b)),dict(name='ROOT_MATH',argv=[str(PYTHON),'-B',str(STAGE_PINS[4][0]),'--provider',str(frozen_provider),'--output-dir',str(m)],output=str(m)),dict(name='ROOT_RENDERER_V2',argv=[str(PLOT_PYTHON),'-B',str(STAGE_PINS[5][0]),'--provider',str(frozen_provider),'--output-root',str(fig)],output=str(fig))]

def subprocess_stage(stage,attempt,env):
 name=stage['name'];log=P(attempt)/(name+'.stdout_stderr.log');verify_true164(stage['output']);started=utc()
 with log.open('xb')as out:
  child=subprocess.Popen(stage['argv'],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,env=env,cwd=str(attempt),close_fds=True)
  exclusive(P(attempt)/(name+'.PROCESS.json'),dict(pid=child.pid,argv=stage['argv'],started_utc=started,only_CPU_analysis=True))
  rc=child.wait()
 receipt=dict(stage=name,argv=stage['argv'],started_utc=started,finished_utc=utc(),returncode=rc,log=dict(path=str(log),sha256=sha(log),bytes=log.stat().st_size),output=stage['output']);exclusive(P(attempt)/(name+'.RC.json'),receipt);return receipt

def stage_result(stage,provider_sha,accepted):
 out=P(stage['output']);name=stage['name']
 if name=='C_FINAL48':
  r=rd(out/'REVIEW.json');assert r['status']=='PASS_ALL48_INDEPENDENT_LIFECYCLE_AND_REVIEWED_INTEGER_STATISTICS'and r['mode']=='final'and r['whole48_independent_automated_review_complete']is True and len(r['rows'])==48 and r['accepted']==accepted and r['archived_negative']==48-accepted;return dict(review=dict(path=str(out/'REVIEW.json'),sha256=sha(out/'REVIEW.json')),final_automated_review=True,Root_signoff_not_granted=True)
 if name=='B_FINAL24':
  verify_manifest(out/'MANIFEST.json');r=rd(out/'public/SOURCE_AND_COMPLETION_RECEIPT.json');assert r['captured_provider_sha256']==provider_sha and r['all48terminal']is True and r['new48_accepted']==accepted and r['new48_archived_negative']==48-accepted and r['fixed24_input_n']==24 and r['live_raw_consumed']is False;return dict(manifest=dict(path=str(out/'MANIFEST.json'),sha256=sha(out/'MANIFEST.json')))
 if name=='ROOT_MATH':
  verify_manifest(out/'MANIFEST.json');r=json.loads(gzip.decompress((out/'AUDIT.json.gz').read_bytes()));assert r['status']=='PASS'and r['accepted_slots_rechecked']==144+accepted and r['new48_raw_cycle_endpoints_rechecked']==accepted;return dict(manifest=dict(path=str(out/'MANIFEST.json'),sha256=sha(out/'MANIFEST.json')),final_full32=r['final_full32'])
 assert name=='ROOT_RENDERER_V2';p=rd(A/'root_figures_v2/PUBLICATION_PROVIDER.json');snap=P(p['snapshot']).resolve();assert snap.is_relative_to(out.resolve())and p['source_provider_sha256']==provider_sha and p['plot_source_sha256']==STAGE_PINS[5][1];verify_manifest(p['manifest']['path'],p['manifest']['sha256']);return dict(v2_figure_provider=p,visual_review_and_D_approval='ROOT_ONLY_STILL_REQUIRED',original_A_provider_not_written=True)

def chain(stages,runner,checker,sourcecheck):
 receipts=[]
 for stage in stages:
  try:sourcecheck()
  except Exception as e:return dict(success=False,failed_stage=stage['name'],reason='SOURCE_DRIFT_HOLD',error=repr(e),receipts=receipts)
  receipt=runner(stage);receipts.append(receipt)
  if receipt['returncode']!=0:return dict(success=False,failed_stage=stage['name'],reason='NONZERO_CPU_EXIT',receipts=receipts)
  try:receipt['validated_result']=checker(stage)
  except Exception as e:return dict(success=False,failed_stage=stage['name'],reason='CPU_RESULT_CONTRACT_HOLD',error=repr(e),receipts=receipts)
 return dict(success=True,receipts=receipts)

def watch(preparation_manifest_sha):
 verify_true164(PREP);STATE.mkdir(exist_ok=True);lock=acquire_lock(STATE/'ANALYSIS_WAITER.lock')
 if lock is None:print(json.dumps(dict(status='ALREADY_RUNNING_NO_SECOND_WAITER')));return 3
 identity=own_identity();atomic(STATE/'PID_AND_START.json',identity)
 try:
  if(STATE/'ANALYSIS_HOLD.json').exists():print(json.dumps(dict(status='EXISTING_ANALYSIS_HOLD_NO_AUTOMATIC_RETRY')));return 2
  if(STATE/'ATTEMPT_CLAIM.json').exists():
   if(STATE/'AUTOMATED_ANALYSIS_COMPLETE.json').exists():print(json.dumps(dict(status='ALREADY_COMPLETE_NO_CPU_RETRY')));return 0
   return hold(STATE,'EXISTING_ATTEMPT_NOT_RETRIED')
  verify_source_contract(preparation_manifest_sha)
  while True:
   verify_source_contract(preparation_manifest_sha);raw=OFFICIAL.read_bytes();p=json.loads(raw);gate=light_gate(p);atomic(STATE/'STATUS.json',dict(status='WAITING_FOR_ALL48_TERMINAL'if not gate['ready']else'GATE_READY',utc=utc(),gate=gate,official_provider_sha256=digest(raw)))
   if gate['ready']:break
   time.sleep(60)
  p,proof=full_gate(raw);tag='analysis_once_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+str(identity['pid'])+'_'+secrets.token_hex(4);attempt=STATE/'attempts'/tag;attempt.mkdir(parents=True,exist_ok=False);frozen=attempt/'PROVIDER.fixed.json'
  with frozen.open('xb')as f:f.write(raw)
  exclusive(attempt/'GATE_PROOF.json',proof);stages=make_plan(tag,frozen);exclusive(attempt/'STAGE_PLAN.json',stages)
  claim_attempt(STATE/'ATTEMPT_CLAIM.json',dict(identity=identity,tag=tag,attempt=str(attempt),provider_sha256=digest(raw),utc=utc(),exact_once_CPU_chain=True,no_native_or_model_actions=True))
  temp=attempt/'tmp';temp.mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(temp),TMP=str(temp),TEMP=str(temp),PIP_CACHE_DIR=str(temp/'unused_pip_cache'),MPLCONFIGDIR=str(attempt/'mpl-config'));atomic(STATE/'STATUS.json',dict(status='CPU_ANALYSIS_CHAIN_RUNNING',utc=utc(),attempt=str(attempt)))
  original_A_provider=A/'agents/A_figures_v1/PUBLICATION_PROVIDER.json';before_A=sha(original_A_provider)if original_A_provider.exists()else None
  result=chain(stages,lambda s:subprocess_stage(s,attempt,env),lambda s:stage_result(s,digest(raw),proof['accepted']),lambda:verify_source_contract(preparation_manifest_sha));exclusive(attempt/'CHAIN_RESULT.json',result)
  assert(sha(original_A_provider)if original_A_provider.exists()else None)==before_A,'ORIGINAL_A_PROVIDER_CHANGED'
  if not result['success']:return hold(STATE,result['reason'],dict(attempt=str(attempt),failed_stage=result['failed_stage']))
  done=dict(status='AUTOMATED_ANALYSIS_COMPLETE_ROOT_REVIEW_PENDING',utc=utc(),attempt=str(attempt),captured_provider_sha256=digest(raw),source_gate=proof,chain_result=pinfile(attempt/'CHAIN_RESULT.json'),visual_review=False,D_fixed_figure_approval=False,final_narrative_signoff=False,Git_publication=False,Goal_completed=False,model_actions=0);exclusive(STATE/'AUTOMATED_ANALYSIS_COMPLETE.json',done);atomic(STATE/'STATUS.json',done);print(json.dumps(done));return 0
 except Exception:
  return hold(STATE,'WATCHER_OR_SOURCE_CONTRACT_FAILURE',traceback.format_exc())
 finally:lock.close()

def pinfile(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
def main():
 ap=argparse.ArgumentParser();mode=ap.add_mutually_exclusive_group(required=True);mode.add_argument('--check-contract',action='store_true');mode.add_argument('--watch',action='store_true');ap.add_argument('--preparation-manifest-sha256');args=ap.parse_args()
 if args.check_contract:verify_true164(PREP);r=verify_source_contract();r.update(service_started=False,CPU_chain_started=False,models_started=0);print(json.dumps(r));return 0
 assert args.preparation_manifest_sha256 and len(args.preparation_manifest_sha256)==64,'REVIEWED_PREPARATION_MANIFEST_SHA_REQUIRED'
 return watch(args.preparation_manifest_sha256)
if __name__=='__main__':raise SystemExit(main())
