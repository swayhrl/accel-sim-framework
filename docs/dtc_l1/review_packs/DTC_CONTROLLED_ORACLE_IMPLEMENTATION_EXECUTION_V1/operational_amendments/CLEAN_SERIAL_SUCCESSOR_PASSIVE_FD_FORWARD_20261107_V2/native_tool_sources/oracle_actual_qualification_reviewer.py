"""Independent closed-qualifier review. Read-only; never call from owner locks/safety loop.
Main runs this separately and exclusively publishes the returned small native JSON.
No model, registration, signal, repair, restore, request or dispatcher is created here.
"""
import pathlib, hashlib, json, os, stat, re, gzip, fcntl, time, subprocess
P = pathlib.Path
AUTHORITY = '18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
MODES = {'OFF_MATCHED':0,'M_DATAREAD':1,'L2_DATAREAD':2,'L1_DATAREADY':3}
QUALIFIERS = {
 'OFF_MATCHED':('vectorAdd','e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799'),
 'M_DATAREAD':('vectorAdd','e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799'),
 'L2_DATAREAD':('ATAX','eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950'),
 'L1_DATAREADY':('MVT','f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079')}
CORE8 = {
 '2DCONV':'d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0',
 'GEMM':'fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318',
 'convolutionSeparable':'4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449',
 'scan':'6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39',
 'ATAX':'eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950',
 'MVT':'f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079',
 'BICG':'ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef',
 'vectorAdd':'e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799'}
class ReviewHold(Exception): pass
def need(ok, why):
 if not ok: raise ReviewHold(why)
def read(p): return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  while True:
   b=f.read(8*1024*1024)
   if not b: break
   h.update(b)
 return h.hexdigest()
def js(v): return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def registry_snapshot():
 n=P('/root/data/ep_l2_dtc_l1_native_v2/control');lock=n/'science_authority/REGISTRY_UPDATE.lock'
 with lock.open('rb') as f:
  until=time.monotonic()+2
  while True:
   try: fcntl.flock(f,fcntl.LOCK_SH|fcntl.LOCK_NB);break
   except BlockingIOError:
    need(time.monotonic()<until,'REGISTRY_BUSY_HOLD');time.sleep(.02)
  p=n/'science_authority/NATIVE_SCIENCE_REGISTRY.json';r=read(p);e=read(n/'CURRENT_SCIENCE_EPOCH.json')
  need(e['epoch']==2 and e['native_registry_sha256']==sha(p),'REGISTRY_EPOCH_SHA')
  return r

def option_echo(text, expected):
 values={}
 for line in text.splitlines():
  mm=re.match(r'^\s*(-\S+)\s+(.*?)\s*$',line)
  if mm and mm[1] in expected:
   v=mm[2].split('#',1)[0].split()
   need(mm[1] not in values or values[mm[1]]==v,'CONFLICTING_OPTION_ECHO_'+mm[1])
   values[mm[1]]=v
 need(values==expected,'ACTUAL_EXACT_271_ECHO')
 return values

