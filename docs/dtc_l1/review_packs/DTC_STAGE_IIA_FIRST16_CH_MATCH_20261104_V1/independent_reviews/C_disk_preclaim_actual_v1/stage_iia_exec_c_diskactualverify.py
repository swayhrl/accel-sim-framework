from pathlib import Path
import json,hashlib,importlib.util,os,datetime
R=Path('/root/data/dtc_stage_iia_first16_20261104_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');O=A/'agents/C_disk_preclaim_actual_v1';O.mkdir(parents=True,exist_ok=True);rd=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();receiptp=R/'control/operational_amendments/disk_preclaim_v1/actual_single_callback_v1/APPLIED.json';receipt=rd(receiptp);plan=rd(R/'control/EXECUTION_PLAN.json');sp=importlib.util.spec_from_file_location('C_postpatch_actual_readonly',R/'tools/stage2_native.py');e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e);reg,ep=e.authority();q=reg['registered_future_requests'][e.REQ];matrix=rd(R/'control/MATRIX.json');checks=[]
def ck(n,b,d=None):checks.append({'check':n,'PASS':bool(b),'detail':d})
ck('Exact applied source receipt and same-owner limited amendment',sha(receiptp)=='35bcda9bb1c9c39741ebf6b23b5031a8f4117e2c28266919dea1eede5dbb72c8' and receipt['owner_pid']==1498278 and receipt['owner_start_ticks']==977758783 and receipt['source_sha256']==sha(R/'control/operational_amendments/disk_preclaim_v1/owner_disk_preclaim.py') and receipt['new_authority_grants']==receipt['new_dispatchers']==receipt['existing_models_signaled']==0 and receipt['only_adds_disk_check_before_future_claim'])
ck('Frozen62 source pins and original plan unchanged',receipt['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')=='56efce4221b9b4a192552ad530ac94a1232024f23da2b7f0045c7bd72e8f5716' and all(sha(x['path'])==x['sha256'] for x in plan['source_pins']))
ck('Existing5 model UUID identities retained without reset/refund',all(q['consumed'][c]['uuid']==u for c,u in receipt['before']['consumed_UUIDs'].items()) and q['budget']==16 and q['remaining']==16-len(q['consumed']) and len(q['consumed'])<=16 and set(q['consumed'])<=set(q['admitted_specs'])=={x['cohort']for x in matrix['points']} and q['model_automatic_retries']==0)
prior=[]
for c,u in receipt['before']['consumed_UUIDs'].items():
 out=R/'DTC/run/results'/u;pid=rd(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=Path('/proc')/str(pid['pid']);live=False
 if proc.exists():
  st=(proc/'stat').read_text().rsplit(')',1)[1].split();live=int(st[19])==pid['start_ticks']and st[0]not in['Z','X']
 dp=R/'control/qualification_ledger'/(c+'.DONE.json');done=rd(dp)if dp.exists()else None;prior.append({'cohort':c,'uuid':u,'pid':pid['pid'],'start_ticks':pid['start_ticks'],'live_same_generation':live,'natural_done_if_closed':bool(done and done.get('stop_reason')is None and done.get('launcher_wait_returncode')==0),'stop_reason_if_closed':done.get('stop_reason')if done else None,'PASS':live or bool(done and done.get('stop_reason')is None and done.get('launcher_wait_returncode')==0)})
ck('All prepatch5 healthy model generations remain alive or naturally closed',all(x['PASS']for x in prior),prior)
oldq=reg['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];oldsha=hashlib.sha256(json.dumps(oldq,sort_keys=True,separators=(',',':')).encode()).hexdigest();ck('Old StageI full request still unchanged',oldsha==rd(A/'agents/C/OWNER_AND_NATIVE_PATTERN_READONLY.json')['old_request_canonical_sha256'])
postevents=[]
for p in (A/'events').glob('*DISPATCH_AUTHORIZED_UNUSED_IDENTITY.json'):
 v=rd(p)
 if v['UTC']>receipt['UTC']:postevents.append({'cohort':v['cohort'],'UTC':v['UTC'],'host_cpu':v['cpu'],'event_path':str(p),'event_sha256':sha(p),'consumed_after':v['cohort']in q['consumed']})
postevents.sort(key=lambda x:x['UTC']);ck('Observed further legal dispatch after amendment without scope expansion',len(postevents)>0 and all(x['cohort']in q['admitted_specs'] for x in postevents),postevents)
accepted=[];live=[];stop=[]
for c,row in q['consumed'].items():
 out=R/'DTC/run/results'/row['uuid'];pidp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 if pidp.exists():
  pp=rd(pidp);proc=Path('/proc')/str(pp['pid'])
  if proc.exists():
   st=(proc/'stat').read_text().rsplit(')',1)[1].split()
   if int(st[19])==pp['start_ticks']and st[0]not in['Z','X']:live.append(c)
 dp=R/'control/qualification_ledger'/(c+'.DONE.json')
 if dp.exists()and rd(dp).get('stop_reason'):stop.append({'cohort':c,'stop_reason':rd(dp)['stop_reason']})
 rp=R/'analysis'/(c+'.RESULT.json')
 if rp.exists()and rd(rp).get('state')=='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE':accepted.append(c)
oldmanifest=rd(A/'agents/C_actual_execution_v1/MANIFEST.json');ck('Original actual-execution verification package unchanged',all(sha(A/'agents/C_actual_execution_v1'/x['path'])==x['sha256']for x in oldmanifest['files']))
out={'schema':'DTC_STAGE_IIA_C_DISK_PRECLAIM_ACTUAL_VERIFICATION_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_checks_PASS':all(x['PASS']for x in checks),'checks':checks,'APPLIED_receipt_path':str(receiptp),'APPLIED_sha256':sha(receiptp),'runtime_overlay_source_sha256':receipt['source_sha256'],'budget':16,'consumed_snapshot':len(q['consumed']),'remaining_snapshot':q['remaining'],'live_snapshot':len(live),'accepted_new_CH_at_snapshot':len(accepted),'guard_stop_outcomes_at_snapshot':stop,'models_before_patch':prior,'postpatch_dispatch_events':postevents,'models_started_or_signaled_by_this_review':0,'authority_or_record_mutations_by_this_review':0,'evidence_limits':['The installed operational wrapper is explicitly recorded; unchanged62 source hashes do not mean scheduler behavior is unchanged.','Source review, applied receipt and subsequent legal dispatch support behavior; no extra callback was queued to inspect private memory.','Existing ZERO_START_HOLD entries remain historical and are not model failures or consumed retries.','New runtime activity remains not performance accepted until natural strict/archive/native restore result exists.']};(O/'DISK_PRECLAIM_ACTUAL_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'allPASS':out['all_checks_PASS'],'checks':len(checks),'consumed':out['consumed_snapshot'],'remaining':out['remaining_snapshot'],'live':out['live_snapshot'],'accepted':len(accepted),'postpatch_dispatches':len(postevents),'review_sha256':sha(O/'DISK_PRECLAIM_ACTUAL_VERIFICATION.json'),'failed':[x for x in checks if not x['PASS']]},indent=2))
