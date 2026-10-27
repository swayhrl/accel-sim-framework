"""Analytical cumulative-counter and closed-source gate fixtures; no model."""
import pathlib,importlib.util,json,gzip,hashlib,tempfile,copy
H=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('sidecar_fixture',H/'raw_reason_sidecar.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=0
def ck(v):
 global checks
 assert v;checks+=1
def frame(uid,stream,reason=None,value=None,reject=None,access='GLOBAL_ACC_R'):
 out=[f'kernel_launch_uid = {uid}\n',f'kernel_stream_id = {stream}\n']
 if reject is not None:out.append(f'L2_total_cache_reservation_fails = {reject}\n')
 if reason is not None:out.append(f' L2_cache_stats_fail_breakdown[{access}][{reason}] = {value}\n')
 return out
v=m.parse_frames(frame(1,0,'MSHR_MERGE_ENRTY_FAIL',3,3)+frame(2,0,'MSHR_MERGE_ENRTY_FAIL',7,7))
ck(v['sum_known_positive_reason_contributions']==7);ck(v['printed_stats_frame_count']==2);ck(v['last_cumulative_frame_by_stream']['0']['kernel_uid']==2);ck(v['last_cumulative_frame_by_stream']['0']['reason_lines'][0]['line']==8)
v=m.parse_frames(frame(1,0,'MISS_QUEUE_FULL',3,3)+frame(2,1,'MISS_QUEUE_FULL',7,7)+frame(3,0,'MISS_QUEUE_FULL',9,9));ck(v['sum_known_positive_reason_contributions']==16);ck(v['stream_ids']==[0,1]);ck(len(v['last_cumulative_frame_by_stream'])==2)
v=m.parse_frames(frame(1,0,'MISS_QUEUE_FULL',3,3)+frame(1,0,'MISS_QUEUE_FULL',5,5));ck(v['sum_known_positive_reason_contributions']==5)
v=m.parse_frames(frame(1,0,None,None,0));ck(v['positive_reason_known_contributions']is None);ck(v['sum_known_positive_reason_contributions']is None);ck(v['unprinted_reasons']is None)
v=m.parse_frames(frame(1,0,'MSHR_MERGE_ENRTY_FAIL',3,3)+frame(2,0,None,None,0));ck(v['positive_reason_known_contributions']is None)
v=m.parse_frames(frame(1,0,'MSHR_ENRTY_FAIL',4,4));ck('GLOBAL_ACC_R:MSHR_ENRTY_FAIL'in v['positive_reason_known_contributions']);ck('GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL'not in v['positive_reason_known_contributions'])
v=m.parse_frames(['L2_cache_stats_fail_breakdown[GLOBAL_ACC_R][MISS_QUEUE_FULL] = 3\n']);ck(len(v['unbound_reason_lines'])==1);ck(v['positive_reason_known_contributions']is None)
v=m.parse_frames(frame(1,0)+['L2_cache_stats_fail_breakdown[GLOBAL_ACC_R][MISS_QUEUE_FULL] = -3\n']);ck(len(v['unparsed_reason_lines'])==1);ck(v['positive_reason_known_contributions']is None)
v=m.parse_frames(frame(1,0,'MISS_QUEUE_FULL',4,7)+['L2_cache_stats_fail_breakdown[GLOBAL_ACC_W][MISS_QUEUE_FULL] = 3\n']);ck(v['sum_known_positive_reason_contributions']==7);ck(len(v['positive_reason_known_contributions'])==2)

with tempfile.TemporaryDirectory()as td:
 root=pathlib.Path(td)/'new';old=pathlib.Path(td)/'old';d='a'*64;matrix=[]
 def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
 def make(cohort,profile,uid,reference=False,bad=False):
  dest=old if reference else root;sc='E2-DTCHASH18-fixture-DH-P0-V1'if reference else cohort
  point=dict(cohort=cohort,input_digest=d,program='fixture',suite='fixture',cell='DH',profile=profile,expected=dict(kernels=2));matrix.append(point)
  out=dest/'DTC/run/results'/uid;out.mkdir(parents=True);text=''.join(frame(1,0,'MISS_QUEUE_FULL',3,3)+frame(2,0,'MISS_QUEUE_FULL',5,5)).encode();compressed=gzip.compress(text);(out/'raw.log.gz').write_bytes(compressed)
  proof=dict(cohort=sc,cell='DH',input_digest=d,performance_accepted=True,cycles=100,raw_gzip_sha256=hashlib.sha256(compressed).hexdigest(),raw_uncompressed_sha256=hashlib.sha256(text).hexdigest())
  strict=out/('DOWNSTREAM_STRICT.json'if reference else'L2_STRICT.json');write(strict,proof)
  receipt=dict(status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',target_mount_path='/164/fixture',archive_sha256='archive',native_restore='/native/fixture')
  original=dict(cohort=sc,state='PASS_DOWNSTREAM18_STRICT_ARCHIVE_NATIVE_RESTORE'if reference else'PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE',uuid=uid,cycles=100,proof=proof,archive=dict(receipt=receipt,independently_verified_entries=1))
  write(dest/'analysis'/(sc+'.RESULT.json'),original)
  write(dest/'control/qualification_ledger'/(sc+'.INTENT.json'),dict(cohort=sc,uuid=uid,output=str(out)))
  done=dict(uuid=uid,stop_reason='TIMEOUT'if bad else None,launcher_wait_returncode=0,native_simulator_observed=True,raw_sha256=proof['raw_gzip_sha256'],raw_uncompressed_sha256=proof['raw_uncompressed_sha256'])
  write(dest/'control/qualification_ledger'/(sc+'.DONE.json'),done);write(out/'NATIVE_EXIT.json',done)
  write(dest/'DTC/control'/('SCIENCE_QUALIFICATION_'+sc+'.json'),dict(strict_sha256=hashlib.sha256(strict.read_bytes()).hexdigest(),uuid=uid))
  write(dest/'control'/(sc+'_ARCHIVE_RECEIPT.json'),receipt)
  if reference:
   reused=dict(original,state='REFERENCE_ACCEPTED_NO_NEW_START',cohort=cohort,reuse_verification={k:True for k in['strict_verified','natural_done_verified','archive_native_restore_verified','complete_effective_options_equal','core_framework_binary_equal','input_scope_equal']});write(root/'analysis'/(cohort+'.RESULT.json'),reused)
  return out,proof
 good,proof=make('E2-DTCL2MLP-fixture-DH-E384-V1','E384','uuid-new');make('E2-DTCL2MLP-fixture-DH-E768-V1','E768','uuid-unclosed',bad=True);make('E2-DTCL2MLP-fixture-DH-P0-V1','P0','uuid-ref',reference=True)
 write(root/'control/MATRIX_CURRENT.json',dict(points=matrix,revision=0));scope=pathlib.Path(td)/'scope.json';write(scope,dict(rows=[dict(input_digest=d,complete_header_coverage=True,stream_ids=[0])]))
 raw_scanner=m.scan_raw;calls=[]
 def wrapped(raw,proof):calls.append(raw);return raw_scanner(raw,proof)
 m.scan_raw=wrapped;v=m.collect(root,old,scope)
 ck(len(v['rows'])==3);ck(len(calls)==2);ck(all('uuid-unclosed'not in str(p)for p in calls))
 goodrows=[r for r in v['rows']if r['status']=='SIDECAR_EXTRACTED_CLOSED_ACCEPTED'];ck(len(goodrows)==2)
 for r in goodrows:
  ck(r['closed_raw']['sum_known_positive_reason_contributions']==5);ck(r['known_reason_sum_matches_observed_reservation_fail_total']is True);ck(r['complete_declared_stream_stats_coverage']);ck(r['source_closure']['source_verified_natural_closed_before_raw_open'])
 ref=next(r for r in goodrows if r['state']=='REFERENCE_ACCEPTED_NO_NEW_START');ck(ref['source_closure']['source_root']==str(old));ck(ref['source_closure']['source_cohort'].startswith('E2-DTCHASH18-'));ck('uuid-ref'in ref['closed_raw']['raw_gzip_path'])
 ck(next(r for r in v['rows']if r['uuid']=='uuid-unclosed')['status']=='SIDECAR_EVIDENCE_ERROR_NO_RECLASSIFICATION')
 bad=dict(proof,raw_gzip_sha256='wrong')
 try:raw_scanner(good/'raw.log.gz',bad)
 except AssertionError:ck(True)
 else:raise AssertionError('corrupt compressed SHA accepted')
 bad=dict(proof,raw_uncompressed_sha256='wrong')
 try:raw_scanner(good/'raw.log.gz',bad)
 except AssertionError:ck(True)
 else:raise AssertionError('corrupt body SHA accepted')
print(json.dumps(dict(status='CPU_ONLY_PASS',checks=checks,actual_simulator_starts=0,source_sha256=hashlib.sha256((H/'raw_reason_sidecar.py').read_bytes()).hexdigest(),analytical_cases=['successive cumulative prints retained once','per-stream last snapshots','repeated same UID','missing None versus printed zero','literal ENRTY spelling','unbound/malformed lines','closed primary DONE gate','old reference source ancestry','zero raw opens for unclosed record','compressed and body SHA rejection']),indent=2))
