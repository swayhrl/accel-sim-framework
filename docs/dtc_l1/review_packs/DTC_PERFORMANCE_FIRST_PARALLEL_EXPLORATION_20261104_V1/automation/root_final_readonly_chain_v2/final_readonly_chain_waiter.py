"""Root CPU-only final evidence chain; never dispatches or retries a model."""
from pathlib import Path
import json,sys,hashlib,subprocess,os,time,datetime,fcntl,traceback
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');S=A/'final_readonly_chain_v2';PUB=A/'publication_service_v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def put(p,v,once=False):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 if once:
  with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 else:t=p.with_name('.'+p.name+'.'+str(os.getpid())+'.writing');t.write_bytes(b);t.replace(p)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def state(s,**kw):put(S/'STATUS.json',dict(UTC=stamp(),state=s,new_models=0,native_writes=0,Goal_actions=0,**kw))
def manifest(p):
 p=Path(p);v=rd(p)
 for row in v['files']:
  rel=Path(row.get('path',row.get('relative_path',row.get('name'))));assert not rel.is_absolute()and'..'not in rel.parts
  f=p.parent/rel;assert f.is_file()and not f.is_symlink()and sha(f)==row['sha256']
 return v
def command(label,argv,timeout):
 put(S/(label+'.INVOKED.json'),dict(UTC=stamp(),argv=argv,CPU_only=True,one_time=True),True)
 x=subprocess.run(argv,text=True,capture_output=True,timeout=timeout);put(S/(label+'.RESULT.json'),dict(UTC=stamp(),returncode=x.returncode,stdout=x.stdout[-10000:],stderr=x.stderr[-10000:]),True)
 assert x.returncode==0,label+'_CPU_HOLD_NO_AUTOMATIC_RETRY';return x
def packet(p,where):
 p=Path(p);mf=manifest(p)
 if any('path'not in row and'relative_path'not in row for row in mf['files']):
  original=p;export=S/'publication_exports'/where.replace('/','__');export.mkdir(parents=True,exist_ok=True);members=[]
  for row in mf['files']:
   rel=Path(row.get('path',row.get('relative_path',row.get('name'))));dst=export/rel;dst.parent.mkdir(parents=True,exist_ok=True);b=(original.parent/rel).read_bytes()
   with dst.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
   members.append(dict(path=str(rel),bytes=len(b),sha256=sha(dst)))
  dst=export/'ORIGINAL_SOURCE_MANIFEST.json'
  with dst.open('xb')as f:f.write(original.read_bytes());f.flush();os.fsync(f.fileno())
  members.append(dict(path=dst.name,bytes=dst.stat().st_size,sha256=sha(dst)));put(export/'MANIFEST.json',dict(schema='ROOT_FORWARD_NAME_KEY_FINAL_EXPORT_ADAPTER_V1',original_source_manifest_path=str(original),original_source_manifest_sha256=sha(original),files=members),True);p=export/'MANIFEST.json'
 return dict(manifest_path=str(p),manifest_sha256=sha(p),public_directory=where)
def invariants(cfg):
 pins={row['path']:row['sha256']for row in cfg['source_pins']}
 for path,pin in pins.items():assert sha(path)==pin,'FINAL_CHAIN_SOURCE_DRIFT '+path
 assert sha(__file__)==cfg['self_sha256']
 for key in ['C_validator','mechanism_source','figure_source','figure_python']:assert cfg[key]in pins and sha(cfg[key])==pins[cfg[key]],'UNPINNED_ACTUALLY_USED_PROGRAM '+key
 assert Path(cfg['C_validator']).resolve()==(A/'C_final_structure32_preparation_v2r1/final_structure32_readonly_audit.py').resolve()
 assert pins[cfg['C_validator']]=='aa3918b351c8831b202295f43213177e96605c62bc8773310fc4618eac3bc453'
 assert Path(cfg['C_final_review']).resolve()==(A/'C_final_structure32_v1/FINAL_REVIEW.json').resolve()
 assert Path(cfg['B3_provider']).resolve()==(A/'agents/B_perf_results_consumer_v3/PUBLICATION_PROVIDER.json').resolve()
 for key in ['mechanism_output','figure_output']:assert Path(cfg[key]).resolve().is_relative_to(A.resolve())and not Path(cfg[key]).resolve().is_relative_to((A/'execution-worktree').resolve())
 assert Path(cfg['mechanism_output']).resolve().is_relative_to(Path(cfg['mechanism_source']).resolve().parent/'snapshots'),'MECHANISM_CLI_OUTPUT_NAMESPACE_REQUIRED'
