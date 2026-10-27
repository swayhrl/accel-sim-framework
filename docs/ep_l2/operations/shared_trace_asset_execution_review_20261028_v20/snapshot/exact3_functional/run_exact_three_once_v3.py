"""Exact3 once launcher: original full R4 forecast, exact own6+SC2+metadata1=9GiB admission, then original tracked watchdog."""
from pathlib import Path
import os,json,hashlib,types,time,subprocess,sys,resource
D=Path(__file__).resolve().parent;G=2**30
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 with Path(p).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def need(v,m):
 if not v:raise RuntimeError('EXACT3_ONCE:'+m)
def load(ref,name):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'source drift '+str(p));m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def main():
 need(sys.argv[1:]==['--run-reviewed'],'exact reviewed invocation only')
 review=D/'MINIMAL_RUNNER_BINDING_REVIEW_V1.json';rr=json.loads(review.read_text())
 release=D/'ROOT_EXACT_THREE_FUNCTIONAL_RELEASE.json';a=json.loads(release.read_text())
 need(a['status']=='ROOT_EXPLICIT_EXACT_THREE_ONCE_RELEASED' and a['launcher_sha256']==sha(__file__) and a['review_sha256']==sha(review),'exact Root release source/review')
 need(a['asset_ids']==[x['asset_id'] for x in rr['cases']],'only exact three')
 need(time.time()<a['absolute_deadline_unix']<=a['not_before_unix']+2400 and a['not_before_unix']<=time.time(),'finite Root once window')
 need(not(D/'ACTUAL_LAUNCHER_AFTER_EPOCH_READ_START.json').exists(),'once launcher no model retry')
 resource.setrlimit(resource.RLIMIT_AS,(512*2**20,4*G));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,{496});need(os.getpriority(os.PRIO_PROCESS,0)==0,'launcher inherited nice must be0 so original model preexec nice15 remains exact')
 me=dict(pid=os.getpid(),start_ticks=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
 save(D/'ACTUAL_LAUNCHER_AFTER_EPOCH_READ_START.json',dict(identity=me,release_sha256=sha(release),review_sha256=sha(review),launcher_sha256=sha(__file__)))
 O=load(rr['full_R4_gate_ref'],'reviewed_full_R4_gate')
 H=load({'path': '/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/current3_native_cpu_post_prepare_20261028_v1/functional_exact3_prepare_v1/full_r4_coherent_read_v1.py', 'sha256': 'dc62e7cb4a14399bd15e68a5f1f68dfb9c63351a1f26bac8a059aa1484d1d581'},'coherent_full_R4_short_read')
 policy=json.loads(Path(rr['full_R4_gate_policy_ref']['path']).read_text());need(sha(rr['full_R4_gate_policy_ref']['path'])==rr['full_R4_gate_policy_ref']['sha256'],'original gate policy drift')
 memory=O.mod(policy['V9_memory_module_ref']['path'],'original_V9_exact3',policy['V9_memory_module_ref']['sha256']);results=[]
 for case in rr['cases']:
  root=Path(case['case_dir']);policy_path=root/'ROOT_PREPARED_POLICY.json';cp=json.loads(policy_path.read_text())
  for key in ['runner_ref','watcher_ref','pins_ref','policy_ref']:need(sha(case[key]['path'])==case[key]['sha256'],'case source drift '+key)
  old=H.collect(O,policy)
  # Reuse original complete foreign forecast and same kernel snapshot, replace only the requested combined own reservation.
  snap=old['kernel_snapshot'];foreign=old['foreign_observation']['additional_active_RAM_commitments_bytes']
  own=cp['own_total_planning_bytes'];peers=cp['peer_SC_bridge_reserved_bytes']+cp['metadata_reserved_bytes'];need(own==6*G and peers==3*G,'exact own and peers')
  verdict=memory.evaluate(snap,foreign,own+peers,'native174')
  gate=dict(schema='EXACT3_FULL_R4_FUNCTIONAL_OWN6_PLUS_SC2_METADATA1_V1',status='PASS' if old['status']=='PASS' and verdict['status']=='PASS' else 'HOLD',original_complete_R4_observation=old,exact_functional_verdict=verdict,own_functional6_bytes=own,SC_bridge2_plus_metadata1_bytes=peers,combined_once9_bytes=own+peers,foreign_registry_or_budget_modified=False,unix=time.time())
  save(root/'FRESH_FULL_R4_EXACT9_ADMISSION.json',gate);need(gate['status']=='PASS','fresh full R4 exact own9 resource admission HOLD')
  deadline=min(time.time()+cp['outer_max_seconds'],a['absolute_deadline_unix']);need(deadline-time.time()>=cp['model_wall_seconds']+30,'Root window too short before one model attempt')
  delegated=dict(status='ROOT_EXPLICIT_EXACT_CURRENT3_ONCE_RELEASED',authority_source='Actual Root exact3 bundle release; this per-case release is delegated by once launcher.',bundle_release_sha256=sha(release),policy_sha256=sha(policy_path),watcher_sha256=case['watcher_ref']['sha256'],runner_sha256=case['runner_ref']['sha256'],pins_sha256=case['pins_ref']['sha256'],absolute_deadline_unix=deadline,asset_id=case['asset_id'],no_retry=True)
  save(root/'ROOT_EXACT_FUNCTIONAL_ONCE_RELEASE.json',delegated)
  out=open(root/'WATCHER.stdout.log','xb');err=open(root/'WATCHER.stderr.log','xb')
  p=subprocess.Popen(['/usr/bin/python3.10','-I','-S','-B',case['watcher_ref']['path']],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,env={'PATH':'/usr/bin:/bin','HOME':'/root','LANG':'C','PYTHONDONTWRITEBYTECODE':'1'})
  ident=dict(pid=p.pid,start_ticks=Path('/proc',str(p.pid),'stat').read_text().rsplit(')',1)[1].split()[19])
  save(root/'ACTUAL_WATCHER_LAUNCH.json',dict(identity=ident,launcher=me,gate_sha256=sha(root/'FRESH_FULL_R4_EXACT9_ADMISSION.json')))
  print('ACTUAL_CASE_START '+json.dumps(dict(name=case['name'],asset_id=case['asset_id'],watcher=ident)),flush=True)
  rc=p.wait();out.close();err.close()
  proc=Path('/proc',str(p.pid));present=proc.exists() and (proc/'stat').read_text().rsplit(')',1)[1].split()[19]==ident['start_ticks'];need(not present,'tracked watcher absent after join')
  terminal=json.loads((root/'WATCHER_TERMINAL.json').read_text()) if (root/'WATCHER_TERMINAL.json').exists() else None
  r=dict(name=case['name'],asset_id=case['asset_id'],watcher_identity=ident,watcher_returncode=rc,watcher_absent=True,watcher_terminal=terminal,stdout_sha256=sha(root/'WATCHER.stdout.log'),stderr_sha256=sha(root/'WATCHER.stderr.log'))
  save(root/'ACTUAL_CASE_JOINED.json',r);results.append(r);print('ACTUAL_CASE_CLOSED '+json.dumps(dict(name=case['name'],returncode=rc,status=terminal['status'] if terminal else 'NO_TERMINAL')),flush=True)
  need(terminal and terminal['all_owned_closed'],'no next case unless all own children closed')
 save(D/'ACTUAL_THREE_FUNCTIONAL_ROUND_RESULT.json',dict(status='ALL_THREE_EXACT_FULL_INPUT_FUNCTIONAL_PASS' if all(x['watcher_returncode']==0 and x['watcher_terminal']['status']=='PASS_EXACT_FULL_INPUT_FUNCTIONAL' for x in results) else 'SOME_FAILED_OR_BOUNDED_INCOMPLETE',results=results,launcher=me,no_auto_retry=True,source_KEEP=True,release_bytes=0,science_or_performance=False))
 return 0 if all(x['watcher_returncode']==0 for x in results) else 2
if __name__=='__main__':sys.exit(main())
