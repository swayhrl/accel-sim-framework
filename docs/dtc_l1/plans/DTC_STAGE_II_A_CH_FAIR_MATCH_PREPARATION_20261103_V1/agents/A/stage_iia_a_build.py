from pathlib import Path
import json,hashlib,subprocess,importlib.util,datetime,shutil,os
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents/A');O.mkdir(parents=True,exist_ok=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,x):
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode();assert not p.exists() or p.read_bytes()==b;p.write_bytes(b)
def pin(p):return {'path':str(p),'sha256':H(p)}
def load(p):return json.loads(Path(p).read_text())
source=R/'tools/l2_config_generator.py';spec=importlib.util.spec_from_file_location('pure_gen',source);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
scope=load(R/'control/SCOPE.json');summary=load(R/'analysis/AUTO_SUMMARY.json');pop=load(A/'agents/A/adaptive_ch_ad1_candidates_v1/INPUT_POPULATION_MANIFEST.json')['inputs'];oldidx=load(A/'agents/A/adaptive_ch_ad1_candidates_v1/CANDIDATE_INDEX.json')
checks=[]
def ck(n,b):assert b,n;checks.append(n)
protected=[R/'control/SCOPE.json',R/'control/MATRIX_CURRENT.json']+[R/'analysis'/f"{t['cohort']}.RESULT.json" for t in scope['points'] if (R/'analysis'/f"{t['cohort']}.RESULT.json").is_file()]
before={str(p):H(p) for p in protected};ck('35_inputs',len(pop)==35);ck('350_primary_cells',len(scope['points'])==350)
smallres=[];states={};accepted=0
for t in scope['points']:
 p=R/'analysis'/f"{t['cohort']}.RESULT.json";x=load(p) if p.is_file() else None
 if x:
  yes=x['state'] in ['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','REFERENCE_ACCEPTED_NO_NEW_START'];accepted+=yes
  r={**t,'state':x['state'],'accepted':yes,'cycles':x.get('cycles')if yes else None,'uuid':x.get('uuid'),'result_evidence':pin(p),'proof_identity':{k:x.get('proof',{}).get(k) for k in ['core_commit','framework_commit','binary_sha256','input_digest','performance_accepted','status','profile','downstream_profile']}}
  if x['state']=='REFERENCE_ACCEPTED_NO_NEW_START':r.update(reference_cohort=x.get('reference_cohort'),reference_result_path=x.get('reference_result_path'),reference_result_sha256=x.get('reference_result_sha256'),reuse_verification=x.get('reuse_verification'))
 else:
  guard=R/'analysis'/f"{t['cohort']}.ENGINEERING_GUARD.json";ck('only_registered_scan_engineering_missing_result',t['program']=='scan' and t['profile']=='M16' and guard.is_file());r={**t,'state':'ENGINEERING_NEGATIVE_NO_PRIMARY_RESULT','accepted':False,'cycles':None,'uuid':None,'engineering_evidence':pin(guard),'auto_summary_state_preserved':'PENDING'}
 smallres.append(r);states[r['state']]=states.get(r['state'],0)+1