def main():
 os.nice(10);S.mkdir(parents=True,exist_ok=True)
 with(S/'READONLY_FINALIZER.lock').open('a+b')as held:
  fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);cfg=rd(S/'CONTRACT.fixed.json')
  while True:
   invariants(cfg)
   final=Path(cfg['C_final_review']);out=final.parent
   if(S/'FINAL_AUDIT.INVOKED.json').exists():state('EXISTING_ONE_SHOT_ATTEMPT_REQUIRES_ROOT_FORWARD_RECONCILIATION',no_retry=True);return
   if out.exists():state('EXISTING_FINAL_OUTPUT_REQUIRES_ROOT_FORWARD_RECONCILIATION_NO_DUPLICATE_AUDIT',no_retry=True);return
   x=subprocess.run(['/usr/bin/python3','-B',cfg['C_validator'],'--check-readiness'],text=True,capture_output=True,timeout=120);r=json.loads(x.stdout);assert type(r.get('ready'))is bool
   if not r['ready']:state('WAIT_ALL32_LEGAL_TERMINAL_AND_SOURCE_QUALIFIED_B3',readiness=r);time.sleep(60);continue
   provider=rd(cfg['B3_provider']);assert provider['baseline_source_qualified']and provider['all_existing_closed_results_qualified']and provider['admission_hold_metadata_qualified']and provider['all32_candidates_accounted_verified']
   assert sha(provider['manifest']['path'])==provider['manifest']['sha256'];put(S/'FINAL_B3_PROVIDER.fixed.json',provider,True)
   state('ONE_SHOT_C_FINAL_INDEPENDENT_STRICT_ARCHIVE_RESTORE_STATISTICS')
   command('FINAL_AUDIT',['/usr/bin/python3','-B',cfg['C_validator'],'--audit'],7200)
   assert not(out/'HOLD_NO_AUTOMATIC_RETRY.json').exists();review=rd(final);assert review['schema']==cfg['C_required_schema']and review['status']=='PASS'and review['independent_verification_passed']is True and review['all32_candidates_accounted_verified']is True
   assert review['Root_signoff']is False and review['manuscript_signoff']is False and review['old_Goal_completion']is False;manifest(out/'MANIFEST.json')
   # Source data is terminal and immutable; generated analysis remains scoped to eight inputs.
   state('FINAL_CPU_MECHANISM_AND_FIGURES_NO_NEW_SIMULATIONS')
   command('FINAL_MECHANISM',['/usr/bin/python3','-B',cfg['mechanism_source'],'--provider',str(S/'FINAL_B3_PROVIDER.fixed.json'),'--output-dir',cfg['mechanism_output']],3600)
   figure_run=command('FINAL_FIGURES',[cfg['figure_python'],'-B',cfg['figure_source'],'--provider',str(S/'FINAL_B3_PROVIDER.fixed.json'),'--provider-sha256',sha(S/'FINAL_B3_PROVIDER.fixed.json'),'--output-root',cfg['figure_output']],900)
   figure_result=json.loads(figure_run.stdout.strip().splitlines()[-1]);fig=Path(figure_result['output']);assert fig.resolve().is_relative_to(Path(cfg['figure_output']).resolve())
   mech=Path(cfg['mechanism_output']);manifest(mech/'MANIFEST.json');manifest(fig/'MANIFEST.json')
   packets=[packet(out/'MANIFEST.json','independent_reviews/C_final_structure32_v1'),packet(mech/'MANIFEST.json','final_analysis/B_mechanisms_v1'),packet(fig/'MANIFEST.json','final_analysis/figures_v1')]+cfg['static_final_packets']
   audit=Path(cfg['first4_gate_output']).parent/'MANIFEST.json'
   if audit.exists():packets.append(packet(audit,'first4_execution/C_full_terminal_gate_v1'))
   put(PUB/'approved_additions/900_FINAL_INDEPENDENT_SCIENCE_AND_ANALYSIS.json',dict(Root_report_publication_only=True,packets=packets),True)
   put(PUB/'FINAL_C_REVIEW_PUBLICATION_READY.json',dict(final_review_path=str(final),final_review_sha256=sha(final),public_final_review_relative_path='independent_reviews/C_final_structure32_v1/FINAL_REVIEW.json',actual_C_process_returncode=0,full_final_manifest_sha256=sha(out/'MANIFEST.json'),visual_review='GENERATED_DRAFT_REQUIRES_ROOT_VISUAL_SIGNOFF',new_simulations=0,oldGoal_unchanged=True),True)
   if not(PUB/'REQUEST_PUBLISH.json').exists():put(PUB/'REQUEST_PUBLISH.json',dict(UTC=stamp(),reason='Final C independent audit plus complete eight-input structure analysis and draft figures; no new science'),True)
   state('FINAL_EVIDENCE_READY_AWAIT_REPORT_ONLY_GIT_PUBLICATION',C_review_sha256=sha(final),Root_narrative_visual_and_total_Goal_signoff_not_implied=True);return
if __name__=='__main__':
 try:main()
 except BaseException:
  state('FINAL_CPU_CHAIN_HOLD_NO_AUTOMATIC_RETRY',traceback=traceback.format_exc(),model_retries=0)
  raise
