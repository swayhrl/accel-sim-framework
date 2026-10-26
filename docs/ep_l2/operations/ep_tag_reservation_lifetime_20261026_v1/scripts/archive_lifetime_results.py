#!/usr/bin/env python3
"""Exact two-case, COPY_ONLY held-postrun archival. Never starts a model.

Frozen storage primitives are reused, not old application/source authorities.
No registry update here. Caller closes only its own row after both restores.
"""
import sys
sys.dont_write_bytecode=True
import fcntl,hashlib,importlib.util,inspect,json,os,pathlib,resource,subprocess,uuid
P=pathlib.Path;M=1<<20;G=1<<30
J=P('/root/data/ep_tag_reservation_lifetime_20261026_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
OLD=P('/root/data/ep_l2_main_vector_r5_20261023_v1')
CASES={'EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2','EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2'}
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_application_v2')
RESOURCE_SHA='3074ba6467bb192160e199b49fc8448f46d78ae4c2a18c82c63894511961fe80'
FROZEN_RESULT_SHA='f4c8258ed366f17a07fc241bbb4f088defb3e91aad01e06c48b594c4421687e3'
def need(x,s):
 if not x:raise RuntimeError(s)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(M),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_text())
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put_once(p,v):
 p=P(p)
 if p.exists():need(read(p)==v,'immutable receipt collision '+str(p));return
 with p.open('xb') as f:f.write(canon(v));f.flush();os.fsync(f.fileno())