ck('primary_accepted331',accepted==331);ck('primary_fail18',states.get('FAIL_L2MLP_ARCHIVED_NO_RETRY')==18)
put('PHASE_I_ORIGINAL350_FREEZE.json',{'schema':'STAGE_IIA_ORIGINAL350_READONLY_FREEZE_V1','authority_commit':'361fa6fa0700825bb9cda43e25b9fd1f60e0b262','states':states,'accepted':accepted,'named336_not_imported':True,'original6_P0_references_preserved_disclosed':True,'cells':smallres})
by={(r['input_digest'],r['cell'],r['profile']):r for r in smallres}
records=[];config_records={};inputrows=[];rs=[];L1diff=None
for inp in pop:
 dig=inp['input_digest'];prog=inp['program'];prefix=dig[:16];binding=Path(inp['input_binding_path']);ck(prog+'_input_binding_sha',H(binding)==inp['input_binding_sha256']);b=load(binding)
 dest=O/'inputs'/f'{prefix}.INPUT_BINDING.json';dest.parent.mkdir(exist_ok=True);shutil.copyfile(binding,dest)
 trace=Path(inp['trace_entry']);asset=b['asset'];ck(prog+'_commandlist_sha',H(trace)==asset['commandlist_sha256'])
 q=b['qualification'];qkern=q.get('kernels',[]);allmembers=all((trace.parent/m['relative_path']).is_file() for m in asset['members']);ck(prog+'_trace_members_readable',allmembers)
 inputrows.append({'program':prog,'suite':inp['suite'],'input_digest':dig,'input_binding':pin(binding),'binding_snapshot':str(dest.relative_to(O)),'trace_entry':str(trace),'commandlist_sha256':asset['commandlist_sha256'],'expected':inp['expected'],'coverage':inp['coverage'],'native_values':'UNPROVEN','existing_full_SHA_receipts_reused_without_trace_reread':True,'trace_member_count':len(asset['members']),'trace_member_SHA_contract':inp['trace_SHA_contract'],'asset_extent':asset.get('extent'),'asset_kind':asset.get('kind'),'qualification_status':q.get('status'),'current_readability_check':allmembers})
 chsp=R/'control/specs'/f'E2-DTCL2MLP-{prefix}-CH-P0-V1.json';dhsp=R/'control/specs'/f'E2-DTCL2MLP-{prefix}-DH-P0-V1.json';ch=load(chsp);dh=load(dhsp)
 diff={k:{'CH':ch['expected_options'].get(k),'DH':dh['expected_options'].get(k)}for k in set(ch['expected_options'])|set(dh['expected_options'])if ch['expected_options'].get(k)!=dh['expected_options'].get(k)}
 if L1diff is None:L1diff=diff
 ck(prog+'_same_CH_DH_L1_contract',diff==L1diff)
 hist=[]
 for t in scope['points']:
  if t['input_digest']!=dig:continue
  done=R/'control/qualification_ledger'/f"{t['cohort']}.DONE.json"
  if done.is_file():
   z=load(done);hist.append({'cohort':t['cohort'],'cell':t['cell'],'profile':t['profile'],'accepted':by[(dig,t['cell'],t['profile'])]['accepted'],'elapsed_seconds':z.get('elapsed_seconds'),'peak_observed_rss_bytes':z.get('peak_observed_rss_bytes'),'stop_reason':z.get('stop_reason'),'launcher_wait_returncode':z.get('launcher_wait_returncode'),'DONE':pin(done)})
 rss=[x['peak_observed_rss_bytes']for x in hist if isinstance(x['peak_observed_rss_bytes'],int)];elapsed=[x['elapsed_seconds']for x in hist if isinstance(x['elapsed_seconds'],(int,float))];mx=max(rss) if rss else None
 estimate=max(4*1024**3,int(mx*1.25)+1024**3)if mx else None
 rs.append({'program':prog,'input_digest':dig,'history':hist,'max_observed_rss_bytes':mx,'proposed_reservation_bytes':estimate,'reservation_is_plan_not_authorized_cap':True,'CH_P0_history':[x for x in hist if x['cell']=='CH'],'min_completed_elapsed_seconds':min(elapsed)if elapsed else None,'max_completed_elapsed_seconds':max(elapsed)if elapsed else None,'qualification':'RESOURCE_REVIEW_REQUIRED_HIGH_MEMORY'if prog=='lavamd' else 'HISTORY_ESTIMATE_ONLY_NEW_RUNTIME_AUTH_REQUIRED'})
 for prof in ['F128','F256']:
  texts=[Path(c['path']).read_text()for c in ch['configs']];tt,transform=g.generate(texts,prof)
  for i,(txt,old)in enumerate(zip(tt,ch['configs'])):
   ck(prog+'_'+prof+'_old_config_pin_'+str(i),H(old['path'])==old['sha256']);p=O/'configs'/f'CH_{prof}'/f'config-{i}.config';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(txt);ck(prog+'_'+prof+'_gen_sha_'+str(i),H(p)==transform['config_sha256_after'][i])
  dp=R/'control/specs'/f'E2-DTCL2MLP-{prefix}-DH-{prof}-V1.json';ds=load(dp);candopt={k:[v] if isinstance(v,str)else v for k,v in transform['effective_options'].items()}
  # Compare the full tokenized effective manifest; multiline timing values use original token arrays.
  eo=json.loads(json.dumps(ch['expected_options']));eo[g.FR]=[str(128 if prof=='F128'else 256)]
  delta={k:{'CH':eo.get(k),'DH':ds['expected_options'].get(k)}for k in set(eo)|set(ds['expected_options'])if eo.get(k)!=ds['expected_options'].get(k)}
  ck(prog+'_'+prof+'_all_downstream_equal',delta==L1diff)
  parent=by[(dig,'CH','P0')];d0=by[(dig,'DH','P0')];dv=by[(dig,'DH',prof)]
  if prog=='SYRK' or not dv['accepted']:category='DEFERRED';reason='Original DH variant missing/negative; SYRK also lacks both original P0 baselines. New separately authorized recovery prerequisite; IR/R2 not substituted.'
  elif prog in ['hybridsort','lavamd']:category='SUPPLEMENT';reason='Single accepted original DH F level outside common F128/F256 core; preserve separately. '+('Original CH-P0 negative: only absolute CH-F/DH-F comparison possible; P0-normalized CH and relative-gain metrics unavailable.'if prog=='lavamd'else'F128 original DH negative; F256 supplement cannot enter common F128/F256 GM.')
  else:category='CORE';reason='Original CH-P0, DH-P0, DH-F128 and DH-F256 all accepted; fixed common32 population independent of new CH outcomes.'
  ident='PLAN-DTC-IIA-'+prefix+'-CH-'+prof+'-V1';cfg=[{'path':f'configs/CH_{prof}/config-{i}.config','sha256':h}for i,h in enumerate(transform['config_sha256_after'])]
  config_records.setdefault(prof,{'configs':cfg,'transform':transform,'exact_changed_option':g.FR,'same_DH_downstream_options':True})
  records.append({'candidate_id':ident,'schema':'DTC_STAGE_IIA_PLANNING_CANDIDATE_NOT_NATIVE_SPEC_V1','registration_status':'NOT_REGISTERED','scientific_execution_authorized':False,'model_starts':0,'runtime_uuid':None,'program':prog,'suite':inp['suite'],'input_digest':dig,'cell':'CH','profile':prof,'category':category,'category_reason':reason,'configs':cfg,'parent_CH_P0':parent,'matched_DH_P0':d0,'matched_DH_variant':dv,'original_parent_spec':pin(chsp),'original_DH_variant_spec':pin(dp),'input_binding':pin(binding),'trace_entry':str(trace),'expected':inp['expected'],'effective_options':eo,'all_downstream_equal_DH':True,'CH_DH_exact_L1_differences':delta,'resource_estimate_bytes':estimate,'baseline_fourway_available_before_new_CH':parent['accepted']and d0['accepted']and dv['accepted'],'authorization_gate':'NEW_DTC_MAIN_SCIENTIFIC_IDENTITY_RESOURCE_EXECUTION_APPROVAL_REQUIRED','old_AD1_candidate_not_promoted':True})
