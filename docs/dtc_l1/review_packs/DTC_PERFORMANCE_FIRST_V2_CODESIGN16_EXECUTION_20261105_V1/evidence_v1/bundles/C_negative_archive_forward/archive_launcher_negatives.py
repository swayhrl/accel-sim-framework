"""Closed LauncherMissingStrace127 negative evidence only; no model/registry writes.
Root invokes --archive-all only after independent source qualification.
"""
from pathlib import Path
import argparse,ast,copy,fcntl,gzip,hashlib,json,os,subprocess,types
D=Path(__file__).resolve().parent
R=Path('/root/data/dtc_perf_first_v2_codesign16_20261105_v1')
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1')
REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1'
SCOPE='DTC_CODESIGN16_LAUNCHER_MISSING_STRACE_NEGATIVE_ARCHIVE_SCOPE_V1'
PRIMITIVE=Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_outbox.py')
PRIMITIVE_SHA='b2bac008c8de73d3f6e7344129f094cd073d19d1572005374dc067fb2077e229'
REGISTERED_OUTBOX_SHA='2b55983c9b3f974e97d6deaac573a0ef0a27fbced28d75eccdfa96465088df20'
PIN_SOURCE=Path('/root/data/dtc_perf_first_remaining28_20261104_v1/control/RESULT_ENGINE_PIN.json')
PIN_SHA='b93dcc20e07082c688f58704a65fd533109d35b01b64180f9f23eaedd3a0e14b'
N=Path('/root/data/ep_l2_dtc_l1_native_v2')
G=1024**3;M=1024**2
ANCHOR=""" pid=read(src/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 if proc.exists():require(int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'native simulator still active')"""
REPLACEMENT=" _verify_closed_launcher_missing_strace(cohort,intent,done,src)"

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jsonsha(x):return hashlib.sha256((json.dumps(x,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def load(p,name):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m

def authority():
 # Use the already-qualified atomic registry reader. This is read-only, outside
 # any registry EX lock. No original engine prepare/run/update path is invoked.
 base=load(Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py'),'NEGATIVE_ONLY_QUALIFIED_REGISTRY_READER')
 reg,epoch=base.read_current_authority();q=reg['registered_future_requests'][REQ]
 assert q['request']==REQ and q['budget']==16 and len(q['admitted_specs'])==16 and len(q['consumed'])==16 and q['remaining']==0 and q['model_automatic_retries']==0
 matrix=read(R/'control/MATRIX.fixed.json');assert matrix['request']==REQ and matrix['count']==16
 assert set(q['admitted_specs'])=={p['cohort']for p in matrix['points']}==set(q['consumed'])
 assert q['outbox_sha256']==REGISTERED_OUTBOX_SHA==sha(R/'tools/perf16_outbox.py')
 return reg,epoch,q,matrix

def verify_raw(done,raw):
 assert done['raw_storage']=='GZIP_LOSSLESS_1'and done['raw_uncompressed_bytes']==236
 assert hashlib.sha256(raw).hexdigest()==done['raw_uncompressed_sha256']
 expected=(str(R/'tools/bin/strace')+': error while loading shared libraries: '+str(R/'tools/bin/strace')+': cannot open shared object file: No such file or directory\n').encode()
 assert raw==expected,'ONLY_EXACT_OBSERVED_LAUNCHER_MISSING_STRACE_STDERR_ALLOWED'
 assert b'kernel_name ='not in raw and b'GPGPU-Sim'not in raw

def verify_failure_flags(d):
 assert d['launcher_wait_returncode']==127 and d['native_simulator_observed']is False and d['stop_reason']is None and d['new_attempt_consumed']==1 and d['automatic_retry']is False
 assert d['source_disposition']=='SOURCE_KEEP'and d['raw_uncompressed_bytes']==236

def qualify(cohort):
 reg,ep,q,matrix=authority();assert cohort in q['consumed'];row=q['consumed'][cohort]
 ip=R/'control/qualification_ledger'/(cohort+'.INTENT.json');dp=ip.with_name(cohort+'.DONE.json');i=read(ip);d=read(dp);out=Path(i['output']);verify_failure_flags(d)
 assert i['cohort']==d['cohort']==cohort and i['uuid']==d['uuid']==row['uuid']and i['automatic_retry']is False and i['consumed_before_launcher_fork']==1
 assert sha(ip)==row['intent_sha256']and d==row['execution_receipt']==read(out/'NATIVE_EXIT.json')
 assert out==R/'DTC/run/results'/i['uuid']and out.is_dir()and out.stat().st_dev==2128
 assert not(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').exists(),'MISSING_PID_ONLY_EXCEPTION_NOT_GENERAL_NEGATIVE_PATH'
 assert not(out/'actual_file_process_network.log').exists(),'NO_TRACE_EXPECTED_FOR_MISSING_STRACE_LOADER'
 launch=read(out/'NATIVE_LAUNCH.json');assert launch['scientific_qualification_uuid']==i['uuid']
 assert type(launch['launcher_pid'])is int and launch['launcher_pid']>0 and not Path('/proc',str(launch['launcher_pid'])).exists(),'LAUNCHER_PID_PRESENT_HOLD_NEVER_ASSUME_NO_LIVE'
 cp=R/'control/specs'/(cohort+'.json');sp=read(cp);assert sp['request']==REQ and sp['cohort']==cohort
 assert sha(cp)==q['admitted_specs'][cohort]==sha(R/'control'/(cohort+'_SPEC.json'))==sha(out/'DOWNSTREAM_FROZEN_SPEC.json')
 assert read(out/'DOWNSTREAM_INTENT.json')==i
 binding=read(R/'control/dispatch_bindings'/(cohort+'.json'));assert read(out/'DISPATCH_BINDING.json')==binding and sha(out/'DISPATCH_BINDING.json')==i['dispatch_binding_sha256']==launch['dispatch_binding_sha256']
 resolved=dict(sp,host_cpu=binding['host_cpu']);assert binding['resolved_spec_sha256']==jsonsha(resolved)and i['spec_sha256']==binding['canonical_spec_sha256']==q['admitted_specs'][cohort]
 assert sha(out/'raw.log.gz')==d['raw_sha256'];raw=gzip.decompress((out/'raw.log.gz').read_bytes());verify_raw(d,raw)
 for name in ['progress.jsonl.gz','RESOURCE_SAMPLES.jsonl.gz']:
  assert gzip.decompress((out/name).read_bytes())==b'','NO_FAKE_TELEMETRY_OR_GUARD_ROWS'
 assert not (out/'L2_STRICT.json').exists()and not(R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cohort+'.json')).exists()
 return {'cohort':cohort,'uuid':i['uuid'],'output':str(out),'INTENT_path':str(ip),'INTENT_sha256':sha(ip),'DONE_path':str(dp),'DONE_sha256':sha(dp),'NATIVE_EXIT_sha256':sha(out/'NATIVE_EXIT.json'),'canonical_spec_sha256':sha(cp),'raw_gzip_sha256':d['raw_sha256'],'raw_uncompressed_sha256':d['raw_uncompressed_sha256'],'raw_uncompressed_bytes':236,'native_simulator_observed':False,'launcher_wait_returncode':127,'launcher_PID_absent':True,'model_PID_maps_absent':True,'trace_absent':True,'telemetry_and_guard_streams_empty':True,'original_registered_outbox_sha256':q['outbox_sha256'],'program':sp['program'],'input_digest':sp['input_digest'],'profile':sp['profile']}

def ensure_engine_pin(write=False):
 assert sha(PIN_SOURCE)==PIN_SHA and sha(D/'RESULT_ENGINE_PIN.exact.json')==PIN_SHA
 pin=read(PIN_SOURCE);assert pin['full_result_bundle_sha256']=='9d21217af5c694a20ba11cc3890c53dd2a2334a3693c748cc898f523a4a22c47'and pin['v9_sha256']=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
 target=R/'control/RESULT_ENGINE_PIN.json';present=target.exists()
 if present:assert target.read_bytes()==PIN_SOURCE.read_bytes(),'ENGINE_PIN_EXISTING_DIFFERS_REFUSE_OVERWRITE'
 elif write:
  with target.open('xb')as f:f.write(PIN_SOURCE.read_bytes());f.flush();os.fsync(f.fileno())
 return {'source_path':str(PIN_SOURCE),'source_sha256':PIN_SHA,'new_metadata_target':str(target),'target_was_present':present,'target_initialized_by_this_call':write and not present,'scientific_source_or_registry_modified':False}

def transformed_primitive():
 assert sha(PRIMITIVE)==PRIMITIVE_SHA;raw=PRIMITIVE.read_text();assert raw.count(ANCHOR)==1;new=raw.replace(ANCHOR,REPLACEMENT,1);assert new.replace(REPLACEMENT,ANCHOR,1)==raw
 return new,{'original_immutable_outbox_primitive_path':str(PRIMITIVE),'original_immutable_outbox_primitive_sha256':PRIMITIVE_SHA,'private_transformed_primitive_sha256':hashlib.sha256(new.encode()).hexdigest(),'private_manifest_PID_guard_replacement_count':1,'all_other_immutable_primitive_source_bytes_unchanged':True}

def engineering_scope():
 text,transform=transformed_primitive()
 return dict(schema=SCOPE,request=REQ,engineering_classification='LauncherMissingStrace',actual_negative_archive_adapter_path=str(Path(__file__).resolve()),actual_negative_archive_adapter_sha256=sha(__file__),original_registered_outbox_sha256=REGISTERED_OUTBOX_SHA,negative_only=True,performance_accepted=False,accepted_cycles=None,no_PID_trace_guard_or_counter_evidence_synthesized=True,**transform)

def _verify_closed_launcher_missing_strace(c,intent,done,src):
 v=qualify(c);assert v['uuid']==intent['uuid']==done['uuid']and v['output']==str(src)

def adapter(cohort):
 text,transform=transformed_primitive();base=types.ModuleType('PRIVATE_LAUNCHER_MISSING_STRACE_MANIFEST_ADAPTER');base.__file__=str(PRIMITIVE);exec(compile(text,str(PRIMITIVE)+':NEGATIVE_MANIFEST_FORWARD_ONLY','exec'),base.__dict__)
 base.ROOT=R;base.NAS=A/'results';base.COHORTS={p['cohort']:'DTC'for p in read(R/'control/MATRIX.fixed.json')['points']};base._verify_closed_launcher_missing_strace=_verify_closed_launcher_missing_strace
 original_manifest=base.manifest_for
 def manifest(c):
  m=original_manifest(c);assert m['scientific_status']=='STOP_UNACCEPTED'and m['source_disposition']=='SOURCE_KEEP';m['engineering_source_scope']=engineering_scope();return m
 base.manifest_for=manifest
 engine=load(R/'tools/perf16_native.py','PRIVATE_NEGATIVE_ARCHIVE_READONLY_ENGINE')
 def gate(reservation=0,other_reservation=None):
  assert other_reservation is None and type(reservation)is int and reservation>=0
  v=qualify(cohort);out=Path(v['output']);assert reservation<=sum(p.stat().st_size for p in out.rglob('*')if p.is_file())+16*M
  assert os.uname().nodename=='huangrulin-sshfs-174'and R.stat().st_dev==2128
  parent=base.NAS
  while not parent.exists():parent=parent.parent
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(parent)],text=True))['filesystems'][0];assert fs['fstype']=='fuse.sshfs'and fs['source']=='admin-wcx@10.208.130.164:/home/shared'
  s=engine.canonical(cohort);sample=engine.resources(s,False)
  assert sample['physical_RAM_pass']and sample['physical_disk_pass']and sample.get('admission_disk_pass',False)and sample['native_free_bytes']>sample['required_free_bytes']+8*M,'RESOURCE_HOLD_CLOSED_NEGATIVE_COPY_SOURCE_KEEP'
  return dict(sample,new_native_restore_reserved_bytes=reservation,copy_metadata_bound_bytes=8*M,true164_mount=fs,new_model_starts=0,engineering_negative_archive_only=True)
 base.gate=gate
 return base

def verify_archive(cohort,base=None):
 base=adapter(cohort)if base is None else base;m=base.manifest_for(cohort);a=read(R/'control'/(cohort+'_ARCHIVE_RECEIPT.json'));root=Path(a['target_mount_path']);assert read(root/'SOURCE_MANIFEST.json')==m
 f,v=base.libraries(root);idx=f.verify_archive(root,m);proof=f.check_native(Path(a['native_restore']),m);assert idx['archive_sha256']==a['archive_sha256']and len(proof)==len(m['entries'])
 assert a['scientific_status']=='STOP_UNACCEPTED'and a['source_disposition']=='SOURCE_KEEP'and a['source_release_bytes']==0 and a['scientific_acceptance_granted_by_archive']is False
 return {'receipt':a,'independently_verified_entries':len(proof),'archive_overlay_sha256':sha(__file__),'original_registered_outbox_sha256':REGISTERED_OUTBOX_SHA,'engineering_source_scope':engineering_scope()}

def exclusive(p,data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(data,indent=2,sort_keys=True)+'\n').encode()
 if p.exists():assert p.read_bytes()==raw,'EXISTING_FORWARD_EVIDENCE_DIFFERENT_NO_OVERWRITE:'+str(p)
 else:
  with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())

