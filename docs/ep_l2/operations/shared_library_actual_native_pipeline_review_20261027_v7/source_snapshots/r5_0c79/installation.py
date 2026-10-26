"""Controlled future-only delegate installer. No Source/controller/trace modification."""
from pathlib import Path
import os,sys,json,hashlib,fcntl,time
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(x):return hashlib.sha256(x).hexdigest()
def need(x,msg):
 if not x:raise RuntimeError('RESOURCE_HOLD_BINDING_INSTALL_'+msg)
NAMES=dict(resume='run_goal.py',publish='publish_library.py',cross='cross_project_validate.py',restore='restore_all_windows.py',finish='finish_report.py')
MARKERS=dict(publish='LIBRARY_PUBLICATION.json',cross='CROSS_PROJECT_VALIDATION.json',restore='BOUNDED_NATIVE_RESTORE_COMPLETE.json',finish='FINAL_VALIDATION.json')
def delegate(stage,phase,spec_path,spec_sha,phase_sha):
 return ("""#!/usr/bin/python3
from pathlib import Path
import os,sys,hashlib
p=Path(%r)
with p.open('rb')as f:raw=f.read(8*2**20+1)
if len(raw)>8*2**20 or hashlib.sha256(raw).hexdigest()!=%r:raise RuntimeError('RESOURCE_HOLD_BINDING_V3_PHASE_PIN')
env={k:v for k,v in os.environ.items()if k not in ['LD_PRELOAD','LD_LIBRARY_PATH','CUDA_INJECTION64_PATH','TRACES_FOLDER','PYTHONHOME','PYTHONPATH','VIRTUAL_ENV','CONDA_PREFIX']}
os.execve('/usr/bin/python3',['/usr/bin/python3','-I','-S','-B',str(p),'--stage',%r,'--integration-spec',%r,'--spec-sha256',%r],env)
"""%(str(phase),phase_sha,stage,str(spec_path),spec_sha)).encode()
def install(r,spec_path,spec_sha,approval_ref,dry_run=True):
 raw=r.bounded_metadata_raw(spec_path);need(digest(raw)==spec_sha,'SPEC')
 spec=json.loads(raw);profile=r.profile();code=r.verify_package()
 approval_raw=r.bounded_metadata_raw(approval_ref['path']);need(digest(approval_raw)==approval_ref['sha256'],'INSTALL_APPROVAL_REF')
 approval=json.loads(approval_raw);need(approval['status']=='ROOT_APPROVED_EXACT_FUTURE_DELEGATE_INSTALLATION'and approval['spec_sha256']==spec_sha and approval['code_version_id']==code['code_version_id'],'ROOT_APPROVAL')
 need(spec['code_version_id']==code['code_version_id']and spec['suite_complete']is True,'COMPLETE_CODE_SUITE')
 goal=Path(spec['legacy_goal_root'])
 need(profile['execution_scope']=='QUALIFICATION'or str(goal)=='/root/data/shared_sm70_trace_library_20261024_v1','OWNED_DATA_GOAL_SCOPE')
 # Installation is a closed old-owner boundary. COPY_ONLY continuations may live; old run_goal may not.
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   cmd=(proc/'cmdline').read_bytes().split(b'\0');row=(proc/'stat').read_text().rsplit(')',1)[1].split()
  except (FileNotFoundError,ProcessLookupError):continue
  need(row[0]in['Z','X','x']or str(goal/'tools/run_goal.py').encode()not in cmd,'OLD_RUN_GOAL_OWNER_MUST_EXIT_NATURALLY')
 tools=goal/'tools';control=goal/'control';phase=r.PACKAGE/'phase_r5.py';phase_sha=digest(r.bounded_metadata_raw(phase,8*2**20))
 need(profile['execution_scope']=='QUALIFICATION'or(phase.resolve().is_relative_to(Path(profile['nas_mount_root']))and Path(spec_path).resolve().is_relative_to(Path(profile['nas_mount_root']))),'PUBLIC_CODE_SPEC_ONLY')
 for row in spec['unchanged_source_pins']:
  need(digest(r.bounded_metadata_raw(row['path']))==row['sha256'],'UNCHANGED_SOURCE_PIN')
 preimages={}
 for stage,name in NAMES.items():
  path=tools/name;old=r.bounded_metadata_raw(path);need(digest(old)==approval['expected_old_tools'][str(path)],'OLD_TOOL_PREIMAGE');preimages[stage]=old
 marker_preimages={}
 for stage,name in MARKERS.items():
  path=control/name
  if os.path.lexists(path):
   old=r.bounded_metadata_raw(path);need(digest(old)==approval['expected_old_markers'].get(str(path)),'OLD_MARKER_PREIMAGE');marker_preimages[stage]=old
 result=dict(status='REVIEWED_FUTURE_ONLY_INSTALL_PLAN',spec_sha256=spec_sha,code_version_id=code['code_version_id'],old_tools={s:digest(x)for s,x in preimages.items()},old_markers={s:digest(x)for s,x in marker_preimages.items()},source_signals=0,source_engine_unchanged=True,public_CURRENT_not_changed=True)
 r.load_verified('stages_r5').admission(r,spec,spec_sha)
 need(sum(len(delegate(stage,phase,spec_path,spec_sha,phase_sha))for stage in NAMES)<=65536,'EXACT_NATIVE_DELEGATE64KIB')
 if dry_run:return result
 resources=r.load_verified('stages_r5').control_resources(r,spec,spec_sha);resources.check(True);storage=r.load_verified('storage');primitive=r.load_verified('primitive');writer=storage.Writer(r.library_root(),resources,primitive)
 work=Path(profile['native_work_root']);work.mkdir(parents=True,exist_ok=True)
 lock=(work/'FUTURE_DELEGATE_INSTALL.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old_owner=None
 try:
  old_owner=(control/'SUPERVISOR.lock').open('a+b')
  fcntl.flock(old_owner,fcntl.LOCK_EX|fcntl.LOCK_NB)
  primitive.no_symlinks(tools);primitive.no_symlinks(control)
  for proc in Path('/proc').iterdir():
   if not proc.name.isdigit():continue
   try:cmd=(proc/'cmdline').read_bytes().split(b'\0');row=(proc/'stat').read_text().rsplit(')',1)[1].split()
   except (FileNotFoundError,ProcessLookupError):continue
   need(row[0]in['Z','X','x']or str(goal/'tools/run_goal.py').encode()not in cmd,'LIVE_OLD_OWNER_POSTLOCK')
  for stage,name in NAMES.items():need(r.bounded_metadata_raw(tools/name)==preimages[stage],'TOOL_CHANGED_BEFORE_LOCK')
  for row in spec['unchanged_source_pins']:need(digest(r.bounded_metadata_raw(row['path']))==row['sha256'],'SOURCE_CHANGED_BEFORE_LOCK')
  # Immutable preimages are durably on public NAS before any future path changes.
  refs={s:writer.cas(raw,'receipts/future_delegate_preimages')for s,raw in preimages.items()}
  marker_refs={s:writer.cas(raw,'receipts/future_marker_preimages')for s,raw in marker_preimages.items()}
  history=control/'BINDING_V3_TRANSITION_HISTORY'/spec['integration_id'];history.mkdir(parents=True,exist_ok=True)
  for stage in marker_preimages:
   path=control/MARKERS[stage];need(digest(r.bounded_metadata_raw(path))==digest(marker_preimages[stage]),'MARKER_CHANGED_DURING_INSTALL')
   dest=history/(MARKERS[stage]+'.preserved')
   need(not dest.exists(),'MARKER_HISTORY_COLLISION');primitive.rename_noreplace(path,dest)
  # Publish goes first. Every delegate requires complete sealed package+Root activation+archive closure.
  for stage in ['publish','cross','restore','finish','resume']:
   target=tools/NAMES[stage];need(r.bounded_metadata_raw(target)==preimages[stage],'TOOL_CHANGED_DURING_INSTALL')
   new=delegate(stage,phase,spec_path,spec_sha,phase_sha);temp=target.with_name('.'+target.name+'.binding-v3-'+str(os.getpid()))
   with temp.open('xb')as f:f.write(new);f.flush();os.fsync(f.fileno())
   temp.chmod(0o555);os.replace(temp,target);primitive.fsync_dir(target.parent)
   need(r.bounded_metadata_raw(target)==new,'DELEGATE_CLOSED_BYTES')
  for row in spec['unchanged_source_pins']:need(digest(r.bounded_metadata_raw(row['path']))==row['sha256'],'SOURCE_CHANGED_POSTINSTALL')
  result.update(status='INSTALLED_EXACT_FUTURE_DELEGATES_ACTIVATION_STILL_GUARDED',preimage_refs=refs,marker_preimage_refs=marker_refs)
  writer.json('receipts/future_delegate_installs/'+spec['integration_id']+'.json',result)
  return result
 finally:
  if old_owner is not None:fcntl.flock(old_owner,fcntl.LOCK_UN);old_owner.close()
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
