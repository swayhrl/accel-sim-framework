"""Root report publisher; never imports or calls model/native dispatch modules."""
from pathlib import Path
import json,os,subprocess,hashlib,datetime,fcntl,urllib.request,time,sys,traceback,gzip
P=Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
R=P('/root/data/dtc_stage_iia_remaining48_20261104_v1');D=A/'publication_service_v1';W=A/'execution-worktree'
BRANCH='hrl/dtc-stage-iia-remaining48-execution-20261104-v1'
REL='docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1';O=W/REL
REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1';BASE='5f67b4d6b94568a9f1acc80c3e56736bd81e4753'
BP=A/'agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json'
FP=D/'APPROVED_FIGURE_PROVIDER.fixed.json'
REG=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
PLAN_SHA='9f257eeea3ebe81610a88cef8ad37512b54bdb50728f965e8d73ccf5dd89a4b3'
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',http_proxy='http://127.0.0.1:27890',https_proxy='http://127.0.0.1:27890')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def rd(p):return json.loads(P(p).read_bytes())
def sb(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sb(P(p).read_bytes())
def write(p,b):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists()and p.read_bytes()==b:return
 t=p.with_name('.'+p.name+'.'+str(os.getpid())+'.writing');t.write_bytes(b);os.replace(t,p)
def put(p,v):write(p,(json.dumps(v,indent=2,sort_keys=True)+'\n').encode())
def rel(s):
 p=P(s);assert not p.is_absolute()and '..'not in p.parts and p.parts,s
 return p
def verified(p,expected,under=None):
 p=P(p)
 if under is not None:assert p.is_relative_to(under)and p.resolve().is_relative_to(under.resolve()),str(p)
 b=p.read_bytes();assert sb(b)==expected,(str(p),'SHA mismatch');return b
def manifest_copy(path,dest,expected):
 path=P(path);raw=verified(path,expected);m=json.loads(raw)
 for x in m['files']:
  r=rel(x['path']);b=verified(path.parent/r,x['sha256'],path.parent);assert len(b)<8*1024**2
  write(dest/r,b)
 write(dest/path.name,raw)
def checked_provider(v):
 assert v['schema']=='DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1'
 assert v['request']==REQ and v['sole_publisher']=='ROOT_ONLY'and v['source_qualified']is True
 assert v['new_model_starts']==0 and v['native_scientific_writes']==0
 s=v['summary'];assert s['expected_CH']==48 and s['expected_six_source_slots']==192 and s['core32_fixed_input_n']==32
 assert s['source_qualified']is True and 0<=s['accepted_CH']<=48 and 0<=s['core32_common_both_F_n']<=32
 assert s['accepted_CH']+s['archived_negative_CH']+s['verification_hold']+s['await_result']==48
 assert s['accepted_six_source_slots']==144+s['accepted_CH']
 assert s['frozen_reference_RESULT_SHA_rechecked']==144 and s['original128_and_first16_separate_source_roles']is True
 assert all(isinstance(s[k],int)and s[k]>=0 for k in ['accepted_CH','archived_negative_CH','verification_hold','await_result','registered_consumed','registered_remaining'])
 assert s['registered_consumed']+s['registered_remaining']==48
 assert v['all_registered48_terminal_verified']is s['all_registered48_terminal_verified']
 assert not v['all_registered48_terminal_verified']or(s['accepted_CH']+s['archived_negative_CH']==48 and s['verification_hold']==0 and s['registered_consumed']==48 and s['registered_remaining']==0)
 q=v['qualification_manifest'];assert q['path']==str(A/'agents/B_runtime_analysis_v1/runtime_adapter_v1/MANIFEST.json')and q['sha256']=='ff7555aff68156598df69ef83a1d48750b29884383ba8362f91f04c6ab5a16ea'
 verified(q['path'],q['sha256'])
 root=A/'agents/B_runtime_analysis_v1/snapshot_runner_v1/snapshots'
 verified(v['manifest']['path'],v['manifest']['sha256'],root);names=set()
 for x in v['files']:
  r=rel(x['name']);assert len(r.parts)==1;verified(x['path'],x['sha256'],root);names.add(x['name'])
 assert names=={'STAGEIIA_REMAINING48_OBSERVATIONS.json.gz','STAGEIIA_REMAINING48_CORE32_RESULTS.json.gz','STAGEIIA_REMAINING48_SUMMARY.json.gz','STAGEIIA_REMAINING48_CORE32_RESULTS.md'}
 sx=next(x for x in v['files']if x['name']=='STAGEIIA_REMAINING48_SUMMARY.json.gz')
 assert json.loads(gzip.decompress(verified(sx['path'],sx['sha256'])))==s
 return v
def git(*args,timeout=60):
 cmd=['git','-c','safe.directory='+str(W),'-c','http.version=HTTP/1.1','-c','user.name=swayhrl','-c','user.email=56393103+swayhrl@users.noreply.github.com','-C',str(W),*args]
 x=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,env=ENV)
 if x.returncode:raise RuntimeError((args,x.stderr[-1800:]))
 return x.stdout.strip()
