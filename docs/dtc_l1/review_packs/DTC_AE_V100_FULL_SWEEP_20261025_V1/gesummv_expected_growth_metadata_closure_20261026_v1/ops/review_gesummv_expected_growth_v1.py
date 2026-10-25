"""Exact one-generation metadata review; default read-only, never model execution.

Future --apply performs only pinned original COPY+native restore and independent
POSTPROCESS closure outside the scientific output. Old RESULT/ledgers stay intact.
"""
import argparse,copy,datetime,fcntl,gzip,hashlib,importlib.util,json,os,pathlib,re
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');F=P('/root/data/dtc_failure_repair_20261025_v1');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';CELL='E2-AEV100-769e6d9fd5f9cd53-CH';UUID='0b3b03d2-1cfd-46d2-adc8-721c5e51c4f2';STOP='DTC_ORIGINAL_RESOURCE_POLICY:CURRENT_GUARD:expected_growth';PUB='587c163ec312d3a5abdc3c392db03048e99fa747';PROOF_SHA='2c742f501470618643f893abf2073463fa3cbdbaf617a1f730fa9ed7898e2a44';OUTBOX_SHA='b2bac008c8de73d3f6e7344129f094cd073d19d1572005374dc067fb2077e229'
PROOF=F/'analysis/new_original_failures_20261026_v1'/(CELL+'.DIAGNOSIS.json');D=F/'analysis/gesummv_expected_growth_metadata_closure_v1'
def require(v,msg):
 if not v:raise RuntimeError(msg)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def exclusive(p,b):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def encoded(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def alive(pid):
 try:s=(P('/proc')/str(pid['pid'])/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==pid['start_ticks'] and s[0] not in ['Z','X']
 except (FileNotFoundError,ProcessLookupError):return False
def validate_samples(samples,policies):
 require(samples and len(samples)==938,'unexpected outer sample population')
 require(all(x['physical_RAM_pass'] is True for x in samples),'RAM failure is different scope')
 bad=[x for x in samples if not x['physical_disk_pass']];require(len(bad)==1 and bad[0]==samples[-1],'not exact last sole disk failure')
 b=bad[0];require(b['utc']=='2026-10-25T16:40:18.963083+00:00' and b['native_free_bytes']==40906543104 and b['required_free_bytes']==40914488049,'failure snapshot identity changed')
 require(b['required_free_bytes']-b['native_free_bytes']==7944945 and b['free_inodes']>=100000,'not exact reservation margin shortage')
 require(b['local_safety_floor_bytes']==5*1024**3 and b['required_free_bytes']==b['local_safety_floor_bytes']+b['bounded_own_remaining_write_and_restore_bytes']+b['other_outstanding_write_reservations_bytes'],'required arithmetic mismatch')
 require(b['peer_reservations']==[{'request':'DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1','reserved_write_bytes':8724152320}],'peer ceiling snapshot changed')
 require(policies and len(policies)==938,'missing policy samples');stops=[p for p in policies if p['decision']['decision']=='STOP'];require(len(stops)==1 and stops[0]==policies[-1],'not exact last sole BA STOP')
 for p in policies:
  dd=p['decision'];require(dd['decision'] in ['CONTINUE','WARN','STOP'],'unrecognized BA decision')
  if dd['decision']!='STOP':require(not dd['stop_reasons'],'prior stop reason')
 dd=stops[0]['decision'];require(dd['stop_reasons']==['CURRENT_GUARD:expected_growth'] and not dd['warnings'],'different stop cause')
 require(set(dd['domains'])=={'host','cgroup'} and all(x['decision']=='CONTINUE' and not x['stop_reasons'] and not x['warnings'] for x in dd['domains'].values()),'other BA domain failure')
 require(b['elapsed_seconds']<=stops[0]['sample']['monotonic_ns']/1e9,'invalid timestamps')
 return b,stops[0]
def review():
 require(sha(PROOF)==PROOF_SHA,'published failure proof changed');published=read(F/'ops/BARRIER_RECONCILIATION_PUBLICATION_READBACK_V1.json');require(published['verified'] and published['commit']==PUB,'published source proof unavailable')
 oldproof=read(PROOF);require(oldproof['cohort']==CELL and oldproof['uuid']==UUID and oldproof['accepted_cycles'] is None,'published proof identity/acceptance mismatch')
 ip=T/'control/qualification_ledger'/(CELL+'.INTENT.json');dp=ip.with_name(CELL+'.DONE.json');intent=read(ip);done=read(dp);out=T/'DTC/run/results'/UUID;s=read(T/'control'/(CELL+'_SPEC.json'));pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');launch=read(out/'NATIVE_LAUNCH.json')
 with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as lock:
  fcntl.flock(lock,fcntl.LOCK_SH);rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';reg=read(rp);epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');require(sha(rp)==epoch['native_registry_sha256'],'authority SHA mismatch');row=copy.deepcopy(reg['registered_future_requests'][REQ]['consumed'][CELL])
 require(intent['uuid']==done['uuid']==row['uuid']==UUID and done['cohort']==intent['cohort']==CELL,'cohort UUID mismatch')
 require(sha(ip)==row['intent_sha256'] and intent['spec_sha256']==sha(T/'control'/(CELL+'_SPEC.json')),'INTENT/spec pin mismatch')
 require(done==read(out/'NATIVE_EXIT.json')==row['execution_receipt'] and intent['output']==done['output']==str(out),'actual DONE/EXIT/row mismatch')
 require(done['stop_reason']==STOP and done['launcher_wait_returncode']==-15 and done['new_attempt_consumed']==1 and done['native_simulator_observed'],'not exact spent native disk-policy STOP')
 require(not alive(pid),'old model generation still live')
 op=intent['operational_resource_profile'];binary=op['framework_binary'];require(binary==oldproof['actual_framework_binary'] and sha(binary['path'])==binary['sha256'],'actual operational binary mismatch')
 require(op['framework_commit']==oldproof['actual_launch_operational_Framework_commit'] and op['Core_commit']==oldproof['actual_launch_Core_commit'],'actual source identity mismatch')
 argv=copy.deepcopy(s['native_simulator_argv']);argv[0]=binary['path'];require(launch['argv'][-len(argv):]==argv and binary['path'] in pid['maps'],'actual argv/maps mismatch')
 for x in op['source_pins']:require(sha(x['path'])==x['sha256'],'operational source pin changed')
 for x in oldproof['evidence']:
  # RESULT is deliberately independent and may gain a newer engineering error;
  # immutable native evidence must continue matching the published raw diagnosis.
  if '/DTC/run/results/' in x['path']:require(sha(x['path'])==x['sha256'],'published native evidence changed')
 raw=out/'raw.log.gz';require(sha(raw)==done['raw_sha256'],'raw compressed SHA mismatch');rawbody=gzip.open(raw,'rb').read();require(hashlib.sha256(rawbody).hexdigest()==done['raw_uncompressed_sha256']==oldproof['raw_uncompressed_sha256'] and len(rawbody)==done['raw_uncompressed_bytes'],'raw full replay mismatch')
 require(op['framework_commit'].encode() in rawbody and op['Core_commit'][:7].encode() in rawbody,'raw actual versions missing')
 require(not any(x in rawbody for x in [b'GPGPU-Sim: *** exit detected ***',b'=== CRASH:',b'ERROR ** deadlock detected:',b'Assertion `']),'natural or different crash signature')
 progress=[]
 with gzip.open(out/'progress.jsonl.gz','rt') as f:
  for line in f:
   p=json.loads(line);require(p['seq']==len(progress)+1 and (p['pid'],p['start_ticks'],p['generation'])==(pid['pid'],pid['start_ticks'],UUID) and p['input']==s['original_environment']['DTC_AG7_INPUT_SHA'] and p['roi']==s['original_environment']['DTC_AG7_ROI_SHA'] and p['end']=='NONE','progress identity/terminal mismatch')
   if progress:require(p['mono_ns']>progress[-1]['mono_ns'] and p['completed']>=progress[-1]['completed'],'progress monotonic failure')
   progress.append(p)
 require(len(progress)==961 and progress[-1]==oldproof['progress']['last'] and progress[-1]['completed']<s['expected']['instructions'],'progress population mismatch')
 records=[json.loads(x) for x in gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt')];samples=[x for x in records if 'physical_RAM_pass' in x];policies=[x['DTC_exact_original_policy'] for x in records if 'DTC_exact_original_policy' in x];b,stop=validate_samples(samples,policies)
 require(0<=done['elapsed_seconds']-b['elapsed_seconds']<2 and abs(stop['sample']['monotonic_ns']/1e9-pid['start_ticks']/os.sysconf('SC_CLK_TCK')-b['elapsed_seconds'])<1,'resource STOP/actual generation elapsed window mismatch')
 trace=(out/'actual_file_process_network.log').read_text();require(re.search(str(pid['pid'])+r' \+\+\+ killed by SIGTERM \+\+\+',trace) is not None,'actual target SIGTERM termination missing')
 require(not (out/'AEFAIR_STRICT.json').exists(),'unexpected positive strict marker')
 resultpath=T/'analysis'/(CELL+'.RESULT.json');original_result=read(resultpath);require(original_result['cohort']==CELL and original_result['state']=='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS' and original_result['error']=="AssertionError('not a reviewed closed failure signature')",'old engineering preimage not exact')
 ap=T/'control'/(CELL+'_ARCHIVE_RECEIPT.json');obpath=T/'tools/sweep_outbox.py';require(sha(obpath)==OUTBOX_SHA,'pinned original outbox changed');outbox=load(obpath,'independent_gesu_original_outbox');manifest=outbox.manifest_for(CELL);require(manifest['scientific_status']=='STOP_UNACCEPTED','manifest scientific state mismatch')
 bundle=outbox.NAS/CELL/manifest['txid'];existing=ap.exists() or (bundle/'COMMIT.json').exists();archive=None
 if existing:
  require(ap.exists(),'committed archive without local receipt requires explicit original outbox reconciliation, not independent overwrite')
  archive=verify_archive(outbox,manifest,read(ap))
 return dict(schema='DTC_GESUMMV_EXPECTED_GROWTH_INDEPENDENT_READ_ONLY_REVIEW_V1',status='CLOSED_DISK_RESERVATION_MARGIN_STOP_UNACCEPTED',cohort=CELL,uuid=UUID,recorded_stop_reason=STOP,accepted_cycles=None,scientific_acceptance=False,partial_cycles_accepted=False,models_started=0,signals=0,authority_changes=0,published_diagnosis_commit=PUB,published_diagnosis_path=str(PROOF),published_diagnosis_sha256=PROOF_SHA,actual_framework_commit=op['framework_commit'],actual_core_commit=op['Core_commit'],frozen_ancestor_framework_commit=s['framework_commit'],raw_compressed_sha256=done['raw_sha256'],raw_uncompressed_sha256=done['raw_uncompressed_sha256'],raw_uncompressed_bytes=len(rawbody),progress_records=len(progress),last_progress=progress[-1],resource_samples=len(samples),last_failing_sample=b,last_policy_stop=stop,shortfall_bytes=7944945,shortfall_MiB=7944945/1024**2,root_cause='Observed physical_disk_pass false from finite known-write reservation margin; sole CURRENT_GUARD expected_growth STOP, RAM and host/cgroup domains pass. No actual disk-full, OOM, model assertion or accepted performance implied.',classifier_gap='Frozen failure-review fallback only admits old deadlock/telemetry signatures; exact expected_growth was omitted.',old_RESULT_path=str(resultpath),old_RESULT_sha256=sha(resultpath),intent_sha256=sha(ip),DONE_sha256=sha(dp),NATIVE_EXIT_sha256=sha(out/'NATIVE_EXIT.json'),outbox_sha256=OUTBOX_SHA,manifest_sha256=outbox.sha(outbox.canon(manifest)),archive_already_exists=existing,archive=archive,source_disposition='SOURCE_KEEP',tool_sha256=sha(__file__))
def verify_archive(outbox,manifest,receipt):
 require(receipt['cohort']==CELL and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['scientific_status']=='STOP_UNACCEPTED','archive receipt mismatch')
 bundle=P(receipt['target_mount_path']);require(bundle==outbox.NAS/CELL/manifest['txid'] and read(bundle/'SOURCE_MANIFEST.json')==manifest,'archive/source manifest drift')
 f,v=outbox.libraries(bundle);idx=f.verify_archive(bundle,manifest);restored=f.check_native(P(receipt['native_restore']),manifest);require(idx['archive_sha256']==receipt['archive_sha256'] and len(restored)==len(manifest['entries']),'archive/restore mismatch')
 return dict(receipt=receipt,independently_verified_restored_entries=len(restored))
def apply(plan_path,publication_path):
 """Only called following root's specific publication/execution authorization."""
 plan=read(plan_path);pub=read(publication_path);require(pub['verified'] and pub['tool_sha256']==sha(__file__) and pub['qualification_sha256']==sha(F/'ops/GESUMMV_EXPECTED_GROWTH_REVIEW_CPU_QUALIFICATION_V1.json'),'new review publication/source proof missing')
 fresh=review();require(plan==fresh,'review plan drift; no writes or archive attempted')
 dest=D/UUID;result=dest/'POSTPROCESS.RESULT.json';require(not result.exists(),'metadata closure already exists; independently verify it instead of overwriting')
 # The original output tree is never appended. Only the already-pinned original
 # archive coordinator writes COPY/restore. A resource/receiver HOLD creates no
 # independent metadata result and can be inspected before an authorized retry.
 original=P(fresh['old_RESULT_path']);outbox=load(T/'tools/sweep_outbox.py','gesu_close_original_outbox');manifest=outbox.manifest_for(CELL);ap=T/'control'/(CELL+'_ARCHIVE_RECEIPT.json')
 if ap.exists():archive=verify_archive(outbox,manifest,read(ap));copied=False
 else:
  require(not (outbox.NAS/CELL/manifest['txid']/'COMMIT.json').exists(),'committed archive appeared; stop for separate original outbox receipt recovery')
  outbox.archive(CELL);archive=verify_archive(outbox,manifest,read(ap));copied=True
 require(sha(original)==fresh['old_RESULT_sha256'] and outbox.sha(outbox.canon(outbox.manifest_for(CELL)))==fresh['manifest_sha256'],'old RESULT/output drift during closure')
 exclusive(dest/'OLD_ENGINEERING_RESULT.PREIMAGE.json',original.read_bytes());exclusive(dest/'REVIEW.json',encoded(fresh))
 closed=dict(schema='ORIGINAL_EXPECTED_GROWTH_INDEPENDENT_POSTPROCESS_CLOSURE_V1',state='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY',cohort=CELL,uuid=UUID,accepted_cycles=None,scientific_acceptance=False,partial_cycles_accepted=False,archive=archive,review_sha256=sha(dest/'REVIEW.json'),review_tool_sha256=sha(__file__),old_RESULT_preserved=True,old_RESULT_sha256=sha(original),DONE_sha256=fresh['DONE_sha256'],NATIVE_EXIT_sha256=fresh['NATIVE_EXIT_sha256'],publication_commit=pub['commit'],COPY_invoked=copied,models_started=0,model_retries=0,signals=0,authority_changes=0,source_disposition='SOURCE_KEEP',utc=now());exclusive(result,encoded(closed));return closed
def main():
 p=argparse.ArgumentParser();p.add_argument('--review-output',type=P);p.add_argument('--apply',action='store_true');p.add_argument('--plan',type=P);p.add_argument('--publication',type=P);a=p.parse_args()
 if a.apply:require(a.plan is not None and a.publication is not None,'apply requires reviewed plan and source publication');print(json.dumps(apply(a.plan,a.publication),indent=2));return
 proof=review()
 if a.review_output:exclusive(a.review_output,encoded(proof))
 print(json.dumps(dict(status='READ_ONLY_REVIEW_PASS_UNACCEPTED',cohort=CELL,uuid=UUID,archive_already_exists=proof['archive_already_exists'],shortfall_bytes=proof['shortfall_bytes'],review_output=str(a.review_output) if a.review_output else None,tool_sha256=sha(__file__),models_started=0,archive_COPY_calls=0,authority_changes=0)))
if __name__=='__main__':main()
