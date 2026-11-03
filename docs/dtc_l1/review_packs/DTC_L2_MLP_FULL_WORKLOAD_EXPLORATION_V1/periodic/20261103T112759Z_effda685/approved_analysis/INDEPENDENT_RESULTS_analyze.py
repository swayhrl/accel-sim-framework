"""Independent frozen-result arithmetic + only28 nonaccepted delta probes.
No summary(), raw scan, controller, registry writes, model, Git or READY action.
"""
import pathlib,json,hashlib,math,collections,time,copy
P=pathlib.Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');E=A/'agents/E/results_refresh_20261028_v4';D=A/'agents/A/results_independent_20261028_v1';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D.mkdir(exist_ok=True)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(name,v):(D/name).write_text(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
manifest=read(E/'MANIFEST.json');assert sha(E/'MANIFEST.json')=='9f4e873cc4898e2fa1a078244f48b2b86084bec3657bf068108e5c8ef25bfb1f'
for item in manifest['files']:assert sha(E/item['name'])==item['sha256']
e=read(E/'EVIDENCE.json');d=read(E/'PRIMARY_SNAPSHOT.json');supp=read(E/'SUPPLEMENTAL_SNAPSHOT.json');assert e['accepted_primary']==322 and e['planned_primary']==350 and e['programs']==35
sources=[dict(path=str(E/'MANIFEST.json'),sha256=sha(E/'MANIFEST.json'),read_mode='CURRENT_BYTES_VERIFIED')]+[dict(path=str(E/x['name']),sha256=x['sha256'],read_mode='CURRENT_BYTES_VERIFIED')for x in manifest['files']]
for name in ['SCOPE.json','MATRIX_CURRENT.json']:
 p=R/'control'/name;frozen=next(x for x in d['source_snapshots']if x['path']==str(p));assert sha(p)==frozen['sha256'];sources.append(dict(path=str(p),sha256=sha(p),read_mode='CURRENT_BYTES_VERIFIED'))
scope=read(R/'control/SCOPE.json');matrix=read(R/'control/MATRIX_CURRENT.json');assert len(scope['points'])==len(matrix['points'])==350 and {x['cohort']for x in matrix['points']}=={x['cohort']for x in e['all_cells']}
assert len({x['input_digest']for x in matrix['points']})==35
accepted=[x for x in e['all_cells']if x['accepted']];unaccepted=[x for x in e['all_cells']if not x['accepted']];assert len(accepted)==322 and len(unaccepted)==28
delta=[];fresh_liveness=[]
for x in unaccepted:
 p=R/'analysis'/(x['cohort']+'.RESULT.json')
 if p.exists():
  value=read(p);delta.append(dict(cohort=x['cohort'],path=str(p),sha256=sha(p),state=value.get('state')))
 live=x.get('live_identity')
 if live:
  stat=P('/proc')/str(live['pid'])/'stat'
  try:
   text=stat.read_text();v=text.rsplit(')',1)[1].split();before=int(v[19]);state=v[0];again=stat.read_text();after=int(again.rsplit(')',1)[1].split()[19]);fresh_liveness.append(dict(cohort=x['cohort'],pid=live['pid'],expected_start_ticks=live['start_ticks'],observed_start_ticks=before,state=state,same_birth_live=before==after==live['start_ticks']and state not in['Z','X']))
  except(FileNotFoundError,ProcessLookupError):fresh_liveness.append(dict(cohort=x['cohort'],pid=live['pid'],same_birth_live=False,reason='PROC_DISAPPEARED_NO_TERMINAL_INFERENCE'))
assert not delta,'New candidate result exists; independent delta review needed, do not label accepted automatically'
new3=e['new_since_v3']
for x in new3:
 # E new rows can be nested; match exact frozen accepted cell by cohort.
 c=x['cohort'];cell=next(y for y in accepted if y['cohort']==c);p=P(cell['result_path']);assert sha(p)==cell['result_sha256'];sources.append(dict(path=str(p),sha256=sha(p),read_mode='CURRENT_V3_TO_V4_DELTA_BYTES_VERIFIED'))