def archive_one(cohort):
 observed=qualify(cohort);base=adapter(cohort);base.archive(cohort);archive=verify_archive(cohort,base);receipt=archive['receipt'];bundle=Path(receipt['target_mount_path'])
 # Additional immutable recovery-tool metadata is outside the original source
 # stream. It never pretends a missing PID/trace/guard file existed in that stream.
 actual=bundle/'negative_archive_adapter.py'
 if actual.exists():assert actual.read_bytes()==Path(__file__).read_bytes()
 else:
  with actual.open('xb')as f:f.write(Path(__file__).read_bytes());f.flush();os.fsync(f.fileno())
 exclusive(bundle/'NEGATIVE_ARCHIVE_ENGINEERING_SCOPE.json',engineering_scope())
 proof={'status':'PERFV2_CODESIGN16_NATIVE_NEGATIVE_UNACCEPTED','engineering_classification':'LauncherMissingStrace','native_simulator_observed':False,'returncode':127,'stop_reason':None,'accepted_cycles':None,'performance_accepted':False,'raw_sha256':observed['raw_gzip_sha256'],'raw_uncompressed_sha256':observed['raw_uncompressed_sha256'],'raw_uncompressed_bytes':236,'actual_PID_maps_absent':True,'actual_trace_absent':True,'telemetry_and_guard_streams_empty':True,'engineering_source_scope':engineering_scope()}
 result={'state':'FAIL_PERFV2_CODESIGN16_DH_ARCHIVED_NO_RETRY','cohort':cohort,'uuid':observed['uuid'],'cycles':None,'proof':proof,'archive':archive,'new_contract_only':True,'original_or_repair_results_replaced':False,'scientific_role':'PERFV2_CODESIGN16_AUTHORIZED_DH','validated_union_authorized':False,'union_scope':'EXPLORATORY_FIXED8_TWO_UNIFORM_COMBINATIONS_16_NOT_CORE32','input_digest':observed['input_digest'],'cell':'DH','profile':observed['profile'],'structure_variant':observed['profile'],'downstream_profile':'P0','engineering_source_scope':engineering_scope(),'engineering_source_scope_status':'FORWARD_NEGATIVE_ARCHIVE_ONLY_NOT_ORIGINAL_REGISTERED_OUTBOX','SOURCE_KEEP':True}
 exclusive(R/'analysis'/(cohort+'.RESULT.json'),result)
 exclusive(D/'receipts'/(cohort+'.ENGINEERING_NEGATIVE_ARCHIVE.json'),{'schema':'DTC_CODESIGN16_CLOSED_NEGATIVE_ARCHIVE_FORWARD_RECEIPT_V1','cohort':cohort,'uuid':observed['uuid'],'classification':'LauncherMissingStrace','qualified_original_closed_evidence':observed,'engineering_source_scope':engineering_scope(),'base_archive_receipt_path':str(R/'control'/(cohort+'_ARCHIVE_RECEIPT.json')),'base_archive_receipt_sha256':sha(R/'control'/(cohort+'_ARCHIVE_RECEIPT.json')),'result_path':str(R/'analysis'/(cohort+'.RESULT.json')),'result_sha256':sha(R/'analysis'/(cohort+'.RESULT.json')),'archive':archive,'scientific_consumption_or_retry_by_adapter':0})
 return {'cohort':cohort,'uuid':observed['uuid'],'state':result['state'],'cycles':None,'result_sha256':sha(R/'analysis'/(cohort+'.RESULT.json')),'restored_entry_count':archive['independently_verified_entries']}

