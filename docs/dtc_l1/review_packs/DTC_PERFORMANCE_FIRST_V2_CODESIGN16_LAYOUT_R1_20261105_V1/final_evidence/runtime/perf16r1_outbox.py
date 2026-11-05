"""R1 registered SOURCE_KEEP outbox: natural positive and honest closed negative."""
from pathlib import Path
import ast,gzip,hashlib,json,os,subprocess,types
P=Path;R=P('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');REQ='DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1';G=1024**3;M=1024**2
PRIMITIVE=T/'tools/sweep_outbox.py';PRIMITIVE_SHA='b2bac008c8de73d3f6e7344129f094cd073d19d1572005374dc067fb2077e229'
ANCHOR=""" pid=read(src/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 if proc.exists():require(int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'native simulator still active')"""
REPLACEMENT=' _registered_closed_source_guard(cohort,intent,done,src)'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m

def failed(d):return bool(d['stop_reason']or d['launcher_wait_returncode']or not d['native_simulator_observed'])
def classification(d):
 if not failed(d):return 'NATURAL_OBSERVED_STRICT_PENDING_OR_QUALIFIED'
 if not d['native_simulator_observed']:
  return 'LauncherFailureBeforeSimulatorObserved'if d['launcher_wait_returncode']else'NativeStoppedOrExitedBeforeSimulatorObserved'
 return 'ObservedNativeStoppedOrNonzero'

def closed(c):
 e=load('R1_OUTBOX_READONLY_ENGINE',R/'tools/perf16r1_native.py');reg,ep,q,plan=e.registered();assert q['outbox_sha256']==sha(__file__)and c in q['consumed'];row=q['consumed'][c];ip=R/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');i=read(ip);d=read(dp);out=P(i['output'])
 assert out==R/'DTC/run/results'/row['uuid']and row['uuid']==i['uuid']==d['uuid']and row['intent_sha256']==sha(ip)
 assert d==row['execution_receipt']==read(out/'NATIVE_EXIT.json')and d['cohort']==i['cohort']==c and d['new_attempt_consumed']==1 and d['automatic_retry']is False
 assert type(d['launcher_wait_returncode'])is int and type(d['native_simulator_observed'])is bool
 assert sha(out/'raw.log.gz')==d['raw_sha256'];raw=gzip.decompress((out/'raw.log.gz').read_bytes());assert len(raw)==d['raw_uncompressed_bytes']and hashlib.sha256(raw).hexdigest()==d['raw_uncompressed_sha256']
 pidpath=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 if pidpath.exists():
  assert d['native_simulator_observed']is True;pid=read(pidpath);proc=P('/proc',str(pid['pid']))
  if proc.exists():assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'ACTUAL_SIMULATOR_STILL_LIVE'
 else:
  # Explicitly authorized upfront R1 negative lifecycle. No nonexistent PID,
  # trace, guard or performance counter is synthesized.
  assert failed(d)and d['native_simulator_observed']is False,'NATURAL_POSITIVE_REQUIRES_ACTUAL_PID_MAPS'
  launch=read(out/'NATIVE_LAUNCH.json');assert launch['scientific_qualification_uuid']==d['uuid']
  assert not P('/proc',str(launch['launcher_pid'])).exists(),'UNPROVEN_LAUNCHER_LIVENESS_HOLD'
 if not failed(d):
  strict=read(out/'L2_STRICT.json');qual=read(R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json'))
  assert strict['status']=='PERFV2_CODESIGN16_LAYOUT_R1_NATIVE_TRACE_PERFORMANCE_QUALIFIED'and strict['performance_accepted']is True and strict['uuid']==d['uuid']and strict['raw_gzip_sha256']==d['raw_sha256']
  assert qual['uuid']==d['uuid']and qual['strict_sha256']==sha(out/'L2_STRICT.json')and qual['status']==strict['status']
 return e,q,plan,i,d,out

def transformed():
 assert sha(PRIMITIVE)==PRIMITIVE_SHA;old=PRIMITIVE.read_text();assert old.count(ANCHOR)==1;new=old.replace(ANCHOR,REPLACEMENT,1);assert new.replace(REPLACEMENT,ANCHOR,1)==old
 return new,dict(original_immutable_primitive_sha256=PRIMITIVE_SHA,private_manifest_lifecycle_guard_replacement_count=1,private_transformed_primitive_sha256=hashlib.sha256(new.encode()).hexdigest(),all_other_primitive_source_bytes_unchanged=True)

def adapted(c):
 e,q,plan,i,d,out=closed(c);text,change=transformed();base=types.ModuleType('R1_REGISTERED_PRIVATE_ARCHIVE_PRIMITIVES');base.__file__=str(PRIMITIVE);exec(compile(text,str(PRIMITIVE)+':R1_REGISTERED_LIFECYCLE','exec'),base.__dict__);base.ROOT=R;base.NAS=A/'results';base.COHORTS={k:'DTC'for k in q['admitted_specs']}
 def guard(cohort,intent,done,src):
  _,_,_,ii,dd,oo=closed(cohort);assert ii==intent and dd==done and oo==src
 base._registered_closed_source_guard=guard;original=base.manifest_for
 def manifest(cohort):
  m=original(cohort);_,_,_,_,dd,oo=closed(cohort)
  if failed(dd):m['scientific_status']='STOP_UNACCEPTED'
  m['registered_outbox_binding']=dict(schema='DTC_CODESIGN16_LAYOUT_R1_REGISTERED_OUTBOX_BINDING_V1',request=REQ,registered_outbox_sha256=sha(__file__),observed_native_simulator=dd['native_simulator_observed'],failure_classification=classification(dd),negative_performance_accepted=False if failed(dd)else None,missing_files_not_synthesized=True,**change)
  return m
 base.manifest_for=manifest
 def gate(reservation=0,other_reservation=None):
  assert other_reservation is None and type(reservation)is int and 0<=reservation<=sum(p.stat().st_size for p in out.rglob('*')if p.is_file())+16*M
  assert R.stat().st_dev==2128 and os.uname().nodename=='huangrulin-sshfs-174';parent=base.NAS
  while not parent.exists():parent=parent.parent
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(parent)],text=True))['filesystems'][0];assert fs['fstype']=='fuse.sshfs'and fs['source']=='admin-wcx@10.208.130.164:/home/shared'
  res=e.resource_module();v=res.archive_resources(e.canonical(c))
  assert v['physical_RAM_pass']and v['physical_disk_pass']and v.get('admission_disk_pass',False)and v['native_free_bytes']>v['required_free_bytes']+8*M,'R1_ARCHIVE_FULL_DISK_RESERVATION_HOLD_SOURCE_KEEP'
  return dict(v,new_native_restore_reserved_bytes=reservation,copy_metadata_bound_bytes=8*M,true164_mount=fs,new_model_starts=0)
 base.gate=gate;return base

def archive(c):return adapted(c).archive(c)
def verify(c):
 b=adapted(c);a=read(R/'control'/(c+'_ARCHIVE_RECEIPT.json'));m=b.manifest_for(c);root=P(a['target_mount_path']);assert read(root/'SOURCE_MANIFEST.json')==m;f,v=b.libraries(root);idx=f.verify_archive(root,m);proof=f.check_native(P(a['native_restore']),m);assert idx['archive_sha256']==a['archive_sha256']and len(proof)==len(m['entries'])
 return dict(receipt=a,independently_verified_entries=len(proof),archive_overlay_sha256=sha(__file__),registered_outbox_binding=m['registered_outbox_binding'])