assert len(new3)==3
rows={(x['input_digest'],x['profile'],x['cell']):x for x in e['all_cells']};profiles=[x for x in d['profiles']if x!='P0'];programs=d['programs']
paired={}
for f in profiles:
 values={}
 for i in programs:
  b=rows[(i,'P0','DH')];v=rows[(i,f,'DH')]
  if b['accepted']and v['accepted']:
   assert all(b[k]==v[k]and b[k]for k in ['core_commit','framework_commit','binary_sha256']);values[i]=b['cycles']/v['cycles']
 paired[f]=values
common=set.intersection(*(set(v)for v in paired.values()));assert len(common)==31 and common==set(e['fixed_common_population'])
def aggregate(values):
 vals=list(values.values());return dict(n=len(vals),GM=math.exp(sum(math.log(x)for x in vals)/len(vals))if vals else None,median=sorted(vals)[len(vals)//2]if vals else None,positive=sum(x>1 for x in vals),neutral=sum(x==1 for x in vals),negative=sum(x<1 for x in vals),population=sorted(values),min=min(vals)if vals else None,max=max(vals)if vals else None)
stats={}
for f in profiles:
 stats[f]={}
 for suite in ['ALL']+sorted({x['suite']for x in programs.values()}):
  av={i:x for i,x in paired[f].items()if suite=='ALL'or programs[i]['suite']==suite};fixed={i:x for i,x in av.items()if i in common};stats[f][suite]=dict(available=aggregate(av),common31=aggregate(fixed))
  for what,key in [('available','available'),('common31','fixed_common')]:
   theirs=e['statistics'][f][suite][key]
   assert stats[f][suite][what]['n']==theirs['n']and abs(stats[f][suite][what]['GM']-theirs['GM'])<1e-12
   assert all(stats[f][suite][what][k]==theirs[k]for k in ['positive','neutral','negative'])
def prog(name):return next(i for i,v in programs.items()if v['program']==name)
flat=[programs[i]['program']for i in sorted(common)if all(paired[f][i]==1 for f in profiles)]
e_same=[i for i in paired['E384']if rows[(i,'E384','DH')]['cycles']==rows[(i,'E768','DH')]['cycles']]
assert len(e_same)==len(paired['E384'])==32
fchanges={i:rows[(i,'F128','DH')]['cycles']/rows[(i,'F256','DH')]['cycles']for i in set(paired['F128'])&set(paired['F256'])}
fhead=aggregate(fchanges)
population_differences={f:dict(available_extra_over_common31=[programs[i]['program']for i in sorted(set(paired[f])-common)],missing_from35=[programs[i]['program']for i in programs if i not in paired[f]])for f in profiles}
remaining=[]
for name in sorted({x['program']for x in unaccepted}):
 rr=[x for x in unaccepted if x['program']==name];remaining.append(dict(program=name,count=len(rr),states=dict(collections.Counter(x['state']for x in rr)),cells=[dict(cohort=x['cohort'],cell=x['cell'],profile=x['profile'],state_at_anchor=x['state'])for x in rr]))
p0matched={i:rows[(i,'P0','CH')]['cycles']/rows[(i,'P0','DH')]['cycles']for i in programs if rows[(i,'P0','CH')]['accepted']and rows[(i,'P0','DH')]['accepted']}
params={f:{k:v for k,v in d['profile_parameters'][f].items()if not k.startswith('source_')}for f in d['profiles']}
assert all(v['L2_total_capacity_bytes']==10485760 and v['dram_MHz']==850 and v['clock_domains']=='1410.0:1410.0:1410.0:850.0'for v in params.values())
qpath=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';q=read(qpath)['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];sources.append(dict(path=str(qpath),sha256=sha(qpath),read_mode='READONLY_CURRENT_COUNTER_CONTEXT_NOT_STATISTICS_AUTHORITY'))
observations=[
 dict(id=1,claim='同一31输入上，F128/F256的DH自对照GM分别为1.008259和1.011581；所有8配置中位数均为1，14个共同输入在8组变体中周期完全不变。',limit='这是当前共同人口描述，不是最终35输入winner或逐程序择优GM。'),
 dict(id=2,claim='F增益与回退并存：F256在convolutionSeparable为1.422263、scan为1.283635、2DCONV为1.078012；vectorAdd为0.919938。',limit='scan不在共同31中，不能把其贡献带入共同31GM；F容量增大并不单调改善所有程序。'),
 dict(id=3,claim='E384与E768在32个已配对输入上周期逐项相等。M8/M16整体近1且有不同符号，Q64/Q128当前共同31GM为0.997271/0.996942。',limit='现有数据未显示把MSHR项从384继续翻倍到768的增量周期收益；不能推出所有未完成输入或更大边界无效。'),
 dict(id=4,claim='各配置可用人口通常32，M16为31；所有配置共同31排除SYRK、hybridsort、lavamd、scan。F256可用GM1.019138与共同GM1.011581的差来自人口差异。',limit='保持同一输入集合比较；不把新完成CUTCP三个中性点引起的GM变化当作旧输入性能变化。'),
 dict(id=5,claim='非P0 CH accepted仍为0；本轮只能确认DH参数自敏感性。R2 scan/M16已独立accepted6702538cycles，但原M16仍未accepted，全部primary统计排除R2及工程canary。',limit='不能声称相对传统CH的DTC优势改善；需匹配的同参数CH和正式全35门解锁。')]
summary=dict(schema='INDEPENDENT_PRIMARY_RESULTS_REVIEW_20261028_V1',status='READONLY_FROZEN_ARITHMETIC_VERIFIED',review_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),anchor_snapshot_utc=e['snapshot_utc'],anchor_manifest_sha256=sha(E/'MANIFEST.json'),population=dict(primary_accepted=322,new_accepted=316,references=6,planned_primary=350,inputs=35,unresolved_other_inputs=7,final_target_programs=42,profile_pairs=255,total_possible_DH_variant_pairs=280,common_all_eight_input_n=31,CH_nonP0_accepted=0,P0_DH_accepted=34,P0_CH_accepted=33,P0_CH_DH_matched_n=len(p0matched)),anchor_state_counts=e['state_counts'],current_delta_probe=dict(nonaccepted_cells_checked=28,new_RESULT_files=delta,fresh_pid_birth_checks=fresh_liveness,confirmed_same_birth=sum(x['same_birth_live']for x in fresh_liveness),interpretation='No new candidate RESULT among prior28. Reuse accepted322 freeze; do not rerun oldQA/raw. PID birth checks prove liveness, not future acceptance.'),statistics=stats,population_differences=population_differences,perprogram_speedups={programs[i]['program']:{f:paired[f].get(i)for f in profiles}for i in programs},all_eight_neutral_common31=flat,E384_E768_exact_cycle_equal_n=len(e_same),F256_over_F128_same32=fhead,remaining=remaining,profile_parameters=params,robust_observations=observations,supplemental=dict(R2_cohort=e['supplemental']['cohort'],R2_accepted=True,R2_cycles=6702538,original_M16_replaced=False,primary_included=False,engineering_canaries_primary_included=False),current_authority_context=dict(budget=q['budget'],remaining=q['remaining'],consumed=len(q['consumed']),meaning='Includes independent R2 technicalgrant; not primary350 statistical denominator.'),cautions=['E historical batch.dynamic_memory_budget_fraction=.88 is a stale metadata field; not used to infer actual current resource policy.','Counter association is not causal attribution: MRQ last printed is not an application weighted mean; zero DRAM counters do not prove real application has no DRAM traffic; missing MSHR reasons remain missing.','F FRFCFS queue sizing changes partition-credit coupling, so a cycle effect is not isolated queue occupancy evidence.','No fullraw rescan, AUTO_SUMMARY writer, oldQA, model launch, controller or authority mutation, Git or READY action.'],old_acceptance_receipts_reverified=False,new3_delta_RESULT_hashes_reverified=True)
put('SUMMARY.json',summary)
sources.extend(dict(path=x['result_path'],sha256=x['result_sha256'],read_mode='FROZEN_E_ACCEPTED_RECEIPT_INDEX_REUSED_NOT_RAW_RESCAN')for x in accepted)
put('SOURCE_SHA_LIST.json',dict(schema='INDEPENDENT_RESULT_REVIEW_SOURCES_V1',sources=sources,accepted_receipts=322,source_generator_sha256=sha(P(__file__))))
lines=['独立结果核对（只读）','',f'采集：{summary["review_utc"]}；统计锚点：{e["snapshot_utc"]}。原350矩阵/35输入中322 accepted（316新结果+6历史参考），仍有12同代模型、15未启动、1原始scan/M16工程负例；本轮仅检查其余28个结果路径，没有新增RESULT，复用冻结322证据。R2与工程canary均不并入primary。另7输入仍unresolved，不把当前35改称全部42。','', '统一配置的DH自对照：speedup=同输入DH P0周期/该变体周期；大于1为加速。以下每行均为统一配置，不做逐程序择优组合。','', '|配置|可用n/35|可用GM|共同31 GM|共同31 + / = / -|','|---|---:|---:|---:|---:|']
for f in profiles:
 s=stats[f]['ALL'];v=s['available'];c=s['common31'];lines.append(f'|{f}|{v["n"]}|{v["GM"]:.6f}|{c["GM"]:.6f}|{c["positive"]} / {c["neutral"]} / {c["negative"]}|')
