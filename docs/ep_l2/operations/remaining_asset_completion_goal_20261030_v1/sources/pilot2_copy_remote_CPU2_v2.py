"""Exact2pair COPY phases, Root-inherited resource channel; unchanged reviewed wholeSHA transfer."""
from pathlib import Path
import os,sys,json,resource,time,signal,hashlib,shutil
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D));import pilot2_common_v1 as C
def main():
 C.need(len(sys.argv)==3,'SCOPE_PATH_RAW_SHA');a=C.scope(Path(sys.argv[1]),sys.argv[2],'ROOT_APPROVED_PILOT2_COPY_PHASE_V1');C.need(a['phase']in ['ORDINARY','DERIVED'],'COPY_PHASE_ONLY')
 C.need(a['remote_boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'CURRENT_REMOTE_BOOT');C.need(a['remote_runtime_root']==str(D),'EXACT_REMOTE_RUNTIME')
 C.need(a['CPU_ids']==[2],'EXACT_COPY_CPU2_SINGLE');os.nice(15);os.sched_setaffinity(0,{2});resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 R=C.module('cpu1_repeat_nas_resource_v1.py');cg=R.service();C.need(str(cg).endswith('/ep-pilot2-copy-'+a['run_id']+'.service'),'EXACT_OWN_CGROUP')
 Wire=C.module('ssh_stdin_light_control_v2.py');reader=Wire.RemoteReader(0,sys.argv[2],a['run_id']).start();reader.wait_ready()
 out=D/'runs'/a['run_id'];out.mkdir(parents=True,exist_ok=False);C.put(out/'START.json',dict(owner=[os.getpid(),Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]],scope_sha256=sys.argv[2],cgroup=str(cg)))
 H=C.module('reviewed_copy_primitives.py');Alias=C.module('existing_st_alias_guard_reused_v1.py');Alias.exact_existing_ST_alias(a,H);objects=[];error=None
 def checkpoint():
  reader.check();C.need(time.time()<a['absolute_deadline_unix'],'SIGNED_DEADLINE');C.need(shutil.disk_usage(D).free>=5*2**30+64*2**20+sum(r['logical_bytes']for r in C.rows()),'NAS_ACTUAL_FLOOR_PLUS_EXACT_PENDING');v=R.fresh(cg,28*2**30);C.need(v['PASS'],'REAL_RAM_OOM_PSI');return v
 def alarm(*_):raise TimeoutError('ABSOLUTE_COPY_DEADLINE')
 signal.signal(signal.SIGALRM,alarm);signal.alarm(max(1,int(a['absolute_deadline_unix']-time.time())))
 try:
  checkpoint();selected=[r for r in C.rows()if r['kind']==('FULL_APPLICATION_TRACE'if a['phase']=='ORDINARY'else'DERIVED_COMPLETE_CTA_TRACE')]
  if a['phase']=='DERIVED':C.need(a.get('Root_parent_independent_acceptance_ref')is not None,'ROOT_ACTUAL_PARENT_ACCEPTANCE_REQUIRED');C.pinned(a['Root_parent_independent_acceptance_ref'])
  for r in selected:
   checkpoint();m=C.pinned(r['manifest_ref']);plan=C.pinned(r['sender_plan_ref']);sources=plan['sources'];parent=None
   C.need(set(sources)=={x['path']for x in m['files']},'EXACT_SENDER_SET');H.member_rows(m)
   if a['phase']=='DERIVED':
    parentid=r['asset_id'].replace('_DERIVED_CTA_STRIDE40_V1','_ORDINARY_V1');par=D/'committed'/parentid
    parent=C.bind_parent(parentid,C.raw(par/'COMMIT.json'),C.raw(par/'MANIFEST.json'))
    expected=a['parents_by_asset'][r['asset_id']];C.need(parent==expected,'ROOT_EXACT_REAL_PARENT_NOT_PREDICTED')
    prep=out/('bound_'+r['asset_id']);prep.mkdir()
    asset=json.loads(C.raw(C.alias(sources['ASSET.json'])));asset.update(parent)
    receipt=json.loads(C.raw(C.alias(sources['DERIVED_VALIDATION.json'])));asset['kernels']=[dict(name=x['kernel'],selected_ctas=x['selected_CTAs'],records=x['selected_records'])for x in receipt['results']]
    C.put(prep/'ASSET.json',asset);C.put(prep/'PARENT_INPUT_REFERENCE.json',dict(parent,input_members=[],input_payload_duplicate_bytes=0))
    sources=dict(sources);sources.update({'ASSET.json':str(prep/'ASSET.json'),'PARENT_INPUT_REFERENCE.json':str(prep/'PARENT_INPUT_REFERENCE.json')})
    m=dict(m);m['files']=[dict(path=n,bytes=C.alias(s).stat().st_size,sha256=H.whole_sha(C.alias(s),a['absolute_deadline_unix'])[1])for n,s in sorted(sources.items())];m['logical_bytes']=sum(x['bytes']for x in m['files']);m.update(parent)
   target=D/'committed'/r['asset_id'];C.need(not target.exists(),'PARTIAL_OR_EXISTING_OBJECT_ROOT_RECONCILIATION');target.mkdir(parents=True)
   for row in H.member_rows(m):checkpoint();H.transfer(C.alias(sources[row['path']]),target/row['path'],row,a['absolute_deadline_unix'])
   C.put(target/'MANIFEST.json',m);mh=C.h(C.raw(target/'MANIFEST.json'));H.verify_members(target,mh,a['absolute_deadline_unix']);checkpoint()
   commit=dict(schema='RTX4080_ENGINEERING_PILOT_COMMIT_V1',asset_id=r['asset_id'],kind=m['kind'],status='COMMITTED_VERIFIED',manifest_sha256=mh,object_id=C.h((r['asset_id']+':'+mh).encode()),files=len(m['files']),logical_bytes=m['logical_bytes'],profile_use=C.PURPOSE,source_keep=True,release_bytes=0,producer_sha256='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73',original_worker_success=False,actual_all_DSO_mapping_coverage='UNKNOWN_NOT_PERSISTED',consumer_qualification='NOT_GRANTED_BY_COPY',Root_archive_scope_sha256=sys.argv[2])
   if parent:commit.update(parent)
   C.put(target/'COMMIT.json',commit);C.need(json.loads(C.raw(target/'COMMIT.json'))==commit,'CLOSED_COMMIT_READBACK');objects.append(dict(asset_id=r['asset_id'],kind='ordinary'if a['phase']=='ORDINARY'else'derived',commit_ref=C.ref(target/'COMMIT.json'),manifest_ref=C.ref(target/'MANIFEST.json'),object_id=commit['object_id']))
  C.put(out/'COPY_RESULT.json',dict(status='EXACT_TWO_PRIVATE_OBJECTS_WHOLESHA_COMMITTED',phase=a['phase'],objects=objects,scope_sha256=sys.argv[2]))
 except BaseException as e:error=repr(e);C.put(out/'FAILED_RETAINED.json',dict(error=error,no_retry_or_rollback=True));raise
 finally:
  signal.alarm(0);reader.finish_after_owned_closed();C.put(out/'RESOURCE_AND_CLOSURE.json',dict(owner=[os.getpid(),Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]],scope_sha256=sys.argv[2],cgroup=str(cg),tracked_children=[],reader_joined=True,error=error))
if __name__=='__main__':main()
