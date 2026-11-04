"""Root report-only publisher. No experiment/registry/owner/Goal mutation API."""
from pathlib import Path
import json,hashlib,subprocess,os,sys,time,fcntl,datetime,traceback
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');S=A/'publication_service_v2';W=A/'execution-worktree';REL='docs/dtc_l1/review_packs/DTC_PERFORMANCE_FIRST_PARALLEL_EXPLORATION_20261104_V1';D=W/REL;BR='hrl/dtc-perf-first-parallel-exploration-20261104-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode();t=p.with_name('.'+p.name+'.'+str(os.getpid())+'.writing');t.write_bytes(b);t.replace(p)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*args):
 r=subprocess.run(['git','-c','core.bare=false','-c','safe.directory='+str(W),'-c','user.name=swayhrl','-c','user.email=56393103+swayhrl@users.noreply.github.com','-c','http.version=HTTP/1.1','-C',str(W),*args],text=True,capture_output=True,timeout=180,env={**os.environ,'http_proxy':'http://127.0.0.1:27890','https_proxy':'http://127.0.0.1:27890'});assert r.returncode==0,(args,r.stderr[-3000:]);return r.stdout.strip()
def copy(p,relative):
 p=Path(p);assert p.is_file()and not p.is_symlink()and p.stat().st_size<8*1024**2
 relative=Path(relative);assert not relative.is_absolute()and'..'not in relative.parts;dst=D/relative;dst.parent.mkdir(parents=True,exist_ok=True);b=p.read_bytes()
 if dst.exists():assert dst.read_bytes()==b,'IMMUTABLE_COPY_MISMATCH '+str(dst)
 else:dst.write_bytes(b)
def export_packet(row):
 p=Path(row['manifest_path']);assert p.resolve().is_relative_to(A.resolve());assert sha(p)==row['manifest_sha256'];m=rd(p)
 for x in m['files']:
  rel=x.get('path',x.get('relative_path'));assert not Path(rel).is_absolute()and'..'not in Path(rel).parts;assert sha(p.parent/rel)==x['sha256'];copy(p.parent/rel,row['public_directory']+'/'+rel)
 copy(p,row['public_directory']+'/MANIFEST.json')
def publish():
 cfg=rd(S/'PUBLICATION_SOURCES.fixed.json');assert sha(cfg['consumer_source'])==cfg['consumer_source_sha256']and sha(cfg['consumer_manifest'])==cfg['consumer_manifest_sha256'];assert git('branch','--show-current')==BR
 # Recover only an already-created Root publication commit after a transient push error.
 if(S/'PENDING_PUSH.json').exists():
  pending=rd(S/'PENDING_PUSH.json');assert git('rev-parse','HEAD')==pending['commit']and not git('status','--porcelain');git('push','origin','HEAD:refs/heads/'+BR);assert git('ls-remote','origin','refs/heads/'+BR).split()[0]==pending['commit'];put(S/'RECOVERED_PUSH.json',pending);(S/'PENDING_PUSH.json').unlink()
 assert not git('status','--porcelain'),'UNEXPECTED_WORKTREE_WRITES_ROOT_REVIEW_REQUIRED'
 x=subprocess.run([sys.executable,'-B',cfg['consumer_source']],capture_output=True,text=True,timeout=900);assert x.returncode==0,x.stderr[-4000:]
 provider=rd(cfg['consumer_provider']);assert provider['report_only']and provider['native_writes']==0 and provider['new_models']==0 and provider['baseline_source_qualified'];assert sha(provider['manifest']['path'])==provider['manifest']['sha256']
 summary=provider['summary'];snapshot_name=Path(provider['snapshot']).name
 for row in provider['files']:
  assert sha(row['path'])==row['sha256'];copy(row['path'],'progress_snapshots/'+snapshot_name+'/'+row['name'])
 copy(provider['manifest']['path'],'progress_snapshots/'+snapshot_name+'/MANIFEST.json')
 for row in cfg['packets']:export_packet(row)
 for addition in sorted((S/'approved_additions').glob('*.json')):
  extra=rd(addition);assert extra['Root_report_publication_only']is True
  for row in extra['packets']:export_packet(row)
 put(D/'LATEST_RESULTS_PROVIDER.json',dict(provider=provider,publication_observed_utc=stamp(),source_manifest_sha256=provider['manifest']['sha256'],report_only=True,no_new_science=True))
 put(D/'LATEST_RESULTS_SUMMARY.json',summary)
 count=summary['accepted_new_points'];negative=summary['archived_negative_new_points'];pending=summary['pending_nonTag_points'];hold=summary['Tag_safety_HOLD'];unused=summary.get('unstarted_family_HOLD_points',summary.get('unused_family_HOLD_points',0))
 lines=['# Latest Performance-First results','',f'Updated {provider["observed_utc"]}. Fixed48 planned cells: Tag safety HOLD={hold}; non-Tag accepted={count}, archived negative={negative}, unused-family-HOLD={unused}, pending={pending}. Fixed exploratory inputs=8. These are not the core32 population.','',f'Immutable complete table, source identities, CSV and missingness: [snapshot](progress_snapshots/{snapshot_name}/README.md). See LATEST_RESULTS_SUMMARY.json and the matching JSON/CSV in that snapshot.','', 'All curves and GM use one fixed variant at a time. Direct variant comparison requires the common accepted input intersection; no best-per-program stitching. Tag HOLD cells have no simulated cycles and are not performance negatives. Missing counters are unavailable, not zero.','', '| Variant | Accepted / planned | GM DH-P0 / candidate (available set) |','| --- | ---: | ---: |']
 for name,v in summary['variants'].items():
  z=v['available_set_metrics']['S_DH']['GM'];lines.append('| '+name+' | '+str(v['accepted_n'])+' / '+str(v['planned_n'])+' | '+('missing'if z is None else format(z,'.6f'))+' |')
 lines+=['','The four original PHYS768 points must all pass the independent complete strict/true164/native-restore gate before the separate remaining28 request can attach. This report process cannot dispatch, register, reset, stop models or change any Goal. Only the existing legal owner may execute models. Full32 direction review and frozen manuscript v0.23 boundaries remain in CURRENT_STATUS.md and authority_amendments/.','']
 (D/'LATEST_RESULTS.md').write_text('\n'.join(lines));git('add','--',REL);changed=git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(REL+'/')for p in changed)
 git('commit','-m',f'docs: DTC structure exploration checkpoint {count} accepted {negative} negative {hold} Tag HOLD');com=git('rev-parse','HEAD');pending_record=dict(commit=com,UTC=stamp(),summary_counts=summary['status_counts'],terminal=provider['all32_nonTag_closed_verified']);put(S/'PENDING_PUSH.json',pending_record)
 git('push','origin','HEAD:refs/heads/'+BR);assert git('ls-remote','origin','refs/heads/'+BR).split()[0]==com;(S/'PENDING_PUSH.json').unlink();put(S/'LAST_PUBLICATION.json',dict(pending_record,remote_SHA_readback=com,source_provider_manifest_sha256=provider['manifest']['sha256']))
 return provider
