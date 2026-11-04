from pathlib import Path
import json,hashlib,subprocess,datetime,os,math,collections
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');O=A/'agents/A_remaining48_readonly_qualification_v1';O.mkdir(parents=True,exist_ok=True);G='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/planning-isolated.git';COMMIT='5001c3f35052f7f91f1ad41eeff83f2947a0878d';PREFIX='docs/dtc_l1/plans/DTC_STAGE_II_A_CH_FAIR_MATCH_PREPARATION_20261103_V1/agents/A/';H=lambda b:hashlib.sha256(b).hexdigest();sha=lambda p:H(Path(p).read_bytes());checks=[];gaps=[]
def put(n,x):p=O/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def blob(n):return subprocess.check_output(['git','--git-dir='+G,'show',COMMIT+':'+PREFIX+n])
def require(n,v):assert v,n;checks.append(n)
def verify_file(pin,kind,identity):
 try:
  b=Path(pin['path']).read_bytes();assert H(b)==pin['sha256'],'SHA_MISMATCH';return b
 except (OSError,AssertionError)as ex:gaps.append(dict(identity=identity,kind=kind,path=pin['path'],reason=repr(ex)));return None
cp=A/'agents/C_final_all16_review_v1/MANIFEST.json';require('formal_all16_review_manifest_exact',sha(cp)=='0107f6b6d8c6ed0a330a36eec03e74209e1eb485682e882b5e635c3dc9ff04ce');cm=json.loads(cp.read_text());cref=next(x for x in cm['files']if x['path']=='FINAL_REVIEW.json');cb=(cp.parent/'FINAL_REVIEW.json').read_bytes();require('formal_review_statement_SHA',H(cb)==cref['sha256']);review=json.loads(cb);require('all16_independent_review_passed',review['decision'].startswith('PASS')and review['scientific_execution_complete']and review['independent_final_first16_review_complete']and review['accepted_new_CH']==16 and review['missing_new_CH']==0 and review['approved_contract_commit']==COMMIT)
rawmatrix=blob('CH_CANDIDATE_MATRIX.json');matrix=json.loads(rawmatrix);rawfirst=blob('FIRST_BATCH.json');first=json.loads(rawfirst);rawresource=blob('RESOURCE_AND_ARCHIVE_QUALIFICATION.json');history={r['input_digest']:r for r in json.loads(rawresource)['per_input_history']};core={r['candidate_id']:r for r in matrix['candidates']if r['category']=='CORE'};firstids=set(first['candidate_ids']);remaining={k:v for k,v in core.items()if k not in firstids};require('fixed_64_core',len(core)==64);require('fixed_first16_exact_core_members',len(firstids)==16 and firstids<=set(core));require('remaining_exact_set_difference48',len(remaining)==48 and set(remaining)==set(core)-firstids);require('remaining24_input_pairs',len({r['input_digest']for r in remaining.values()})==24)
for d in {r['input_digest']for r in remaining.values()}:require('both_F_for_'+d,{r['profile']for r in remaining.values()if r['input_digest']==d}=={'F128','F256'})
configs={};config_sourcepins={}
for r in remaining.values():
 cid='CH_'+r['profile']
 if cid in configs:continue
 cfg=[]
 for f in r['configs']:
  b=blob(f['path']);require(cid+'_'+f['path']+'_Git_bytes_SHA',H(b)==f['sha256']);dst=O/'frozen_config_bytes'/f['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b);cfg.append(dict(fixed_commit=COMMIT,git_path=PREFIX+f['path'],sha256=H(b),bytes=len(b),readonly_plan_copy=str(dst.relative_to(O))))
 configs[cid]={'profile':r['profile'],'cell':'CH','configs':cfg,'effective_target_values':{k:r['effective_options'][k]for k in ['-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size','-gpgpu_clock_domains','-gpgpu_dram_partition_queues','-gpgpu_dram_return_queue_size']},'expected_options_canonical_SHA256':H((json.dumps(r['effective_options'],sort_keys=True,separators=(',',':'))+'\n').encode()),'not_a_native_spec':True}
refs={};specpins={};inputs={};records=[]
for r in sorted(remaining.values(),key=lambda x:(x['suite'],x['program'],x['input_digest'],x['profile'])):
 cid=r['candidate_id'];d=r['input_digest'];recordgaps=[]
 if d not in inputs:
  b=verify_file(r['input_binding'],'INPUT_BINDING',cid);inputrow={'program':r['program'],'suite':r['suite'],'input_digest':d,'input_binding':r['input_binding'],'trace_entry':r['trace_entry'],'expected':r['expected'],'registered_by_this_preparation':False}
  if b:
   bd=json.loads(b);q=bd['qualification'];asset=bd['asset'];ok=(bd['input_digest']==d and q['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS'and not q.get('issues'));expected={'kernels':len(q['rows']),'instructions':sum(x['active_thread_instructions']for x in q['rows']),'CTA':sum(x['complete_ctas']for x in q['rows'])};ok=ok and expected==r['expected'];checks.append(cid+'_input_identity_expected_checked')
   if not ok:gaps.append(dict(identity=cid,kind='INPUT_EXPECTED_OR_QUALIFICATION',reason='current binding identity/ROI qualification differs from frozen candidate'))
   trace=Path(r['trace_entry'])
   try:
    raw=trace.read_bytes();entrypass=H(raw)==asset['commandlist_sha256'];assert entrypass
    for qrow in q['rows']:
     p=Path(qrow['path']);st=p.stat();assert [st.st_size,st.st_mtime_ns]==qrow['full_SHA_current_size_mtime'];assert p.is_file()
    checks.append(cid+'_trace_entry_SHA_and_qualified_member_stats')
   except(OSError,AssertionError)as ex:gaps.append(dict(identity=cid,kind='TRACE_ENTRY_OR_MEMBER',path=str(trace),reason=repr(ex)));entrypass=False
   inputrow.update(binding_status=q['status'],binding_digest_equal=bd['input_digest']==d,binding_expected=expected,expected_matches_fixed=expected==r['expected'],commandlist_sha256=asset['commandlist_sha256'],trace_entry_readable_SHA_verified=entrypass,trace_member_count=len(q['rows']),trace_body_SHA_reused_not_rehashed=True,trace_member_stat_basis='size/mtime since fullbodySHA qualification; no large trace reread',existing_asset_extent=asset.get('extent'),existing_asset_kind=asset.get('kind'),native_application_numeric_values='UNPROVEN')
  hr=history[d];estimate=hr['proposed_reservation_bytes'];require('frozen_prediction_equals_candidate_'+d,estimate==r['resource_estimate_bytes']);inputrow['resource_estimate']={'bytes':estimate,'GiB':estimate/1024**3,'kind':'HISTORICAL_PLANNING_ESTIMATE_ONLY_NOT_RSS_CAP_OR_ADMISSION_GRANT','source_commit':COMMIT,'source_git_path':PREFIX+'RESOURCE_AND_ARCHIVE_QUALIFICATION.json','source_sha256':H(rawresource),'same_input_max_observed_RSS_bytes':hr['max_observed_rss_bytes'],'failed_runs_retained_in_source_history':True,'native_runtime_cap_not_proposed':None,'remeasure_before_any_future_authorized_admission':True};inputs[d]=inputrow
 refkeys={}
 for name,cell,pf in [('parent_CH_P0','CH','P0'),('matched_DH_P0','DH','P0'),('matched_DH_variant','DH',r['profile'])]:
  ref=r[name];refpin=ref['result_evidence'];key=refpin['path'];refkeys[name]=key
  if key not in refs:
   b=verify_file(refpin,'ORIGINAL_REFERENCE_RESULT',cid);rr={'path':key,'sha256':refpin['sha256'],'cell':cell,'profile':pf,'input_digest':d,'frozen_cohort':ref['cohort'],'frozen_accepted':ref['accepted'],'performance_not_used_for_membership':True}
   if b:
    z=json.loads(b);p=z.get('proof',{});expected=r['expected'];ok=(ref['accepted']is True and z['state']in ['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','REFERENCE_ACCEPTED_NO_NEW_START']and p.get('performance_accepted')is True and p.get('input_digest')==d and p.get('cell')==cell and p.get('profile',p.get('downstream_profile'))==pf and p.get('core_commit')=='9eedb3131937748f0492fa83aad37d3691118d70'and p.get('framework_commit')=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and p.get('binary_sha256')=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'and p.get('CTA')==expected['CTA']and p.get('instructions')==expected['instructions']and p.get('kernel_count')==expected['kernels']);rr.update(current_state=z['state'],accepted_identity_verified=ok,original_reference_alias=z.get('reference_result_path'),Core=p.get('core_commit'),Framework=p.get('framework_commit'),binary_sha256=p.get('binary_sha256'),expected_verified=ok)
    if not ok:gaps.append(dict(identity=cid,kind='ORIGINAL_REFERENCE_IDENTITY',path=key,reason='accepted source identity/expected differs from fixed counterpart'))
    else:checks.append(cid+'_'+name+'_accepted_identity_SHA')
   refs[key]=rr
 sp={}
 for name in ['original_parent_spec','original_DH_variant_spec']:
  z=r[name];sp[name]=z['path']
  if z['path']not in specpins:
   b=verify_file(z,'OLD_SPEC',cid);specrow=dict(z,readable_SHA_verified=b is not None)
   if b:
    v=json.loads(b);ok=v['input_digest']==d and v['expected']==r['expected'];specrow.update(cell=v['cell'],profile=v['profile'],input_expected_equal=ok)
    if not ok:gaps.append(dict(identity=cid,kind='OLD_SPEC_IDENTITY',path=z['path'],reason='spec input/expected mismatch'))
    else:checks.append(cid+'_'+name+'_SHA_expected')
   specpins[z['path']]=specrow
 records.append(dict(plan_candidate_id=cid,program=r['program'],suite=r['suite'],input_digest=d,cell='CH',profile=r['profile'],fixed_category='CORE',fixed_reason=r['category_reason'],config_profile_reference='CH_'+r['profile'],input_reference=d,old_reference_keys=refkeys,old_spec_keys=sp,not_a_native_cohort=True,native_cohort=None,model_UUID=None,new_scientific_request=None,registration_authorized=False,models_started=0))
require('96_unique_original_reference_results',len(refs)==96);require('72_unique_old_spec_pins',len(specpins)==72);require('two_config_profiles_eightfiles',sum(len(x['configs'])for x in configs.values())==8)
for row in records:
 rowg=[g for g in gaps if g['identity']==row['plan_candidate_id']or(g.get('path')in row['old_reference_keys'].values())or(g.get('path')in row['old_spec_keys'].values())or(g.get('path')==inputs[row['input_digest']]['input_binding']['path'])];row['qualification_status']='QUALIFICATION_GAP_RETAINED'if rowg else'READONLY_IDENTITY_AND_CONFIG_CHECKS_PASS_NOT_EXECUTION_QUALIFIED';row['qualification_gap_count']=len(rowg)
classes={cat:[dict(plan_candidate_id=x['candidate_id'],program=x['program'],suite=x['suite'],input_digest=x['input_digest'],profile=x['profile'],category_reason=x['category_reason'],registered_by_this_preparation=False)for x in matrix['candidates']if x['category']==cat]for cat in ['SUPPLEMENT','DEFERRED']};require('fixed_supplement2_deferred4_retained',len(classes['SUPPLEMENT'])==2 and len(classes['DEFERRED'])==4)
progs=[dict(program=x['program'],suite=x['suite'],input_digest=d,profiles=['F128','F256'],resource_estimate=x['resource_estimate'])for d,x in sorted(inputs.items(),key=lambda x:(x[1]['suite'],x[1]['program'],x[0]))];put('REMAINING48_PLAN_IDENTITIES.json',dict(schema='DTC_STAGEIIA_REMAINING48_READONLY_PLANNING_IDENTITIES_V1',fixed_plan_commit=COMMIT,selection_formula='fixed5001 CORE64 candidate IDs MINUS fixed5001 FIRST_BATCH16 candidate IDs; no performance/time/PASS-based reselection',source_pins={'CH_CANDIDATE_MATRIX':dict(git_path=PREFIX+'CH_CANDIDATE_MATRIX.json',sha256=H(rawmatrix)),'FIRST_BATCH':dict(git_path=PREFIX+'FIRST_BATCH.json',sha256=H(rawfirst))},candidate_count=48,input_count=24,programs24=progs,candidates48=records,first16_excluded_candidate_ids=sorted(firstids),supplement2_unchanged=classes['SUPPLEMENT'],deferred4_unchanged=classes['DEFERRED'],batch_execution_order=None,reporting_group_order_not_created_here=True,scientific_execution_authorized=False,new_registration=False,new_model_starts=0,seven_UNRESOLVED_inputs_not_changed=True))
put('QUALIFICATION_EVIDENCE.json',dict(schema='DTC_STAGEIIA_REMAINING48_READONLY_EVIDENCE_V1',inputs24=list(inputs.values()),original_results96=list(refs.values()),old_specs72=list(specpins.values()),config_profiles=configs,qualification_gaps=gaps,qualification_gap_count=len(gaps),known_model_execution_qualification=False,resource_RSS_caps_not_set=True,large_trace_bodies_not_reread=True))
# Timestamped planning observation only, without model/owner process inventory or runtime checks.
mem={}
for line in Path('/proc/meminfo').read_text().splitlines():
 k,v=line.split(':',1)
 if k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']:mem[k]=int(v.strip().split()[0])*1024
cg={}
for f in ['memory.current','memory.max','memory.events','memory.swap.current','memory.swap.max','cpu.max','cpuset.cpus.effective','cpuset.mems.effective','memory.pressure','cpu.pressure','io.pressure']:
 p=Path('/sys/fs/cgroup')/f
 if p.is_file():cg[f]=p.read_text().strip()
numa=[]
for p in sorted(Path('/sys/devices/system/node').glob('node[0-9]*')):
 numa.append(dict(node=p.name,cpulist=(p/'cpulist').read_text().strip(),meminfo=(p/'meminfo').read_text()))
spaces={}
for label,p in [('native',Path('/root/data/dtc_stage_iia_first16_20261104_v1')),('true164_archive',O)]:
 v=os.statvfs(p);spaces[label]=dict(path=str(p),available_bytes=v.f_bavail*v.f_frsize,free_inodes=v.f_favail,device=p.stat().st_dev,findmnt=json.loads(subprocess.check_output(['findmnt','-J','-T',str(p)],text=True))['filesystems'][0])
put('PLANNING_RESOURCE_OBSERVATION.json',dict(schema='DTC_STAGEIIA_REMAINING48_PLANNING_RESOURCE_OBSERVATION_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),host_memory_bytes=mem,cgroup=cg,inspecting_process_cgroup=Path('/proc/self/cgroup').read_text(),inspecting_process_allowed_CPUs=sorted(os.sched_getaffinity(0)),NUMA=numa,storage=spaces,no_owner_or_model_runtime_process_check=True,no_resource_admission_grant=True,no_RSS_cap_set=True,warning='Inspecting process CPU mask is not an owner/model allocation; this snapshot and historical predictions do not authorize future admission or prove48-way feasibility.'))
put('CPU_READONLY_QUALIFICATION.json',dict(schema='DTC_STAGEIIA_REMAINING48_CPU_READONLY_QUALIFICATION_V1',status='PASS_READONLY_PREPARATION'if not gaps else'QUALIFICATION_GAPS_RETAINED',checks=checks,loop_assertions=len(checks),gaps=gaps,formal_first16_review=dict(path=str(cp),sha256=sha(cp),decision=review['decision'],FINAL_REVIEW_sha256=H(cb)),original_core64_count=64,excluded_first16_count=16,remaining48_count=48,input_count24=24,scientific_execution_qualified=False,no_new_spec_or_request_or_cohort_or_UUID=True,new_models_started=0,runtime_owner_model_actions=0))
(O/'README.md').write_text('''# Remaining48 read-only qualification — proposal identities only

Membership is exactly fixed5001 CORE64 minus the16 fixed FIRST_BATCH IDs, yielding24 frozen programs xCH-F128/F256. Formal first16 independent review manifest0107f6b6 was SHA-verified and its PASS/complete statement checked before preparation. No performance, runtime, host ETA or PASS outcome selected or replaced any member.

REMAINING48_PLAN_IDENTITIES.json contains all48 PLAN identities,24 programs, exact input digests and unchanged2 supplemental/4 deferred candidates. PLAN IDs are not native cohorts, scientific requests or UUIDs. There is no execution authorization, registration, spec creation, model/GPU/trace capture or owner action. No actual batch order is supplied here.

QUALIFICATION_EVIDENCE.json contains24 input-binding/trace contracts,96 original accepted-result identities,72 old CH-parent/DH-variant spec pins and8 exact config-file bytes extracted from fixedGit5001. Expected kernels/CTA/instructions, genuine existing whole-body SHA bindings, current commandlist SHA/readability and member size/mtime were checked; large trace bodies were not rehashed. Any gap is retained with its exact candidate, never replaced or dropped. Existing full-application/capture-ELF/numerical-certification limits remain.

Per-input RAM numbers are the fixed historical planning predictions and observed history maxima only. They are not proposed RSS hardcaps, not new memory grants and not workload-selection criteria. PLANNING_RESOURCE_OBSERVATION.json is a timestamped host/cgroup/CPU/NUMA/disk observation from the inspecting process, with no model/owner process inspection; future same-owner legal CPU/resource contracts still require their own authorization and fresh admission.

Original350/named336, prior negative/engineering/recovery identities, current16 results, all7 UNRESOLVED inputs and English LaTeXv0.23 remain unchanged. This directory is CPU-only evidence for the coordinator's independent remaining48 proposal; it does not release the48 or2 supplemental/4 deferred points.
''');print(json.dumps({'status':'PASS_READONLY_PREPARATION'if not gaps else'GAPS_RETAINED','candidates':len(records),'programs':len(inputs),'oldrefs':len(refs),'specpins':len(specpins),'checks':len(checks),'gaps':len(gaps),'programs24':[r['program']for r in progs],'max_estimate_GiB':max(r['resource_estimate']['GiB']for r in progs)}))