def closed_case(case):
 need(case in CASES,'unknown exact lifetime case');b=J/'cases'/case;s=read(b/'control/FROZEN_SPEC.json')
 binding=read(b/'control/SPEC_AUTHORIZATION_BINDING.json')
 need(binding['spec_sha256']==sha(b/'control/FROZEN_SPEC.json'),'spec SHA drift')
 need(binding['authorization_sha256']==sha(b/'control/USER_AUTHORIZATION.json'),'authorization SHA drift')
 for path,h in s['pinned_files'].items():need(sha(path)==h,'pinned dependency drift '+path)
 for path,h in s['env_hashes'].items():need(sha(path)==h,'environment/input drift '+path)
 need((b/'control/RESULT_ENGINE_PIN.json').read_bytes()==(OLD/'control/RESULT_ENGINE_PIN.json').read_bytes(),'case storage-engine pin mismatch')
 need(s['cohort']==case and s['application_budget']==1 and s['automatic_retry'] is False,'finite case scope')
 need(s['reserved_write_bytes']==512*M and s['result_cap_bytes']==128*M,'declared held copy envelope')
 need(sha(J/'control/SOURCE_QUALIFICATION_V2.json')=='8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814','frozen exact SourceQ SHA drift')
 sourceq=read(J/'control/SOURCE_QUALIFICATION_V2.json')
 need(sourceq['status']=='SOURCEQ_CPU_PASS_NOT_APPLICATION_ACCEPTED' and sourceq['source_identity']==s['source_identity'],'exact new source Q')
 intent=read(N/'control/qualification_ledger'/(case+'.INTENT.json'));done=read(N/'control/qualification_ledger'/(case+'.DONE.json'));out=P(done['output'])
 need(intent['uuid']==done['uuid'] and out==b/'run/results'/done['uuid'] and read(out/'NATIVE_EXIT.json')==done,'closed exact intent/DONE')
 need(done['cohort']==case and done['new_attempt_consumed']==1 and done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'natural native completion required for accepted archive route')
 need(sha(out/'raw.log')==done['raw_sha256'],'raw drift')
 point=read(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
 need(point['status']=='EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED' and point['cohort']==case and point['uuid']==done['uuid'] and point['raw_sha256']==done['raw_sha256'] and point['source_identity']==s['source_identity'],'independent exact new application acceptance required')
 pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 try:need(int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'same model generation still present')
 except FileNotFoundError:pass
 return b,s,intent,done,out,point
def case_footprint(b,out):
 groups={name:{'logical_bytes':0,'allocated_bytes':0} for name in ('closed_result','temporary_cache','native_restores','metadata_env_help')}
 roots={'temporary_cache':[b/'run/tmp',b/'run/cache'],'native_restores':[b/'run/recovery']}
 files=0
 for parent,dirs,names in os.walk(b,followlinks=False):
  for name in dirs:need(not (P(parent)/name).is_symlink(),'case footprint directory alias')
  for name in names:
   path=P(parent)/name;t=path.lstat();files+=1
   need(files<=20000 and not path.is_symlink() and path.is_file(),'case footprint bound/type')
   if path.is_relative_to(out):group='closed_result'
   elif any(path.is_relative_to(r) for r in roots['temporary_cache']):group='temporary_cache'
   elif any(path.is_relative_to(r) for r in roots['native_restores']):group='native_restores'
   else:group='metadata_env_help'
   need(not path.is_relative_to(b/'run/results') or group=='closed_result','unmatched additional result UUID')
   groups[group]['logical_bytes']+=t.st_size;groups[group]['allocated_bytes']+=t.st_blocks*512
 caps={'closed_result':112*M,'temporary_cache':128*M,'native_restores':256*M,'metadata_env_help':16*M}
 for group,row in groups.items():
  row['charged_bytes']=max(row.values());row['cap_bytes']=caps[group]
  need(row['charged_bytes']<=caps[group],'own whole-operation footprint cap '+group)
 recovery=b/'run/recovery'
 if recovery.exists():
  for child in recovery.iterdir():
   if not child.is_dir():continue
   logical=allocated=0
   for path in child.rglob('*'):
    if path.is_file():t=path.stat();logical+=t.st_size;allocated+=t.st_blocks*512
   need(max(logical,allocated)<=128*M,'individual native restore cap')
 return {'groups':groups,'charged_total_bytes':sum(row['charged_bytes'] for row in groups.values()),'total_cap_bytes':512*M,'closed_archive_source_cap_bytes':112*M,'metadata_env_help_reserve_bytes':16*M,'files_observed':files}

def registered_join(case,b,s,intent,done,out):
 registry=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';epoch=N/'control/CURRENT_SCIENCE_EPOCH.json'
 rb=registry.read_bytes();eb=epoch.read_bytes();reg=json.loads(rb);ep=json.loads(eb)
 need(ep['epoch']==2 and ep['holder']==os.uname().nodename and ep['native_registry_sha256']==hashlib.sha256(rb).hexdigest(),'authority pair mismatch')
 row=reg['registered_future_requests'][case]
 need(row['consumed']==1 and row['budget']==1 and row['automatic_retry'] is False,'own exact consumed request')
 need(row['uuid']==done['uuid']==intent['uuid'] and row['output']==str(out),'own registered UUID/output mismatch')
 need(row['spec_path']==str(b/'control/FROZEN_SPEC.json') and row['spec_sha256']==sha(b/'control/FROZEN_SPEC.json'),'own registered spec mismatch')
 need(row['authorization_path']==str(b/'control/USER_AUTHORIZATION.json') and row['authorization_sha256']==sha(b/'control/USER_AUTHORIZATION.json'),'own registered authorization mismatch')
 need(row['reserved_write_bytes']==s['advertised_peer_reservation_bytes'] and row['actual_write_restore_envelope_bytes']==s['reserved_write_bytes'],'own exact advertised and actual guarantees not held')
 qpath=b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json';q=read(qpath)
 need(row['native_qualification_sha256']==sha(qpath) and q['source_identity']==s['source_identity'] and q['spec_sha256']==sha(b/'control/FROZEN_SPEC.json'),'registered nativeQ/source mismatch')
 need(registry.read_bytes()==rb and epoch.read_bytes()==eb,'authority changed during archive join; resample required')
 return {'registry_sha256':hashlib.sha256(rb).hexdigest(),'epoch_sha256':hashlib.sha256(eb).hexdigest(),'own_uuid':row['uuid'],'own_spec_sha256':row['spec_sha256'],'own_authorization_sha256':row['authorization_sha256'],'own_native_qualification_sha256':row['native_qualification_sha256'],'advertised_guarantee_bytes':row['reserved_write_bytes'],'actual_write_restore_guarantee_bytes':row['actual_write_restore_envelope_bytes']}

def adapter(case):
 b,s,intent,done,out,point=closed_case(case)
 resourcepath=J/'tools/resource_snapshot.py';need(sha(resourcepath)==RESOURCE_SHA,'resource code drift')
 r=load(resourcepath,'lifetime_held_postrun_resource_reference')
 original=OLD/'vector_result.py';need(sha(original)==FROZEN_RESULT_SHA,'frozen COPY_ONLY primitive drift')
 frozen=load(original,'lifetime_frozen_result_library_authority');m=load(original,'lifetime_private_result_primitives')
 m.ROOT=b;m.NAS=NAS;m.COHORTS={case:'.'};m.CHUNK=16*M;m.RATE=30*M
 m.libraries=lambda bundle=None:frozen.libraries(bundle)
 def gate(reservation=0,other_reservation=None):
  need(other_reservation is None,'no external guessed reservation override')
  need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','native identity drift')
  mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0]
  need(mount['fstype']=='fuse.sshfs' and mount['source']=='admin-wcx@10.208.130.164:/home/shared','genuine164 required')
  own=registered_join(case,b,s,intent,done,out)
  footprint=case_footprint(b,out)
  snapshot=r.snapshot(J,case,'postrun',s['reserved_write_bytes'],s['memory_cap_bytes'])
  need(snapshot['consistent_snapshot'] and snapshot['disk_pass'] and snapshot['RAM_pass'],'held COPY_ONLY resource HOLD')
  need(0<=reservation<=128*M,'single restored result cap128MiB')
  need(snapshot['own_reservation_held'],'own guarantee released before copy closure')
  # Base postrun reference includes256MiB. Add768MiB to bound parent384 +
  # portable child384 +256MiB small tooling:1GiB aggregate, no model forecast.
  extra=768*M
  need(snapshot['host_MemAvailable_bytes']>=snapshot['required_host_available_RAM_bytes']+extra,'COPY_ONLY aggregate parent/child host RAM HOLD')
  head=snapshot['cgroup_effective_headroom_bytes']
  need(head is None or head>=snapshot['required_cgroup_headroom_bytes']+extra,'COPY_ONLY aggregate parent/child cgroup RAM HOLD')
  snapshot.update(copy_only_aggregate_process_margin_bytes=1024*M,copy_only_parent_AS_cap_bytes=384*M,copy_only_child_AS_cap_bytes=384*M,own_registration_join=own,whole_operation_footprint=footprint)
  return snapshot
 m.gate=gate
 def manifest_for(cohort):
  need(cohort==case,'exact archive case');closed_case(case);f,v=m.libraries();entries=[]
  for p in [out,*sorted(out.rglob('*'))]:
   stat=p.lstat();kind='directory' if p.is_dir() and not p.is_symlink() else 'file' if p.is_file() and not p.is_symlink() else 'unsupported'
   need(kind!='unsupported','result links/special files not qualified');row=f.ident(stat);row.update(path=p.relative_to(out).as_posix(),type=kind)
   if kind=='file':row['sha256']=f.file_sha(p)
   entries.append(row)
  raw=sum(x['size'] for x in entries if x['type']=='file');need(raw<=112*M,'closed source cap112MiB plus16MiB metadata reserve; first frozen restore gate includes16MiB overhead')
  selector=hashlib.sha256(canon(entries)).hexdigest();tx=hashlib.sha256(canon({'cohort':case,'uuid':done['uuid'],'selector_sha256':selector,'source_root':str(out),'destination':str(NAS/case)})).hexdigest()
  return {'schema':'NATIVE_QUALIFICATION_EVIDENCE_COPY_ONLY_MANIFEST_V1','cohort':case,'project':'.','txid':tx,'source_root':str(out),'selector_sha256':selector,'entries':entries,'reused_objects':{},'source_disposition':'SOURCE_KEEP','scientific_status':point['status'],'native_execution_receipt_sha256':sha(out/'NATIVE_EXIT.json'),'source_filesystem_identity':{'host':os.uname().nodename,'mount_namespace':os.readlink('/proc/self/ns/mnt'),'device':out.stat().st_dev},'persistent164_root':str(NAS/case/tx).replace('/root/share/mnt164','/home/shared',1)}
 m.manifest_for=manifest_for
 source=inspect.getsource(m.archive);old="else:science_lock=(ROOT/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb')"
 need(source.count(old)==1,'private lease splice contract drift');source=source.replace(old,"else:science_lock=(ROOT/'control/ARCHIVE_JOB.lock').open('a+b')")
 exec(compile(source,'LIFETIME_PRIVATE_LEASE_FROZEN_COPY_ONLY_ARCHIVE','exec'),m.__dict__)
 return m,b,s
