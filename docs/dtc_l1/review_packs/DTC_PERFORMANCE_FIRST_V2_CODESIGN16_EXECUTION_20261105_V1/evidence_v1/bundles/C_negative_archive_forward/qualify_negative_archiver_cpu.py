"""CPU-only negative manifest/library qualification; never archive/restore or write R4."""
from pathlib import Path
import ast,copy,json,hashlib,types
O=Path(__file__).resolve().parent;source=O/'archive_launcher_negatives.py';m=types.ModuleType('CPU_NEGATIVE_ONLY_ADAPTER');m.__file__=str(source);exec(compile(source.read_bytes(),str(source),'exec'),m.__dict__)
checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'PASS':True})
def reject(n,f):
 try:f()
 except(AssertionError,KeyError,ValueError,TypeError):ck(n,True);return
 raise AssertionError(n)
all16=m.check_all();ck('all16_actual_consumed_closed_classifier_only',all16['consumed']==16 and all16['remaining']==0 and len(all16['rows'])==16 and all16['archive_written']is False);ck('sixteen_actual_UUIDs_unique',len({r['uuid']for r in all16['rows']})==16)
# Existing original archive/restore code and V9 bytes are actually SHA-verified
# and imported through a CPU-private exact pin, without creating native metadata.
text,trans=m.transformed_primitive();ck('one_PID_guard_only_transformed_reverse_roundtrip',trans['private_manifest_PID_guard_replacement_count']==1 and trans['all_other_immutable_primitive_source_bytes_unchanged']and text.replace(m.REPLACEMENT,m.ANCHOR,1)==m.PRIMITIVE.read_text())
lib=types.ModuleType('CPU_UNCHANGED_ARCHIVE_LIBRARIES');lib.__file__=str(m.PRIMITIVE);exec(compile(m.PRIMITIVE.read_bytes(),str(m.PRIMITIVE),'exec'),lib.__dict__);F=O/'cpu_library_fixture';(F/'control').mkdir(parents=True,exist_ok=True);(F/'control/RESULT_ENGINE_PIN.json').write_bytes(m.PIN_SOURCE.read_bytes());lib.ROOT=F;f,v=lib.libraries();ck('actual_immutable_full_result_bundle_SHA',hashlib.sha256((lib.BASELINE/'full_result_bundle.py').read_bytes()).hexdigest()==m.read(m.PIN_SOURCE)['full_result_bundle_sha256']);ck('actual_V9_source_SHA',hashlib.sha256((lib.BASELINE/'v9_transaction.py').read_bytes()).hexdigest()==m.read(m.PIN_SOURCE)['v9_sha256'])
# Actual read-only source manifests: original entries/type/hash generation remains
# unchanged. Only missingPID guard is replaced after stricter exact127 qualification.
entries=[]
for row in all16['rows']:
 base=m.adapter(row['cohort']);base.libraries=lambda bundle=None:(f,v);manifest=base.manifest_for(row['cohort']);actual={'.',*map(lambda p:p.relative_to(Path(row['output'])).as_posix(),Path(row['output']).rglob('*'))};members={e['path']for e in manifest['entries']};ck(row['cohort']+'_actual_entries_only',members==actual);ck(row['cohort']+'_STOP_SOURCE_KEEP_no_performance',manifest['scientific_status']=='STOP_UNACCEPTED'and manifest['source_disposition']=='SOURCE_KEEP'and manifest['engineering_source_scope']['performance_accepted']is False);ck(row['cohort']+'_no_fabricated_PID_trace_strict',not{'NATIVE_SIMULATOR_PID_AND_MAPS.json','actual_file_process_network.log','L2_STRICT.json'}&members);ck(row['cohort']+'_actual_adapter_original_outbox_provenance',manifest['engineering_source_scope']['actual_negative_archive_adapter_sha256']==m.sha(source)and manifest['engineering_source_scope']['original_registered_outbox_sha256']==m.REGISTERED_OUTBOX_SHA)
 entries.append({'cohort':row['cohort'],'uuid':row['uuid'],'typed_entry_count':len(manifest['entries']),'regular_file_count':sum(e['type']=='file'for e in manifest['entries']),'source_manifest_canonical_sha256':hashlib.sha256(base.canon(manifest)).hexdigest(),'source_payload_logical_bytes':sum(e['size']for e in manifest['entries']if e['type']=='file')})
done=m.read(all16['rows'][0]['DONE_path']);raw=__import__('gzip').decompress((Path(all16['rows'][0]['output'])/'raw.log.gz').read_bytes())
for key,value in [('launcher_wait_returncode',0),('native_simulator_observed',True),('stop_reason','CPU_FAKE_FOR_REJECTION'),('automatic_retry',True),('new_attempt_consumed',0),('raw_uncompressed_bytes',0)]:
 bad=copy.deepcopy(done);bad[key]=value;reject('reject_'+key,lambda b=bad:m.verify_failure_flags(b))
reject('reject_changed_raw_SHA',lambda:m.verify_raw(done,raw+b'CORRUPT'));bad=copy.deepcopy(done);bad['raw_uncompressed_sha256']=hashlib.sha256(b'kernel_name = fake\n').hexdigest();reject('reject_non_exact_loader_stderr_even_if_own_SHA',lambda:m.verify_raw(bad,b'kernel_name = fake\n'))
ck('native_RESULT_ENGINE_PIN_still_not_written_by_CPU',m.ensure_engine_pin(False)['target_initialized_by_this_call']is False)
ck('no_archive_or_restore_operation_in_this_CPU_script',not(O/'ALL16_NEGATIVE_ARCHIVE_SUMMARY.json').exists())
report={'schema':'DTC_CODESIGN16_LAUNCHER_NEGATIVE_ARCHIVE_FORWARD_CPU_V1','status':'PASS_CPU_AND_READONLY_REAL_CLOSED_SOURCE_MANIFEST_ONLY_NOT_ARCHIVE_EXECUTION','adapter_source_sha256':m.sha(source),'checks':checks,'count':len(checks),'source_rows':entries,'read_only_eligibility_sha256':m.sha(O/'READONLY_ALL16_ELIGIBILITY.json'),'real_archive_restore_result_or_registry_writes':0,'scientific_models_or_UUIDs_created':0,'forward_only_missing_PID_engineering_classification':'LauncherMissingStrace'};(O/'CPU_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'source_rows':len(entries),'entries':sum(r['typed_entry_count']for r in entries)}))
