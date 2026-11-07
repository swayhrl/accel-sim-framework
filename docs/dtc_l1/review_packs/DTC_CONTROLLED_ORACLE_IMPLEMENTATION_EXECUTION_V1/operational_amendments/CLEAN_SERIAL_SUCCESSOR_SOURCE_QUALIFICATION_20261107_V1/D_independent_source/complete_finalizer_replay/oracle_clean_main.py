"""Dormant serial-successor bootstrap; ordinary new process, no debugger path.

Default CLI is inert. --runtime needs a separately reviewed complete release,
truthful terminal-old-process evidence and actual four-lock acquisition. This
CPU package intentionally supplies no actual execution release/configuration.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,threading,types
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def need(x,why):
 if not x:raise RuntimeError(why)
def load(ref,name):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p))
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def main(argv=None):
 parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path)
 args=parser.parse_args(argv)
 if args.runtime is None:
  return dict(status='CPU_PREPARATION_ONLY_UNARMED',registrations=0,models=0,production_locks_acquired=0)
 need(threading.current_thread()is threading.main_thread()and sys.dont_write_bytecode,'REAL_CLEAN_MAIN_WITH_BYTECODE_DISABLED')
 release=read(args.runtime);review=read(release['independent_live_review']['path'])
 need(sha(release['independent_live_review']['path'])==release['independent_live_review']['sha256'],'INDEPENDENT_REVIEW_PIN')
 need(release['actual_execution_authorized']is True and review['status']=='PASS_LIVE_SERIAL_CLEAN_SUCCESSOR'
      and review['authority_commit']=='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1','NO_ACTUAL_RELEASE_FROM_CPU_PREPARATION')
 need(release['request']=='DTC_ORACLE_REMAINING24_20261106_V1'and release['budget']==96
      and release['old32_new_starts']==0 and release['CH_new_starts']==0,'EXACT_NEW96_NO_EXTENSION')
 need(review['clean_main_sha256']==sha(__file__)and review['guard_sha256']==release['guard']['sha256']
      and review['runtime_adapter_sha256']==release['runtime_adapter']['sha256']
      and review['RSS_history_adapter_sha256']==release['RSS_history_adapter']['sha256'],
      'ALL_DYNAMIC_COMPONENTS_MUST_BE_INDEPENDENTLY_REVIEWED_BEFORE_LOAD')
 # Review coupling is checked before importing any operational helper.
 guard=load(release['guard'],'CLEAN_MAIN_ACTUAL_GUARD')
 runtime=load(release['runtime_adapter'],'CLEAN_MAIN_REVIEWED_PRIVATE_RUNTIME')
 need(runtime.READINESS=='PASS_CPU_EQUIVALENT_CLEAN_RUNTIME_ADAPTER',
      'COMPLETE_PRIVATE_NATIVE_LAYOUT_RESOURCES_STRICT_SCOPE_NOT_YET_QUALIFIED')
 closed=read(release['original32_closed_proof']['path'])
 need(sha(release['original32_closed_proof']['path'])==release['original32_closed_proof']['sha256'],'ORIGINAL32_PROOF_PIN')
 guard.require_old32_closed(closed)
 # Old artifacts are read-only, not lease inputs for a counterfeit parent.
 for ref in release['immutable_historical_refs']:
  need(sha(ref['path'])==ref['sha256'],'IMMUTABLE_HISTORICAL_BYTES_DRIFT')
 with guard.CleanMainLocks(release['lock_paths'])as locks:
  parent=guard.build_private_lease(dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),locks,closed)
  # The complete adapter must CPU-qualify new root/layout/plan/engine pins before
  # its first registry mutation; install an independent actual management grant.
  # The new private lease uses this process's real PID/start/source/lock FDs.
  return runtime.run_released_new96(release,parent,locks)
if __name__=='__main__':
 print(json.dumps(main(),sort_keys=True))