def main():
 os.nice(10)
 S.mkdir(parents=True,exist_ok=True)
 with(S/'REPORT_ONLY_PUBLISHER.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);last=0;prior=None
  while True:
   try:
    fingerprints=[]
    for root in ['/root/data/dtc_perf_first_parallel_exploration_20261104_v1','/root/data/dtc_perf_first_remaining28_20261104_v1']:
     p=Path(root)/'analysis/BATCH_STATE.json';v=rd(p)if p.exists()else{};fingerprints.append([v.get('consumed'),v.get('remaining'),v.get('states'),v.get('errors')])
    final_ready=rd(S/'FINAL_C_REVIEW_PUBLICATION_READY.json')if(S/'FINAL_C_REVIEW_PUBLICATION_READY.json').exists()else None
    key=json.dumps([fingerprints,final_ready],sort_keys=True)
    if prior!=key or time.monotonic()-last>=1800 or(S/'REQUEST_PUBLISH.json').exists():
     p=publish();last=time.monotonic();prior=key;put(S/'STATUS.json',dict(UTC=stamp(),status='REPORT_ONLY_ACTIVE',interval_seconds=1800,models_started=0,native_writes=0,last_publication=rd(S/'LAST_PUBLICATION.json')))
     if(S/'REQUEST_PUBLISH.json').exists():(S/'REQUEST_PUBLISH.json').rename(S/('REQUEST_CONSUMED.'+str(time.time_ns())+'.json'))
     if (S/'STOP_AFTER_CURRENT_PUBLICATION').exists():put(S/'CONTROLLED_REPORT_ONLY_STOP.json',dict(UTC=stamp(),no_scientific_signals=True,last_publication=rd(S/'LAST_PUBLICATION.json')));return
     if final_ready and p.get('all32_candidates_accounted_verified',p['all32_nonTag_closed_verified']):
      final_path=Path(final_ready['final_review_path']);final_review=rd(final_path);assert sha(final_path)==final_ready['final_review_sha256']and final_review['independent_verification_passed']is True and final_review['all32_candidates_accounted_verified']is True
      assert sha(D/final_ready['public_final_review_relative_path'])==final_ready['final_review_sha256']
      put(S/'TERMINAL_PUBLICATION_COMPLETE.json',dict(UTC=stamp(),report_only=True,scientific_manual_signoff_not_implied=True,last_publication=rd(S/'LAST_PUBLICATION.json'),independent_final_review_sha256=final_ready['final_review_sha256']));return
    if '--once'in sys.argv:return
   except BaseException:
    put(S/('PUBLISH_ERROR.'+str(time.time_ns())+'.json'),dict(UTC=stamp(),traceback=traceback.format_exc(),model_actions=0))
    if '--once'in sys.argv:raise
   time.sleep(30)
if __name__=='__main__':main()