def static_export():
 assert sha(R/'control/EXECUTION_PLAN.json')==PLAN_SHA
 plan=rd(R/'control/EXECUTION_PLAN.json');assert plan['initial_finite_budget']==48 and plan['core32_reporting_authorized']is True
 frozen=A/'execution_frozen_metadata_v1';index=[]
 for x in plan['source_pins']:
  p=P(x['path']);b=verified(p,x['sha256']);r=rel(str(p).lstrip('/'));dest=frozen/r;write(dest,b)
  rec=dict(x,bytes=len(b),true164_metadata_copy=str(dest),public_copy=None)
  if p.is_relative_to(R)and 'input_bindings'not in p.parts:
   out=O/'execution'/p.relative_to(R);write(out,b);rec['public_copy']=str(out.relative_to(O))
  elif not p.is_relative_to(R):
   out=O/'execution/shared_pinned_sources'/r;write(out,b);rec['public_copy']=str(out.relative_to(O))
  index.append(rec)
 assert len(index)==122
 put(O/'execution/FROZEN_SOURCE_INDEX.json',dict(source_pins=index,plan_sha256=PLAN_SHA,raw_trace_or_binary_exported=False,full_binding_metadata_on_true164=True))
 for n in ['EXECUTION_PLAN.json','CPU_QUALIFICATION.json','REGISTRY_REQUEST_CANDIDATE.json','PARENT_ADDON_ACK.json','DISPATCH_STARTED.json']:
  write(O/'execution/control'/n,(R/'control'/n).read_bytes())
 packs=[('A_resource_config_v1/MANIFEST.json','df42319b431cf98d24f2421fe6fa7eb3401ff5ff0a3db9892725cf76cc4e3649'),
 ('C_execution_qualification_v1/MANIFEST.json','c6c939e30ff8bba98474818f274bd12f33cd2f40921b527770c4d7726ef40f5c'),
 ('C_post_registration_review_v1/MANIFEST.json','0a1c209711081e09889f19c71862f7fc315b1f6074faedf0e5ed57f372f31245'),
 ('C_actual_canary_lifecycle_v1/MANIFEST.json','d7a0b375595415ba11156598c4460a0ed27cefa074c870a81d72c5282c6b6685'),
 ('B_runtime_analysis_v1/PREQUALIFICATION_MANIFEST_V1.json','8184a327048dc01d66b5ddd56e5a346b137510087278c83be70678f462206268'),
 ('B_runtime_analysis_v1/runtime_adapter_v1/MANIFEST.json','ff7555aff68156598df69ef83a1d48750b29884383ba8362f91f04c6ab5a16ea'),
 ('B_runtime_analysis_v1/snapshot_runner_v1/MANIFEST.json','a8307827df10e81f9513fced86b1d54a53fe87df53cc98ed2ce905c9a940f079'),
 ('A_figures_v1/HANDOFF_MANIFEST.json','30e56e3764becb44798375e450dbc84d540aa84dcaa7000f2683e06b16df904d')]
 for r,s in packs:
  p=A/'agents'/r;manifest_copy(p,O/'independent_reviews'/p.parent.relative_to(A/'agents'),s)
 put(D/'STATIC_EXPORT_COMPLETE.json',dict(UTC=utc(),base=BASE,plan_sha256=PLAN_SHA,pin_n=122,packs=packs,scientific_starts=0))
