"""CPU fixture only, running the exact proposed production process guard."""
from common import *
from freeze_static import freeze_executable
from guarded_process import run_guarded
import copy

def main():
 target=BUILD/'ag3-cpu-production-wrapper';library=BUILD/'combined-final'
 manifests={};metadata={}
 for path in [target,Path('/usr/bin/dash'),Path('/usr/bin/cat')]:
  manifest,objects=freeze_executable(path,library);manifests[manifest['target']]=manifest;metadata[manifest['target']]=objects
 dest=RAW/'cpu-qualification/production-wrapper-qualified-final';dest.mkdir(parents=True,exist_ok=False)
 write(dest/'PREREGISTRATION.json',dict(manifests=manifests,static_metadata=metadata,guard_sha256=sha(PACK/'tools/guarded_process.py'),mapping_role_sha256=sha(PACK/'tools/mapping_roles.py'),before_any_CPU_target=True,simulator_starts=0),exclusive=True)
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',LD_LIBRARY_PATH=str(library),CUDA_VISIBLE_DEVICES='')
 results=[]
 for label,args,expected,timeout in [('positive',[],True,30),('unknown_file',['unknown'],False,30),('writable_loader_data',['writablecache'],False,30),('timeout',['hang'],False,1)]:
  result=run_guarded([str(target),*args],env,manifests,dest/label,'CPU_FIXTURE',timeout)
  results.append(dict(case=label,expected_success=expected,result=result));write(dest/'RESULTS_IN_PROGRESS.json',results)
  assert (result['status']=='PASS_GUARDED_NATURAL_EXIT0')==expected,(label,result)
 write(PACK/'PRODUCTION_WRAPPER_CPU.json',dict(status='PASS_INITIAL_PRODUCTION_GUARD_CPU_CASES',cases=results,manifests=manifests,guard_sha256=sha(PACK/'tools/guarded_process.py'),simulator_starts=0))
 print(json.dumps(dict(status='PASS_INITIAL_PRODUCTION_GUARD_CPU_CASES',cases=len(results),simulator_starts=0)))
if __name__=='__main__':main()
