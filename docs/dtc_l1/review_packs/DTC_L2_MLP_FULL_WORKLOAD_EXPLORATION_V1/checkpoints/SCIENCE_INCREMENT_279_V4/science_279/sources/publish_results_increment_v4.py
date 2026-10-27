"""Small scientific delta publication. Old-pair populations remain explicit."""
import pathlib,json,hashlib,math,collections,gzip,datetime
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=A/'agents/A/results_increment_v4';read=lambda p:json.loads(P(p).read_bytes());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();cap=read(D/'LATEST_CAPTURE.json');run=P(cap['run_path']);a=read(run/'ANALYSIS.json');r=read(run/'report.json');s=read(run/'SUPPLEMENT.json');oldrun=P(cap['previous_checkpoint_path']).parent;old=read(oldrun/'ANALYSIS.json');osup=read(oldrun/'SUPPLEMENT.json');oldpairs={(p['input_digest'],p['profile']):p for p in old['all_matched_DH_pairs']};pairs={(p['input_digest'],p['profile']):p for p in a['all_matched_DH_pairs']};assert len(oldpairs)==191 and len(pairs)==207
def gm(v):return math.exp(math.fsum(math.log(x)for x in v)/len(v))if v else None
def stats(rows):
 v=[x['DH_speedup']for x in rows];return dict(n=len(v),GM=gm(v),positive=sum(x>1 for x in v),neutral=sum(x==1 for x in v),negative=sum(x<1 for x in v),minimum=min(v)if v else None,maximum=max(v)if v else None,population=[x['input_digest']for x in rows])
for key,p in oldpairs.items():
 n=pairs[key];assert all(n[k]==p[k]for k in['P0_result_sha256','variant_result_sha256','P0_uuid','variant_uuid','P0_cycles','variant_cycles','DH_speedup','non_target_options_sha256','input_binding_sha256'])
population_changes={}
for profile,ps in a['partial_uniform_DH_statistics'].items():
 prior=old['partial_uniform_DH_statistics'][profile];ids=set(prior['population']);anchor_rows=[p for (d,f),p in pairs.items()if f==profile and d in ids];added=[p for(d,f),p in pairs.items()if f==profile and d not in ids];same=stats(anchor_rows);assert abs(same['GM']-prior['GM'])<1e-14;population_changes[profile]=dict(anchor_population_n=prior['n'],anchor_GM=prior['GM'],same_anchor_population_now=same,new_population_rows=added,expanded_available=s['profile_statistics'][profile]['available'],current_all8_common=s['profile_statistics'][profile]['common_all8'],same_population_cycle_or_speedup_changes=0,population_expansion_not_new_measurement_of_oldpairs=True)
newpairs=a['new_or_newly_matched_pairs'];grouped=collections.defaultdict(list)
for p in newpairs:grouped[p['program']].append(p)
p0missing=[];chmissing=[]
for d,ps in r['table'].items():
 program=r['programs'][d];b=ps['P0']['DH'];variants=[f for f in r['profiles']if f!='P0'];accepted=[f for f in variants if ps.get(f,{}).get('DH',{}).get('accepted')]
 if not b['accepted']:p0missing.append(dict(**program,P0_cohort=b['cohort'],P0_state=b['state'],accepted_variants_waiting_denominator=accepted,blocked_pair_count=len(accepted)))
 b=ps['P0']['CH']
 if not b['accepted']:chmissing.append(dict(**program,P0_cohort=b['cohort'],P0_state=b['state']))