def check_all():
 reg,ep,q,matrix=authority();rows=[qualify(p['cohort'])for p in matrix['points']];assert len({r['uuid']for r in rows})==16
 _,transform=transformed_primitive();return {'schema':'DTC_CODESIGN16_CLOSED_LAUNCHER_NEGATIVE_ALL16_READONLY_CHECK_V1','status':'PASS_CLOSED_LAUNCHER_ENGINEERING_NEGATIVE_ELIGIBILITY_NOT_PERFORMANCE','request':REQ,'registered_budget':16,'consumed':16,'remaining':0,'rows':rows,'engineering_source_scope':engineering_scope(),'engine_pin':ensure_engine_pin(False),'archive_written':False,'models_or_registry_actions':0}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check-all',action='store_true');ap.add_argument('--archive-all',action='store_true');args=ap.parse_args();assert args.check_all!=args.archive_all,'SELECT_EXACTLY_ONE_OPERATION'
 checked=check_all()
 if args.check_all:print(json.dumps(checked,indent=2));return
 # Independent serialization, plus the unchanged primitive's own per-cohort
 # CLOSED_COPY and global true164 receiver locks. Never hold the registry lock.
 with(D/'NEGATIVE_ARCHIVE_SERIAL.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);pin=ensure_engine_pin(True);rows=[archive_one(r['cohort'])for r in checked['rows']]
  out={'schema':'DTC_CODESIGN16_LAUNCHER_NEGATIVE_ARCHIVE_ALL16_SUMMARY_V1','status':'ALL16_LAUNCHER_ENGINEERING_NEGATIVES_ARCHIVED_SOURCE_KEEP_NATIVE_RESTORED','request':REQ,'count':16,'cycles_available':0,'accepted_performance_results':0,'rows':rows,'engine_pin_initialization':pin,'engineering_source_scope':engineering_scope(),'new_models_or_registry_writes_or_UUID_reuse':0};summary=D/'ALL16_NEGATIVE_ARCHIVE_SUMMARY.json'
  if summary.exists():
   previous=read(summary);assert previous['rows']==rows and previous['engineering_source_scope']==out['engineering_source_scope']and previous['request']==REQ;out=previous
  else:exclusive(summary,out)
  print(json.dumps(out,indent=2))
if __name__=='__main__':main()


