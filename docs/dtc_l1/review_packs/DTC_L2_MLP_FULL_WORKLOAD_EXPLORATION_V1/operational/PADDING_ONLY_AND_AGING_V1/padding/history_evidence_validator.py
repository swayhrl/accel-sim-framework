"""Independent offline certificate closure. Reads receipts, never models/signals."""
import copy,datetime,hashlib,json,pathlib,re
P=pathlib.Path;HERE=P(__file__).resolve().parent
CP=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/padding_only_admission_v1/A_ONLY_ELIGIBILITY_CERTIFICATE_V1.json')
EXPECTED='b7f408346d2b513864b203aa34cd1ceedc195c4bf1ca72dcf9a2bbe8be88b9aa'
cache={};sources={}
def h(b):return hashlib.sha256(b).hexdigest()
def raw(p):
 p=str(p)
 if p not in cache:cache[p]=P(p).read_bytes();sources[p]=h(cache[p])
 return cache[p]
def read(p):return json.loads(raw(p))
def pointer(v,p):
 for k in p.strip('/').split('/'):
  if k:v=v[int(k)]if isinstance(v,list)else v[k]
 return v
def sig(opts):
 c=opts['-gpgpu_cache:dl2'];c=c[-1]if isinstance(c,list)else c
 match=re.fullmatch(r'S:128:128:16,L:B:m:L:L,A:(\d+):(\d+),(\d+):0,32',c);assert match
 v=list(map(int,match.groups()));f=opts['-gpgpu_frfcfs_dram_sched_queue_size'];v.append(int(f[-1]if isinstance(f,list)else f))
 assert all(x in a for x,a in zip(v,[(192,384,768),(4,8,16),(32,64,128),(64,128,256)]))and sum(x!=y for x,y in zip(v,[192,4,32,64]))<=1
 return {k:x for k,x in opts.items()if k not in ['-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size']},v
ALLOWED={'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE':'REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE','PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE':'L2_MLP_NATIVE_TRACE_PERFORMANCE_QUALIFIED','PASS_DOWNSTREAM18_STRICT_ARCHIVE_NATIVE_RESTORE':'DOWNSTREAM18_NATIVE_TRACE_PERFORMANCE_QUALIFIED'}
def validate_history(cert,ev,get=read,getraw=raw):
 pins={r['path']:r['sha256']for r in cert['pinned_files']};assert len(pins)==len(cert['pinned_files'])
 required=['spec_path','DONE_path','intent_path','strict_path','archive_evidence_path']
 for key in required:
  p=ev[key];assert p in pins and h(getraw(p))==pins[p]
 for p in ev['pinned_files']:assert p['path']in pins and p['sha256']==pins[p['path']]
 hs=get(ev['spec_path']);done=get(ev['DONE_path']);intent=get(ev['intent_path']);result=get(ev['strict_path']);proof=pointer(result,ev['strict_json_pointer']);archive=pointer(get(ev['archive_evidence_path']),ev['archive_json_pointer'])
 assert hs['cohort']==ev['cohort']==done['cohort']==intent['cohort']==result['cohort']==proof['cohort']
 assert hs['cell']==cert['cell']and hs.get('input_digest',hs.get('workload'))==cert['input_digest']
 assert all(hs[k]==cert[k]==proof[k]for k in ['core_commit','framework_commit','binary_sha256'])
 assert hs['input_binding_sha256']==ev['input_binding_sha256']==cert['input_binding_sha256']
 assert hs['expected']==cert['expected_population']
 assert sig(hs['expected_options'])[0]==cert['normalized_non_target_options']
 assert done['uuid']==intent['uuid']==result['uuid']==proof['uuid']==ev['uuid']
 assert done['launcher_wait_returncode']==0 and done['stop_reason']is None and done['native_simulator_observed']is True
 assert done['peak_observed_rss_bytes']==ev['certified_peak_RSS_bytes']>0
 assert result['state']in ALLOWED and proof['status']==ALLOWED[result['state']]
 assert all(proof[k]==cert['expected_population'][p]for k,p in [('instructions','instructions'),('CTA','CTA'),('kernel_count','kernels')])
 assert proof['progress_records']>0 and proof['resource_samples']>0
 if result['state']=='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE':
  assert proof['correctness_validation_passed']is True and proof['whole_input_model_trace_population_and_lifecycle_validated']is True
  assert proof['performance_accepted']is False and result['accepted_cycles']is None
 else:assert proof['performance_accepted']is True and proof['effective_options']==hs['expected_options']
 assert intent['output']==done['output']
 receipt=archive['receipt'];assert receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and receipt['cohort']==hs['cohort']and receipt['source_disposition']=='SOURCE_KEEP'
 assert max(archive.get('independently_verified_entries',0),archive.get('independently_verified_restored_entries',0))>0
 arc_pins=[p for p in ev['pinned_files']if p['role']=='HISTORY_ARCHIVE_NATIVE_RESTORE_RECEIPT'];assert len(arc_pins)==1
 ar=get(arc_pins[0]['path']);assert ar['status']==receipt['status']and ar['archive_sha256']==receipt['archive_sha256']and ar['cohort']==receipt['cohort']and ar['manifest_sha256']==receipt['manifest_sha256']
 return done['peak_observed_rss_bytes']