def archive(case):
 resource.setrlimit(resource.RLIMIT_AS,(384*M,384*M))
 m,b,s=adapter(case);whole=(b/'control/ARCHIVE_WHOLE_OPERATION.lock').open('a+b');fcntl.flock(whole,fcntl.LOCK_EX|fcntl.LOCK_NB)
 existing=b/'control'/(case+'_ARCHIVE_RECEIPT.json')
 result={'receipt':read(existing),'verified_reused_transaction':True} if existing.exists() else m.archive(case)
 receipt=result['receipt'];bundle=P(receipt['target_mount_path']);f,tx=m.libraries(bundle);manifest=read(bundle/'SOURCE_MANIFEST.json')
 need(m.manifest_for(case)==manifest,'closed source changed');before=m.gate();f.verify_archive(bundle,manifest)
 receiver=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(receiver,fcntl.LOCK_EX|fcntl.LOCK_NB)
 tool=bundle/'RESTORE_EP_TAG_LIFETIME.py';code=(J/'tools_v2/portable_application_restore.py').read_bytes()
 if tool.exists():need(tool.read_bytes()==code,'portable restore tool collision')
 else:
  with tool.open('xb') as stream:stream.write(code);stream.flush();os.fsync(stream.fileno())
 names=['RESTORE_EP_TAG_LIFETIME.py','full_result_bundle.py','v9_transaction.py','RESULT_ENGINE_PIN.json']
 binding={'schema':'EP_TAG_LIFETIME_PORTABLE_RESTORE_TOOL_BINDING_V1','cohort':case,'txid':manifest['txid'],'tool_sha256':{n:sha(bundle/n) for n in names},'legacy_native_result_py':'reference only; never use old default routes for this new case','scope':'supplemental independent restore tools; original COMMIT payload unchanged'}
 put_once(bundle/'RESTORE_TOOL_MANIFEST.json',binding);receiver.close()
 target=b/'run/recovery'/('INDEPENDENT_'+receipt['txid'])
 args=['/usr/bin/python3','-B',str(tool),'--destination',str(target),'--minimum-free-bytes',str(before['required_bytes'])]
 cp=subprocess.run(args,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=180)
 need(cp.returncode==0,'independent restore failed '+cp.stderr[-2000:]);proof=json.loads(cp.stdout)
 need(proof['status']=='INDEPENDENT_BUNDLE_TO_NATIVE_TARGET_RESTORE_PASS' and proof['runtime_or_controller_imported'] is False,'independent restore identity')
 put_once(b/'control/INDEPENDENT_NATIVE_TARGET_RESTORE.json',proof);put_once(b/'control/PORTABLE_RESTORE_TOOL_BINDING.json',binding)
 return {'archive':result,'independent_restore':proof,'held_postrun_resources':m.gate(),'source_keep':True,'scientific_acceptance_granted_by_archive':False,'registry_or_budget_mutated':False,'whole_operation_footprint':case_footprint(b,P(manifest['source_root']))}