def counter_block(text, mode):
 """Independent source-matched cumulative counters, including absence errors."""
 mr={};lr={}
 for line in text.splitlines():
  if line.startswith('DTC_ORACLE_M_V1 '):
   d={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)}
   keys={'mode','cluster','parents_enqueued','required_sectors','sectors_enqueued','parents_transferred','sectors_received','parents_closed','pending_parents','peak_parents','fifo_stalls','normal_grants'}
   need(set(d)==keys and d['mode']==MODES[mode],'M_COUNTER_SCHEMA_OR_MODE');mr[d['cluster']]=d
  if line.startswith('dtc_oracle_l2 '):
   d={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)}
   need(set(d)=={'sub_partition','eligible_seen','virtual_hit_served','returned','outstanding'},'L2_COUNTER_SCHEMA');lr[d['sub_partition']]=d
 need(set(mr)==set(range(64)) and set(lr)==set(range(40)),'MISSING_PHYSICAL_UNIT_COUNTERS')
 for d in mr.values():
  need(d['parents_enqueued']==d['parents_transferred']==d['parents_closed'] and d['pending_parents']==0,'M_PARENT_OWNERSHIP_DRAIN')
  need(d['required_sectors']==d['sectors_enqueued']==d['sectors_received'],'M_SECTOR_OWNERSHIP')
  if mode!='M_DATAREAD':need(all(d[k]==0 for k in set(d)-{'mode','cluster'}),'M_ACTIVE_OUTSIDE_MODE')
 for d in lr.values():
  need(d['eligible_seen']==d['virtual_hit_served']==d['returned'] and d['outstanding']==0,'L2_OWNERSHIP_DRAIN')
  if mode!='L2_DATAREAD':need(all(d[k]==0 for k in set(d)-{'sub_partition'}),'L2_ACTIVE_OUTSIDE_MODE')
 l1={}
 for k in ['eligible_admitted','events_enqueued','events_delivered','events_pending']:
  v=re.findall(r'^DTC_ORACLE_L1_'+k+r'\s*=\s*(\d+)\s*$',text,re.M);need(bool(v),'MISSING_L1_COUNTER_'+k);l1[k]=int(v[-1])
 need(l1['events_pending']==0 and l1['events_enqueued']==l1['events_delivered'],'L1_EVENT_DRAIN')
 if mode!='L1_DATAREADY':need(all(v==0 for v in l1.values()),'L1_ACTIVE_OUTSIDE_MODE')
 nums={k:int(v) for k,v in re.findall(r'^\s*(DTC_L1_\w+|gpu_sim_cycle|gpu_tot_sim_cycle|gpu_sim_insn|gpu_tot_sim_insn|gpu_tot_issued_cta|kernel_launch_uid)\s*=\s*(\d+)\s*$',text,re.M)}
 def val(k):need('DTC_L1_'+k in nums,'MISSING_ORIGINAL_COUNTER_'+k);return nums['DTC_L1_'+k]
 need(val('oo_new_misses')==val('oo_lower_created')+l1['events_enqueued'],'REAL_VIRTUAL_MISS_OWNERSHIP')
 need(all(val(k)==0 for k in ['oo_pib_occupancy','oo_inflight_current','oo_active_refs','lower_outstanding']),'ORIGINAL_TERMINAL_DRAIN')
 need(len({val(k) for k in ['lower_credit_acquired','lower_credit_released','oo_lower_created','oo_lower_issued','oo_lower_responses']})==1,'ORIGINAL_REAL_CREDIT_CONSERVATION')
 need(val('oo_completion_dependency_count')==val('oo_completion_dependency_closed')==val('oo_valid_hits')+val('oo_pending_hits')+val('oo_new_misses'),'ORIGINAL_REF_DEPENDENCY_CONSERVATION')
 exposure={'OFF_MATCHED':0,'M_DATAREAD':sum(v['parents_enqueued'] for v in mr.values()),'L2_DATAREAD':sum(v['virtual_hit_served'] for v in lr.values()),'L1_DATAREADY':l1['events_enqueued']}[mode]
 return {'exposure':exposure,'M_clusters':64,'L2_subpartitions':40,'L1':l1,'numeric':nums}

def typed_tree(root, entries):
 root=P(root);need(root.is_dir() and root.stat().st_dev==2128,'NOT_NATIVE_TYPED_TREE');seen=set()
 for e in entries:
  rel=P(e['path']);need(not rel.is_absolute() and '..' not in rel.parts and e['path'] not in seen,'UNSAFE_OR_DUPLICATE_MANIFEST_PATH');seen.add(e['path']);p=root/rel;v=p.lstat()
  need(stat.S_IMODE(v.st_mode)==e['mode'] and v.st_uid==e['uid'] and v.st_gid==e['gid'],'TYPED_MODE_OWNER_'+e['path'])
  if e['type']=='file':need(stat.S_ISREG(v.st_mode) and v.st_size==e['size'] and sha(p)==e['sha256'],'TYPED_FILE_SHA_'+e['path'])
  elif e['type']=='directory':need(stat.S_ISDIR(v.st_mode),'TYPED_DIRECTORY_'+e['path'])
  elif e['type']=='symlink':need(stat.S_ISLNK(v.st_mode) and os.readlink(p)==e['target'],'TYPED_SYMLINK_'+e['path'])
  else:raise ReviewHold('UNSUPPORTED_MANIFEST_TYPE')
 return len(seen)

