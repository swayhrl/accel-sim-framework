"""Main-only preparation helper. Reads fresh formal specs, never registers or starts."""
from pathlib import Path
import hashlib,json
J=Path("/root/data/ep_l2_full_workload_performance_20261027_v1")
V=J/"research/performance_first_v3_20261104_v1";ACT=V/"activation_20261104_v1";C=ACT/"control"
def ref(p):
 p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def build():
 a=json.loads((C/"USER_AUTHORIZATION.json").read_text())
 groups={};points=[]
 for f in a["families"]:
  g=f["name"];root=Path(f["data_root"]);entry=root.parent/"bin"/("native_midtag_v3"if g=="midtag"else"native_vector1700_v3")
  groups[g]=dict(request_id=f["request_id"],budget=f["budget"],data_root=str(root),runtime_root=str(ACT/"runtimes/midtag"if g=="midtag"else ACT/"agent_b_formal/runtime"),native_entry_ref=ref(entry),authorization_ref=ref(root/"control/USER_AUTHORIZATION.json"))
  for c in f["allowed_cohorts"]:
   points.append(dict(cohort=c,group=g,spec_ref=ref(root/"cases"/c/"control/FROZEN_SPEC.json")))
 base=J/"execution_performance_first_20261103_v1/control"
 return dict(schema="EP_MAIN_PFV3_AUTHORIZED10_EXECUTION_MANIFEST_V1",control_root=str(C),
  new_model_start_ceiling=10,authorized_max_concurrent_models=10,automatic_retry=False,refund=False,
  user_authorization_ref=ref(C/"USER_AUTHORIZATION.json"),groups=groups,points=points,
  global_admission_lock=str(base/"ADMISSION.lock"),runtime_global_restore_lock=str(base/"ARCHIVE_SHARED_WINDOW.lock"),
  accept_serial_lock=str(C/"MAIN_ACCEPT_SERIAL.lock"),host_cpu_candidates=list(range(512)),
  admission_wait_and_execution_wall_seconds=7*86400,
  publication=dict(repo=str(V/"review"),branch="hrl/ep-l2-performance-first-v3-20261104-v1",
   relative_directory="docs/ep_l2/operations/ep_performance_first_v3_20261104_v1/activation_20261104_v1/execution"),
  summary_archive_root="/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_performance_first_v3_20261104_v1/execution_summaries")
if __name__=="__main__":print(json.dumps(build(),indent=2))
