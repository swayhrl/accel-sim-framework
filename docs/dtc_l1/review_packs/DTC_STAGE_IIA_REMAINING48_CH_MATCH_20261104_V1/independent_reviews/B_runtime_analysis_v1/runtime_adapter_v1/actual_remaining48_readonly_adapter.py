"""Actual-schema read-only StageII first16 result adapter. No native-model imports/actions."""
from __future__ import annotations
import argparse,copy,datetime,hashlib,importlib.util,json,os,pathlib,stat,subprocess,sys
sys.dont_write_bytecode=True
P=pathlib.Path;HERE=P(__file__).resolve().parent
R=P('/root/data/dtc_stage_iia_remaining48_20261104_v1')
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/results')
REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
PASS='PASS_STAGEII48_CH_STRICT_ARCHIVE_NATIVE_RESTORE'
FAIL='FAIL_STAGEII48_CH_ARCHIVED_NO_RETRY'
STRICT_STATUS='STAGEII_REMAINING48_NATIVE_TRACE_PERFORMANCE_QUALIFIED'
def require(v,msg):
 if not v:raise ValueError(msg)
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def hashbytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def get(p):
 p=P(p);b=p.read_bytes();return json.loads(b),{'path':str(p),'sha256':hashbytes(b)}
def exact_safe(root,relative):
 root=P(root);q=P(relative)
 require(not q.is_absolute() and '..' not in q.parts,'UNSAFE_MANIFEST_RELATIVE_PATH')
 out=root/q
 require(out.parent.resolve().is_relative_to(root.resolve()) or out==root,'MANIFEST_PARENT_ESCAPE')
 return out

FIXED_SHA='eb9eaab821a81984c4559bb95844cbd90114664fa6b6d9d329e0f8d3e3049b15'
SOURCE_DEV=2128;ARCHIVE_DEV=39;RESTORE_DEV=2128 # explicitly qualified new48 tiers, not inferred equality