def archive_review(a, out, cohort, done):
 receipt=a['receipt'];need(receipt['cohort']==cohort and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','ARCHIVE_STATUS')
 need(receipt['source_disposition']=='SOURCE_KEEP' and receipt['source_release_bytes']==0,'SOURCE_KEEP_REQUIRED')
 root=P(receipt['target_mount_path']);need(root.is_absolute() and '/root/share/mnt164/' in str(root),'ARCHIVE_ROOT')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(root)],text=True,timeout=10))['filesystems'][0]
 need(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','NOT_TRUE164')
 manifest=read(root/'SOURCE_MANIFEST.json');commit=read(root/'COMMIT.json');idx=read(root/'ARCHIVE_INDEX.json')
 need(sha(root/'SOURCE_MANIFEST.json')==receipt['manifest_sha256']==commit['manifest_sha256'],'ARCHIVE_MANIFEST_SHA')
 need(commit['archive_index_sha256']==sha(root/'ARCHIVE_INDEX.json') and commit['txid']==receipt['txid']==manifest['txid'],'ARCHIVE_COMMIT')
 need(manifest['cohort']==cohort and manifest['source_root']==str(out) and manifest['native_execution_receipt_sha256']==sha(out/'NATIVE_EXIT.json'),'ARCHIVE_SOURCE_UUID_BINDING')
 need(manifest['source_disposition']=='SOURCE_KEEP','MANIFEST_SOURCE_KEEP')
 total=0;h=hashlib.sha256()
 for c in idx['chunks']:
  name=P(c['name']);need(len(name.parts)==1 and name.name not in ['.','..'] and c['offset']==total and c['txid']==receipt['txid'],'ARCHIVE_CHUNK_SEQUENCE');p=root/'chunks'/name;need(p.stat().st_size==c['size'] and sha(p)==c['sha256'],'ARCHIVE_CHUNK_SHA')
  with p.open('rb') as f:
   while True:
    b=f.read(8*1024*1024)
    if not b:break
    h.update(b)
  total+=c['size']
 need(total==idx['archive_bytes']==receipt['archive_bytes'] and h.hexdigest()==idx['archive_sha256']==receipt['archive_sha256'],'ARCHIVE_FULL_SHA')
 restore=P(receipt['native_restore']);need(restore.is_relative_to(out.parents[1]/'recovery'),'RESTORE_OUTSIDE_NATIVE_STAGE')
 n=typed_tree(out,manifest['entries']);need(typed_tree(restore,manifest['entries'])==n==a['independently_verified_entries'],'TYPED_NATIVE_RESTORE_COUNT')
 rr=read(root/'RESTORE_VERIFIED_NATIVE_TARGET.json');need(len(rr['rows'])==n,'NATIVE_RESTORE_RECEIPT_ROWS')
 return {'true164_source':fs['source'],'archive_sha256':idx['archive_sha256'],'manifest_sha256':receipt['manifest_sha256'],'archive_index_sha256':sha(root/'ARCHIVE_INDEX.json'),'typed_source_entries':n,'typed_native_restore_entries':n,'native_restore':str(restore),'SOURCE_KEEP':True}

def _verify_closed_row(stage_root, cohort, require_declared_qualifier):
 result={'schema':'DTC_CONTROLLED_ORACLE_INDEPENDENT_ACTUAL_QUALIFIER_V1','status':'HOLD','cohort':cohort,'reviewer_source_sha256':sha(__file__),'scientific_starts':0,'review_scope':'Closed actual qualifier only; independent read of identity/raw counters/archive chunks and both native typed trees. Never invoke inside owner lock or safety loop.'}
 try:
  r=P(stage_root).resolve();need(r.stat().st_dev==2128,'NATIVE_STAGE_REQUIRED');plan=read(r/'control/EXECUTION_PLAN.json');build=read(r/'control/BUILD_PROFILE.json');point=next(p for p in read(r/'control/MATRIX.fixed.json')['points'] if p['cohort']==cohort)
  mode=point['mode'];need(mode in MODES and point['initial_fixed8'] and CORE8.get(point['program'])==point['input_digest'],'FROZEN_INITIAL8_ROW_IDENTITY')
  if require_declared_qualifier:need(plan['initial_qualifiers'][mode]==cohort and point['actual_qualification_row'] and (point['program'],point['input_digest'])==QUALIFIERS[mode],'NOT_DECLARED_ACTUAL_QUALIFIER')
  pin=plan['actual_qualification_reviewer'];need(pin['sha256']==sha(__file__) and pin['function']=='verify_actual_qualifier','REVIEWER_SOURCE_PIN')
  reg=registry_snapshot();q=reg['registered_future_requests'][plan['request']];s=read(r/'control/specs'/(cohort+'.json'));need(q['admitted_specs'][cohort]==sha(r/'control/specs'/(cohort+'.json')),'REGISTERED_SPEC_SHA');need(q['execution_plan_sha256']==sha(r/'control/EXECUTION_PLAN.json') and q['authority_commit']==AUTHORITY,'REGISTERED_PLAN_SHA')
  i=read(r/'control/qualification_ledger'/(cohort+'.INTENT.json'));d=read(r/'control/qualification_ledger'/(cohort+'.DONE.json'));consumed=q['consumed'][cohort];uid=consumed['uuid'];result.update(input_uuid=uid,mode=mode,input_digest=s['input_digest'],plan_id=s['plan_id'])
  need(uid==i['uuid']==d['uuid'] and consumed['execution_receipt']==d and consumed['intent_sha256']==sha(r/'control/qualification_ledger'/(cohort+'.INTENT.json')),'ONE_USE_UUID_RECEIPT')
  out=P(i['output']);need(out==r/'DTC/run/results'/uid and read(out/'NATIVE_EXIT.json')==d,'NATIVE_OUTPUT_UUID')
  need(d['stop_reason'] is None and d['launcher_wait_returncode']==0 and d['native_simulator_observed'] is True and d['new_attempt_consumed']==1 and d['automatic_retry'] is False,'NATURAL_ACTUAL_ONE_USE_REQUIRED')
  pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');launch=read(out/'NATIVE_LAUNCH.json')
  need(pid['oracle_execution_binding']==launch['oracle_execution_binding']==i['oracle_execution_binding'],'ACTUAL_PROCESS_BINDING')
  need(s['native_simulator_argv'][0] in pid['maps'] and launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv'],'ACTUAL_BINARY_MAPS_ARGV')
  late=read(out/'NATIVE_SIMULATOR_VERIFIED_LATE_MAPS.json')
  cudart=next(x['actual_realpath'] for x in s['runtime_files'] if x['sha256']==build['libcudart_sha256'])
  loader=str((r/'common-lib/ld-linux-x86-64.so.2').resolve())
  need(late['pid']==pid['pid'] and late['start_ticks']==pid['start_ticks'] and late['mnt_namespace']==pid['mnt_namespace']==s['execution_mnt_namespace'],'ACTUAL_LATE_PROCESS_GENERATION')
  need(late['host_cpu_affinity_actual']==pid['host_cpu_affinity_actual'] and late['oracle_execution_binding']==i['oracle_execution_binding'] and late['uuid']==uid and late['cohort']==cohort,'ACTUAL_LATE_IDENTITY_BINDING')
  need(all(x in late['maps'] for x in [s['native_simulator_argv'][0],cudart,loader]),'ACTUAL_BINARY_CUDART_LOADER_MAPS')
  proc=P('/proc')/str(pid['pid'])
  if proc.exists():need(int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'ACTUAL_SIMULATOR_STILL_LIVE')
  rp=r/'analysis'/(cohort+'.RESULT.json');v=read(rp);result['result_sha256']=sha(rp);need(v['state']=='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE' and v['cohort']==cohort and v['uuid']==uid,'STRICT_ACCEPTED_RESULT_REQUIRED')
  proof=v['proof'];need(read(out/'L2_STRICT.json')==proof and proof['performance_accepted'] is True and type(v['cycles']) is int and v['cycles']>0 and v['cycles']==proof['cycles'],'STRICT_CYCLES')
  need(proof['cohort']==cohort and proof['uuid']==uid and s['cohort']==cohort and v['cell']=='DH' and v['oracle_mode']==s['oracle_mode']==mode and v['input_digest']==s['input_digest']==point['input_digest'] and v['plan_id']==s['plan_id']==point['plan_id'],'RESULT_IDENTITY')
  need(proof['core_commit']==s['core_commit']==build['core_commit'] and proof['framework_commit']==s['framework_commit']==build['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4' and proof['binary_sha256']==s['binary_sha256']==build['binary_sha256'],'SAMEBUILD_SOURCE_BINARY')
  for p in plan['source_pins']:need(sha(p['path'])==p['sha256'],'RUNTIME_SOURCE_PIN_'+p['path'])
  for f in s['runtime_files']:need(sha(f['actual_realpath'])==f['sha256'],'RUNTIME_FILE_PIN')
  historical=read(s['historical_DH_P0_spec_path']);need(sha(s['historical_DH_P0_spec_path'])==s['historical_DH_P0_spec_sha256'],'HISTORICAL_CONTRACT_SHA')
  expected=dict(historical['expected_options'],**{'-gpgpu_dtc_oracle_mode':[str(MODES[mode])]});need(len(historical['expected_options'])==270 and len(expected)==271 and expected==s['expected_options']==proof['effective_options'],'EXACT_270_PLUS_ENUM')
  need(expected['-gpgpu_perfect_mem']==expected['-l2_ideal']==['0'],'STOCK_FLAGS_DISABLED')
  for f in s['configs']:need(sha(f['path'])==f['sha256'],'CONFIG_SHA')
  need(sha(s['input_binding_path'])==s['input_binding_sha256']==historical['input_binding_sha256'],'FULL_INPUT_SHA')
  need(sha(out/'raw.log.gz')==d['raw_sha256']==proof['raw_gzip_sha256'],'RAW_GZIP_SHA')
  with gzip.open(out/'raw.log.gz','rb') as f:raw=f.read()
  need(len(raw)==d['raw_uncompressed_bytes'] and hashlib.sha256(raw).hexdigest()==d['raw_uncompressed_sha256']==proof['raw_uncompressed_sha256'],'RAW_UNCOMPRESSED_SHA');text=raw.decode();need(text.count('GPGPU-Sim: *** exit detected ***')==text.count('GPGPU-Sim: *** simulation thread exiting ***')==1,'ONE_NATURAL_MODEL_EXIT')
  option_echo(text,expected)
  marks=list(re.finditer(r'^kernel_name = (\S+)[ \t]*$',text,re.M));need(len(marks)==s['expected']['kernels']==len(proof['kernels']),'FULL_KERNEL_COUNT');kr=[]
  for n,mm in enumerate(marks):
   b=text[mm.start():marks[n+1].start() if n+1<len(marks) else len(text)];c=counter_block(b,mode);pk=proof['kernels'][n];nums=c['numeric'];need(pk['ordinal']==n+1 and pk['kernel']==mm[1] and pk['cycles']==nums['gpu_sim_cycle'] and pk['total_cycles']==nums['gpu_tot_sim_cycle'],'PER_KERNEL_CYCLES');kr.append({'ordinal':n+1,'kernel':mm[1],'exposure':c['exposure']})
  nums=c['numeric'];need(nums['gpu_tot_sim_cycle']==v['cycles'] and nums['gpu_tot_sim_insn']==s['expected']['instructions'] and nums['gpu_tot_issued_cta']==s['expected']['CTA'],'WHOLE_INPUT_POPULATION')
  exposure=max(x['exposure'] for x in kr);need(not require_declared_qualifier or mode=='OFF_MATCHED' or exposure>0,'NO_EXPOSURE_HOLD');need(proof['actual_mechanism_exposure']==kr[-1]['exposure'],'RUNTIME_EXPOSURE_PARSE_MISMATCH')
  ar=archive_review(v['archive'],out,cohort,d)
  result.update(status='PASS',cycles=v['cycles'],core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],effective_options_count=271,actual_libcudart_maps_path=cudart,actual_loader_maps_path=loader,late_maps_sha256=sha(out/'NATIVE_SIMULATOR_VERIFIED_LATE_MAPS.json'),libcudart_sha256=build['libcudart_sha256'],config_sha256=[x['sha256'] for x in s['configs']],input_binding_sha256=s['input_binding_sha256'],strict_sha256=sha(out/'L2_STRICT.json'),raw_gzip_sha256=d['raw_sha256'],raw_uncompressed_sha256=d['raw_uncompressed_sha256'],actual_mechanism_exposure=exposure,kernels=kr,archive_native_review=ar,source_plan_sha256=sha(r/'control/EXECUTION_PLAN.json'),reason=None)
 except Exception as e:result.update(status='HOLD',reason=type(e).__name__+': '+str(e))
 return result

def verify_actual_qualifier(stage_root, cohort):
 return _verify_closed_row(stage_root, cohort, True)

def verify_mode_core32_extension(initial8_root, mode):
 """Read-only per-mode Gate2; no other mode's tail, speedup or budget is used."""
 result={'schema':'DTC_CONTROLLED_ORACLE_INDEPENDENT_MODE_GATE2_V1','status':'HOLD','mode':mode,'reviewer_source_sha256':sha(__file__),'scientific_starts':0,'new_request_or_UUID_created':False}
 try:
  need(mode in set(MODES)-{'OFF_MATCHED'},'BAD_EXTENSION_MODE');r=P(initial8_root).resolve();plan=read(r/'control/EXECUTION_PLAN.json');matrix=read(r/'control/MATRIX.fixed.json')['points']
  need(plan['stage']=='initial8' and mode in plan['qualified_modes'],'NOT_QUALIFIED_INITIAL_MODE')
  result.update(initial_request=plan['request'],initial_plan_sha256=sha(r/'control/EXECUTION_PLAN.json'),source_plan_sha256=sha(r/'control/EXECUTION_PLAN.json'))
  rows=[p for p in matrix if p['mode'] in ['OFF_MATCHED',mode]]
  need(len(rows)==16 and len({p['cohort'] for p in rows})==16,'FIXED8_MATCHED16_ROWS')
  for name in ['OFF_MATCHED',mode]:need({p['program']:p['input_digest'] for p in rows if p['mode']==name}==CORE8,'EXACT_FROZEN8_INPUT_POPULATION')
  # Cheap closed-state gate first: no large archive/FUSE read for missing rows.
  for point in rows:
   rp=r/'analysis'/(point['cohort']+'.RESULT.json');need(rp.is_file(),'FIXED8_RESULT_NOT_CLOSED_'+point['cohort']);v=read(rp)
   need(v.get('state')=='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE','FIXED8_NOT_ALL_ACCEPTED_'+point['cohort'])
  qualifier=plan['initial_qualifiers'][mode];qr=read(r/'control/actual_qualification_reviews'/(qualifier+'.json'))
  need(qr['status']=='PASS' and qr['reviewer_source_sha256']==sha(__file__) and qr['cohort']==qualifier and qr['result_sha256']==sha(r/'analysis'/(qualifier+'.RESULT.json')) and qr['actual_mechanism_exposure']>0,'MODE_ACTUAL_QUALIFIER_NOT_INDEPENDENTLY_PASSED')
  offq=plan['initial_qualifiers']['OFF_MATCHED'];oq=read(r/'control/actual_qualification_reviews'/(offq+'.json'))
  need(oq['status']=='PASS' and oq['reviewer_source_sha256']==sha(__file__) and oq['cohort']==offq and oq['result_sha256']==sha(r/'analysis'/(offq+'.RESULT.json')),'OFF_ACTUAL_QUALIFIER_NOT_INDEPENDENTLY_PASSED')
  refs=[];reviews=[]
  for point in rows:
   review=_verify_closed_row(r,point['cohort'],False);need(review['status']=='PASS','INDEPENDENT_ROW_HOLD_'+point['cohort']+':'+str(review.get('reason')));reviews.append(review)
   refs.append({'cohort':point['cohort'],'uuid':review['input_uuid'],'result_sha256':review['result_sha256'],'input_digest':review['input_digest'],'program':point['program'],'mode':point['mode'],'plan_id':point['plan_id'],'strict_sha256':review['strict_sha256'],'archive_sha256':review['archive_native_review']['archive_sha256'],'native_restore':review['archive_native_review']['native_restore'],'cycles':review['cycles'],'actual_mechanism_exposure':review['actual_mechanism_exposure']})
  need(len({x['input_uuid'] for x in reviews})==16,'UUID_REUSE')
  need(len({(x['core_commit'],x['framework_commit'],x['binary_sha256'],x['libcudart_sha256']) for x in reviews})==1,'MATCHED_BUILD_MISMATCH')
  first=reviews[0];result.update(status='PASS',core_commit=first['core_commit'],framework_commit=first['framework_commit'],binary_sha256=first['binary_sha256'],libcudart_sha256=first['libcudart_sha256'],input_count=8,accepted_result_count=16,result_refs=refs,independent_row_reviews=reviews,mode_qualifier=qualifier,matched_OFF_qualifier=offq,all_fixed8_and_samebuild_OFF_accepted=True,strict_archive_native_reviewed=True,performance_selection_used=False,reason=None)
 except Exception as e:result.update(status='HOLD',reason=type(e).__name__+': '+str(e))
 return result
