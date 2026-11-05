from pathlib import Path
import json,subprocess,hashlib,os
r=Path(__file__).parent;os.nice(15)
plan=json.loads((r/'FINAL_INCREMENTAL_BUILD_PLAN.json').read_text());out=Path(plan['new_build'])/'incarnation_delta.cpu'
cmd=['/usr/bin/c++','-std=c++17','-O0','-g0','-I'+str(r/'core_candidate/src/gpgpu-sim'),str(r/'reclaim_incarnation_exhaustion_delta.cc'),'-o',str(out)]
q=subprocess.run(cmd,capture_output=True,text=True,timeout=20);assert q.returncode==0,q.stderr
q=subprocess.run([str(out)],capture_output=True,text=True,timeout=5);assert q.returncode==0,(q.returncode,q.stderr)
(r/'INCARNATION_EXHAUSTION_DELTA_PASS.json').write_text(json.dumps({'argv':cmd,'returncode':q.returncode,'stdout':q.stdout,'test_only_fault_injection':'UINT64_MAX incarnation','scope':'new reserved reclaim guards only','Core':'0ab3af3d6aecf0e123f7b4fa4bfa85783c99bf8a','old_suite_rerun':False},indent=2)+'\n')
print(q.stdout)
