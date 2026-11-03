"""Root-owned report-only publisher; never imports dispatch/native/model modules."""
from pathlib import Path
import json,os,subprocess,hashlib,datetime,fcntl,urllib.request,time,sys,traceback
P=Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');R=P('/root/data/dtc_stage_iia_first16_20261104_v1');D=A/'publication_service_v2';W=A/'execution-worktree';B='hrl/dtc-stage-iia-first16-execution-20261104-v1';REL='docs/dtc_l1/review_packs/DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1';O=W/REL
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',http_proxy='http://127.0.0.1:27890',https_proxy='http://127.0.0.1:27890')
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name('.'+p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');os.replace(t,p)
def git(*a,timeout=50):
 c=['git','-c','safe.directory='+str(W),'-c','http.version=HTTP/1.1','-c','user.name=swayhrl','-c','user.email=56393103+swayhrl@users.noreply.github.com','-C',str(W),*a]
 x=subprocess.run(c,capture_output=True,text=True,timeout=timeout,env=env)
 if x.returncode:raise RuntimeError((a,x.stderr[-2000:]))
 return x.stdout.strip()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def publish():
 with(A/'PUBLICATION.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  pending=D/'PENDING_PUSH.json'
  if pending.exists():v=rd(pending)
  else:
   assert git('branch','--show-current')==B and not git('status','--porcelain')
   provider=rd(A/'agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json');assert provider['schema']=='DTC_STAGEIIA_FIRST16_ANALYSIS_PUBLICATION_PROVIDER_V1'and provider['sole_publisher']=='ROOT_ONLY'and provider['summary']['remaining48_locked']is True
   assert sha(provider['manifest']['path'])==provider['manifest']['sha256']
   for x in provider['files']:
    assert P(x['path']).is_relative_to(A/'agents/B_runtime_analysis_v1/snapshots')and sha(x['path'])==x['sha256']
    p=O/'analysis'/x['name'];p.parent.mkdir(exist_ok=True);p.write_bytes(P(x['path']).read_bytes())
   put(O/'analysis/PROVIDER.json',provider);put(O/'snapshots/BATCH_STATE.json',rd(R/'analysis/BATCH_STATE.json'))
   req=rd('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1'];assert req['budget']==16 and len(req['admitted_specs'])==16
   put(O/'snapshots/NEW_REQUEST.json',req)
   for ad in ['A_actual_admission_v1','C_actual_execution_v1','C_disk_preclaim_v1','C_disk_preclaim_actual_v1','B','B_runtime_adapter_v1','B_runtime_analysis_v1']:
    for p in ((A/'agents'/ad).glob('*') if ad=='B_runtime_analysis_v1' else (A/'agents'/ad).rglob('*')):
     if p.is_file()and p.stat().st_size<2*1024**2 and p.suffix in ['.py','.json','.md']:
      dest=O/'independent_reviews'/ad/p.relative_to(A/'agents'/ad);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
   for p in (A/'agents/B_runtime_analysis_v1/readonly_findings').rglob('*'):
    if p.is_file()and p.suffix in ['.json','.md','.py']and p.stat().st_size<2*1024**2:
     dest=O/'independent_reviews/B_runtime_analysis_v1/readonly_findings'/p.relative_to(A/'agents/B_runtime_analysis_v1/readonly_findings');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
   for p in [R/'control/RESULT_ENGINE_PIN.json',A/'ARCHIVE_ENGINE_METADATA_COMPLETION.json']:
    if p.exists():
     dest=O/'execution/archive_metadata'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
   for p in [D/'FORWARD_SERVICE_AMENDMENT.json',D/'CPU_CHECKS.json',D/'report_only_publisher.py']:
    dest=O/'publication_service'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
   for p in (R/'control/operational_amendments').rglob('*'):
    if p.is_file()and '__pycache__'not in p.parts and p.stat().st_size<2*1024**2:
     dest=O/'execution/control/operational_amendments'/p.relative_to(R/'control/operational_amendments');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
   for p in (R/'analysis').glob('*.RESULT.json'):
    dest=O/'accepted_or_negative_receipts'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
   complete=provider['all_registered16_terminal_verified'];assert not complete or provider['summary']['accepted_CH']+provider['summary']['archived_negative_CH']==16
   put(O/'LATEST_STATUS.json',dict(UTC=utc(),status='FIRST16_TERMINAL_INDEPENDENT_ANALYSIS_AVAILABLE_ROOT_FINAL_REVIEW_PENDING'if complete else'FIRST16_BACKGROUND_EXECUTION',summary=provider['summary'],batch_running=rd(R/'analysis/BATCH_STATE.json')['running'],next48_released=False,models_launched_by_publication_service=0))
   text="""# Recommendation for the remaining 48 core CH matching points

The remaining 48 are not authorized or registered by this execution. Preserve the original frozen input set and original P0/F128/F256 reference roles. Do not use first-batch performance to change which inputs belong to the core set.

Before a new execution request, review first16 coverage and all strict/archive/restore holds. Carry positive, zero, negative and missing outcomes into the decision. Compare F128 and F256 on the same common accepted inputs; report CH own gain, DH own gain, same-F CH/DH and relative extra DH gain. A common downstream gain is not uniquely a DTC mechanism gain.

If the scientific review approves extending coverage, use a new exact48 request and unused identities under the same unique owner, with fresh live CPU/RSS/pressure/native write-and-restore admission and true164 qualification. Keep all eight first-batch inputs and remaining frozen programs in the predetermined statistics; never choose configurations or programs by their best speedup. Treat hybridsort F256 and lavamd F128 as the separately scoped supplemental points, and leave the four deferred points unresolved until their original prerequisites are met.

This file is a review checklist and proposed execution boundary. No next-batch release, combination, capture, old model retry or manuscript edit is performed. Quantitative parameter recommendations remain subject to the independent paired tables in `analysis` and the final DTC-MAIN review.
"""
   (O/'NEXT48_RECOMMENDATION_PENDING_APPROVAL.md').write_text(text)
   manifest=rd(O/'MANIFEST.json');manifest.update(UTC=utc(),schema='DTC_STAGEII_FIRST16_EXECUTION_PROGRESS_V1',first16_terminal_verified=complete,files=[dict(path=str(p.relative_to(O)),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(O.rglob('*'))if p.is_file()and p!=O/'MANIFEST.json']);put(O/'MANIFEST.json',manifest)
   files=[str(p.relative_to(W))for p in O.rglob('*')if p.is_file()];git('add','-f','--',*files)
   if not git('diff','--cached','--name-only'):return dict(no_changes=True)
   git('diff','--cached','--check','--',REL+'/LATEST_STATUS.json',REL+'/NEXT48_RECOMMENDATION_PENDING_APPROVAL.md',REL+'/MANIFEST.json')
   git('commit','-m','docs(dtc): '+('archive first16 CH paired results for final review'if complete else'update first16 CH execution and independent paired results'),'--',*files)
   v=dict(commit=git('rev-parse','HEAD'),branch=B,UTC=utc(),first16_terminal_verified=complete,manifest_sha256=sha(O/'MANIFEST.json'));put(pending,v)
  assert git('rev-parse','HEAD')==v['commit']
  git('push','origin',v['commit']+':refs/heads/'+B);assert git('ls-remote','origin','refs/heads/'+B,timeout=30).split()[0]==v['commit']
  op=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:27890'}));checks={}
  for n in ['MANIFEST.json','LATEST_STATUS.json','analysis/STAGEIIA_FIRST16_RESULTS.md','analysis/STAGEIIA_FIRST16_SUMMARY.json.gz']:
   url='https://raw.githubusercontent.com/swayhrl/accel-sim-framework/'+v['commit']+'/'+REL+'/'+n;b=op.open(url,timeout=25).read();assert hashlib.sha256(b).hexdigest()==sha(O/n);checks[n]=dict(url=url,sha256=sha(O/n))
  v.update(status='PUSH_LSREMOTE_HTTPS_VERIFIED',HTTPS_readbacks=checks);put(D/'receipts'/(v['commit']+'.json'),v);put(D/'LATEST_PUBLICATION.json',v);pending.unlink();return v
def main():
 with(D/'SERVICE.lock').open('a+b')as service:
  fcntl.flock(service,fcntl.LOCK_EX|fcntl.LOCK_NB);put(D/'PID.json',dict(pid=os.getpid(),start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),source_sha256=sha(__file__),read_only_science=True,no_dispatch=True))
  last=0
  while True:
   try:
    provider=rd(A/'agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json');terminal=provider['all_registered16_terminal_verified']
    if time.monotonic()-last>=1800 or terminal or(D/'PENDING_PUSH.json').exists():
     v=publish();last=time.monotonic();put(D/'STATUS.json',dict(UTC=utc(),last_publication=v,automatic_next48=False))
     if terminal and v.get('first16_terminal_verified')and v.get('status')=='PUSH_LSREMOTE_HTTPS_VERIFIED':put(D/'TERMINAL_PUBLICATION_COMPLETE.json',v);return
   except BaseException:
    put(D/'LAST_ERROR.json',dict(UTC=utc(),traceback=traceback.format_exc(),retry_same_commit=bool((D/'PENDING_PUSH.json').exists()),models_retried=0))
   time.sleep(30)
if __name__=='__main__':main()
