"""Small new-results publication view. Reads only frozen captured metadata."""
import collections,gzip,hashlib,json,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):P(p).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
c=read(HERE/'LATEST_CAPTURE.json');run=P(c['run_path']);a=read(run/'ANALYSIS.json');s=read(run/'SUPPLEMENT.json');r=read(run/'report.json');deps=read(run/'BASELINE_DEPENDENCIES.json')
anchor=P(c['previous_checkpoint_path']).parent;old=read(anchor/'ANALYSIS.json');old_s=read(anchor/'SUPPLEMENT.json')
newraw=read(run/'NEW_RAW_REASONS.json')['rows'];new=[]
for row in newraw:
 d=row['input_digest'];profile=row['profile'];cell=row['cell'];DH_P0=r['table'][d]['P0']['DH']
 item={k:row[k]for k in ('cohort','uuid','input_digest','program','suite','cell','profile','cycles','result_path','result_sha256')}
 item.update(strict_raw_status=row['status'],scope_complete=row.get('complete_declared_stream_stats_coverage'),
  IO_chain_status=row.get('IO_extra_chain',{}).get('status'),DH_P0_state=DH_P0['state'],DH_P0_accepted=DH_P0['accepted'],
  comparison_status='CH_P0_COMPLETED_DH_P0_STILL_MISSING'if cell=='CH'else'MATCHED_DH_SELF_NEW_PAIR'if DH_P0['accepted']else'DH_VARIANT_ACCEPTED_AWAIT_DH_P0')
 new.append(item)
oldcomplete={p['input_digest']for p in old['coverage']if p['DH_P0_accepted']and len(p['accepted_DH_variants'])==8}
newcomplete=[p['program']for p in a['coverage']if p['input_digest']not in oldcomplete and p['DH_P0_accepted']and len(p['accepted_DH_variants'])==8]
by={(p['input_digest'],p['profile']):p for p in a['all_matched_DH_pairs']}
same=[dict(input_digest=d,program=p['program'],E384_cycles=p['variant_cycles'],E768_cycles=by[(d,'E768')]['variant_cycles'])for(d,prof),p in by.items()if prof=='E384'and(d,'E768')in by]
assert all(p['E384_cycles']==p['E768_cycles']for p in same)
assert len(a['all_matched_DH_pairs'])==a['previous_identity_validation_reused_count']+a['new_pair_identity_validated_count']
assert len(new)==c['current_accepted']-c['previous_accepted']and not c['new_raw_evidence_errors']and not a['pair_identity_validation_errors']
assert s['relative_values_present']==0 and s['CH_nonP0_accepted_pairs']==0
structured=dict(schema='DTC_L2_MLP_SCIENTIFIC_INCREMENT_V3',utc=r['utc'],capture=c,
 frozen_primary_scope=dict(programs=35,cells=350,supplemental_V2_included=False),
 newly_accepted=new,newly_complete_DH_P0_and_all8_programs=newcomplete,
 new_strict_pairs=a['new_or_newly_matched_pairs'],reused_pair_count=a['previous_identity_validation_reused_count'],
 reused_pair_anchor=dict(path=str(anchor/'ANALYSIS.json'),sha256=sha(anchor/'ANALYSIS.json')),
 current_profile_statistics=s['profile_statistics'],previous_common_population=old_s['common_all8_population'],
 current_common_population=s['common_all8_population'],E384_E768_exact_cycles_same_available_population=same,
 baseline_dependencies=deps,coverage=a['coverage'],typed_negative_excluded=s['typed_engineering_negative'],
 no_old_raw_rescan=True,no_missing_imputation=True,no_CH_variant_relative_inference=True)
