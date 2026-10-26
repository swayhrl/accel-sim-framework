"""Finite2 original negative metadata closure; default read-only.

New exact-scope reviewer derived from published GESUMMV review. No resource
policy changes, scientific execution, old RESULT/ledger writes, or out appends.
"""
import argparse,copy,datetime,fcntl,gzip,hashlib,importlib.util,json,os,pathlib,re
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=F/'analysis/two_stencil_expected_growth_metadata_closure_v1';REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';STOP='DTC_ORIGINAL_RESOURCE_POLICY:CURRENT_GUARD:expected_growth';DIAG=F/'analysis/TWO_STENCIL_EXPECTED_GROWTH_READONLY_DIAGNOSIS_20261026_V1.json';DIAG_SHA='77804c818ad56d40e6c6d9345c5895e0b415ee5ef85a046bf87f3424aa5b849f';OUTBOX_SHA='b2bac008c8de73d3f6e7344129f094cd073d19d1572005374dc067fb2077e229';BASE_REVIEW=F/'ops/review_gesummv_expected_growth_v1.py';BASE_SHA='3e3fc02241b7af259b363ba7da61d300b1e73489d137ea9dcaaca821ee01ca22';QUAL=F/'ops/TWO_STENCIL_EXPECTED_GROWTH_REVIEW_CPU_QUALIFICATION_V1.json'
CELLS={'E2-AEV100-c885293ad99e21ee-CM':{'uuid':'aa2a9d12-99a9-4cab-b934-964efe5936c1','progress':461,'utc':'2026-10-26T02:41:59.478252+00:00','free':36526264320,'required':36526810801,'shortfall':546481},'E2-AEV100-c885293ad99e21ee-DH':{'uuid':'be98901a-2730-4ea9-86d2-854bab0a59c8','progress':419,'utc':'2026-10-26T02:41:59.582810+00:00','free':36525805568,'required':36526810801,'shortfall':1005233}}
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def exclusive(p,body):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as s:s.write(body);s.flush();os.fsync(s.fileno())
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def alive(pid):
 try:s=(P('/proc')/str(pid['pid'])/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==pid['start_ticks'] and s[0]not in ['Z','X']
 except (FileNotFoundError,ProcessLookupError):return False
def validate_identity(cell,i,d,row,exit,out,spec_sha,intent_sha):
 require(cell in CELLS,'outside finite2 stencil scope');uid=CELLS[cell]['uuid']
 require(i['cohort']==d['cohort']==cell and i['uuid']==d['uuid']==row['uuid']==uid,'cohort/UUID mismatch')
 require(row['intent_sha256']==intent_sha and i['spec_sha256']==spec_sha,'INTENT/spec SHA mismatch')
 require(d==exit==row['execution_receipt'] and i['output']==d['output']==str(out),'real DONE/EXIT/execution_receipt/output mismatch')
 require(d['stop_reason']==STOP and d['launcher_wait_returncode']==-15 and d['native_simulator_observed'] is True and d['new_attempt_consumed']==1 and d['actual_simulator_wait_and_file_evidence'] and d['launcher_is_strace_parent_of_native_simulator'] is True,'different native completion or absent actual wait evidence')
def validate_samples(cell,samples,policies):
 c=CELLS[cell];require(len(samples)==len(policies)==288,'each stream must contain288 records;576 is combined outer+policy, not outer count')
 require(all(r['physical_RAM_pass'] is True for r in samples),'RAM failure outside this scope');bad=[r for r in samples if not r['physical_disk_pass']];require(len(bad)==1 and bad[0]==samples[-1],'not sole final disk failure')
 b=bad[0];require(b['utc']==c['utc'] and b['native_free_bytes']==c['free'] and b['required_free_bytes']==c['required'] and b['required_free_bytes']-b['native_free_bytes']==c['shortfall'],'different observed disk snapshot')
 require(b['free_inodes']>=100000 and b['local_safety_floor_bytes']==5*1024**3 and b['required_free_bytes']==b['local_safety_floor_bytes']+b['bounded_own_remaining_write_and_restore_bytes']+b['other_outstanding_write_reservations_bytes'],'floor/known-write arithmetic or inode scope mismatch')
 peers=[{'request':'DTC_AE_LATE_FAILURE_REPAIR_20261026_V1','reserved_write_bytes':3221225472},{'request':'DTC_AE_LAVAMEM_REPAIR_20261026_V2','reserved_write_bytes':1610612736}];require(b['peer_reservations']==peers and b['other_outstanding_write_reservations_bytes']==sum(x['reserved_write_bytes'] for x in peers),'historical peer ceiling changed')
 stops=[r for r in policies if r['decision']['decision']=='STOP'];require(len(stops)==1 and stops[0]==policies[-1],'not sole final BA STOP')
 for r in policies:
  d=r['decision'];require(d['decision']in ['CONTINUE','WARN','STOP'],'unknown BA decision')
  if d['decision']!='STOP':require(not d['stop_reasons'],'earlier stop reason')
 d=stops[0]['decision'];require(d['stop_reasons']==['CURRENT_GUARD:expected_growth'] and not d['warnings'],'different BA cause');require(set(d['domains'])=={'host','cgroup'} and all(x['decision']=='CONTINUE' and not x['stop_reasons'] and not x['warnings'] for x in d['domains'].values()),'other host/cgroup cause')
 return b,stops[0]
def verify_archive(cell,ob,manifest,receipt):
 require(receipt['cohort']==cell and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['scientific_status']=='STOP_UNACCEPTED','archive science/identity mismatch');bundle=P(receipt['target_mount_path']);require(bundle==ob.NAS/cell/manifest['txid'] and read(bundle/'SOURCE_MANIFEST.json')==manifest,'archive manifest mismatch');f,v=ob.libraries(bundle);index=f.verify_archive(bundle,manifest);restored=f.check_native(P(receipt['native_restore']),manifest);require(index['archive_sha256']==receipt['archive_sha256'] and len(restored)==len(manifest['entries']),'archive or native restore mismatch');return {'receipt':receipt,'independently_verified_restored_entries':len(restored)}
def review_point(cell):
 require(cell in CELLS,'outside finite2 scope');require(sha(DIAG)==DIAG_SHA and sha(BASE_REVIEW)==BASE_SHA,'diagnosis/published reference source drift');c=CELLS[cell];uid=c['uuid'];diagnosis=read(DIAG);prior=next(x for x in diagnosis['points'] if x['cohort']==cell);require(prior['uuid']==uid and prior['accepted_cycles'] is None and prior['model_retries']==0,'diagnosis identity/acceptance drift')
 ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');sp=T/'control'/(cell+'_SPEC.json');i=read(ip);d=read(dp);s=read(sp);out=T/'DTC/run/results'/uid;pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');launch=read(out/'NATIVE_LAUNCH.json')
 with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as lock:
  fcntl.flock(lock,fcntl.LOCK_SH);rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';reg=read(rp);epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');require(sha(rp)==epoch['native_registry_sha256'],'authority hash mismatch');row=copy.deepcopy(reg['registered_future_requests'][REQ]['consumed'][cell])
 validate_identity(cell,i,d,row,read(out/'NATIVE_EXIT.json'),out,sha(sp),sha(ip));require(d==prior['DONE'] and s['program']=='stencil','diagnosed native receipt/program mismatch');require(not alive(pid) and not(P('/proc')/str(launch['launcher_pid'])).exists(),'model generation or launcher PID still present')
 op=i['operational_resource_profile'];binary=op['framework_binary'];require(binary['sha256']=='b963139b72ea1fe5000c35803386f3a5b5eaf4905e127f1bdb12f16e13486329' and sha(binary['path'])==binary['sha256'] and op['framework_commit']=='3b362ab5c0934fdcea9697b10244c6de5c4a14ae' and op['Core_commit']=='2e3bef4364e578cddd0e881c0baace2e51c55930','actual original source identity mismatch')
 for pin in op['source_pins']:require(sha(pin['path'])==pin['sha256'],'operational source pin drift')
 argv=copy.deepcopy(s['native_simulator_argv']);argv[0]=binary['path'];require(launch['argv'][-len(argv):]==argv and binary['path']in pid['maps'],'actual argv/maps mismatch')
 raw=out/'raw.log.gz';body=gzip.open(raw,'rb').read();require(sha(raw)==d['raw_sha256'] and hashlib.sha256(body).hexdigest()==d['raw_uncompressed_sha256'] and len(body)==d['raw_uncompressed_bytes'],'raw dual SHA/size mismatch');require(op['framework_commit'].encode()in body and op['Core_commit'][:7].encode()in body,'raw versions absent');require(not any(x in body for x in [b'GPGPU-Sim: *** exit detected ***',b'=== CRASH:',b'ERROR ** deadlock detected:',b'Assertion `',b'std::bad_alloc']),'natural/different fatal signature')
 progress=[]
 for line in gzip.open(out/'progress.jsonl.gz','rt'):
  p=json.loads(line);require(p['seq']==len(progress)+1 and (p['pid'],p['start_ticks'],p['generation'])==(pid['pid'],pid['start_ticks'],uid) and p['input']==s['original_environment']['DTC_AG7_INPUT_SHA'] and p['roi']==s['original_environment']['DTC_AG7_ROI_SHA'] and p['end']=='NONE','progress identity/sequence/terminal mismatch')
  if progress:require(p['mono_ns']>progress[-1]['mono_ns'] and p['completed']>=progress[-1]['completed'],'progress monotonicity failure')
  progress.append(p)
 require(len(progress)==c['progress']==prior['progress_count'] and progress[-1]==prior['last_progress'] and progress[-1]['completed']<s['expected']['instructions'],'progress population mismatch')
 records=[json.loads(x) for x in gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt')];samples=[x for x in records if 'physical_RAM_pass'in x];policies=[x['DTC_exact_original_policy'] for x in records if 'DTC_exact_original_policy'in x];b,stop=validate_samples(cell,samples,policies);require(len(records)==prior['sample_count']==576,'combined stream count mismatch')
 require(0<=d['elapsed_seconds']-b['elapsed_seconds']<2 and abs(stop['sample']['monotonic_ns']/1e9-pid['start_ticks']/os.sysconf('SC_CLK_TCK')-b['elapsed_seconds'])<1,'STOP/generation elapsed window mismatch');trace=(out/'actual_file_process_network.log').read_text();require(re.search(str(pid['pid'])+r' \+\+\+ killed by SIGTERM \+\+\+',trace)is not None,'target actual SIGTERM absent');require(not(out/'AEFAIR_STRICT.json').exists(),'positive strict marker outside negative scope')
 resultpath=T/'analysis'/(cell+'.RESULT.json');old=read(resultpath);require(old==prior['old_canonical_RESULT'] and old['cohort']==cell and old['state']=='RESOLVING_ISSUE_NO_MODEL_RETRY' and 'not a reviewed closed failure signature'in old['error'] and old['partial_cycles_accepted'] is False,'old resolving preimage changed')
 obpath=T/'tools/sweep_outbox.py';require(sha(obpath)==OUTBOX_SHA,'original outbox changed');ob=load(obpath,'stencil_readonly_original_outbox');manifest=ob.manifest_for(cell);require(manifest['scientific_status']=='STOP_UNACCEPTED','manifest positive science state');ap=T/'control'/(cell+'_ARCHIVE_RECEIPT.json');bundle=ob.NAS/cell/manifest['txid'];existing=ap.exists() or(bundle/'COMMIT.json').exists();archive=None
 if existing:require(ap.exists(),'committed164 archive lacks local receipt; explicit original recovery required');archive=verify_archive(cell,ob,manifest,read(ap))
 return {'schema':'FINITE2_STENCIL_EXPECTED_GROWTH_INDEPENDENT_NEGATIVE_REVIEW_V1','status':'CLOSED_DISK_RESERVATION_MARGIN_STOP_UNACCEPTED','cohort':cell,'uuid':uid,'accepted_cycles':None,'scientific_acceptance':False,'partial_cycles_accepted':False,'recorded_stop_reason':STOP,'returncode':-15,'diagnosis_path':str(DIAG),'diagnosis_sha256':DIAG_SHA,'published_GESUMMV_reference_source_sha256':BASE_SHA,'actual_framework_commit':op['framework_commit'],'actual_core_commit':op['Core_commit'],'raw_compressed_sha256':d['raw_sha256'],'raw_uncompressed_sha256':d['raw_uncompressed_sha256'],'raw_uncompressed_bytes':len(body),'progress_records':len(progress),'last_progress':progress[-1],'outer_samples':len(samples),'policy_samples':len(policies),'combined_record_count':len(records),'last_failing_sample':b,'last_policy_stop':stop,'shortfall_bytes':c['shortfall'],'shortfall_MiB':c['shortfall']/1024**2,'old_RESULT_path':str(resultpath),'old_RESULT_sha256':sha(resultpath),'INTENT_sha256':sha(ip),'DONE_sha256':sha(dp),'NATIVE_EXIT_sha256':sha(out/'NATIVE_EXIT.json'),'outbox_sha256':OUTBOX_SHA,'source_manifest_sha256':ob.sha(ob.canon(manifest)),'archive_already_exists':existing,'archive':archive,'resource_policy_relaxed':False,'models_started':0,'signals':0,'authority_changes':0,'tool_sha256':sha(__file__),'SOURCE_KEEP':True}
def review():return {'schema':'FINITE2_STENCIL_EXPECTED_GROWTH_READ_ONLY_PLAN_V1','tool_sha256':sha(__file__),'diagnosis_sha256':DIAG_SHA,'points':[review_point(c) for c in CELLS],'models_started':0,'real_COPY_calls':0,'authority_changes':0}
def stable(point):return {k:v for k,v in point.items() if k not in ['archive_already_exists','archive']}
def apply_point(planned,publication):
 cell=planned['cohort'];fresh=review_point(cell);require(stable(planned)==stable(fresh),'immutable native review plan drift');dest=D/fresh['uuid'];result=dest/'POSTPROCESS.RESULT.json';ob=load(T/'tools/sweep_outbox.py','stencil_apply_original_outbox');manifest=ob.manifest_for(cell);ap=T/'control'/(cell+'_ARCHIVE_RECEIPT.json');original=P(fresh['old_RESULT_path'])
 if result.exists():
  closed=read(result);stored=read(dest/'REVIEW.json');require(closed['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY' and closed['cohort']==cell and closed['uuid']==fresh['uuid'] and closed['accepted_cycles'] is None and closed['scientific_acceptance'] is False and closed['partial_cycles_accepted'] is False and closed['review_tool_sha256']==sha(__file__) and closed['old_RESULT_sha256']==sha(original) and closed['DONE_sha256']==fresh['DONE_sha256'] and closed['NATIVE_EXIT_sha256']==fresh['NATIVE_EXIT_sha256'],'existing negative closure conflict');require(closed['review_sha256']==sha(dest/'REVIEW.json') and stable(stored)==stable(fresh) and sha(dest/'OLD_RESOLVING_RESULT.PREIMAGE.json')==fresh['old_RESULT_sha256'],'stored review/preimage changed');require(closed['model_starts']==closed['model_retries']==closed['signals']==closed['authority_changes']==0 and closed['resource_policy_relaxed'] is False,'existing closure safety fields changed');require(ap.exists(),'existing closure missing archive');require(verify_archive(cell,ob,manifest,read(ap))==closed['archive'],'existing closure archive/restore drift');return closed
 if ap.exists():archive=verify_archive(cell,ob,manifest,read(ap));copied=False
 else:
  require(not(ob.NAS/cell/manifest['txid']/'COMMIT.json').exists(),'committed archive without receipt requires recovery');ob.archive(cell);archive=verify_archive(cell,ob,manifest,read(ap));copied=True
 require(sha(original)==fresh['old_RESULT_sha256'] and ob.sha(ob.canon(ob.manifest_for(cell)))==fresh['source_manifest_sha256'],'old RESULT/out changed during closure');exclusive(dest/'OLD_RESOLVING_RESULT.PREIMAGE.json',original.read_bytes());exclusive(dest/'REVIEW.json',encoded(fresh))
 closed={'schema':'FINITE2_ORIGINAL_STENCIL_EXPECTED_GROWTH_POSTPROCESS_V1','state':'FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY','cohort':cell,'uuid':fresh['uuid'],'accepted_cycles':None,'scientific_acceptance':False,'partial_cycles_accepted':False,'archive':archive,'review_sha256':sha(dest/'REVIEW.json'),'review_tool_sha256':sha(__file__),'old_RESULT_preserved':True,'old_RESULT_sha256':sha(original),'DONE_sha256':fresh['DONE_sha256'],'NATIVE_EXIT_sha256':fresh['NATIVE_EXIT_sha256'],'publication_commit':publication['commit'],'COPY_invoked':copied,'model_starts':0,'model_retries':0,'signals':0,'authority_changes':0,'resource_policy_relaxed':False,'SOURCE_KEEP':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};exclusive(result,encoded(closed));return closed
def apply(plan_path,publication_path):
 plan=read(plan_path);pub=read(publication_path);qualification=read(QUAL);require(pub['verified'] and pub['commit'] and pub['tool_sha256']==sha(__file__) and pub['qualification_sha256']==sha(QUAL) and pub['plan_sha256']==sha(plan_path) and pub['diagnosis_sha256']==DIAG_SHA,'exact publication/source/qualification/plan missing');require(qualification['status']=='PASS' and qualification['tool_sha256']==sha(__file__) and qualification['plan_sha256']==sha(plan_path) and qualification['diagnosis_sha256']==DIAG_SHA,'qualification not PASS for exact source/plan/diagnosis');require(plan['tool_sha256']==sha(__file__) and plan['diagnosis_sha256']==DIAG_SHA and [p['cohort'] for p in plan['points']]==list(CELLS),'finite2 plan/source scope mismatch')
 # All immutable evidence is rechecked before any COPY. Only archive presence
 # may change from prior successful finite-point metadata closure.
 fresh=review();require([stable(p) for p in fresh['points']]==[stable(p) for p in plan['points']],'finite2 review plan drift before COPY')
 lockpath=D/'FINITE2_APPLY.lock';lockpath.parent.mkdir(parents=True,exist_ok=True)
 with lockpath.open('a+b') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);return [apply_point(p,pub) for p in plan['points']]
def main():
 p=argparse.ArgumentParser();p.add_argument('--review-output',type=P);p.add_argument('--apply',action='store_true');p.add_argument('--plan',type=P);p.add_argument('--publication',type=P);a=p.parse_args()
 if a.apply:require(a.plan is not None and a.publication is not None,'apply needs reviewed plan and publication');print(json.dumps(apply(a.plan,a.publication),indent=2));return
 plan=review()
 if a.review_output:exclusive(a.review_output,encoded(plan))
 print(json.dumps({'status':'FINITE2_READONLY_NEGATIVE_REVIEW_PASS','points':[{'cohort':x['cohort'],'uuid':x['uuid'],'shortfall_bytes':x['shortfall_bytes'],'outer_samples':x['outer_samples'],'policy_samples':x['policy_samples'],'archive_exists':x['archive_already_exists']} for x in plan['points']],'tool_sha256':sha(__file__),'real_COPY_calls':0,'model_starts':0}))
if __name__=='__main__':main()
