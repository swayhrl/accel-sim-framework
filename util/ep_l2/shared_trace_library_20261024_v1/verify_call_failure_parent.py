"""Preserve a native exit0 that failed semantic execution; never relabel it PASS."""
from pathlib import Path
import sys,json,hashlib,re
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy as e
B=Path('/root/data/ep_l2_main_ada_call_compat_20261024_v1');O=B/'run/1bbdd38370474a1ea567a6cf53fcd6ca'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B/'control/FROZEN_SPEC.json')=='d44b73b8283a4ccfb9ba481a267ee615519ef224d34584296396f40ee9a6470d'
s=json.loads((B/'control/FROZEN_SPEC.json').read_text());result=json.loads((O/'EXIT.json').read_text())
for p,digest in s['pinned_files'].items():assert sha(p)==digest
assert result['exit_code']==0 and result['stop_reason'] is None and result['application_attempt_consumed']==1 and result['native_observed']
raw=(O/'raw.log').read_text();assert sha(O/'raw.log')==result['raw_sha256']
assert re.findall(r'^gpu_tot_sim_insn\s*=\s*(\d+)',raw,re.M)==['0']
assert re.findall(r'^gpgpu_n_mem_const\s*=\s*(\d+)',raw,re.M)==['0']
decoded=[l for l in raw.splitlines() if l.startswith('ADA8_DECODE ')]
assert len(decoded)==75
proof={'status':'PARENT_INDEPENDENT_CANDIDATE_FAILURE_RETAINED','native_exit_code':0,'decoded_uops':75,'actually_issued_active_lane_uops':0,'expected_active_lane_uops':1932,'actual_constant_requests':0,'pinned_files_rehashed':len(s['pinned_files']),'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'raw_sha256':sha(O/'raw.log'),'scientific_qualification_granted':False,'application_attempt_consumed':1,'budget_refunded':False,'root_cause_evidence':'Distinct corrected Core64 case passes; this original candidate keeps its zero-issue failure unchanged'}
(O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json').write_text(json.dumps(proof,indent=2)+'\n')
dest=e.NAS/'rtx4080_sm89/bulk_20261024_v1/objects/stage_evidence_ada8_174new_20261024_v1/PARENT_FAILED_CANDIDATE_JOIN.json'
e.publish_bytes(dest,e.canon(proof),e.v9());print(json.dumps(proof))