ck('70_unregistered_candidates',len(records)==70);from collections import Counter
ct=dict(Counter(x['category']for x in records));ck('64_2_4_partition',ct=={'CORE':64,'SUPPLEMENT':2,'DEFERRED':4})
put('INPUT_SHA_AND_COVERAGE.json',{'schema':'DTC_STAGE_IIA_FROZEN35_INPUT_CONTRACT_V1','count':35,'inputs':inputrows,'new_trace_capture':False,'full_trace_body_reread':False,'limitations':'Pinned existing full SHA/body qualification reused; commandlists rehashed and member existence checked. Complete declared captured trace does not certify full native application or numerical correctness.'})
put('CH_CANDIDATE_MATRIX.json',{'schema':'DTC_STAGE_IIA_70_PLANNING_IDENTITIES_V1','candidate_counts':ct,'matrix_registered':False,'models_started':0,'full35_population_frozen':True,'named336_performance_used':False,'candidates':records})
put('CONFIG_QUALIFICATION.json',{'schema':'DTC_STAGE_IIA_CONFIG_EXACT_MATCH_V1','Core':'9eedb3131937748f0492fa83aad37d3691118d70','Framework':'02775fd795cde5aae1480d81cee6eb481d0a08f4','binary_sha256':'02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d','generator':pin(source),'profiles':config_records,'CH_DH_only_differences':L1diff,'FRFCFS_coupling':{'P0':{'FRFCFS':64,'shared_credits_per_controller':255},'F128':{'FRFCFS':128,'shared_credits_per_controller':319},'F256':{'FRFCFS':256,'shared_credits_per_controller':447},'formula':'F + 192 - (2 - 1)','private_limit_per_subpartition':1,'private_credit_slots_per_controller':2,'source':pin('/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/l2cache.cc'),'lines':'131-147','interpretation':'Coupled FRFCFS scheduler capacity and shared memory-partition-credit limit; not isolated pure queue capacity.'},'physical_area_or_latency_cost':'UNKNOWN; CH/DH L1 structures differ; not iso-area. Expanded slots are not free physical hardware.'})
put('RESOURCE_AND_ARCHIVE_QUALIFICATION.json',{'schema':'DTC_STAGE_IIA_RESOURCE_ARCHIVE_PLANNING_V1','execution_qualified':False,'model_starts':0,'per_input_history':rs,'resource_rule':'Before future authorization remeasure host/cgroup/affinity/NUMA; dynamic safe admission using same-input peak RSS plus margin and measured pressure. Proposed reservations are not guaranteed caps. No model signals/controller mutation in preparation.','lavamd_rule':'Original CH-P0 recorded high RSS and failed resource guard; independently review CH-F128 resource envelope and explicit baseline gaps. Never silently reuse old 4 GiB prediction or 16 GiB hard cap.','archive_rule':'Future execution: native epoch2 source, logs streamed compressed to true164; exact source/binary/input/config/DONE/strict/archive/native restore receipts; preserve original UUID and all failures; new scientific request/independent identity; sole owner only after authorization.','not_yet_qualified':['New scientific identity and grant','New execution authorization','Actual host/cgroup admission envelope at launch','Runtime workload liveness for CH-F128/F256','lavamd resource approval','No new simulator qualification run permitted by this Goal']})
put('CPU_CHECKS_INITIAL.json',{'status':'PASS','check_count':len(checks),'checks':checks,'protected_before':before,'model_launches':0,'source_only_transform':True})
print(json.dumps({'output':str(O),'checks':len(checks),'candidates':ct,'original350states':states,'protected_count':len(before)}))

