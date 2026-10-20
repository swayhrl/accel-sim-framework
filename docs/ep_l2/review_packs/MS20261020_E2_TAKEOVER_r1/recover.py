"""One-shot read-only E2 takeover and producer verification; no native execution."""
import sys,json,time,subprocess,hashlib,socket,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
P=Path(__file__).resolve().parent
A=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1')
AP=A/'docs/ep_l2/review_packs/MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1'
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def ref(path):return dict(path=str(path),sha256=c.digest(path))
def main():
 coord=c.Coordinator();s=coord.snapshot();d=json.loads((c.SHARED/'RUN_REGISTRY.json').read_text());assert s['actual_starts']==7
 assert not git(ROOT,'status','--porcelain','--untracked-files=no')
 active={k:{i:r for i,r in d[k].items() if r['status'] in c.ACTIVE} for k in ['runs','resource_leases']}
 assert not any(active.values());assert s['controller']['state']=='STOPPED'
 retired=[]
 for proc in [s['controller']['process']]+[a.get('process') for a in s['attempts'] if a.get('process')]:
  try: live=c.process_identity(proc['pid'])==proc
  except (FileNotFoundError,ProcessLookupError):live=False
  assert not live;retired.append(dict(expected=proc,same_process_live=live))
 heads={b:git(ROOT,'ls-remote','origin','refs/heads/'+b).split()[0] for b in ['hrl/ep-l2-ms20261019-e-eval-v1','hrl/ep-l2-ms20261019-a-core-v1']}
 assert heads['hrl/ep-l2-ms20261019-e-eval-v1']==git(ROOT,'rev-parse','HEAD')
 release=json.loads((AP/'RELEASE.json').read_text());source=release['source_identity'];assert release['producer_release_complete']
 published='44ebe13890c8e0402895e890cf2000d01513f836';remote=[]
 for f in AP.glob('*'):
  if not f.is_file():continue
  rel=f.relative_to(A).as_posix()
  blob=subprocess.check_output(['git','-C',str(ROOT),'show',heads['hrl/ep-l2-ms20261019-a-core-v1']+':'+rel])
  assert hashlib.sha256(blob).hexdigest()==c.digest(f),rel
  remote.append(rel)
 assert git(ROOT,'merge-base','--is-ancestor',published,heads['hrl/ep-l2-ms20261019-a-core-v1'])==''
 verified=json.loads(subprocess.check_output([sys.executable,'-B',str(AP/'verify_release.py')],text=True))
 core=release['production_source_path'];fw=release['runtime_framework_path'];vendor=release['vendor_path']
 identities={}
 for name,repo,expected in [('core',core,source['core_source_commit']),('framework',fw,source['framework_source_commit']),('vendor',vendor,source['vendor_pybind11_commit'])]:
  assert git(repo,'rev-parse','HEAD')==expected
  tracked=git(repo,'status','--porcelain','--untracked-files=no');assert not tracked,(name,tracked)
  identities[name]=dict(path=repo,HEAD=expected,tracked_status='CLEAN',untracked_status=git(repo,'status','--porcelain'))
 assert c.digest(release['binary_path'])==source['binary_sha256']
 build=json.loads((AP/'BUILD_PROVENANCE.json').read_text());archive=release['production_archive']['path'];members={}
 for name,row in build['archive_members'].items():
  blob=subprocess.check_output(['ar','p',archive,name]);sha=hashlib.sha256(blob).hexdigest();assert sha==row['new_sha256']
  members[name]=sha
 delta=git(core,'diff','27ec10bda848e4929181c60a7cbb40d6b007945c',source['core_source_commit'],'--','src','libcuda','CMakeLists.txt')
 (P/'PRODUCTION_DELTA.patch').write_text(delta+'\n')
 usage=c.output_usage();resources=c.local_resources();buckets=collections.Counter(c.policy_v2.charged_bucket(a,s['reservations']) for a in s['attempts'] if a.get('actual_start'))
 receipt=dict(schema='E2_CONTINUOUS_CAMPAIGN_TAKEOVER_V1',lane='E2',at_unix=time.time(),host=socket.gethostname(),uid=__import__('os').getuid(),execution_environment='original174',E_HEAD_before_takeover=git(ROOT,'rev-parse','HEAD'),remote_heads=heads,worktree=str(ROOT),uncommitted_at_entry='CLEAN',active_global=active,retired_process_checks=retired,controller=s['controller'],T0=s['t0_unix'],actual_starts=7,maximum_actual_starts=40,remaining=33,budget_buckets=dict(buckets),contingency_remaining=3,start_deadline_unix=s['start_deadline_unix'],intake_deadline_unix=c.INTAKE_DEADLINE,output_usage=usage,output_caps=dict(new_bytes=6*c.GIB,total_bytes=20*c.GIB),resources=resources,disk_policy=coord.work_disk_policy(),scientific_holds=s['scientific_holds'],attempts=[dict(attempt_id=a['attempt_id'],state=a['state'],actual_start=a.get('actual_start'),budget_bucket=c.policy_v2.charged_bucket(a,s['reservations']),result_directory=a['result_directory']) for a in s['attempts']],CLIENT=ref(c.HANDOFF/'CLIENT_CONTRACT.json'),tooling_source=c.tooling_binding(),parser_identity=ref(Path(json.loads((c.HANDOFF/'CLIENT_CONTRACT.json').read_text())['terminal_adapter'])),source_identity=source,source_worktrees=identities,main=ref(Path(release['binary_path'])),archive=release['production_archive'],A2_formal_release=ref(AP/'RELEASE.json'),A2_release_publication=published,A2_remote_blobs_verified=remote,A2_readonly_verification=verified,archive_member_hashes=members,no_new_goal_budget_or_controller=True,new_compiles=0,new_native_runs=0,new_application_starts=0,status='TAKEOVER_COMPLETE_A2_FORMAL_RELEASE_AVAILABLE_INDEPENDENT_OFF_NEXT',dependency='A2 formal publication is now present and independently read back; source-specific OFF and original11+7 gates remain required before Conv S/F. Reuse applicable E17/26 evidence; no replay.')
 c.write_json(P/'RECEIPT.json',receipt)
 print(json.dumps({k:receipt[k] for k in ['status','host','remote_heads','actual_starts','contingency_remaining','resources','output_usage']}))
if __name__=='__main__':main()
