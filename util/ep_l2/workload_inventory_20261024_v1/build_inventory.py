#!/usr/bin/env python3
"""Merge bounded metadata/evidence into one input-variant inventory."""
from pathlib import Path
import json,csv,collections,datetime,hashlib,os
W=Path('/root/data/ep_l2_main_20261023_v1/worktree');O=W/'docs/ep_l2/operations/ep_main_workload_inventory_20261024_v1';N=Path('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
sourcep=next((N/'control/source_historical_preimages').glob('EP_REGISTRY_*'));reg=read(sourcep);m=reg['mechanism_study_20261019_v1']
obs=read(O/'SOURCE_CURRENT_EXACT_METADATA.json');byentry={x['entry']:x for x in obs['inputs']}
roster=list(csv.DictReader((O/'evidence/legacy_roster.csv').open()));rod=read(O/'evidence/rodinia_metadata.json')['inputs'];coverage=read(O/'evidence/local_coverage.json')
legacy={r['trace_list']:r for r in roster}
selections={}
for sid,record in m['input_selections'].items():
 i=record['selection']['full_input_identity'];s=i['runtime_independent_input_source'];entry=s.get('entry_trace_path',s.get('entry'))
 selections[entry]=(sid,record,i,s)
nativeassets=read(O/'NATIVE_CURRENT_EXACT_ASSETS.json')
native_by_entry={a['source_root']+'/kernelslist.g':(aid,a) for aid,a in nativeassets.items()}
current_results={p['path']:p for p in read(O/'RECENT_RESULTS_CURRENT_METADATA.json')['data']['paths']}
family={
 '3mm':('PolyBench/GPU','3mm','NO_ARGS; actual compile-time dimensions UNKNOWN','矩阵链乘微基准'),
 'gemm':('PolyBench/GPU','gemm','NO_ARGS; actual compile-time dimensions UNKNOWN','密集矩阵乘微基准'),
 'FWT_11_19':('CUDA SDK/Samples','fastWalshTransform','logK=11, logD=19','多阶段Walsh变换样例'),
 'FWT_7_21':('CUDA SDK/Samples','fastWalshTransform','logK=7, logD=21','多阶段Walsh变换样例'),
 'vectorAdd_4M':('CUDA SDK/Samples','vectorAdd','size=4000000','流式向量加法样例/微基准'),
 'convolutionSeparable':('CUDA SDK/Samples','convolutionSeparable','size=3072','可分离卷积样例'),
 'scan':('CUDA SDK/Samples','scan','NO_ARGS; exact defaults/build UNKNOWN','前缀和样例'),
 'cfd_097k':('Rodinia3.1','cfd','fvcorr.domn.097K','非结构网格CFD基准'),
 'dwt2d':('Rodinia3.1','dwt2d','rgb.bmp; 1024x1024; f=5; l=3','二维小波变换基准'),
 'btree':('Rodinia3.1','btree','mil.txt + command.txt','树遍历基准'),
 'sad':('Parboil','sad','default reference.bin + frame.bin','绝对差和/块匹配基准'),
 'sgemm':('Parboil','sgemm','medium matrix1.txt + matrix2t.txt','单精度矩阵乘基准'),
 'spmv':('Parboil','spmv','large Dubcova3 matrix/vector','稀疏矩阵向量乘基准')}
status_labels={
 'EP_NATIVE_PROVEN_INPUT_AND_RUNTIME':'EP原生输入和runtime已验证；新启动仍需新规格/预算',
 'SOURCE_ACCEPTED_NEEDS_NATIVE_INPUT':'近期EP接受；需精确输入物化和native资格/新cohort',
 'SHARED_NATIVE_INPUT_EP_Q_MISSING':'真164共享输入已就位；EP资格/登记待补',
 'KNOWN_INPUT_HOLD':'保留输入语义/格式HOLD',
 'LEGACY_BASELINE_ONLY':'仅旧B0历史索引；当前EP输入/profile资格待补',
 'CONDITIONAL_METADATA_ONLY':'有确切trace元数据；完整输入/host/runtime资格未闭合'}
rows=[]
for entry,x in byentry.items():
 old=legacy.get(entry)
 if old:
  name=old['workload'];suite,program,variant,kind=family[name]
 else:
  rr=next(z for z in rod if z['entry']==entry)
  if 'bfs-' in entry:
   variant=next(z for z in ['graph1MW_6','graph4096','graph65536'] if z in entry)
   name='BFS_'+variant;suite='Rodinia3.1';program='bfs';kind='图遍历/多kernel基准'
  else:
   variant='1024_2_2' if '/1024_2_2' in entry else '512_2_2'
   name='Hotspot_'+variant;suite='Rodinia3.1';program='hotspot';kind='结构网格热传导stencil基准；当前输入仅1kernel'
 recent=[a for a in m['attempts'] if a.get('identity',{}).get('workload')==name]
 accepted={k:a for k,a in m['accepted_results'].items() if a.get('identity',{}).get('workload')==name}
 pairs={k:a for k,a in m['accepted_pairs'].items() if a.get('endpoints',{}).get('left',{}).get('identity',{}).get('workload')==name}
 canonical={k:a for k,a in reg['runs'].items() if a.get('identity',{}).get('workload')==name}
 source_sel=selections.get(entry);aid,na=native_by_entry.get(entry,(None,None))
 stage='SOURCE_ACCEPTED_NEEDS_NATIVE_INPUT' if accepted else 'LEGACY_BASELINE_ONLY' if old else 'CONDITIONAL_METADATA_ONLY'
 holds=[]
 if name=='vectorAdd_4M':stage='EP_NATIVE_PROVEN_INPUT_AND_RUNTIME'
 if name=='gemm':stage='SHARED_NATIVE_INPUT_EP_Q_MISSING';holds.append('DTC_AD_GEMM exact input reuse does not grant EP runtime/profile qualification')
 if name=='btree':
  stage='KNOWN_INPUT_HOLD';holds.append('Nonzero active-mask/full32 address semantics conflict; original E input_scope_HOLD retained')
 if name=='spmv':
  stage='KNOWN_INPUT_HOLD';holds.append('IADD3 record missing source register; no silent trace repair or old-cycle qualification')
 if name=='scan':
  stage='KNOWN_INPUT_HOLD';holds.append('Unsupported nonzero/modern/shared-address tail; complete input clearance not granted')
 if program=='bfs':holds += ['No complete input byte/grammar/non-atomic/domain qualification','Captured graph/source node/build/tools/GPU/payload bindings unresolved','C host-boundary preparation delivered; actual alias/host-update semantics and E adoption still unresolved']
 if program=='hotspot':holds += ['Candidate metadata only, source/input/native profile Q missing','One kernel here does not establish cross-kernel iteration reuse']
 h={'canonical_run_records':len(canonical),'recent_actual_start_count':sum(a.get('actual_start') is True for a in recent),'recent_original_attempt_states':dict(collections.Counter(a['state'] for a in recent)),'accepted_result_index_count':len(accepted),'accepted_result_ids':list(accepted),'accepted_pair_ids':list(pairs),'recent_source_lineages':sorted({a['identity']['core_source_commit'] for a in recent}),'root_run_index_is_not_actual_start_budget':True,'historical_baseline_roster':old}
 if name=='vectorAdd_4M':
  h['native_EP_migration']=[{'cohort':c,'state':read(N/'control/qualification_ledger'/(c+'.DONE.json')).get('stop_reason') or 'NATURAL_COMPLETE','charged':1} for c in ['EP_NATIVE_MIGRATION_Q1','EP_NATIVE_MIGRATION_Q2']]
  h['native_EP_research_point']=read('/root/data/ep_l2_main_vector_r5_20261023_v1/control/SCIENCE_QUALIFICATION_EP_NATIVE_TAGPRESSURE_VECTOR_HOLDOUT_V1.json')
 native_entry=Path(entry)
 pubhash=old['trace_list_sha256'] if old else next(z['entry_sha256'] for z in rod if z['entry']==entry)
 capture=x.get('capture_script')
 row={'input_id':name,'suite_declared_by_saved_asset':suite,'benchmark_program_id':suite+':'+program,'program':program,'variant':variant,'algorithm_or_scope':kind,'input_unit':'exact program+input variant+frozen commandlist; not one independent workload per kernel/profile','source_entry':entry,'source_metadata_asof_utc':obs['utc'],'source_current_metadata':x,'commandlist_hash_matches_frozen_index':x['commandlist_sha256']==pubhash,'kernel_launches':x['kernel_launches'],'unique_trace_files':x['unique_kernel_files'],'trace_body_logical_bytes':x['body_logical_bytes'],'source_body_content_rehashed_this_pass':False,'old_source_physical_presence':'PRESENT_READABLE_METADATA_ONLY','old_source_saved_historical_identity':source_sel[2] if source_sel else None,'source_selection_id':source_sel[0] if source_sel else None,'source_capture_provenance':{'run_sh_present':capture is not None,'captured_command_literal':capture,'application_source_revision':source_sel[3].get('source_revision','UNKNOWN') if source_sel else 'UNKNOWN','capture_GPU_model':'NOT_VERIFIED','CUDA_folder_label_is_not_exact_capture_toolchain_proof':True,'numeric_SASS_output_validation':'UNKNOWN','model_replay_scope':'Frozen complete commandlist where independently qualified; no from-source recapture/numeric claim'},'history':h,'native_input':{'exact_asset_id':aid,'registered_project':'DTC_L1' if aid=='DTC_AD_GEMM' else 'EP_L2' if aid else None,'current_compatibility_entry_exists':native_entry.exists(),'current_compatibility_realpath':str(native_entry.resolve()) if native_entry.exists() else None,'known_true164_mount_root':na['target_mount_root'] if na else None,'current_ensure_metadata_proof':na,'other_true164_archives':'NOT_SEARCHED_NO_WHOLE_NAS_SCAN'},'readiness_stage':stage,'readiness_description':status_labels[stage],'scientific_holds_or_missing':holds,'launch_authorized_now':False,'launch_blocker_common':'No unused EP science cohort budget; fresh exact native spec, qualification, current resource admission and explicit authorization needed','EP_native_runtime_proven':name=='vectorAdd_4M','results_storage_scope':{'recent_result_roots':[a.get('result_directory') for a in recent if a.get('result_directory')],'recent_result_directory_and_raw_stat':'RECENT_RESULTS_CURRENT_METADATA.json','old_complete_result_true164_mapping_known':name=='dwt2d','all_old_results_claimed_archived':False}}
 if old:
  row['kernel_count_matches_historical_roster']=int(old['kernel_launches'])==x['kernel_launches']
  assert row['commandlist_hash_matches_frozen_index'] and row['kernel_count_matches_historical_roster']
 assert x['all_bodies_metadata_present']
 rows.append(row)
rows.sort(key=lambda a:(a['suite_declared_by_saved_asset'],a['program'],a['variant']))
qindex=[]
for qid,r in m['qualifications'].items():
 q=r['qualification'];qindex.append({'qualification_id':qid,'path':r['path'],'sha256':r['sha256'],'status_as_published':q.get('status'),'qualified_by':q.get('qualified_by'),'source_identity':q.get('source_identity'),'input_selection_id':q.get('input_selection_id',q.get('detach_observer_diagnostic',{}).get('input_selection_id')),'supported_profile_names':list(q.get('supported_profiles',{})),'central_scientific_hold':m.get('scientific_holds',{}).get('qualification:'+qid),'native_epoch2_qualification_inherited':False})
put('RUNTIME_PROFILE_QUALIFICATION_INDEX.json',qindex)
history={'schema':'EP_MAIN_READONLY_WORKLOAD_RUN_INDEX_V1','registry_projection_path':str(sourcep),'registry_projection_sha256':sha(sourcep),'canonical_run_record_count':len(reg['runs']),'canonical_records_warning':'Mixed schemas/campaigns/overlapping logical keys. Not 145 charged new starts and not additive with57 attempts.','canonical_run_records':[{k:r[k] for k in ['run_key','experiment_id','campaign_id','lease_id','attempt_id','profile','status','identity','summary_path','result_directory','raw_path','detail','qualification_id'] if k in r} | {'registry_key':key} for key,r in reg['runs'].items()],'current_mechanism_attempts':m['attempts'],'current_mechanism_accepted_results':m['accepted_results'],'current_mechanism_accepted_pairs':m['accepted_pairs'],'original_counts':{'actual_starts':57,'original_execution_COMPLETE_VALID':44,'accepted_result_index':44,'accepted_pairs':25,'T0':1792414193},'new_EP_native_epochs':'EP migrationQ1/Q2 and one Vector r5 research point indexed separately in the Vector input row'}
put('HISTORICAL_RUN_INDEX.json',history)
stages=dict(collections.Counter(r['readiness_stage'] for r in rows))
summary={'input_variants':len(rows),'benchmark_programs_not_kernel_or_profile_count':len({r['benchmark_program_id'] for r in rows}),'suite_count':len({r['suite_declared_by_saved_asset'] for r in rows}),'historical_B0_roster_variants':len(roster),'recent_selected_inputs':len(selections),'recent_distinct_executed_inputs':len({a['identity']['workload'] for a in m['attempts']}),'recent_distinct_accepted_inputs':len({a['identity']['workload'] for a in m['accepted_results'].values()}),'original_MAIN_accepted_inputs':6,'original_MAIN_declared_inputs':7,'independent_SGEMM_exploration_accepted_inputs':1,'metadata_complete_old_source_inputs':sum(r['source_current_metadata']['all_bodies_metadata_present'] for r in rows),'current_source_unique_trace_files':sum(r['unique_trace_files'] for r in rows),'current_source_sum_trace_body_logical_bytes':sum(r['trace_body_logical_bytes'] for r in rows),'logical_size_not_NAS_physical_allocation':True,'native_qualified_EP_input_variants':sum(r['EP_native_runtime_proven'] for r in rows),'known_shared_DTC_native_input_variants_in_EP_roster':sum(r['native_input']['exact_asset_id']=='DTC_AD_GEMM' for r in rows),'readiness_counts':stages,'new_scientific_starts':0,'input_payload_bytes_copied':0,'trace_body_bytes_read':0,'launch_authorized_inputs_now':0}
assert summary['input_variants']==18 and summary['benchmark_programs_not_kernel_or_profile_count']==14 and summary['suite_count']==4
assert sum(summary['readiness_counts'].values())==18
doc={'schema':'EP_MAIN_WORKLOAD_ASSET_INVENTORY_V1','asof_local_time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'EP-L2 known exact workload assets: legacy13 roster, current8 selections,5 named Rodinia variants; DTC only explicit shared input appendix, not its research ledger','science_identity':'H0 Volta-derived simulator target and main61/r4/r5 lineages, not an RTX4080 qualification; capture GPU and simulator target are separate','summary':summary,'readiness_labels':status_labels,'inputs':rows,'research_only_not_materialized_or_qualified':['Parboil stencil','Parboil histo','CUDA SDK histogram','new H200 ML/WMMA public-release ideas (no exact selected input/format/Q in EP inventory)'],'not_a_blanket_asset_search':'Bounded18 exact commandlists+159 body stat records and175 exact recent result/control paths; no directory crawl or all-NAS search','prior_candidate_statuses_must_be_time_joined':'Old FWT/SGEMM pending preparation is superseded for exact later accepted endpoints. OldBFS C package-not-delivered wording is superseded by its actual preparation delivery, but qualification gaps remain.','historical_B0_final_acceptance':'13 historical Legacy cycle/source references exist in lane5 roster; no final26 closeout was located at the two published historical Git paths checked. No new26/26 current scientific acceptance is asserted.'}
put('WORKLOAD_ASSET_INVENTORY.json',doc)
# A single human-readable table with independent run/readiness columns.
stage_zh={'EP_NATIVE_PROVEN_INPUT_AND_RUNTIME':'EP原生已验证','SOURCE_ACCEPTED_NEEDS_NATIVE_INPUT':'旧EP接受；待物化/原生资格','SHARED_NATIVE_INPUT_EP_Q_MISSING':'共享输入就位；缺EP资格','KNOWN_INPUT_HOLD':'HOLD','LEGACY_BASELINE_ONLY':'仅旧B0；需新资格','CONDITIONAL_METADATA_ONLY':'候选；资格未闭合'}
head=f"""# EP-L2 workload资产清点（2026-10-24）

本轮为只读资产盘点。18个精确输入变体、14个benchmark程序、4个suite；不以kernel数、S/F、不同binary或输入尺寸重复计算独立workload。没有启动模拟、native测试、编译、搬运trace或修改科研账本。

已对原174的18份精确commandlist/相邻run.sh作小文件读取，对159个commandlist指定trace文件及175个已知结果/控制路径作stat。18组输入的159个body当前都存在且可读，逻辑总量{summary['current_source_sum_trace_body_logical_bytes']:,}B（约{summary['current_source_sum_trace_body_logical_bytes']/2**30:.2f}GiB）。这不是新完整body内容校验或NAS物理占用证明。除当前exact ensure可核的Vector/GEMM外，没有搜索全NAS或声称其它资产已迁入174-new。

## 已跑过与可准备程度

“原57”指20261019机制研究的57次实际启动；不与145条混合canonical记录相加。该57中44个执行行COMPLETE_VALID、8FAILED、3RESOURCE_LIMIT、2INCOMPLETE；44个接受结果索引/25对，包含另列的补充接受，原失败行保留。MAIN6/7及独立SGEMM探索1项的分组不变。

| 精确输入 | suite | kernel启动数 | trace body GiB | 旧B0索引 | 原57实际启动 | 原57接受结果索引 | 当前准备状态 |
|---|---|---:|---:|---|---:|---:|---|
"""
lines=[]
for r in rows:
 h=r['history'];lines.append(f"| {r['input_id']} | {r['suite_declared_by_saved_asset']} | {r['kernel_launches']} | {r['trace_body_logical_bytes']/2**30:.3f} | {'有历史Legacy引用' if h['historical_baseline_roster'] else '未见'} | {h['recent_actual_start_count']} | {h['accepted_result_index_count']} | {stage_zh[r['readiness_stage']]} |")
text=head+'\n'.join(lines)+'''

旧B0索引记录了精确输入、Legacy cycles和旧Framework/Core；不代表当前B16/main61/r5资格。两处历史final26 closeout Git路径未找到，故本清点不重新宣布26/26接受。更早C5c 22/26及银行归因HOLD不能升级为当前正式结果。

## “可以跑”的四层含义

1. **输入存在**：本轮18个已知输入都通过原174文件级元数据存在/可读检查；不等于内容语义或当前runtime兼容。
2. **具备历史EP接受基础**：Conv、CFD、DWT、SAD、FWT_7_21、Vector的main61主结果与SGEMM独立探索；精确source/config/input/资格各自固定，不跨谱系继承。
3. **当前174-new输入已就位**：EP_VECTORADD_S；以及同一GEMM输入的共享DTC_AD_GEMM真164映射。Vector有main61 S迁移与r5 F的原生接受证据；GEMM共享输入尚不构成EP资格。
4. **可获准启动**：当前EP没有未消费cohort预算。盘点不授予启动或迁移权；每次仍须新精确规格、当前native资格、资源/空间和明确预算。

因此，Vector是当前EP原生已证明的输入；GEMM可先复用共享输入身份。Conv/CFD/DWT/SAD/FWT/SGEMM有历史科学基础，但其输入还需精确物化及本轮native规格。其余不能仅因文件存在而列为ready。

## 明确保留的HOLD与准备缺口

- **Btree mil.txt**：非零active-mask/full32地址解释与native popcount消费存在语义冲突，原input_scope_HOLD未解除。
- **SpMV Dubcova3**：IADD3指令记录缺一个源寄存器；旧B0 cycles、文件小或descriptor压力均不替代当前完整输入资格，不能静默补trace。
- **Scan NO_ARGS**：shared/nonmemory扩展地址尾格式不支持；33次kernel启动、约5.33GB body，当前仍HOLD。
- **BFS graph65536 / graph4096 / graph1MW_6**：已有确切trace元数据。graph65536有20个kernel的F包与C的host边界准备交付；完整body/指令/原子域/host更新与alias及runtime资格尚未闭合。不能继续说C未交准备包，也不能把交付当作资格。
- **Hotspot512_2_2 / 1024_2_2**：当前都是1个kernel的输入，仅为结构网格候选，不能称为已覆盖跨kernel迭代复用。
- **3mm、FWT_11_19**：有旧基线输入/历史结果索引，缺当前EP输入/profile/runtime资格。
- **GEMM**：数据在真164可共享复用；不能把DTC的L1科学接受借给EP-L2。
- **stencil/histo/histogram及新ML/WMMA发布**：只是旧调研中的方向，无本次确切EP输入选择和资格，未计入18个资产。

## “真实吗”与平台边界

这些资产来自CUDA SDK、Rodinia、Parboil、PolyBench/GPU的经典样例/科学计算基准。Vector/Scan/Conv/FWT属于CUDA样例，PolyBench偏参数化kernel微基准；Rodinia/Parboil提供应用领域背景，但冻结trace不自动证明生产端到端代表性。

每个输入的capture run.sh字面内容、文件SHA和完整commandlist保存在JSON；CUDA目录名、visible device编号或SM70 header都不是准确采集GPU/driver/toolchain证明。原capture精确源码revision和数值payload/输出的缺口保留UNKNOWN；本轮没有重新采集或数值验证。

模拟目标是Volta派生H0研究配置，不能称RTX4080实验。Tag几何16way来自研究overlay，与采集GPU及当前执行主机分开。当前已准入资产中没有现代AI完整应用。

## 数据与结果去向

- 原18组trace位于JSON列出的原174精确路径；当前确认存在/可读，不做body重hash或搬运。
- 原57点的result dir/raw/接受控制引用，本轮175个精确路径全存在；只是stat，不重新接受旧结果。
- E057完整结果和本轮Vector r5结果已有真164归档及native恢复入口，见JSON对应字段/上一轮RECOVERY_POINTER。其它旧结果不能一概宣称已完整归档。
- 新原生迁移EP Q1停、Q2接受另记2次；本轮Vector r5科研1次另记，help资格另列，不回填原57。
- 所有源KEEP，释放0B。DTC其它工作负载、C16/AWMA等其它项目不纳入本次EP清单。

机器可读主表为WORKLOAD_ASSET_INVENTORY.json；完整历史索引见HISTORICAL_RUN_INDEX.json，46份历史资格的精确profile/source指针见RUNTIME_PROFILE_QUALIFICATION_INDEX.json。全部原始15份证据的精确Git HEAD/blob/SHA见SOURCE_REFERENCES.json。

下一步可据此逐项选择“补资格”“精确物化”“继续HOLD”或“仅保留历史”；本轮不替用户启动任何条件。
'''
(O/'WORKLOAD_ASSET_INVENTORY.md').write_text(text)
(O/'README.md').write_text('# EP-MAIN workload资产清点\n\n只读盘点完成，无模拟/搬运/账本写入。[人工主表](WORKLOAD_ASSET_INVENTORY.md)；[机器主表](WORKLOAD_ASSET_INVENTORY.json)。\n\n输入18变体/14程序/4suite；当前EP原生已验证Vector，GEMM共享输入可复用但待EP资格。已知HOLD保持，启动预算0。\n')
put('SUMMARY.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
