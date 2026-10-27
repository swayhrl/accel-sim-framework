"""Data-only intake of exact per-row Root-accepted asset receipts. No payload/GPU execution."""
import pathlib,os,stat,json,hashlib,copy,argparse,time
N=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1')
PRODUCER='ROOT_AUTO161_EXACT_ASSET_RECEIPT_INTAKE_V1'
PROFILE='AUTO161_ROOT_EXACT_ASSET_RECEIPT_CPU_V1'
GATE='ROOT_ACCEPTED_EXACT_EXECUTED_ASSET_RECEIPT_REOPENED_V1'
STATUS='ROOT_ACCEPTED_EXACT_ASSET_FOR_EXECUTED_INPUT_SCOPE'
DISPOSITIONS={'NOT_REQUIRED_FOR_THIS_FROZEN_EXECUTED_INPUT_SCOPE','SATISFIED_FOR_THIS_EXACT_ASSET_SCOPE','RETAIN_UNSATISFIED'}
LEVELS={'ACCEPTED_FOR_THIS_EXACT_INPUT','NOT_GRANTED','NOT_REQUIRED_FOR_THIS_ROOT_SELECTED_SCOPE'}
PERMISSIONS={'generic_ISA_support_granted','generic_CFI_support_granted','simulator_qualified','performance_qualified','science_qualified','historical_input_profile_equivalence_granted','new_GPU_execution_authorized','historical_queue_mutation_authorized'}
TERMINAL='EXACT_ASSET_SCOPE_COMPLETE'
WAIT={TERMINAL,'WAIT_EXISTING_AVAILABILITY_REVIEW','WAIT_ISA_ADAPTER','WAIT_ACTUAL_INPUT_ADAPTER','WAIT_MAPPING_ADAPTER','WAIT_SOURCE_RUNTIME_ADAPTER','WAIT_ROOT_GPU_EXACT','WAIT_ROOT_GPU_VARIANT','WAIT_ROOT_GPU_SDK_ARMED','WAIT_CONSUMER_QUALIFICATION'}
RECEIPT_KEYS={'schema','status','queue_id','row_sha256','identity','profile','root_acceptance_ref','evidence','actual_input_identity','levels','progress_facts','proof_dispositions','remaining_proofs','next_stage','permissions','Source_KEEP'}
def need(x,m):
 if not x:raise ValueError('ROOT_EXACT_ASSET_INTAKE_REJECT:'+m)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def identity(row):return {k:copy.deepcopy(row[k])for k in ['job_sha256','binary_sha256','argv']}
def unique_refs(refs):
 result={}
 for r in refs:
  need(isinstance(r,dict)and set(r)=={'path','bytes','sha256'},'REF_SCHEMA')
  key=r['path'];need(key not in result or result[key]==r,'CONFLICTING_REF')
  result[key]=r
 return sorted(result.values(),key=lambda r:r['path'])
