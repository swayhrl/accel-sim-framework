from pathlib import Path
import json,hashlib,importlib.util
C=Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');Q=C.parent/'stencil768_control_accounting_A1';assert not Q.exists();Q.mkdir();(Q/'control').mkdir();(Q/'WORK').mkdir()
f=C/'stencil768_common_v2.py';s=importlib.util.spec_from_file_location('u',f);u=importlib.util.module_from_spec(s);s.loader.exec_module(u);u.C=Q/'control';u.WORK=Q/'WORK'
p=u.C/(u.ID+'_POST_EPOCH4_RESOURCE_EVENTS.jsonl');p.write_bytes(b'x'*1048576);(u.WORK/'payload').write_bytes(b'y'*4096);(u.C/'unrelated').write_bytes(b'z'*8192)
usage=u.epoch_native_usage();assert usage=={'work_bytes':4096,'Native_control_bytes':1048576,'total_bytes':1052672}
retired=u.policy(2**60,14763950080,usage['total_bytes'],stage_budget=0);assert retired['PASS'];assert not u.policy(2**60,0,u.LIMIT+1,stage_budget=0)['PASS']
out={'status':'PASS','actual_Native_control_file_bytes':p.stat().st_size,'actual_work_bytes':4096,'usage':usage,'unrelated_excluded':True,'retired_stage_still_reports_existing_controls':True,'retired_stage_limit_plus1_rejected':True,'common_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'GPU_109_SIM_and_scientific_records':0}
r=Q/'QUALIFICATION.json';r.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'path':str(r),'sha256':hashlib.sha256(r.read_bytes()).hexdigest(),'status':'PASS'}))