put(run/'SCIENTIFIC_INCREMENT.json',structured)
def fmt(v):return '—'if v is None else f'{v:.6f}'
text=['# DTC L2科学增量 V3：新增14点、完整输入增至23','',
'快照：2026-10-28 **04:54:53 CST**。以已冻结257项快照（Main发布标识f519）为锚，现271 accepted＝265本轮＋6 references。仅新开14份accepted raw；旧257份raw与189条旧配对均按RESULT/UUID SHA复用。本轮只重做2条新配对的input binding/Core/FW/binary/全非目标选项及完整population验证，错误0。原始350格状态还包括23 confirmed RUN、55 PENDING和1个scan/M16 spent工程格；该格及未来补充V2均不进入accepted性能。',
'','## 这次真正新增什么','',
'ATAX F128、BICG E768完成后，完整DH-P0＋八变体的程序由21增至23，新增完整输入正是ATAX、BICG。总严格DH自身配对189→191。CH-P0新增GESUMMV、hybridsort、scan，覆盖30→33；DH-P0仍25，CH/DH-P0配对也仍25，没有新的DH基线完成。其余9个新DH变体仍等DH-P0，不能据它们的绝对cycles计算自身收益。',
'','|程序|配置|cycles|本轮比较身份|','|---|---|---:|---|']
for row in new:
 status='新增DH/P0严格配对'if row['comparison_status']=='MATCHED_DH_SELF_NEW_PAIR'else'CH-P0完成，DH-P0未完成'if row['cell']=='CH'else'已accepted，待DH-P0'
 text.append(f"|{row['program']}|{row['cell']}-{row['profile']}|{row['cycles']:,}|{status}|")
text += ['', '新配对均未出现收益：', '',
'|程序/配置|P0 cycles|变体cycles|DH自身加速|L2接受读变化|DRAM读变化|总拒绝尝试变化|','|---|---:|---:|---:|---:|---:|---:|']
for p in a['new_or_newly_matched_pairs']:
 cc=p['counter_changes'];text.append(f"|{p['program']} {p['profile']}|{p['P0_cycles']:,}|{p['variant_cycles']:,}|{p['DH_speedup']:.6f}|{cc['L2_read_sectors']['change_pct']:+.3f}%|{cc['DRAM_read_atoms']['change_pct']:+.3f}%|{cc['L2_reservation_fail']['change_pct']:+.3f}%|")
text += ['',
'**ATAX F128接近无变化（0.999548x）**：miss-queue拒绝18,806,950→106,080（−99.436%），entry拒绝139,657,561→162,115,286（＋16.081%），末次MRQ745→1389。DRAM读只少0.290%，总拒绝反增2.351%；说明消掉一种排队拒绝并不等于提升应用吞吐。与既有F256 1.017823x相比，F128没有显示单调收益。这里是计数器关联，不是已隔离因果。',
'','**BICG E768为0.994996x**：cycles及本轮所列流量与E384相同，DRAM读下降3.817%仍略慢于P0。miss-queue拒绝15,514,452→133,657,611，entry拒绝在该日志未打印，保持None。当前E384/E768在同一24个可配对输入上**24/24 cycles完全相同**；这只是已完成24输入上的饱和证据，不能替代剩余11输入或触发正式参数裁决。',
'','## 更新后的可用与共同人口','',
'每配置可用人口仍不同，右列固定同一23个完整程序。两组均不是全35统计，非P0 CH仍无匹配，不计算相对DTC改善或同配置CH/DH比。',
'','|配置|可用n/35|可用GM|正/平/负|共同23 GM|','|---|---:|---:|---|---:|']
for p,v in s['profile_statistics'].items():
 q=v['available'];text.append(f"|{p}|{q['n']}/35|{q['GM']:.6f}|{q['positive']}/{q['neutral']}/{q['negative']}|{v['common_all8']['GM']:.6f}|")
text += ['',
'共同人口从21变23，F256 GM 1.016754→1.015763、Q128 0.999307→0.996101。**这不是旧配置性能变了**：Q128本轮没有新配对，变化来自ATAX/BICG进入完整八配置共同集合。固定旧21上的原结论不变；当前23仍缺12输入。各suite完整人口现在为CUDA7/9、Parboil5/7、PolyBench5/9、Rodinia6/10；全部suite可用/共同GM与正平负分布保存在SCIENTIFIC_INCREMENT.json，不按收益删程序。',
'','## 当前P0依赖','',
'已accepted但因缺DH-P0暂不能配对的格由13增至22：srad_v1 7、GEMM6、scalarProd3、scan3、GESUMMV2、3MM1。GEMM、scan、GESUMMV、srad_v1的DH-P0已RUN；scalarProd和3MM仍PENDING。该优先级依据覆盖依赖，不依据收益。',
'','|程序|缺失P0状态|已accepted DH变体|待P0配对数|','|---|---|---:|---:|']
for row in deps['rows']:
 text.append(f"|{row['program']}|"+', '.join(p['design']+':'+p['state']for p in row['missing_P0'])+f"|{row['accepted_nonP0_DH_count']}|{row['blocked_DH_self_pairs_due_missing_DH_P0']}|")