def export_figures():
 approval=rd(D/'FIGURE_VISUAL_APPROVAL.json');f=rd(FP)
 assert f['manifest']==approval['approved_manifest']and f['plot_source_sha256']==approval['plot_source_sha256']
 assert f['native_actions']==0 and f['sole_publisher']=='ROOT_ONLY'
 root=A/'agents/A_figures_v1/snapshots';verified(f['manifest']['path'],f['manifest']['sha256'],root)
 for x in f['files']:write(O/'figures'/rel(x['name']),verified(x['path'],x['sha256'],root))
 write(O/'figures/MANIFEST.json',P(f['manifest']['path']).read_bytes());put(O/'figures/PROVIDER.json',f);put(O/'figures/ROOT_VISUAL_APPROVAL.json',approval)
 return f
def publish():
 with(A/'PUBLICATION.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);pending=D/'PENDING_PUSH.json'
  if pending.exists():v=rd(pending)
  else:
   assert git('branch','--show-current')==BRANCH and not git('status','--porcelain')
   assert git('merge-base',BASE,'HEAD')==BASE
   b=checked_provider(rd(BP));s=b['summary'];terminal=b['all_registered48_terminal_verified']
   if not(D/'STATIC_EXPORT_COMPLETE.json').exists():static_export()
   f=export_figures()
   for x in b['files']:write(O/'analysis'/rel(x['name']),verified(x['path'],x['sha256']))
   put(O/'analysis/PROVIDER.json',b);write(O/'analysis/SNAPSHOT_MANIFEST.json',P(b['manifest']['path']).read_bytes())
   batch=rd(R/'analysis/BATCH_STATE.json');put(O/'snapshots/BATCH_STATE.json',batch)
   req=rd(REG)['registered_future_requests'][REQ];assert req['budget']==48 and len(req['admitted_specs'])==48
   put(O/'snapshots/NEW_REQUEST.json',req)
   observations=next(x for x in b['files']if x['name']=='STAGEIIA_REMAINING48_OBSERVATIONS.json.gz')
   observed=json.loads(gzip.decompress(verified(observations['path'],observations['sha256'])))
   for row in observed['observations']:
    if row.get('RESULT_sha256'):
     name=rel(row['cohort']+'.RESULT.json');assert len(name.parts)==1
     write(O/'accepted_or_negative_receipts'/name,verified(R/'analysis'/name,row['RESULT_sha256']))
   for n in ['report_only_publisher.py','FIGURE_VISUAL_APPROVAL.json','APPROVED_FIGURE_PROVIDER.fixed.json','CPU_CHECKS.json','SERVICE_CONTRACT.json']:
    write(O/'publication_service'/n,(D/n).read_bytes())
   put(O/'LATEST_STATUS.json',dict(UTC=utc(),status='ALL48_TERMINAL_FINAL_INDEPENDENT_REVIEW_PENDING'if terminal else'EXACT48_BACKGROUND_EXECUTION',summary=s,batch_asof=batch['UTC'],batch_running=batch.get('running'),canary_gate=batch.get('canary_runtime_gate_passed'),preclaim_resource_holds=batch.get('preclaim_resource_holds',[]),figure_snapshot=f['snapshot'],figure_n=f['common_both_F_n'],figure_accepted_new48=f['accepted_new48'],models_launched_by_publication_service=0,final_scientific_closure=False,additional_experiments_released=False))
   write(O/'README.md',(D/'REVIEW_PACK_README.md').read_bytes())
   members=sorted(p for p in O.rglob('*')if p.is_file()and p!=O/'MANIFEST.json')
   put(O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=utc(),base_authority=BASE,request=REQ,all48_terminal_verified=terminal,final_scientific_closure=False,files=[dict(path=str(p.relative_to(O)),sha256=sha(p),bytes=p.stat().st_size)for p in members]))
   paths=[str(p.relative_to(W))for p in sorted(O.rglob('*'))if p.is_file()];git('add','-f','--',*paths)
   changed=git('diff','--cached','--name-only').splitlines();assert changed and all(x.startswith(REL+'/')for x in changed)
   git('diff','--cached','--check')
   git('commit','-m','docs(dtc): '+('publish exact48 terminal receipts pending final review'if terminal else'publish Remaining48 CH execution and fixed CORE32 interim results'),'--',*paths)
   v=dict(commit=git('rev-parse','HEAD'),branch=BRANCH,UTC=utc(),all48_terminal_verified=terminal,final_scientific_closure=False,manifest_sha256=sha(O/'MANIFEST.json'),summary=s);put(pending,v)
  assert v['branch']==BRANCH and git('rev-parse','HEAD')==v['commit']
  git('push','origin',v['commit']+':refs/heads/'+BRANCH,timeout=90)
  assert git('ls-remote','origin','refs/heads/'+BRANCH,timeout=30).split()[0]==v['commit']
  op=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:27890'}));checks={}
  for n in ['MANIFEST.json','LATEST_STATUS.json','analysis/STAGEIIA_REMAINING48_CORE32_RESULTS.md','analysis/STAGEIIA_REMAINING48_SUMMARY.json.gz']:
   url='https://raw.githubusercontent.com/swayhrl/accel-sim-framework/'+v['commit']+'/'+REL+'/'+n
   raw=op.open(url,timeout=25).read();assert sb(raw)==sha(O/n);checks[n]=dict(url=url,sha256=sb(raw))
  v.update(status='PUSH_LSREMOTE_HTTPS_VERIFIED',HTTPS_readbacks=checks,verified_UTC=utc())
  put(D/'receipts'/(v['commit']+'.json'),v);put(D/'LATEST_PUBLICATION.json',v);pending.unlink();return v
