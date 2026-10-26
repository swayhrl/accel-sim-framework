"""Independent AI source/evidence review only; no candidate execution or mutation."""
import pathlib,json,hashlib,importlib.util,datetime,math,ast,gzip
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision18';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');EXPECTED_MANIFEST='f2fbdc3386fbb1968384d797ea18a4d341cf085c005b5c107156bb400f9c1315'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def canon(x):return hashlib.sha256((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
files=[D/'sweep_controller.py',D/'operational_parent_bridge_v1.py',D/'frontend_v1.py',D/'SHORT_FIRST_DISPATCH_POLICY_V1.json',D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json'];before={str(p):sha(p) for p in files};assert before[str(files[-1])]==EXPECTED_MANIFEST
CONT='b7c302aff28712729efc4c06d5744e8cd184c115a069b2536c52b2cba45e6b31';BRIDGE='f2e5582fa8d27765f0b5a6dbcc2f9bd435b8ff07dd24f5d3991f5a630b94f686';POLICY='285243e87a598ffa2eef22bf4dc8283e0e77e6cea9882719f9c868c0917443e1';assert sha(files[0])==CONT and sha(files[1])==BRIDGE and sha(files[3])==POLICY
checks=[]
def ok(name,condition,evidence=None):assert condition,name;checks.append({'check':name,'status':'PASS','evidence':evidence})
manifest=read(files[-1]);ok('explicit_R18_parent_with_preserved_R16_science_lineage',manifest['actual_parent_sha256']==CONT and manifest['bridge_sha256']==BRIDGE and manifest['scientific_parent_lineage_sha256']=='32ebd671924d4e23eda7960c5957708e5a71f225ceb0887edcbe3249f25f65d3',[str(files[-1])])
for pin in manifest['source_pins']:assert sha(pin['path'])==pin['sha256'],pin['path']
ok('all_manifest_static_source_pins_current',True,{'count':len(manifest['source_pins'])})
proofpaths=[F/'ops/R18_CPU_DRIVER_RESULT_V1.json',D/'BRIDGE_FRONT_REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json',D/'OLD_R16_STRICT_FINISH_AND_BINDING_CPU_QUALIFICATION_V1.json'];proofs=[read(p) for p in proofpaths]
for p,pr in zip(proofpaths,proofs):
 assert pr['status']=='PASS' and pr['controller_sha256']==CONT
 if 'bridge_sha256' in pr:assert pr['bridge_sha256']==BRIDGE and pr['manifest_sha256']==EXPECTED_MANIFEST
 drivers=[f for f in D.glob('*.py') if sha(f)==pr['driver_sha256']];assert len(drivers)==1,(p,'driver hash match')
ok('main_mock21_and_front7_8_and_strict16_proofs_bound_to_exact_sources',proofs[0]['scenario_count']==21 and len(proofs[0]['checks'])==19 and len(proofs[1]['scenarios'])==7 and proofs[1]['check_count']==8 and proofs[2]['check_count']==16,[{'path':str(p),'sha256':sha(p)} for p in proofpaths])
ok('CPU_proofs_do_not_claim_real_scientific_models_or_authority_edits',proofs[0]['real_model_or_component_starts']==proofs[0]['real_registry_or_entry_mutations']==proofs[0]['real_signals']==0 and proofs[1]['real_scientific_Popen_calls']==proofs[1]['production_entry_or_authority_or_epoch_writes']==0 and proofs[2]['real_model_starts']==proofs[2]['production_epoch_authority_entry_or_ledger_writes']==0)
policy=read(files[3]);ep=P(policy['evidence_path']);eta=read(ep);ok('policy_frozen_same_input_elapsed_snapshot_SHA',sha(ep)==policy['evidence_sha256'],{'path':str(ep),'sha256':sha(ep)})
completed={r['cohort']:r for r in eta['completed']};short=[];donor_validation=[];progress_cache={}
for cell,row in policy['points'].items():
 spec=read(T/'control'/(cell+'_SPEC.json'));assert spec['program']==row['program'] and spec['cell']==row['config'] and spec['expected']['instructions']==row['expected_instructions']
 assert type(row['short']) is bool and row['scheduling_heuristic_only_not_science_acceptance'] is True
 estimate=row['estimated_seconds'];assert estimate is None or (type(estimate) in [int,float] and math.isfinite(estimate) and estimate>=0)
 if row['short']:
  assert estimate is not None and estimate<=policy['short_threshold_h']*3600;short.append((cell,estimate))
 for ev in row['evidence']:
  assert cell.split('-')[2] in ev['cohort'],'different input identifier'
  if 'elapsed_h' in ev:
   if ev['cohort'] in completed:
    done=completed[ev['cohort']];assert abs(done['elapsed_h']-ev['elapsed_h'])<1e-10
   else:assert row['basis_kind']=='SAME_INPUT_REPAIR_DIFFERENT_BUILD_HEURISTIC_ONLY' and ev['cohort'].startswith('E2-AEREPAIR-')
   root=T if ev['cohort'].startswith('E2-AEV100-') else F/'validation';dp=root/'control/qualification_ledger'/(ev['cohort']+'.DONE.json');receipt=read(dp);assert receipt['launcher_wait_returncode']==0 and receipt['stop_reason'] is None and receipt['native_simulator_observed'] is True
   if ev['cohort'] not in progress_cache:
    ip=dp.with_name(ev['cohort']+'.INTENT.json');intent=read(ip);pp=P(intent['output'])/'progress.jsonl.gz';first=last=None;count=0
    with gzip.open(pp,'rt') as stream:
     for line in stream:
      e=json.loads(line);count+=1;assert e['seq']==count and e['generation']==intent['uuid'];first=first or e
      if last is not None:assert e['mono_ns']>last['mono_ns'] and e['completed']>=last['completed']
      last=e
    assert last['end']=='NATURAL';progress_cache[ev['cohort']]={'path':str(pp),'sha256':sha(pp),'first_mono_ns':first['mono_ns'],'last_mono_ns':last['mono_ns'],'count':count,'natural_progress_interval_seconds':(last['mono_ns']-first['mono_ns'])/1e9}
   actual=progress_cache[ev['cohort']];assert abs(actual['natural_progress_interval_seconds']/3600-ev['elapsed_h'])<1e-10
   donor_validation.append({'cohort':ev['cohort'],'DONE_sha256':sha(dp),'launcher_elapsed_seconds':receipt['elapsed_seconds'],'natural_progress_interval_proof':actual,'different_build_heuristic':row['basis_kind']=='SAME_INPUT_REPAIR_DIFFERENT_BUILD_HEURISTIC_ONLY'})
ok('policy_points_match_frozen_specs_and_10short_le12h',len(short)==10,{'total_points':len(policy['points']),'shortest_four':[(c,s/3600) for c,s in sorted(short,key=lambda x:x[1])[:4]],'completed_natural_donor_checks':len(donor_validation)})
loader=importlib.util.spec_from_file_location('read_only_actual_r18_helpers',files[0]);mod=importlib.util.module_from_spec(loader);loader.loader.exec_module(mod)
fakeq={'admitted_specs':{c:'not_an_authority' for c in policy['points']},'consumed':{},'sealed':[]};order=mod.admit_order(fakeq,mod.T,{}, {},0);expected=sorted(policy['points'],key=lambda c:(0 if policy['points'][c]['short'] else 1,policy['points'][c]['estimated_seconds'] if policy['points'][c]['estimated_seconds'] is not None else float('inf'),policy['points'][c]['expected_instructions'],c))
ok('actual_pure_admit_order_uses_short_then_empirical_time_then_instructions',order==expected,{'order':order})
skip=order[:5];testq={'admitted_specs':fakeq['admitted_specs'],'consumed':{skip[0]:{}},'sealed':[skip[1]]};filtered=mod.admit_order(testq,mod.T,{skip[2]:{}},{skip[3]:1},0,[skip[4]])
ok('actual_pure_admit_order_keeps_consumed_sealed_claim_cooldown_blocked_exclusions',not set(skip)&set(filtered) and set(filtered)==set(order)-set(skip))
source=files[0].read_text();bridge_src=files[1].read_text();tree=ast.parse(source)
ok('source_shortbackfill_and_long_drain_preserve_dual_resource_gates',"for k in [ORIGINAL,LATE,REPAIR]" in source and "if k==ORIGINAL and wait_for_big" in source and "['points'].get(c,{}).get('short',False):continue" in source and "sample=parent_original_resources(s,True) if k==ORIGINAL else late.resources(s,True)" in source and "original_sample=n.resources(s,True)" in source,[str(files[0])+':120',str(files[0])+':128',str(files[0])+':132',str(files[0])+':135'])
ok('source_preserves_model_caps_and_no_preemption_or_restart',"limits={ORIGINAL:40,REPAIR:2,LATE:4}" in source and not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['kill','killpg','terminate','send_signal'] for n in ast.walk(tree)),[str(files[0])+':84',str(files[0])+':96',str(files[0])+':104',str(files[0])+':129'])
ok('source_checks_entry_before_authority_mutation_and_unknown_claims_before_handoff',source.index("entry=N/'bin/native'")<source.index('n.update_authority(activate)') and "unconsumed/unknown claim blocks operational handoff" in source,[str(files[0])+':50',str(files[0])+':64',str(files[0])+':75'])
ok('source_preserves_old_R1_and_negative_GESUMMV_and_three_missing_receipts',"assert registry['registered_future_requests'][OLD_REPAIR]==oldpeer" in source and "if k==ORIGINAL and c in negatives:" in source and "if k==ORIGINAL and c in exceptions:" in source,[str(files[0])+':57',str(files[0])+':74',str(files[0])+':101',str(files[0])+':102'])
ok('R18_prior_R17_review_delegates_to_exact_legacy_source_and_paths',"legacy=load('r18_prior_r17_receipt_review',F/'ops/revision17/operational_parent_bridge_v1.py')" in bridge_src and "prior_m=legacy.manifest();prior_p=prior_m['requests'][request];assert prior_p==p" in bridge_src and "legacy.continuation_record(q,prior_m)" in bridge_src and "legacy.inspect_operational_receipts(request,cell)" in bridge_src,[str(files[1])+':71',str(files[1])+':72',str(files[1])+':77'])
# Capture actual historical R17 source and current continuation records; existing
# model receipts presently belong to the R16 launch prefix, not a made-up R17 run.
oldpaths=[F/'ops/revision17'/name for name in ['sweep_controller.py','operational_parent_bridge_v1.py','frontend_v1.py','OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json']];oldexpected=['62993baf0d7e1a21de76628a1219287206229fe8c8e67123773396886977eea2','01ad5280d71daa9763b209e2fb22759b9f33604c8e401952299b84eafe524e2b','e2783cc7c7fd823d90bd87380dd10d7b8c8054738a654896b3587d89307fbb68','749bb63c784fb60ca5177531cde71b4d01e0778438c7700e9870560e12fd4be7'];assert all(sha(p)==h for p,h in zip(oldpaths,oldexpected))
reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');historical=[];immutable_paths={};record_before={}
for request,root in [('DTC_AE_LAVAMEM_REPAIR_20261026_V2',F/'validation_lava_memory_v2'),('DTC_AE_LATE_FAILURE_REPAIR_20261026_V1',F/'validation_late_failure_v1')]:
 q=reg['registered_future_requests'][request];records=[r for r in q['operational_parent_continuations'] if r['actual_parent_sha256']==oldexpected[0]];assert len(records)==1;record_before[request]=canon(records[0])
 for c,row in q['consumed'].items():
  ip=root/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);out=P(i['output']);ps=[ip,out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'];es=[read(p) for p in ps];assert sha(ip)==row['intent_sha256'];has=any('operational_parent_continuation_binding' in e for e in es)
  historical.append({'cohort':c,'uuid':row['uuid'],'has_captured_operational_binding':has,'INTENT_sha_matches_authority':True,'receipts':[{'path':str(p),'sha256':sha(p)} for p in ps]})
  immutable_paths.update({str(p):sha(p) for p in ps})
ok('real_R17_source_and_registered_continuation_history_preserved',True,{'R17_source_pins':[{'path':str(p),'sha256':h} for p,h in zip(oldpaths,oldexpected)],'actual_consumed_repair_points_snapshot':len(historical),'actual_model_launches_with_R17_binding_observed':sum(x['has_captured_operational_binding'] for x in historical)})
assert all(sha(p)==h for p,h in before.items()) and all(sha(p)==h for p,h in immutable_paths.items())
reg_after=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
for request,h in record_before.items():assert canon(next(r for r in reg_after['registered_future_requests'][request]['operational_parent_continuations'] if r['actual_parent_sha256']==oldexpected[0]))==h
ok('review_left_candidate_and_historical_receipt_bytes_unchanged',True)
report={'schema':'REVISION18_INDEPENDENT_AI_SOURCE_AND_EVIDENCE_REVIEW_V1','status':'PASS','reviewer_role':'DTC independent AI sub-lane; source/evidence reviewer, not an external human or third-party model service','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controller_sha256':CONT,'bridge_sha256':BRIDGE,'frontend_sha256':sha(files[2]),'policy_sha256':POLICY,'manifest_sha256':EXPECTED_MANIFEST,'checks':checks,'blocking_findings':[],'limitations':['本次是独立AI静态/既有CPU证据审查与纯admit_order函数检查，未启动科学模型，不能保证生产运行已完成或没有未覆盖故障。','10个short是同输入其他配置/repair构建的墙钟启发式估计，非同配置保证；不同AE/hash配置与机器负载可改变耗时，<=12h不是SLA。hybridsort明确用不同修复构建。','short优先不抢占已有长模型、不预留专用slot；仍受40/4G/64host48cgroup/5Gdisk与nativeV4实际门。资源不足时不能承诺10个short立即全起或预期数小时全部结束。','当前所见5个已消费LAVA/LATE科学点均是旧R16 launch无operational binding。真实R17已发布source/manifest与注册continuation PID/start/FD保留；旧R17 launch委托分支的正/负例是明确CPU合成metadata资格，不是实际R17科学模型回放。','保留预算/历史source身份不代表修复run可以并入原性能矩阵；科学正确性仍需原strict全人口/source/runtime/trace/BA与自然DONE，native数值等价未由调度资格证明。','review不执行handoff/activation；实际接管仍需旧R17parent退出、无未消费unknown claim、fresh source/entry/ghost证书校验，所有活模型保持。'],'source_pins':[{'path':p,'sha256':h} for p,h in sorted(before.items())]+[{'path':str(p),'sha256':sha(p)} for p in proofpaths]+[{'path':str(ep),'sha256':sha(ep)}],'natural_elapsed_donor_checks':donor_validation,'actual_historical_receipt_snapshot':historical,'real_model_starts':0,'real_registry_or_authority_or_entry_writes':0,'old_evidence_mutations':0,'signals_sent':0,'intended_publication':'User requested current-state GitHub review package for separate ChatGPT review; this report does not claim that external review has happened.'}
dest=D/'REVISION18_INDEPENDENT_AI_REVIEW_V1.json'
with dest.open('x') as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','check_count':len(checks),'path':str(dest),'sha256':sha(dest),'controller_sha256':CONT,'bridge_sha256':BRIDGE,'policy_sha256':POLICY,'manifest_sha256':EXPECTED_MANIFEST},indent=2))