def main():
 assert h(raw(CP))==EXPECTED;manifest=read(CP);rows=[];negative=[]
 for cert in manifest['certificates']:
  errors=[];peaks=[]
  try:
   assert h(raw(cert['canonical_spec_path']))==cert['canonical_spec_sha256'];spec=read(cert['canonical_spec_path'])
   assert spec['cohort']==cert['actual_cohort']and spec['input_digest']==cert['input_digest']and spec['cell']==cert['cell'];assert spec['input_binding_sha256']==cert['input_binding_sha256']
   assert sig(spec['expected_options'])[0]==cert['normalized_non_target_options']
   for ev in cert['evidence']:peaks.append(validate_history(cert,ev))
   assert max(peaks)==cert['certified_sameDesign_peak_P'];assert cert['approved_new_formula_input_P']>=max(cert['old_peak_provenance_P'],max(peaks))
  except (AssertionError,KeyError,ValueError,TypeError)as e:errors.append(type(e).__name__+':'+str(e))
  rows.append({'cohort':cert['actual_cohort'],'evidence_n':len(cert['evidence']),'errors':errors})
 # Semantic negatives use virtual in-memory copies, never original files.
 cert=manifest['certificates'][0];ev=cert['evidence'][0];base={p['path']:raw(p['path'])for p in cert['pinned_files']}
 def bad_case(label,path,edit):
  c=copy.deepcopy(cert);e=copy.deepcopy(ev);virtual=dict(base);j=json.loads(virtual[path]);edit(j);virtual[path]=(json.dumps(j,sort_keys=True,indent=2)+'\n').encode();digest=h(virtual[path])
  for pp in c['pinned_files']:
   if pp['path']==path:pp['sha256']=digest
  for pp in e['pinned_files']:
   if pp['path']==path:pp['sha256']=digest
  try:validate_history(c,e,lambda p:json.loads(virtual[str(p)]),lambda p:virtual[str(p)])
  except (AssertionError,KeyError,ValueError,TypeError):negative.append({'case':label,'rejected':True})
  else:negative.append({'case':label,'rejected':False})
 bad_case('same-looking booleans cannot replace actual input binding',ev['spec_path'],lambda x:x.__setitem__('input_binding_sha256','0'*64))
 bad_case('natural_done declared but actual nonzero exit',ev['DONE_path'],lambda x:x.__setitem__('launcher_wait_returncode',1))
 bad_case('strict_population declared but actual incomplete',ev['strict_path'],lambda x:x['proof'].__setitem__('instructions',1))
 bad_case('archive_restored declared but actual archive HOLD',ev['archive_evidence_path'],lambda x:x['archive']['receipt'].__setitem__('status','HOLD'))
 bad_case('same design label but source spec other design',ev['spec_path'],lambda x:x.__setitem__('cell','CH'if x['cell']=='DH'else'DH'))
 bad_case('target extension outside authorized transfer',ev['spec_path'],lambda x:x['expected_options'].__setitem__('-gpgpu_cache:dl2',['S:128:128:16,L:B:m:L:L,A:1536:4,32:0,32']))
 out={'status':'PASS'if not any(r['errors']for r in rows)and all(n['rejected']for n in negative)else'HOLD','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'certificate_path':str(CP),'certificate_sha256':EXPECTED,'certificates_n':len(rows),'history_join_n':sum(r['evidence_n']for r in rows),'source_files_n':len(sources),'rows':rows,'semantic_negative_tests':negative,'source_sha256':sources,'signals':0,'model_starts':0,'production_changes':False,'scope':'Independent E immutable evidence closure; not B implementation or runtime-admission qualification.'}
 (HERE/'E_CERTIFICATE_AUDIT.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['rows','source_sha256','semantic_negative_tests']}))
if __name__=='__main__':main()