def selfcheck():
 tests=[]
 for s in ['/outside','../outside','sub/../../outside']:
  try:rel(s)
  except AssertionError:tests.append('reject_path_'+s)
  else:raise AssertionError(s)
 assert rel('safe/NAME.json')==P('safe/NAME.json');tests.append('valid_relative_path')
 actual=rd(BP);checked_provider(actual);tests.append('actual_provider_SHA_checks')
 for k,v in [('source_qualified',False),('new_model_starts',1),('native_scientific_writes',1),('request','old'),('sole_publisher','AGENT')]:
  bad=dict(actual);bad[k]=v
  try:checked_provider(bad)
  except AssertionError:tests.append('reject_provider_'+k)
  else:raise AssertionError(k)
 for name in ['adapter_SHA','budget_mismatch','terminal_mismatch','summary_unbound']:
  bad=json.loads(json.dumps(actual))
  if name=='adapter_SHA':bad['qualification_manifest']['sha256']='0'*64
  if name=='budget_mismatch':bad['summary']['registered_remaining']+=1
  if name=='terminal_mismatch':bad['all_registered48_terminal_verified']=not bad['summary']['all_registered48_terminal_verified']
  if name=='summary_unbound':bad['summary']['registered_consumed']-=1;bad['summary']['registered_remaining']+=1
  try:checked_provider(bad)
  except AssertionError:tests.append('reject_'+name)
  else:raise AssertionError(name)
 assert sha(R/'control/EXECUTION_PLAN.json')==PLAN_SHA;tests.append('frozen_plan_SHA')
 assert git('branch','--show-current')==BRANCH and git('merge-base',BASE,'HEAD')==BASE;tests.append('isolated_branch_base')
 v=dict(UTC=utc(),passed=len(tests),checks=tests,model_starts=0,native_scientific_writes=0,Git_mutations=0,source_sha256=sha(__file__))
 put(D/'CPU_CHECKS.json',v);print(json.dumps(v))
def main():
 D.mkdir(exist_ok=True)
 if '--selfcheck'in sys.argv:selfcheck();return
 if '--once'in sys.argv:print(json.dumps(publish()));return
 with(D/'SERVICE.lock').open('a+b')as service:
  fcntl.flock(service,fcntl.LOCK_EX|fcntl.LOCK_NB)
  put(D/'PID.json',dict(pid=os.getpid(),start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),source_sha256=sha(__file__),no_dispatch=True,read_only_science=True))
  last=0
  while True:
   try:
    b=checked_provider(rd(BP));terminal=b['all_registered48_terminal_verified']
    if time.monotonic()-last>=1800 or terminal or(D/'PENDING_PUSH.json').exists():
     v=publish();last=time.monotonic();put(D/'STATUS.json',dict(UTC=utc(),last_publication=v,scientific_completion_claim=False,automatic_next_phase=False))
     if terminal and v['all48_terminal_verified']and v['status']=='PUSH_LSREMOTE_HTTPS_VERIFIED':put(D/'TERMINAL_PROGRESS_PUBLICATION_COMPLETE.json',v);return
   except Exception:put(D/'LAST_ERROR.json',dict(UTC=utc(),traceback=traceback.format_exc(),retry_same_commit=(D/'PENDING_PUSH.json').exists(),models_retried=0))
   time.sleep(30)
if __name__=='__main__':main()