byprogram={p:dict(new_matched_profiles=[x['profile']for x in rows],pairs=[dict(profile=x['profile'],P0_cycles=x['P0_cycles'],variant_cycles=x['variant_cycles'],DH_speedup=x['DH_speedup'],counter_changes=x['counter_changes'],raw_positive_reason_changes=x['raw_positive_reason_changes'],input_digest=x['input_digest'],P0_uuid=x['P0_uuid'],variant_uuid=x['variant_uuid'],P0_result_sha256=x['P0_result_sha256'],variant_result_sha256=x['variant_result_sha256'],input_binding_sha256=x['input_binding_sha256'],non_target_options_sha256=x['non_target_options_sha256'])for x in rows])for p,rows in grouped.items()}
anchor_common=set(osup['common_all8_population']);current_common=set(s['common_all8_population']);same_common={f:stats([p for(d,g),p in pairs.items()if g==f and d in anchor_common])for f in a['partial_uniform_DH_statistics']};assert all(abs(v['GM']-osup['profile_statistics'][f]['common_all8']['GM'])<1e-14 for f,v in same_common.items());new_cells=[]
for c in cap['newly_accepted']:
 p=next(p for p in read(P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/SCOPE.json'))['points']if p['cohort']==c);new_cells.append(dict(cohort=c,program=p['program'],suite=p['suite'],profile=p['profile'],cell=p['cell'],input_digest=p['input_digest']))
typed=s['typed_engineering_negative'];assert typed['performance_accepted']is False and typed['accepted_cycles']is None;assert all(not(p['program']=='scan'and p['profile']=='M16')for p in pairs.values());assert s['CH_nonP0_accepted_pairs']==s['relative_values_present']==0
inc=dict(schema='DTC_L2_MLP_SCIENTIFIC_INCREMENT_V4',status='READ_ONLY_INCREMENT_FROZEN_35_INITIAL_350',utc=r['utc'],anchor=dict(path=str(oldrun),report_sha256=sha(oldrun/'report.json'),analysis_sha256=sha(oldrun/'ANALYSIS.json'),accepted=271,pairs=191),current=dict(accepted=cap['current_accepted'],new_strict_archive_restore=273,references=6,matched_pairs=len(pairs),CH_P0_accepted=s['coverage_summary']['CH_P0_accepted'],DH_P0_accepted=s['coverage_summary']['DH_P0_accepted'],common_all8_n=len(current_common),full35_profiles=0),raw_increment=dict(new_cells_scanned=8,old271_raw_files_opened_by_increment=0,prior_rows_reused_by_RESULT_SHA_UUID=271,new_raw_errors=cap['new_raw_evidence_errors'],all_279_join=cap['raw_join'],new_IO_chain_status_counts=s['IO_chain_status_counts']),new_accepted_cells=new_cells,unchanged_old191_pairs_identity_and_cycles=True,new_matched_pair_count=len(newpairs),new_pairs_by_program=byprogram,per_profile_population_decomposition=population_changes,per_suite_profile_statistics={f:v['suites']for f,v in s['profile_statistics'].items()},common_population_change=dict(anchor_n=len(anchor_common),current_n=len(current_common),new_programs=[r['programs'][d]for d in sorted(current_common-anchor_common)],unchanged_anchor_population_now=same_common),per_program_coverage=a['coverage'],DH_P0_still_blocking=p0missing,CH_P0_still_missing=chmissing,already_accepted_variants_without_DH_P0=sum(x['blocked_pair_count']for x in p0missing),typed_scanM16_negative_excluded=typed,R2_scope='not included; only original frozen350 cohorts, no future new-source/R2 claims',nonP0_CH_missing=True,relative_DTC_improvement_unavailable=True,whole_application_numerical_values_not_proven=True,FRFCFS_partition_credit_coupling_preserved=True,no_missing_as_zero_or_one=True,no_best_profile_per_program_GM=True,scientific_stage_complete=False,original_campaign_or_production_mutations=0,model_launches=0)
(run/'SCIENTIFIC_INCREMENT.json').write_text(json.dumps(inc,indent=2,sort_keys=True)+'\n');profile_lines=[]
for f,v in s['profile_statistics'].items():
 x=v['available'];cm=v['common_all8'];profile_lines.append(f"| {f} | {x['n']}/35 | {x['GM']:.6f} | {x['positive']}/{x['neutral']}/{x['negative']} | {cm['GM']:.6f} |")
newlines=[]
for p,rows in sorted(grouped.items()):newlines.append('- '+p+': '+', '.join(x['profile']+' '+format(x['DH_speedup'],'.6f')+'x'for x in rows))
block='; '.join(x['program']+' ('+x['P0_state']+', '+str(x['blocked_pair_count'])+' accepted variants)'for x in sorted(p0missing,key=lambda x:x['program']));scan=next(p for p in newpairs if p['program']=='scan'and p['profile']=='F256');sc128=next(p for p in newpairs if p['program']=='scan'and p['profile']=='F128');text=f'''# 科学增量V4：只读快照

采集UTC {r['utc']}（CST05:59:28），原冻结35输入/350点。以E/V3 UTC20:54:53的271 accepted为锚，当前279=273新执行strict+archive/native restore与6已核验reference。仅新8个accepted raw进行闭合/扫描，旧271 raw不重扫；8条raw及新IO链无证据错误。旧191配对的UUID、RESULT SHA、cycles、输入/配置身份全部不变。

## 关键新证据

DH配对191→207，增加16。新增DH-P0 scalarProd/scan/srad_v1解锁3/3/8个配对；另cutcp E384与myocyte Q128各1。新增GESUMMV M16/F256仍缺同design DH-P0，不能计算speedup。所有新增配对核对同输入binding、Core/Framework/binary、完整冻结输入计数以及除L2/FRFCFS两个允许项之外全部effective options；固定DRAM850MHz与10MiB容量。

{chr(10).join(newlines)}

scan F128/F256为{sc128['DH_speedup']:.6f}x/{scan['DH_speedup']:.6f}x，但DRAM_read_atoms只变化{sc128['counter_changes']['DRAM_read_atoms']['change_pct']:.6f}%/{scan['counter_changes']['DRAM_read_atoms']['change_pct']:.6f}%。收益不能归结为显著DRAM读量下降；调度/排队与F+191 partition共享credit同时变化，现证据不分离因果。scan M8回退，srad M8/M16轻微回退；负结果保留。

## 人口口径

| Profile | 当前可配对人口 | 可配对人口GM | 正/平/负 | 全8共同人口25的GM |
|---|---:|---:|---:|---:|
{chr(10).join(profile_lines)}

全8共同人口由{len(anchor_common)}扩大至{len(current_common)}。每个profile在原锚相同人口上的GM均与锚精确相同；全部旧191对没有任何cycles或speedup改变。因此上述GM相对旧报告的变化是新人口/新配对加入，不能当作旧工作负载性能被重新改善。suite分层与available/common两套人口、全部输入列表和新配对counter变化在SCIENTIFIC_INCREMENT.json/SUPPLEMENT.json中保留。

DH-P0 accepted28/35，CH-P0 33/35；DH-P0仍阻塞7项：{block}。这些输入另有{sum(x['blocked_pair_count']for x in p0missing)}个已accepted变体等待分母。CH-P0尚缺：{', '.join(x['program']for x in chmissing)}。

没有任何profile达到full35 accepted。nonP0 CH尚未开展/缺失，不能计算相对DTC收益或正式挑选uniform配置。旧scan M16 typed工程negative保留、accepted_cycles=null，不纳GM；未来R2完全不计本快照。missing不填0/1，不按程序挑最优profile凑GM。raw reservation原因是重试/拒绝次数，非唯一请求数或耗时；last-printed avg latency非全输入加权均值。完整declared trace计数通过不等于原应用数值输出正确性已证明；英文v0.23母版不变。

## 审计边界

本次只写A/results_increment_v4，不改E目录、生产、历史分类或预算，不模拟。主报告/新raw evidence/完整analysis可使用.gz发布；旧锚raw证据按不可变RESULT/UUID链接复用。individual file snapshot不是覆盖全部正在运行任务的单次事务，采集后自然完成的新点不混入本时间截断。
''';(run/'REPORT.md').write_text(text,encoding='utf-8')
for name in ['report.json','ANALYSIS.json','NEW_RAW_REASONS.json','SUPPLEMENT.json','SCIENTIFIC_INCREMENT.json']:(run/(name+'.gz')).write_bytes(gzip.compress((run/name).read_bytes(),mtime=0))
sourcepins=[dict(path=str(D/n),sha256=sha(D/n))for n in ['collect_increment_v4.py','analyze_increment_v4.py','supplement_statistics.py','io_chain_audit.py','publish_results_increment_v4.py','SOURCE_DERIVATION.json']]+[dict(path=str(oldrun/n),sha256=sha(oldrun/n))for n in['report.json','ANALYSIS.json','NEW_RAW_REASONS.json','SUPPLEMENT.json','DELIVERY_MANIFEST.json']];names=['CAPTURE.json','REPORT.md','SCIENTIFIC_INCREMENT.json.gz','SUPPLEMENT.json.gz','ANALYSIS.json.gz','NEW_RAW_REASONS.json.gz','report.json.gz','IO_CHAIN_AUDIT.json'];manifest=dict(schema='A_RESULTS_INCREMENT_V4_DELIVERY_MANIFEST',utc=r['utc'],accepted=279,matched_pairs=207,new_raw_count=8,new_pair_count=16,anchor_sha256=sha(oldrun/'report.json'),source_pins=sourcepins,files=[dict(path=str(run/n),pack_path=n,bytes=(run/n).stat().st_size,sha256=sha(run/n))for n in names],model_launches=0,production_changes=0,E_directory_writes=0);(run/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(path=str(run),manifest_sha256=sha(run/'DELIVERY_MANIFEST.json'),report_sha256=sha(run/'REPORT.md'),accepted=279,pairs=207,new_pairs=16,common_n=len(current_common),missing_DH_P0=[x['program']for x in p0missing],blocked_accepted_variants=sum(x['blocked_pair_count']for x in p0missing),source_pins=len(sourcepins)),indent=2))