class Reader:
 def __init__(self):self.refs=[];self.cache={};self.bytes=0
 def refobj(self,r):
  p=pathlib.Path(r['path']);need(p.is_absolute()and p.is_relative_to(N)and '..'not in p.parts and p.suffix=='.json','SMALL_NAS_JSON_ONLY')
  for q in [p,*p.parents]:need(not q.is_symlink(),'NO_SYMLINK')
  if str(p)not in self.cache:
   fd=os.open(p,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
   try:
    s=os.fstat(fd);need(stat.S_ISREG(s.st_mode)and 0<s.st_size<=2*2**20 and self.bytes+s.st_size<=8*2**20,'BOUNDED_METADATA')
    b=os.read(fd,s.st_size+1);z=os.fstat(fd);v=p.stat();sig=lambda a:(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)
    need(len(b)==s.st_size and sig(s)==sig(z)==sig(v),'STABLE_SAME_RAW')
   finally:os.close(fd)
   self.cache[str(p)]=b;self.bytes+=len(b)
  b=self.cache[str(p)];need(len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'],'REF_RAW_SHA')
  self.refs.append(dict(r));return json.loads(b)
def registry_entry(reg,qid,row=None):
 entry=reg.get('root_exact_asset_receipts',{}).get(qid)
 need(isinstance(entry,dict)and set(entry)=={'row_sha256','identity','active_receipt_sha256','receipts'},'EXACT_ROW_REGISTRY')
 need(type(entry['receipts'])is dict and 1<=len(entry['receipts'])<=32 and entry['active_receipt_sha256']in entry['receipts'],'ACTIVE_REGISTERED_HISTORY')
 if row is not None:need(qid==row['queue_id']and entry['row_sha256']==digest(row)and entry['identity']==identity(row),'FROZEN_ROW_IDENTITY')
 return entry
def deny_escalation(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in PERMISSIONS|{'generic_nonzero_CALL_RET_support_granted','generic_CALL_RET_support_granted','generic_ISA_requirements_granted','new_GPU_execution_by_this_CPU_stage'}:need(v is False,'RESERVED_PERMISSION_'+k)
   deny_escalation(v)
 elif isinstance(x,list):
  for v in x:deny_escalation(v)
def validate_policy(policy):
 keys={'schema','receipt_ref','profile','root_acceptance_ref','root_acceptance_schema','root_acceptance_status','expected_levels','actual_input_identity_sha256','progress_facts_sha256','allowed_proof_dispositions','allowed_remaining_proof_ids','allowed_next_stages','requirements'}
 need(set(policy)in [keys,keys|{'preserve_progress_ref'}]and policy['schema']=='ROOT_AUTO161_EXACT_ASSET_RECEIPT_POLICY_V1','POLICY_SCHEMA')
 need(type(policy['allowed_proof_dispositions'])is dict and all(type(v)is list and v and set(v)<=DISPOSITIONS for v in policy['allowed_proof_dispositions'].values()),'TYPED_ALLOWED_DISPOSITIONS')
 need(type(policy['allowed_remaining_proof_ids'])is list and len(set(policy['allowed_remaining_proof_ids']))==len(policy['allowed_remaining_proof_ids']),'TYPED_REMAINING_IDS')
 need(type(policy['allowed_next_stages'])is list and policy['allowed_next_stages']and set(policy['allowed_next_stages'])<=WAIT,'TYPED_ALLOWED_ROUTE')
def validate_doc(doc,entry,policy,qid,row=None):
 validate_policy(policy)
 need(set(doc)==RECEIPT_KEYS and doc['schema']=='ROOT_AUTO161_EXACT_ASSET_RECEIPT_V1'and doc['status']==STATUS,'ROOT_TYPED_RECEIPT_SCHEMA_STATUS')
 need(doc['queue_id']==qid and doc['row_sha256']==entry['row_sha256']and doc['identity']==entry['identity'],'TYPED_ROW_IDENTITY')
 need(doc['profile']==policy['profile']and doc['profile']and '*'not in doc['profile'],'ROOT_EXACT_PROFILE')
 need(set(doc['permissions'])==PERMISSIONS and all(v is False for v in doc['permissions'].values())and doc['Source_KEEP']is True,'NO_GENERIC_GPU_SCIENCE_OR_MUTATION')
 need(doc['root_acceptance_ref']==policy['root_acceptance_ref'],'EXACT_UNDERLYING_ROOT_ACCEPTANCE')
 need(set(doc['levels'])=={'capture','private_archive','public_catalog','applicable_consumer'}and all(v in LEVELS for v in doc['levels'].values())and doc['levels']==policy['expected_levels'],'EXACT_LEVELS')
 need(doc['levels']['capture']=='ACCEPTED_FOR_THIS_EXACT_INPUT','ACTUAL_CAPTURE_ACCEPTED_ONLY')
 if doc['levels']['public_catalog']=='ACCEPTED_FOR_THIS_EXACT_INPUT':need(doc['levels']['private_archive']=='ACCEPTED_FOR_THIS_EXACT_INPUT','PUBLIC_REQUIRES_ARCHIVE')
 need(type(doc['actual_input_identity'])is dict and doc['actual_input_identity']and digest(doc['actual_input_identity'])==policy['actual_input_identity_sha256'],'EXACT_ACTUAL_INPUT_IDENTITY')
 need(type(doc['progress_facts'])is dict and doc['progress_facts']and digest(doc['progress_facts'])==policy['progress_facts_sha256'],'EXACT_PROGRESS_FACTS')
 deny_escalation(doc['progress_facts'])
 need(type(doc['evidence'])is list and 1<=len(doc['evidence'])<=24,'REAL_BOUNDED_EVIDENCE')
 unique_refs(doc['evidence'])
 ds=doc['proof_dispositions'];need(type(ds)is dict and set(ds)==set(policy['allowed_proof_dispositions']),'EXACT_PROOF_DISPOSITION_KEYS')
 for pid,d in ds.items():
  need(set(d)=={'disposition','reason','generic_proof_satisfied'}and d['disposition']in DISPOSITIONS and d['disposition']in policy['allowed_proof_dispositions'][pid]and type(d['reason'])is str and d['reason']and d['generic_proof_satisfied']is False,'KNOWN_EXPLICIT_SCOPE_DISPOSITION')
 remaining=doc['remaining_proofs'];need(type(remaining)is list and len({p['proof_id']for p in remaining})==len(remaining)and {p['proof_id']for p in remaining}==set(policy['allowed_remaining_proof_ids']),'EXACT_REMAINING_IDS')
 for p in remaining:
  b=p['binding'];need(p['satisfied']is False and p['next_adapter_ABI']=='AUTO161_ARTIFACT_V1'and p['required_evidence']and b['queue_id']==qid and b['job_sha256']==doc['identity']['job_sha256']and b['binary_sha256']==doc['identity']['binary_sha256']and b['argv_sha256']==digest(doc['identity']['argv']),'REMAINING_PROOF_BINDING')
  if row is not None:need(b.get('declared_identity_sha256')==row['declared_identity_sha256'],'REMAINING_DECLARED_IDENTITY')
 req=policy['requirements'];need(set(req)=={'private_archive','public_catalog','applicable_consumer'}and all(type(v)is bool for v in req.values()),'EXPLICIT_APPLICABLE_REQUIREMENTS')
 ids={p['proof_id']for p in remaining}
 for level,pid in [('private_archive','PRIVATE_ASSET_DURABLE_ARCHIVE_COMMIT'),('public_catalog','PUBLIC_ASSET_CURRENT_AND_CATALOG_PUBLICATION'),('applicable_consumer','APPLICABLE_CONSUMER_CONFIGURATION_QUALIFICATION')]:
  if req[level]and doc['levels'][level]=='NOT_GRANTED':need(pid in ids,'MISSING_ACTUAL_REQUIREMENT_'+pid)
  if doc['levels'][level]=='NOT_REQUIRED_FOR_THIS_ROOT_SELECTED_SCOPE':need(req[level]is False,'ROOT_EXPLICIT_NOT_REQUIRED_LEVEL')
 need(doc['next_stage']in WAIT and doc['next_stage']in policy['allowed_next_stages'],'EXACT_NEXT_STAGE')
 if doc['next_stage']==TERMINAL:
  need(not remaining,'TERMINAL_REQUIRES_NO_MISSING_PROOFS')
  need(all(doc['levels'][level]=='ACCEPTED_FOR_THIS_EXACT_INPUT'or(req[level]is False and doc['levels'][level]=='NOT_REQUIRED_FOR_THIS_ROOT_SELECTED_SCOPE')for level in req),'TERMINAL_REQUIRES_ALL_ROOT_SELECTED_LEVELS')
 else:need(bool(remaining),'EMPTY_GAPS_REQUIRE_EXACT_TERMINAL')
 return True
def load_policy(reg,qid,receipt_sha,reader,row=None):
 entry=registry_entry(reg,qid,row);need(receipt_sha in entry['receipts'],'UNREGISTERED_RECEIPT_VERSION')
 policy=entry['receipts'][receipt_sha];need(policy['receipt_ref']['sha256']==receipt_sha,'POLICY_RECEIPT_SHA_KEY')
 doc=reader.refobj(policy['receipt_ref']);validate_doc(doc,entry,policy,qid,row)
 root=reader.refobj(doc['root_acceptance_ref'])
 need(root.get('schema')==policy['root_acceptance_schema']and root.get('status')==policy['root_acceptance_status'],'ORIGINAL_ROOT_ACCEPTED_SCHEMA_STATUS')
 for ref in doc['evidence']:reader.refobj(ref)
 if policy.get('preserve_progress_ref'):
  old=reader.refobj(policy['preserve_progress_ref']);need(old['queue_id']==qid and old['facts']['exact_input_progress']==doc['progress_facts'],'PRIOR_ACCEPTED_FACTS_UNCHANGED')
 return entry,policy,doc
def validate_artifact(a,reg,reader,row=None):
 need(a.get('producer_id')==PRODUCER and a.get('profile')==PROFILE and a.get('provided_gates')==[GATE]and a.get('status')=='PASS','TYPED_INTAKE_ARTIFACT')
 qids=a['target_queue_ids'];need(type(qids)is list and len(qids)==1 and a['family_keys']==[],'ONE_ROW_NO_FAMILY_PROMOTION')
 qid=qids[0];rs=a['root_receipt_ref']['sha256'];entry,policy,doc=load_policy(reg,qid,rs,reader,row)
 need(a['root_receipt_ref']==policy['receipt_ref']and a['root_policy_sha256']==digest(policy)and a['row_bindings']=={qid:entry['row_sha256']},'ARTIFACT_EXACT_POLICY_ROW')
 need(a['next_stage']==doc['next_stage']and a['evidence']==unique_refs([policy['receipt_ref'],doc['root_acceptance_ref']]+doc['evidence']),'ARTIFACT_EXACT_EVIDENCE_ROUTE')
 for k in ['qualification_granted','gpu_executed','historical_queue_mutated','simulation_executed','consumer_qualified','science_qualified','trace_qualified']:need(a[k]is False,'ARTIFACT_NO_NEW_PERMISSION')
 return entry,policy,doc
def apply(row,result,ctx,feedback,reader,reg):
 qid=row['queue_id']
 if qid not in reg.get('root_exact_asset_receipts',{}):return result
 entry=registry_entry(reg,qid,row);active=entry['active_receipt_sha256'];selected=[]
 for ref in ctx.get('dependency_artifacts',[]):
  a=reader.refobj(ref)
  if a.get('producer_id')!=PRODUCER:continue
  _,p,d=validate_artifact(a,reg,reader,row)
  if a['root_receipt_ref']['sha256']==active:selected.append((ref,p,d))
 need(len(selected)==1,'EXACTLY_ONE_ACTIVE_RECEIPT_ARTIFACT')
 ref,policy,doc=selected[0]
 old=copy.deepcopy(result['missing_proofs']);need({x['proof_id']for x in old}==set(doc['proof_dispositions']),'DISPOSE_EXACT_CURRENT_PROOFS_ONLY')
 notreq=[];accepted=[];retained=[]
 for p in old:
  d=doc['proof_dispositions'][p['proof_id']];annotated=dict(p,disposition=d['disposition'],reason=d['reason'],generic_proof_satisfied=False,Root_receipt_ref=policy['receipt_ref'])
  if d['disposition']=='NOT_REQUIRED_FOR_THIS_FROZEN_EXECUTED_INPUT_SCOPE':notreq.append(annotated)
  elif d['disposition']=='SATISFIED_FOR_THIS_EXACT_ASSET_SCOPE':accepted.append(annotated)
  else:
   need(p in doc['remaining_proofs'],'RETAIN_OLD_PROOF_UNCHANGED');retained.append(annotated)
 result['missing_proofs']=copy.deepcopy(doc['remaining_proofs']);result['next_stage']=doc['next_stage']
 result['dependency_requests']=[dict(adapter_id=x['next_adapter_id'],ABI=x['next_adapter_ABI'],target_queue_ids=[qid],family_keys=[],requires_proof_id=x['proof_id'],input_binding=x['binding'],provided_gates_must_remain_CPU_only=True,next_stage=doc['next_stage'])for x in result['missing_proofs']]
 result['facts']['exact_input_progress']=copy.deepcopy(doc['progress_facts'])
 # Keep original unmet proof objects in annotations; never turn generic proof satisfied=True.
 result['facts']['scope_not_required_proofs']=notreq
 result['facts']['Root_accepted_exact_scope_proofs']=accepted
 result['facts']['Root_retained_unsatisfied_proofs']=retained
 result['facts']['Root_exact_asset_receipt']=dict(schema='AUTO161_ROOT_EXACT_ASSET_RECEIPT_INTAKE_FACT_V1',receipt_ref=policy['receipt_ref'],profile=doc['profile'],levels=doc['levels'],actual_input_identity=doc['actual_input_identity'],artifact_ref=ref,permissions=doc['permissions'])
 result['facts']['proof_progress_policy']['remaining_dynamic_ISA_input_runtime_proofs_preserved']=False
 result['facts']['proof_progress_policy']['scope_change_exact_this_row_only']=True
 result['facts']['proof_progress_policy']['generic_ISA_requirements_granted']=False
 return result
def make_artifact(reg,qid,reader,source_sha):
 entry=registry_entry(reg,qid);policy=entry['receipts'][entry['active_receipt_sha256']]
 _,_,doc=load_policy(reg,qid,entry['active_receipt_sha256'],reader)
 return dict(schema='AUTO161_ARTIFACT_V1',producer_id=PRODUCER,profile=PROFILE,producer_source_sha256=source_sha,status='PASS',target_queue_ids=[qid],family_keys=[],row_bindings={qid:entry['row_sha256']},provided_gates=[GATE],requires=[],next_stage=doc['next_stage'],root_receipt_ref=policy['receipt_ref'],root_policy_sha256=digest(policy),evidence=unique_refs([policy['receipt_ref'],doc['root_acceptance_ref']]+doc['evidence']),qualification_granted=False,gpu_executed=False,historical_queue_mutated=False,simulation_executed=False,consumer_qualified=False,science_qualified=False,trace_qualified=False,deterministic_intake_artifact=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--allowlist',required=True);p.add_argument('--qid',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 reg=json.loads(pathlib.Path(a.allowlist).read_bytes());out=pathlib.Path(a.output);need(out.is_absolute()and out.is_relative_to(N)and not out.is_relative_to(N/'auto161_pipeline_20261026_v1/orchestrator')and not out.exists(),'NEW_PRIVATE_ARTIFACT_ONLY')
 source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest();producer=reg['artifact_producers'][PRODUCER]
 need(producer['source_sha256']==source_sha and pathlib.Path(producer['source_path']).resolve()==pathlib.Path(__file__).resolve()and producer['profile']==PROFILE,'EXACT_PRODUCER_SOURCE')
 artifact=make_artifact(reg,a.qid,Reader(),source_sha);out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x')as f:json.dump(artifact,f,indent=2);f.write('\n')
 print(json.dumps(dict(status='ROOT_ACCEPTED_RECEIPT_ARTIFACT_PREPARED',queue_id=a.qid,output=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),new_GPU=False)))
if __name__=='__main__':main()