text += ['', '## 全35覆盖','', '|程序|suite|CH-P0|DH-P0|DH变体A/8|新增A|','|---|---|---|---|---:|---:|']
for row in a['coverage']:
 cells=r['table'][row['input_digest']]
 text.append(f"|{row['program']}|{row['suite']}|"+('A'if row['CH_P0_accepted']else cells['P0']['CH']['state'])+'|'+('A'if row['DH_P0_accepted']else cells['P0']['DH']['state'])+f"|{len(row['accepted_DH_variants'])}/8|{row['new_accepted_cells']}|")
text += ['', '## 证据和限制','',
'14/14新增raw自然闭合、strict、归档/native restore及完整stream身份检查通过。271份累计sidecar中148行positive原因与aggregate闭合、123行未打印原因；缺失字段从不填0。新增14点的IO链为13 legacy、1 shared-JSON额外链，通过原冻结只读审计器052dc251...；其既有CPU/actual资格未无故重跑。没有重扫历史72或旧257 raw，也没有重新全面审计旧189配对。',
'','拒绝计数是尝试数，非唯一miss、请求数或应用停顿cycles；最后打印MRQ不是全应用加权L2→DRAM往返时延。非P0 CH缺失、未完成人口与原scan工程负例都保留。源/输入身份与v0.23论文母稿不变。未注册或重建补充V2计划；它不在本报告scope/GM中，未来native route稳定性由Main另行决定。',
'',f"锚：`{c['previous_checkpoint_path']}` SHA `{c['previous_checkpoint_sha256']}`；旧配对证据`{anchor/'ANALYSIS.json'}` SHA `{sha(anchor/'ANALYSIS.json')}`。当前run：`{run}`。",'',
'`SCIENTIFIC_INCREMENT.json.gz`含新增14点的cohort/UUID/RESULT路径SHA、2条新配对的binding/optionsSHA及counter、完整35覆盖、当前所有suite分布、22格依赖和旧189配对锚；`NEW_RAW_REASONS.json.gz`仅新增14 raw提取。CAPTURE与manifest记录解析器source SHA。D report工具commit fce10d92eb09bc8f562b84a5a84b202bbf1ea385、raw reason发布927c8bd；Core9eedb3131937748f0492fa83aad37d3691118d70、Framework02775fd795cde5aae1480d81cee6eb481d0a08f4，DRAM850。',
'','本轮0模型、0重试、0生产/科学台账修改。']
(run/'REVIEW.md').write_text('\n'.join(text)+'\n');(HERE/'REVIEW.md').write_text('\n'.join(text)+'\n')
for n in ('SCIENTIFIC_INCREMENT.json','NEW_RAW_REASONS.json','report.json','ANALYSIS.json','SUPPLEMENT.json'):(run/(n+'.gz')).write_bytes(gzip.compress((run/n).read_bytes(),compresslevel=6,mtime=0))
names=['REVIEW.md','SCIENTIFIC_INCREMENT.json','SCIENTIFIC_INCREMENT.json.gz','NEW_RAW_REASONS.json.gz','report.json.gz','ANALYSIS.json.gz','SUPPLEMENT.json.gz','CAPTURE.json','BASELINE_DEPENDENCIES.json','IO_CHAIN_AUDIT.json']
manifest=dict(schema='DTC_RESULTS_INCREMENT_V3_DELIVERY',utc=r['utc'],run_path=str(run),anchor_path=c['previous_checkpoint_path'],anchor_sha256=c['previous_checkpoint_sha256'],
 previous_accepted=257,current_accepted=271,new_accepted=14,new_raw_scanned=14,reused_raw=257,strict_pairs=191,reused_identity_pairs=189,new_identity_pairs=2,
 source_hashes={p.name:sha(p)for p in HERE.glob('*.py')},files={n:dict(path=str(run/n),sha256=sha(run/n),bytes=(run/n).stat().st_size)for n in names},
 no_supplemental_V2_in_statistics=True,model_starts=0,production_changes=0,old_72_scans=0)
put(run/'DELIVERY_MANIFEST.json',manifest);put(HERE/'DELIVERY_MANIFEST.json',manifest)
print(json.dumps(dict(status='READONLY_INCREMENT_V3_COMPLETE',run_path=str(run),manifest_sha256=sha(run/'DELIVERY_MANIFEST.json'),review_sha256=sha(run/'REVIEW.md'),compressed_increment_sha256=sha(run/'SCIENTIFIC_INCREMENT.json.gz'),compressed_bytes=(run/'SCIENTIFIC_INCREMENT.json.gz').stat().st_size)))
