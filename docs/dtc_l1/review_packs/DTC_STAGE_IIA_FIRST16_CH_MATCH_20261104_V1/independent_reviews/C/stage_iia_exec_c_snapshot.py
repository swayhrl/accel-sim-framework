from pathlib import Path
import os,json,hashlib,datetime,collections
B=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');O=B/'agents/C';O.mkdir(parents=True,exist_ok=True);T=Path('/root/data/dtc_main_v100_sweep_20261025_v1');R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=Path('/root/data/ep_l2_dtc_l1_native_v2');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();lease=json.loads((T/'control/BATCH_LEASE.json').read_text());pid=lease['pid'];p=Path('/proc')/str(pid)
parents={};cmd={}
for pp in Path('/proc').iterdir():
 if pp.name.isdigit():
  try:
   s=(pp/'stat').read_text().rsplit(')',1)[1].split();parents[int(pp.name)]=int(s[1]);v=(pp/'cmdline').read_bytes()
   if b'accel-sim.out' in v:cmd[int(pp.name)]=v.decode(errors='replace').replace('\0',' ')
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
owned=[]
for model in cmd:
 cur=model
 for _ in range(40):
  if cur==pid:owned.append(model);break
  if cur<=1 or cur not in parents:break
  cur=parents[cur]
qpath=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';epath=N/'control/CURRENT_SCIENCE_EPOCH.json';reg=json.loads(qpath.read_text());epoch=json.loads(epath.read_text());q=reg['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];batch=json.loads((R/'analysis/BATCH_STATE.json').read_text());srcs=[T/'tools/sweep_native_cap1m.py',T/'tools/sweep_controller.py',R/'tools/l2_parent_addon.py',R/'tools/l2_native.py',N/'bin/native',N/'tools/native_v2.py'];sources=[{'path':str(x),'sha256':sha(x)} for x in srcs]
d={'schema':'DTC_STAGE_IIA_C_READONLY_OWNER_PREFLIGHT_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'READ_ONLY_NO_AUTHORITY_WRITE_NO_MODEL','lease':lease,'actual_owner_start_ticks':int((p/'stat').read_text().rsplit(')',1)[1].split()[19]),'actual_lease_fd_target':os.readlink(p/'fd'/str(lease['fd'])),'actual_lease_fdinfo':(p/'fdinfo'/str(lease['fd'])).read_text(),'owner_proc_locks':[x for x in Path('/proc/locks').read_text().splitlines() if f' {pid} ' in x],'owned_accel_sim_processes':owned,'old_stageI':{'budget':q['budget'],'consumed':len(q['consumed']),'remaining':q['remaining'],'registry_display_state':q['state'],'BATCH_running':batch['running'],'BATCH_postprocess':batch['postprocess'],'BATCH_active_claims':batch['active_claims'],'residual_claims_do_not_prove_live_model':True},'registry_sha256':sha(qpath),'epoch_sha256':sha(epath),'registry_epoch_hash_match':epoch['native_registry_sha256']==sha(qpath),'old_request_canonical_sha256':hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'source_pins':sources,'full_approved_plan_commit':'5001c3f35052f7f91f1ad41eeff83f2947a0878d','new_contract_qualification':'PENDING_ROOT_PACKAGE_NOT_YET_REVIEWED'}
(O/'OWNER_AND_NATIVE_PATTERN_READONLY.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'owner':pid,'start':d['actual_owner_start_ticks'],'owned_models':owned,'legacy_display_claims':batch['active_claims'],'sources':sources},indent=2))
