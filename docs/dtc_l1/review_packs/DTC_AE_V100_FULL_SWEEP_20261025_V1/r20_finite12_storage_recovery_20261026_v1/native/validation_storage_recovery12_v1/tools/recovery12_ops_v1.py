"""Sole-parent repair worker/evidence API; never retries a consumed model."""
import pathlib,json,hashlib,importlib.util,subprocess,uuid,time,gzip
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_storage_recovery12_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,R/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(path,value):
 with P(path).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
def archive_closed(cell):
 outbox=load('repair_closed_archive','recovery12_outbox_v1.py');start=time.monotonic()
 while True:
  if (R/'control'/(cell+'_ARCHIVE_RECEIPT.json')).exists():return outbox.verify(cell)
  try:outbox.archive(cell)
  except BlockingIOError:
   assert time.monotonic()-start<21600,'finite COPY receiver wait exhausted';time.sleep(10)
def finish_evidence(cell):
 i=read(R/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(i['output']);done=read(R/'control/qualification_ledger'/(cell+'.DONE.json'));assert done==read(out/'NATIVE_EXIT.json') and done['uuid']==i['uuid'];failed=bool(done['stop_reason'] or done['launcher_wait_returncode'])
 if failed:
  assert sha(out/'raw.log.gz')==done['raw_sha256'];h=hashlib.sha256();count=0
  with gzip.open(out/'raw.log.gz','rb') as stream:
   for chunk in iter(lambda:stream.read(1024**2),b''):h.update(chunk);count+=len(chunk)
  assert h.hexdigest()==done['raw_uncompressed_sha256'] and count==done['raw_uncompressed_bytes'];proof={'status':'NEW_REPAIR_NATIVE_STOP_UNACCEPTED_ROOT_CAUSE_REQUIRES_REVIEW','cohort':cell,'uuid':done['uuid'],'stop_reason':done['stop_reason'],'returncode':done['launcher_wait_returncode'],'accepted_cycles':None,'raw_compressed_sha256':done['raw_sha256'],'raw_uncompressed_sha256':h.hexdigest(),'model_automatic_retries':0};p=R/'analysis'/(cell+'.FAILED_VALIDATION.json')
  if p.exists():assert read(p)==proof
  else:put(p,proof)
 else:
  proof=load('repair_independent_strict','recovery12_strict_v1.py').terminal(cell);sp=out/'REPAIR_STRICT.json'
  if sp.exists():assert read(sp)==proof
  else:put(sp,proof)
  qualification={'status':'REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE','cohort':cell,'uuid':done['uuid'],'strict_sha256':sha(sp),'accepted_cycles':None,'correctness_validation_only':True,'SOURCE_KEEP':True};qp=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')
  if qp.exists():assert read(qp)==qualification
  else:put(qp,qualification)
 archive=archive_closed(cell);result={'state':'FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY' if failed else 'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE','cohort':cell,'uuid':done['uuid'],'correctness_validation_only':True,'accepted_cycles':None,'proof':proof,'archive':archive,'never_merge_into_original288':True};rp=R/'analysis'/(cell+'.RESULT.json')
 if rp.exists():assert read(rp)==result
 else:put(rp,result)
 return result
ZERO_START_HOLD_REASONS={'RESOURCE_HOLD','RESOURCE_HOLD_NO_START','RESOURCE_HOLD_AFTER_DTC_PAIR','DTC original memory/paired/native-device admission HOLD'}
def parsed_zero_start_admission_hold(stderr):
 try:proof=json.loads(stderr)
 except (ValueError,TypeError):return None
 if not isinstance(proof,dict):return None
 if proof.get('status')=='HOLD' and proof.get('error_type')=='RuntimeError' and proof.get('model_retry') is False and isinstance(proof.get('reason'),str) and proof['reason'] in ZERO_START_HOLD_REASONS:return proof
 return None
def run_cell(cell):
 engine=load('repair_worker_lease','recovery12_native_v1.py');engine.assert_parent_lease();ip=R/'control/qualification_ledger'/(cell+'.INTENT.json');assert not ip.exists();roundid=uuid.uuid4().hex
 for stage in ['prepare','run-native']:
  cmd=subprocess.run([str(N/'bin/experiment'),stage,cell,'--project','DTC_L1'],capture_output=True,text=True);put(R/'logs'/(cell+'.'+stage+'.'+roundid+'.json'),{'stdout':cmd.stdout,'stderr':cmd.stderr,'returncode':cmd.returncode})
  if cmd.returncode:
   reg,epoch,q,p=engine.registered()
   proof=parsed_zero_start_admission_hold(cmd.stderr)
   if not ip.exists() and not ip.with_name(cell+'.DONE.json').exists() and cell not in q['consumed'] and proof is not None:return {'state':'REPAIR_ADMISSION_DEFERRED_ZERO_START','cohort':cell,'error':cmd.stderr,'model_starts':0,'exact_admission_hold':proof}
   return {'state':'REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell,'error':cmd.stderr,'original_models_or_ledgers_touched':False,'model_retries':0}
 return finish_evidence(cell)