def frozen_inputs():
 fp=HERE/'FIXED_RUNTIME_INPUTS.json';require(sha(fp)==FIXED_SHA,'FIXED_ADAPTER_INPUTS_CHANGED');fixed,_=get(fp)
 for k in ['execution_plan','registration_candidate_not_grant','matrix','reference_contract','pure_stats','prequalification_manifest']:
  x=fixed[k];require(sha(x['path'])==x['sha256'],'FIXED_BINDING_SHA_CHANGED:'+k)
 p=P(fixed['pure_stats']['path']);sp=importlib.util.spec_from_file_location('fixed_core32_pure_statistics',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 return m,fixed,{'references':fixed['baseline_references']}

def static_runtime_context():
 m,fixed,base=frozen_inputs();plan,planref=get(R/'control/EXECUTION_PLAN.json');candidate,candidate_ref=get(R/'control/REGISTRY_REQUEST_CANDIDATE.json')
 require(planref['sha256']==fixed['execution_plan']['sha256']and candidate_ref['sha256']==fixed['registration_candidate_not_grant']['sha256'],'CANONICAL_PLAN_CANDIDATE_DRIFT')
 require(plan['request']==REQ and plan['initial_finite_budget']==48 and plan['exact_input_count']==24 and plan['core32_reporting_authorized']is True and plan['first16_reexecution_authorized']is False and plan['no_extensions']is True,'WRONG_NEW48_FIXED_SCOPE')
 for x in plan['source_pins']:require(sha(x['path'])==x['sha256'],'NEW48_SOURCE_PIN_DRIFT:'+x['path'])
 require(len(plan['source_pins'])==122,'NEW48_FIXED_SOURCE_PIN_COUNT')
 return fixed,candidate,plan,{'execution_plan':planref,'registration_candidate_not_grant':candidate_ref,'qualified_tiers':fixed['source_tiers'],'registration_granted':False}

def registry_context():
 fixed,candidate,plan,ctx=static_runtime_context();regp=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');epp=regp.parents[1]/'CURRENT_SCIENCE_EPOCH.json';reg,regref=get(regp);ep,epref=get(epp)
 require(ep['native_registry_sha256']==regref['sha256'],'AUTHORITY_PAIR_IN_FLIGHT_OR_DRIFT')
 if REQ not in reg['registered_future_requests']:raise PermissionError('AWAIT_ACTUAL_REGISTRY_GRANT; candidate is not a grant')
 q=reg['registered_future_requests'][REQ]
 for k in ['request','budget','admitted_inputs','admitted_specs','approved_contract_commit','exact_proposal_sha256','execution_plan_sha256','engine_sha256','strict_sha256','outbox_sha256','controller_path','controller_sha256','owner_pid','owner_start_ticks','scientific_role','old_request_budget_reused','new_registration_only','model_automatic_retries']:
  require(q.get(k)==candidate.get(k),'ACTUAL_GRANT_DIFFERS_FIXED_CANDIDATE:'+k)
 require(q['request']==REQ and q['budget']==len(q['admitted_specs'])==48,'WRONG_ACTUAL_NEW48_SCOPE')
 require(set(q['admitted_specs'])=={e['cohort']for e in fixed['expected_CH']},'NEW48_ACTUAL_MEMBERSHIP_DRIFT');require(q['remaining']==48-len(q['consumed'])and set(q['consumed'])<=set(q['admitted_specs']),'NEW48_BUDGET_ACCOUNTING_MISMATCH')
 for k,file in [('engine_sha256','stage2_native.py'),('strict_sha256','stage2_strict.py'),('outbox_sha256','stage2_outbox.py')]:require(q[k]==sha(R/'tools'/file),'REGISTERED_NATIVE_SOURCE_DRIFT:'+k)
 ctx.update(registry=regref,epoch=epref,registration_granted=True,engine_sha256=q['engine_sha256'],strict_sha256=q['strict_sha256'],outbox_sha256=q['outbox_sha256']);return q,plan,ctx

def verify_restore_rows(manifest,proof,restore_root):
 require(len(proof['rows'])==len(manifest['entries']),'RESTORE_PROOF_ROW_COUNT')
 rows={x['path']:x for x in proof['rows']};require(len(rows)==len(proof['rows']),'RESTORE_PROOF_DUPLICATE_PATH')
 for e in manifest['entries']:
  p=exact_safe(restore_root,e['path']);v=rows[e['path']];require(v['type']==e['type'],'RESTORE_TYPE_DISAGREES')
  require(v['identity']['dev']==RESTORE_DEV and p.lstat().st_dev==RESTORE_DEV,'RESTORE_NOT_NATIVE_DEVICE')
  if e['type']=='file':
   require(p.is_file() and not p.is_symlink(),'RESTORE_REGULAR_FILE_REQUIRED')
   require(p.stat().st_size==e['size'] and v['sha256']==e['sha256']==sha(p),'RESTORE_FILE_SIZE_SHA_MISMATCH:'+e['path'])
  elif e['type']=='directory':require(p.is_dir() and not p.is_symlink(),'RESTORE_DIRECTORY_MISMATCH')
  elif e['type']=='symlink':require(p.is_symlink() and os.readlink(p)==e['target']==v['target'],'RESTORE_ALIAS_MISMATCH')
  else:raise ValueError('UNSUPPORTED_RESTORE_MEMBER_TYPE')

def verify_archive(c,result,out,done,successful,ctx,check_mount=True):
 a=result['archive'];receipt=a['receipt'];local,rr=get(R/'control'/(c+'_ARCHIVE_RECEIPT.json'));require(local==receipt,'LOCAL_RECEIPT_DIFFERS_FROM_RESULT')
 require(receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['cohort']==c,'ARCHIVE_RECEIPT_STATUS_IDENTITY')
 require(receipt['source_disposition']=='SOURCE_KEEP' and receipt['source_release_bytes']==0 and receipt['scientific_acceptance_granted_by_archive'] is False,'ARCHIVE_IS_NOT_SCIENTIFIC_ACCEPTANCE')
 target=P(receipt['target_mount_path']);restore=P(receipt['native_restore']);tx=receipt['txid']
 require(out.stat().st_dev==SOURCE_DEV and target.stat().st_dev==ARCHIVE_DEV and restore.stat().st_dev==RESTORE_DEV,'QUALIFIED_SOURCE_ARCHIVE_RESTORE_TIER_MISMATCH')
 require(target==NAS/c/tx and restore==R/'DTC/run/recovery'/tx,'ARCHIVE_OR_RESTORE_NAMESPACE_ESCAPE')
 require(receipt['true164_root']==str(target).replace('/root/share/mnt164','/home/shared',1),'TRUE164_RECEIPT_ROOT_MISMATCH')
 if check_mount:
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(target)],text=True))['filesystems'][0]
  require(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','TRUE164_ACTUAL_MOUNT_MISMATCH')
 arc_receipt,ar=get(target/'RECEIPT.json');require(arc_receipt==receipt,'ARCHIVE_LOCAL_RECEIPT_DISAGREES')
 manifest,mr=get(target/'SOURCE_MANIFEST.json');index,ir=get(target/'ARCHIVE_INDEX.json');commit,cr=get(target/'COMMIT.json');proof,pr=get(target/'RESTORE_VERIFIED_NATIVE_TARGET.json')
 require(manifest['cohort']==c and manifest['txid']==tx and manifest['source_root']==str(out),'ARCHIVE_MANIFEST_IDENTITY')
 require(manifest['scientific_status']==receipt['scientific_status']==(STRICT_STATUS if successful else 'STOP_UNACCEPTED'),'ARCHIVE_SCIENTIFIC_STATUS_DISAGREES')
 require(manifest['native_execution_receipt_sha256']==sha(out/'NATIVE_EXIT.json'),'MANIFEST_NATIVE_EXIT_SHA_MISMATCH')
 require(receipt['manifest_sha256']==commit['manifest_sha256']==hashbytes(canon(manifest)),'MANIFEST_CANONICAL_SHA_MISMATCH')
 require(commit['archive_index_sha256']==hashbytes(canon(index)) and commit['txid']==tx,'ARCHIVE_COMMIT_INDEX_SHA_MISMATCH')
 require(proof['txid']==tx,'RESTORE_PROOF_TXID_MISMATCH')
 require(index['archive_sha256']==receipt['archive_sha256'] and index['archive_bytes']==receipt['archive_bytes'],'ARCHIVE_INDEX_RECEIPT_SHA_SIZE_MISMATCH')
 total=0;stream=hashlib.sha256()
 for ch in index['chunks']:
  require(ch['offset']==total and ch['txid']==tx,'ARCHIVE_CHUNK_OFFSET_OR_TXID')
  p=exact_safe(target/'chunks',ch['name']);require(p.is_file() and not p.is_symlink()and p.stat().st_dev==ARCHIVE_DEV,'ARCHIVE_CHUNK_REGULAR_164_FILE_REQUIRED');require(p.stat().st_size==ch['size'],'ARCHIVE_CHUNK_SIZE')
  part=hashlib.sha256()
  with p.open('rb') as h:
   for b in iter(lambda:h.read(1024*1024),b''):part.update(b);stream.update(b)
  require(part.hexdigest()==ch['sha256'],'ARCHIVE_CHUNK_SHA_MISMATCH');total+=ch['size']
 require(total==index['archive_bytes'] and stream.hexdigest()==index['archive_sha256'],'ARCHIVE_STREAM_SHA_SIZE_MISMATCH')
 verify_restore_rows(manifest,proof,restore)
 entries={x['path']:x for x in manifest['entries']};require(len(entries)==len(manifest['entries']),'MANIFEST_DUPLICATE_MEMBER')
 critical=['NATIVE_EXIT.json','DOWNSTREAM_FROZEN_SPEC.json','DISPATCH_BINDING.json','raw.log.gz']+(['L2_STRICT.json'] if successful else [])
 for n in critical:
  require(n in entries and entries[n]['type']=='file' and entries[n]['sha256']==sha(out/n),'SOURCE_CRITICAL_MEMBER_MISMATCH:'+n)
 require(entries['raw.log.gz']['sha256']==done['raw_sha256'],'MANIFEST_RAW_GZIP_SHA_MISMATCH')
 require(a.get('independently_verified_entries')==len(manifest['entries']),'RESULT_ARCHIVE_ENTRY_VERIFICATION_COUNT')
 require(a.get('archive_overlay_sha256')==ctx['outbox_sha256'],'RESULT_ARCHIVE_OVERLAY_SOURCE_MISMATCH')
 return {'ARCHIVE_RECEIPT':rr,'NATIVE_RESTORE':pr},{'archive_receipt':ar,'source_manifest':mr,'archive_index':ir,'commit':cr,'native_restore':pr,'archive_stream_sha256':stream.hexdigest(),'native_restored_entries_verified':len(manifest['entries']),'critical_source_members':critical}

def validate_result_scope(result,e):
 c=e['cohort']
 require(result['cohort']==c and result['scientific_role']=='STAGEII_REMAINING48_AUTHORIZED_CH' and result['input_digest']==e['input_digest'] and result['cell']=='CH' and result['profile']==e['profile'],'RESULT_ROLE_OR_IDENTITY_DISAGREES')
 require(result['state'] in [PASS,FAIL],'RESULT_NOT_DECLARED_TERMINAL_STATE')
 require(result.get('validated_union_authorized')is True and result.get('union_scope')=='CORE32_FIRST16_PLUS_REMAINING48_FIXED_SHA'and result.get('new_contract_only')is True and result.get('original_or_repair_results_replaced')is False,'WRONG_NEW48_REPORTING_ROLE_OR_UNION_AUTHORITY')

def observation(e,old,ctx,q):
 c=e['cohort'];rp=R/'analysis'/(c+'.RESULT.json');row={'program':e['program'],'suite':e['suite'],'input_digest':e['input_digest'],'design':'CH','profile':e['profile'],'cohort':c,'source_role':'STAGEII_REMAINING48_AUTHORIZED_CH','request':REQ,'accepted':False,'cycles':None}
 if not rp.exists():
  row['status']='AWAIT_ROOT_RESULT'
  if (R/'control/qualification_ledger'/(c+'.INTENT.json')).exists():row['status']='UUID_RECORDED_AWAIT_ROOT_RESULT'
  return row
 result,rref=get(rp);row['sources']={'RESULT':rref};row['observed_native_state']=result.get('state')
 validate_result_scope(result,e)
 successful=result['state']==PASS
 sp=R/'control/specs'/(c+'.json');spec,sref=get(sp);require(sha(R/'control'/(c+'_SPEC.json'))==sref['sha256']==q['admitted_specs'][c],'CANONICAL_REGISTERED_SPEC_SHA')
 for k,v in [('cohort',c),('request',REQ),('cell','CH'),('profile',e['profile']),('input_digest',e['input_digest']),('expected',e['expected']),('expected_options',e['effective_options']),('host_cpu',None),('input_binding_sha256',e['input_binding']['sha256'])]:require(spec.get(k)==v,'SPEC_DISAGREES_WITH_FIXED_CONTRACT:'+k)
 require([x['sha256'] for x in spec['configs']]==[x['sha256'] for x in e['configs']],'SPEC_CONFIG_PIN_DISAGREES')
 for x in spec['configs']:require(sha(x['path'])==x['sha256'],'ACTUAL_CONFIG_BYTES_MISMATCH')
 require(sha(spec['input_binding_path'])==e['input_binding']['sha256'],'ACTUAL_INPUT_BINDING_SHA_MISMATCH')
 for k in ['core_commit','framework_commit','binary_sha256']:require(spec[k]==old['build'][k],'SPEC_BUILD_DISAGREES')
 require(any('libcudart' in x['target'] and x['sha256']==old['build']['libcudart_sha256'] and sha(x['actual_realpath'])==x['sha256'] for x in spec['runtime_files']),'ACTUAL_CORE_LIBRARY_SHA_MISMATCH')
 binary=next(x for x in spec['runtime_files'] if x['sha256']==spec['binary_sha256']);require(sha(binary['actual_realpath'])==spec['binary_sha256'],'ACTUAL_BINARY_SHA_MISMATCH')
 ip=R/'control/qualification_ledger'/(c+'.INTENT.json');intent,iref=get(ip);done,dref=get(ip.with_name(c+'.DONE.json'));uid=result['uuid'];out=R/'DTC/run/results'/uid;exitv,xref=get(out/'NATIVE_EXIT.json');cons=q['consumed'][c]
 require(intent['uuid']==done['uuid']==uid==cons['uuid'] and intent['output']==str(out),'DONE_INTENT_RESULT_UUID_OR_OUTPUT')
 require(cons['intent_sha256']==iref['sha256'] and cons['execution_receipt']==done==exitv,'DONE_NATIVE_EXIT_REGISTERED_RECEIPT_DISAGREES')
 require(sha(out/'raw.log.gz')==done['raw_sha256'],'CLOSED_RAW_GZIP_SHA_MISMATCH')
 require((not bool(done['stop_reason'] or done['launcher_wait_returncode']))==successful,'RESULT_SUCCESS_DISAGREES_NATIVE_EXIT')
 if successful:require(done['native_simulator_observed'] is True,'NO_ACTUAL_NATIVE_SIMULATOR_RECEIPT')
 require(sha(out/'DOWNSTREAM_FROZEN_SPEC.json')==sref['sha256'],'RUN_FROZEN_SPEC_DISAGREES')
 db,dbr=get(R/'control/dispatch_bindings'/(c+'.json'));require(db['canonical_spec_sha256']==sref['sha256'] and sha(out/'DISPATCH_BINDING.json')==dbr['sha256']==intent['dispatch_binding_sha256'],'DISPATCH_BINDING_SHA_DISAGREES')
 arefs,av=verify_archive(c,result,out,done,successful,ctx)
 row.update(uuid=uid,sources={'RESULT':rref,'SPEC':sref,**arefs},archive_verification=av,native_exit=xref,intent=iref,done=dref,dispatch_binding=dbr)
 if not successful:
  require(result['cycles'] is None and result['proof'].get('performance_accepted') is False and result['proof'].get('status')=='STAGEII48_NATIVE_NEGATIVE_UNACCEPTED','NEGATIVE_MUST_NOT_HAVE_ACCEPTED_CYCLES_OR_WRONG_STATUS')
  row.update(status=FAIL,reason={'stop_reason':done['stop_reason'],'returncode':done['launcher_wait_returncode']});return row
 proof=result['proof'];strict,sr=get(out/'L2_STRICT.json');qual,qr=get(R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json'))
 require(strict==proof and proof['schema']=='DTC_STAGEII_REMAINING48_STRICT_V1' and proof['status']==STRICT_STATUS and proof['performance_accepted'] is True,'MISSING_OR_MISMATCHED_STRICT_PROOF')
 require(type(result['cycles']) is int and result['cycles']>0 and result['cycles']==proof['cycles'],'INVALID_ACCEPTED_CYCLES')
 for k,v in [('cohort',c),('uuid',uid),('input_digest',e['input_digest']),('cell','CH'),('profile',e['profile']),('effective_options',e['effective_options'])]+[(k,old['build'][k]) for k in ['core_commit','framework_commit','binary_sha256']]:require(proof.get(k)==v,'STRICT_IDENTITY_DISAGREES:'+k)
 for k,v in [('CTA',e['expected']['CTA']),('instructions',e['expected']['instructions']),('kernel_count',e['expected']['kernels'])]:require(proof[k]==v,'STRICT_ROI_COUNT_DISAGREES:'+k)
 require(proof['raw_gzip_sha256']==done['raw_sha256'] and proof['raw_uncompressed_sha256']==done['raw_uncompressed_sha256'],'STRICT_RAW_SHA_DISAGREES')
 require(qual['status']==STRICT_STATUS and qual['cohort']==c and qual['uuid']==uid and qual['strict_sha256']==sr['sha256'],'ROOT_SCIENCE_QUALIFICATION_DISAGREES')
 row['sources']['STRICT']=sr
 row.update(accepted=True,status=PASS,cycles=result['cycles'],RESULT_sha256=rref['sha256'],input_binding_sha=e['input_binding']['sha256'],roi_fingerprint=e['expected_roi_fingerprint'],build=old['build'],build_fingerprint=old['build_fingerprint'],downstream_fingerprint=e['downstream_fingerprint'],effective_options=e['effective_options'],config_sha256=[x['sha256'] for x in e['configs']],expected_ROI=e['expected'],qualification={x:True for x in ['strict_pass','actual_input_verified','actual_build_verified','actual_effective_options_verified','natural_exit_verified','true164_archive_verified','native_restore_verified']},root_science_qualification=qr,kernel_cycle_rows=proof.get('kernels'),traffic=proof.get('traffic'),metrics=proof.get('metrics'),latency_counters=proof.get('latency_counters'))
 return row


def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def cache_metadata_ok(row):
 refs=list(row.get('sources',{}).values())+list(row.get('archive_verification',{}).get(k)for k in ['archive_receipt','source_manifest','archive_index','commit','native_restore'])+[row.get(k)for k in['native_exit','intent','done','dispatch_binding','root_science_qualification']]
 try:return bool(refs)and all(isinstance(x,dict)and sha(x['path'])==x['sha256']for x in refs if x is not None)
 except(OSError,KeyError,ValueError):return False

def pending(e,status,reason=None):
 return {'program':e['program'],'suite':e['suite'],'input_digest':e['input_digest'],'design':'CH','profile':e['profile'],'cohort':e['cohort'],'source_role':'STAGEII_REMAINING48_AUTHORIZED_CH','request':REQ,'accepted':False,'cycles':None,'status':status,'reason':reason}

def collect(previous_cache=None,force_full_archive=False):
 m,contract,base=frozen_inputs();previous_cache=previous_cache or{};newcache={};rows=[];ctx={};q={};qualified=False
 try:q,plan,ctx=registry_context();qualified=True
 except(PermissionError,AssertionError,KeyError,ValueError,OSError,json.JSONDecodeError)as x:
  return {'schema':'DTC_REMAINING48_ANALYSIS_OBSERVATIONS_V1','request':REQ,'observed_utc':now(),'source_qualified':False,'registration_granted':False,'observations':[pending(e,'AWAIT_ACTUAL_REGISTRY_GRANT'if isinstance(x,PermissionError)else'HOLD_READONLY_VERIFICATION',str(x))for e in contract['expected_CH']],'runtime_source_pins':ctx,'new_model_starts':0,'native_scientific_writes':0},{}
 by={(x['input_digest'],x['design'],x['profile']):x for x in base['references']};full=[];reused=[]
 for e in contract['expected_CH']:
  c=e['cohort'];rp=R/'analysis'/(c+'.RESULT.json');old=previous_cache.get(c)
  try:
   rs=sha(rp)if rp.exists()else None
   if not force_full_archive and old and old['result_sha256']==rs and old['row']['status']in[PASS,FAIL]and cache_metadata_ok(old['row']):
    row=copy.deepcopy(old['row']);row['analysis_validation_mode']='CRITICAL_JSON_SHA_RECHECK_WITH_IMMUTABLE_FULL_ARCHIVE_AUDIT_CACHE';row['critical_json_rechecked_utc']=now();reused.append(c);newcache[c]=old
   else:
    row=observation(e,by[e['input_digest'],'CH','P0'],ctx,q)
    if row['status']in[PASS,FAIL]:
     stamp=now();row.update(analysis_validation_mode='FULL_ARCHIVE_STREAM_AND_NATIVE_RESTORE_AUDIT',full_archive_audit_utc=stamp,critical_json_rechecked_utc=stamp);newcache[c]={'result_sha256':rs,'row':copy.deepcopy(row),'full_archive_audit_utc':stamp};full.append(c)
  except(AssertionError,KeyError,ValueError,OSError,json.JSONDecodeError)as x:row=pending(e,'HOLD_READONLY_VERIFICATION',str(x))
  rows.append(row)
 return {'schema':'DTC_REMAINING48_ANALYSIS_OBSERVATIONS_V1','request':REQ,'observed_utc':now(),'source_qualified':qualified,'registration_granted':True,'registered_consumed':len(q['consumed']),'registered_remaining':q['remaining'],'observations':rows,'runtime_source_pins':ctx,'core32_reporting_authorized':True,'verification':{'full_archive_audited':full,'critical_JSON_rechecked_cached_archive':reused,'forced_full_archive':force_full_archive},'new_model_starts':0,'native_scientific_writes':0},newcache