lines+=['','稳健观察：']
for o in observations:lines+=['',f'{o["id"]}. {o["claim"]} {o["limit"]}']
lines+=['','剩余28点集中于四个程序：']
for r in remaining:lines.append(f'- {r["program"]}：{r["count"]}点；'+', '.join(f'{k}={v}'for k,v in r['states'].items()))
lines+=['','缓存容量固定10MiB、DRAM850MHz及其余clock域一致。E为每L2子分区MSHR项，M为每项merge上限，Q为miss queue，F为每控制器FRFCFS队列；F也影响partition-credit耦合。队列/延迟计数的相关变化不能直接证明关键路径原因。','', '独立算术与E V4所有配置、suite、可用/共同人口的GM和符号数一致；仅对V3→V4新增CUTCP M8/Q64/Q128三份RESULT重新核SHA，不重复旧322的raw/QA。三点均4490473cycles，DH自对照1.0。详见SUMMARY.json及SOURCE_SHA_LIST.json。','', '当前authority预算含R2为345，而primary统计分母仍为350；工程新grant若后续登记也必须分账。采样为各文件只读时间切片，后续自然完成不自动改变本冻结报告。']
(D/'REPORT.txt').write_text('\n'.join(lines)+'\n')
files=[]
for name in ['REPORT.txt','SUMMARY.json','SOURCE_SHA_LIST.json','analyze.py']:
 p=D/name;files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
put('MANIFEST.json',dict(schema='INDEPENDENT_RESULTS_REVIEW_MANIFEST_V1',status='FROZEN',files=files,anchor_manifest_sha256=sha(E/'MANIFEST.json'),analysis_source_sha256=sha(P(__file__)),production_changes=0))
print(json.dumps(dict(path=str(D),manifest_sha256=sha(D/'MANIFEST.json'),summary_sha256=sha(D/'SUMMARY.json'),report_sha256=sha(D/'REPORT.txt'),source_list_sha256=sha(D/'SOURCE_SHA_LIST.json'),stats=summary['population'],liveness=summary['current_delta_probe']['confirmed_same_birth'],F256vsF128=fhead),ensure_ascii=False))
