import pathlib,json,ast,hashlib
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');old=T/'tools/revision2/sweep_controller.py';s=old.read_text();changes=[]
def replace(a,b,n=1):
 global s
 assert s.count(a)==n,(a,s.count(a));s=s.replace(a,b);changes.append(a[:150])
replace("def install(native,lease):", "def unused_original_install(native,lease):")
adopt='''def adopt(native,lease):
 pub=read(T/'control/CONTINUATION_R3_PUBLICATION_READBACK.json');qual=read(T/'control/CONTINUATION_R3_ZERO_MODEL_QUALIFICATION.json')
 assert pub['verified'] and pub['controller_sha256']==sha(__file__) and pub['failure_review_sha256']==sha(T/'tools/sweep_failure_review.py') and qual['status']=='PASS'
 old=read(T/'control/CONTROLLER_LAUNCH_R2.json');p=P('/proc')/str(old['pid'])
 if p.exists():assert int((p/'stat').read_text().rsplit(')',1)[1].split()[19])!=old['start_ticks'],'old controller generation still live'
 reg,epoch=native.read_current_authority();q=reg['registered_future_requests'][REQ];assert q['state']=='RUNNING' and q['budget']==356
 assert not read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 failure=module('closed_failure_adoption','sweep_failure_review.py');recovered={}
 for cell,row in q['consumed'].items():
  assert 'execution_receipt' in row,'active or unclosed prior model cannot be adopted'
  resultfile=T/'analysis'/(cell+'.RESULT.json');result=read(resultfile)
  if result['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE':recovered[cell]=result;continue
  proof=failure.classify(cell);receipt=read(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'));assert receipt['scientific_status']=='STOP_UNACCEPTED' and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
  outbox=module('closed_failure_archive_adoption','sweep_outbox.py');bundle=P(receipt['target_mount_path']);f,v=outbox.libraries(bundle);manifest=read(bundle/'SOURCE_MANIFEST.json');idx=f.verify_archive(bundle,manifest);assert idx['archive_sha256']==receipt['archive_sha256'];f.check_native(P(receipt['native_restore']),manifest)
  pre=T/'analysis/issue_preimages';pre.mkdir(exist_ok=True);saved=pre/(cell+'.RESULT_R2.json');assert not saved.exists();saved.write_bytes(resultfile.read_bytes())
  recovered[cell]={'state':'FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY','cohort':cell,'uuid':row['uuid'],'failure_classification':proof,'archive':receipt,'accepted_cycles':None,'partial_cycles_accepted':False};write(resultfile,recovered[cell])
 before=dict(q);write(T/'control/REQUEST_BEFORE_CONTINUATION_R3.json',q)
 def amend(r):
  actual=r['registered_future_requests'][REQ];assert actual==before
  actual['operational_continuations']=actual.get('operational_continuations',[])+[{'revision':'R3','prior_orchestrator_sha256':actual['orchestrator_sha256'],'new_orchestrator_sha256':sha(__file__),'failure_classifier_sha256':sha(T/'tools/sweep_failure_review.py'),'publication_commit':pub['commit'],'qualification_sha256':sha(T/'control/CONTINUATION_R3_ZERO_MODEL_QUALIFICATION.json'),'prior_consumed':len(actual['consumed']),'same_finite_budget':356,'model_retries':0}]
  actual['orchestrator_sha256']=sha(__file__)
 native.update_authority(amend)
 after=native.read_current_authority()[0]['registered_future_requests'][REQ];assert all(after[k]==v for k,v in before.items() if k not in ['orchestrator_sha256','operational_continuations'])
 write(T/'control/CONTINUATION_R3_ADOPTED.json',{'state':'ALL_PRIOR_SPENT_CELLS_ADOPTED_NO_RERUN','consumed':len(before['consumed']),'remaining':before['remaining'],'accepted':sum(x['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' for x in recovered.values()),'closed_unaccepted':sum(x['state'].startswith('FAIL_CLOSED') for x in recovered.values()),'lease':lease})
 return recovered

'''
replace('def main():',adopt+'def main():')
replace("owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b');fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB)","owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b')\n while True:\n  try:fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB);break\n  except BlockingIOError:event({'state':'WAIT_PREVIOUS_OWNED_CONTROLLER_NATURAL_CLOSE','new_model_starts':0});time.sleep(30)")
replace("assert not (T/'control/CONTROLLER_START_R2.json').exists()","assert not (T/'control/CONTROLLER_START_R3.json').exists()")
replace("write(T/'control/BATCH_LEASE.json',lease);write(T/'control/CONTROLLER_START_R2.json',lease);install(native,lease)","recovered=adopt(native,lease);write(T/'control/BATCH_LEASE.json',lease);write(T/'control/CONTROLLER_START_R3.json',lease)")
replace('admitted={};holds={};results={};running={};issues=False;start_count=0','admitted={};holds={};results=recovered;running={};issues=False;start_count=0')
replace("except BaseException as e:\n  intent=T/'control/qualification_ledger'", "except BaseException as e:\n  try:\n   failure=module('closed_failure_'+cell.replace('-','_'),'sweep_failure_review.py');proof=failure.classify(cell);archive=archive_closed(cell);assert archive['scientific_status']=='STOP_UNACCEPTED'\n   result={'state':'FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY','cohort':cell,'uuid':proof['uuid'],'failure_classification':proof,'archive':archive,'accepted_cycles':None,'partial_cycles_accepted':False};event(result);return result\n  except BaseException as diagnosis_error:event({'state':'FAILURE_CLASS_NOT_REVIEWED_CHECKPOINT','cohort':cell,'error':repr(diagnosis_error)})\n  intent=T/'control/qualification_ledger'")
replace("if result['state']!='PASS_STRICT_ARCHIVE_NATIVE_RESTORE':issues=True", "if result['state'] not in ['PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY']:issues=True")
replace("'closed_point_results':len(results)","'closed_point_results':len(results),'closed_unaccepted_points':sum(x['state'].startswith('FAIL_CLOSED') for x in results.values())")
replace("state='ALL_ELIGIBLE_NATIVE_POINTS_ACCEPTED_ARCHIVED_RESTORED',input_holds=holds", "state='ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES',input_holds=holds,closed_unaccepted_points={k:v for k,v in results.items() if v['state'].startswith('FAIL_CLOSED')}")
ast.parse(s);dest=T/'tools/revision3/sweep_controller.py';dest.parent.mkdir(exist_ok=True)
with dest.open('x') as f:f.write(s)
proof={'status':'PREPARED_NOT_LAUNCHED','base_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'controller_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'failure_review_sha256':hashlib.sha256((T/'tools/sweep_failure_review.py').read_bytes()).hexdigest(),'new_source':str(dest),'adaptation_sites':changes,'scope':'Wait exact prior finite controller/active models to close naturally;adopt spent results;continue only original unused exact cells. Only rechecked deadlock/SIGABRT class is closed as unaccepted,all other failures still checkpoint. No binary/config/input/native launcher changes or retries.','final_delivery_draft_notice':'Earlier consumer/preparer assumes all points PASS. Before final delivery,extend independent consumer/report to include every classified failed point and incomplete comparison. Do not relabel failure as scientific PASS or discard it.'}
with (T/'analysis/CONTINUATION_R3_PREPARATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps({k:v for k,v in proof.items() if k!='adaptation_sites'},indent=2))
