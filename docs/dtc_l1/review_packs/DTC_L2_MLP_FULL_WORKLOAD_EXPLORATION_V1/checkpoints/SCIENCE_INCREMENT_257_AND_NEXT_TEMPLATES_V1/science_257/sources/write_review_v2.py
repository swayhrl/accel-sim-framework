"""Consume frozen increment artifacts only; no model/registry/raw access."""
import collections,gzip,hashlib,json,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):P(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
c=read(HERE/'LATEST_CAPTURE.json');run=P(c['run_path']);a=read(run/'ANALYSIS.json');s=read(run/'SUPPLEMENT.json');r=read(run/'report.json');deps=read(run/'BASELINE_DEPENDENCIES.json');io=read(run/'IO_CHAIN_AUDIT.json')
assert not c['new_raw_evidence_errors']and not a['pair_identity_validation_errors']
pairs=a['all_matched_DH_pairs'];assert all(p['relative_DTC_improvement']is None and not p['CH_variant_accepted']for p in pairs)
identity={tuple(sorted(p['identity'].items()))for p in pairs};assert len(identity)==1
core=dict(next(iter(identity)));by={(p['program'],p['profile']):p for p in pairs}
def f(v):return '—'if v is None else f'{v:.6f}'
def pct(v):return '—'if v is None else f'{v:+.3f}%'
def case(program,profile):
 p=by[(program,profile)];return f"|{program}|{profile}|{p['P0_cycles']:,}|{p['variant_cycles']:,}|{p['DH_speedup']:.6f}|{pct(p['counter_changes']['DRAM_read_atoms']['change_pct'])}|{pct(p['counter_changes']['L2_reservation_fail']['change_pct'])}|"
text=['# DTC L2 科学增量 V2（只读）','',
'快照：2026-10-28 **02:50:41 CST**，固定对照2026-10-27 22:59:15的198 accepted锚。现在257 accepted＝251本轮＋6合法P0 references；新增59点，仅打开这59份新增accepted raw，旧198份raw未重扫。当前原始状态另有33 confirmed RUN、59 PENDING、1 spent未有标准终态。scan/M16的真实typed工程终态证书独立保留，不改原始状态或补cycles。',
'','35程序：CH-P0 accepted30、DH-P0 accepted25，21程序DH-P0及八变体完整。189条严格DH/P0配对，较锚点新增或新可配对46条；严格input/binding/Core/FW/binary/完整population与所有非目标配置检查零错误。没有任何变体达到35条完整配对，不能从部分输入结果正式选择配置或启动新科学方向。CH非P0仍无accepted，189条relative DTC improvement均为None。',
'','## 新增正负结果','',
'加速比为DH-P0 cycles/DH-variant cycles。下列均保留同一冻结输入，不按结果增删workload。',
'','|程序|配置|P0 cycles|变体cycles|DH自身加速|DRAM读变化|L2拒绝尝试变化|','|---|---|---:|---:|---:|---:|---:|']
for pp in [('ATAX','E768'),('ATAX','M8'),('ATAX','M16'),('ATAX','Q128'),('BICG','M16'),('BICG','Q64'),('MVT','M8'),('MVT','Q128'),('MVT','F128'),('histo','F256'),('convolutionSeparable','Q128'),('mri-q','Q128')]:text.append(case(*pp))
text += ['',
'**ATAX**：E768与既有E384完全相同cycles，均1.028813x；M8为1.014056x，但M16反退至0.980088x。Q128退至0.943917x，DRAM读＋6.118%、entry拒绝139,657,561→161,783,927；最后打印MRQ却745→729。更大queue或更小末次MRQ不能单独证明应用更快，未打印MISS_QUEUE_FULL仍记None。',
'','**BICG**：M16为1.012241x、DRAM读−0.575%，好于既有M8的0.967226x，说明merge方向非单调；仍不能据此断言赶上CH。Q64为0.961800x：miss-queue拒绝15,514,452→119,192，但entry拒绝142,533,205→158,482,166，L2接受读＋11.780%，DRAM读＋0.490%。阻塞转移与退化相关，尚未隔离因果。',
'','**MVT**：M8/M16仅1.000052x/1.000039x（约0.005%/0.004%），DRAM读完全相同；不能称实质改善。Q128为0.977938x，DRAM读＋2.966%、entry拒绝＋63.193%；F128为0.981743x，虽然miss-queue拒绝52,360,071→56,276，entry拒绝却升到172,934,579，MRQ最后均值738→1366。',
'','**新受益例**：Parboil histo F256为1.023415x，cycles5,865,589→5,731,388，DRAM读仅−0.217%，总拒绝−53.958%、miss-queue拒绝−78.104%，末次MRQ198→501。convolutionSeparable Q128为1.014358x，miss-queue拒绝−88.394%，entry拒绝1,057→14,785,749；DRAM读几乎不变。它们与并发/调度压力转移一致，但不能分离FR-FCFS窗口与共享credits。既有convolutionSeparable F256的1.422263x没有被本轮重复当新增发现。',
'','**近乎不受益**：MRI-Q Q64/Q128均1.001231x、DRAM读不变，Q128拒绝1,937→123（−93.650%）仍只快约0.123%。dwt2d Q64 cycles完全不变，DRAM百分比缺分母则保留None。拒绝尝试不是唯一miss/请求或停顿cycles，末次MRQ不是全应用加权L2→DRAM往返延迟。',
'','## 可用人口与固定共同人口','',
'左侧每配置各自可用，人口不同不能直接排名；右侧固定同一21程序、八配置及DH-P0完整。两者均非全35最终GM。',
'','|配置|可用n/35|可用GM|正/平/负|共同21 GM|','|---|---:|---:|---|---:|']
for profile,v in s['profile_statistics'].items():
 q=v['available'];text.append(f"|{profile}|{q['n']}/35|{q['GM']:.6f}|{q['positive']}/{q['neutral']}/{q['negative']}|{v['common_all8']['GM']:.6f}|")
text += ['',
'共同21中的F256/F128 GM分别1.016754/1.011497；当前只是观察趋势。缺失输入、长任务和回退都保留，不能将剩余14个程序假定为1或排除。',
'','各suite可用人口统计如下，单元格为**GM（n/固定suite规模；正/平/负）**，详情与各suite同一共同子集的统计都在SUPPLEMENT.json。',
'','|配置|CUDA Samples /9|Parboil /7|PolyBench/GPU /9|Rodinia /10|','|---|---|---|---|---|']
for profile,v in s['profile_statistics'].items():
 vals=[]
 for suite in ['CUDA Samples','Parboil','PolyBench/GPU','Rodinia']:
  q=v['suites'][suite]['available'];vals.append(f"{f(q['GM'])} ({q['n']}/{q['expected_n']}; {q['positive']}/{q['neutral']}/{q['negative']})")
 text.append('|'+profile+'|'+'|'.join(vals)+'|')
text += ['',
'PolyBench/GPU可用Q64/Q128 GM为0.985595/0.980705，其回退不能被CUDA/Parboil的收益遮掉。Rodinia已配对多数完全平，但仍缺大型/慢输入，不能把当前Rodinia人口推广为全suite结论。',
'','## P0覆盖依赖','',
f"有{deps['total_blocked_DH_pairs_due_missing_DH_P0']}个已accepted DH非P0格因缺DH-P0暂不能配对：GEMM5、srad_v1 4、scalarProd3、3MM1。优先P0只依据覆盖依赖，不依据加速比。",'',
'|程序|缺失P0（原始快照状态）|已accepted DH变体|暂阻配对|','|---|---|---:|---:|']
for row in deps['rows']:
 text.append('|'+row['program']+'|'+', '.join(v['design']+':'+v['state'] for v in row['missing_P0'])+'|'+str(row['accepted_nonP0_DH_count'])+'|'+str(row['blocked_DH_self_pairs_due_missing_DH_P0'])+'|')
text += ['',
'scalarProd DH-P0当时未启；已accepted E384/F128/F256，分别自然wall 26.30/23.40/19.68分钟，E768/M8未accepted。GEMM DH-P0未启，已有五个变体自然wall约104–119分钟；3MM DH-P0未启，F256自然wall5.826小时；srad_v1 DH-P0已运行。wall用于既有任务资源排程参考，不能替代cycles，也不保证P0耗时。全部cohort/UUID/DONE SHA见BASELINE_DEPENDENCIES.json。',
'','## 全35覆盖','',
'A为accepted，其余保留原始状态；DH变体分母固定8。scan/M16另有已验真实工程负例sidecar，不冒充accepted或标准DONE/EXIT。',
'','|程序|suite|CH-P0|DH-P0|DH变体A/8|新增A|缺失DH变体|','|---|---|---|---|---:|---:|---|']
for row in a['coverage']:
 cells=r['table'][row['input_digest']];ch='A'if row['CH_P0_accepted']else cells['P0']['CH']['state'];dh='A'if row['DH_P0_accepted']else cells['P0']['DH']['state']
 text.append(f"|{row['program']}|{row['suite']}|{ch}|{dh}|{len(row['accepted_DH_variants'])}/8|{row['new_accepted_cells']}|{', '.join(row['missing_DH_variants'])or'—'}|")
text += ['', '## 可复核证据与边界','',
f"257/257 accepted raw身份和完整stream统计覆盖均匹配；135行positive原因与总拒绝闭合，122行未打印原因保持None。新增59行中IO链57 legacy、2个额外IO binding均只读核验通过；实际IO canary与三种错误链回放共4项PASS。没有调用会创建sidecar的terminal()。",'',
f"Core `{core['core_commit']}`；Framework `{core['framework_commit']}`；binary `{core['binary_sha256']}`。全部严格配对保持DRAM850、同design、完整输入绑定与非目标选项。",'',
f"当前run：`{run}`。`ANALYSIS.json`/`STRUCTURED_PAIRS.json`逐pair含输入digest、P0/variant cohort、UUID、RESULT路径/SHA、bindingSHA、非目标选项SHA、完整population及raw原因证据；`NEW_RAW_REASONS.json`只含新增59 raw；`CAPTURE.json`记录锚/解析器SHA；`SUPPLEMENT.json`记录完整suite分布和共同人口。",'',
f"冻结锚：`{c['previous_checkpoint_path']}` SHA `{c['previous_checkpoint_sha256']}`。D report生成器commit `fce10d92eb09bc8f562b84a5a84b202bbf1ea385`，raw reason工具发布commit `927c8bd`；实际source SHA全部在CAPTURE/manifest，优先按SHA复核。",'',
f"scan工程负例：`{s['typed_engineering_negative']['certificate']}` SHA `{s['typed_engineering_negative']['sha256']}`；独立typed-gate ACK `{s['typed_engineering_negative']['actual_gate_ACK']}`。不从这份负例产生cycles。",'',
'本轮只读，没有新模型、重试、科学台账或调度规则修改；没有触碰历史72输入，7个UNRESOLVED仍排除，未改英文v0.23母稿。']
(run/'REVIEW.md').write_text('\n'.join(text)+'\n');(HERE/'REVIEW.md').write_text('\n'.join(text)+'\n')
structured=dict(schema='DTC_L2_MLP_STRICT_PAIRED_INCREMENT_V2',utc=r['utc'],anchor=c['previous_checkpoint_path'],anchor_sha256=c['previous_checkpoint_sha256'],
 coverage=a['coverage'],statistics=s['profile_statistics'],baseline_dependencies=deps,pairs=pairs,new_pair_cohorts=[p['variant_cohort']for p in a['new_or_newly_matched_pairs']],
 typed_negative=s['typed_engineering_negative'],no_missing_imputation=True,CH_variant_relative_unavailable=True)
put(run/'STRUCTURED_PAIRS.json',structured)
names=['report.json','NEW_RAW_REASONS.json','IO_CHAIN_AUDIT.json','ANALYSIS.json','SUPPLEMENT.json','BASELINE_DEPENDENCIES.json','CAPTURE.json','REVIEW.md','STRUCTURED_PAIRS.json']
for name in ('STRUCTURED_PAIRS.json','ANALYSIS.json','NEW_RAW_REASONS.json','report.json','SUPPLEMENT.json'):
 (run/(name+'.gz')).write_bytes(gzip.compress((run/name).read_bytes(),compresslevel=6,mtime=0));names.append(name+'.gz')
files={n:dict(path=str(run/n),sha256=sha(run/n),bytes=(run/n).stat().st_size)for n in names}
sources={p.name:sha(p)for p in HERE.glob('*.py')}
manifest=dict(schema='DTC_RESULTS_INCREMENT_V2_DELIVERY',utc=r['utc'],run_path=str(run),files=files,source_hashes=sources,
 IO_qualification=dict(path=str(HERE/'IO_AUDIT_CPU_AND_ACTUAL_QUALIFICATION.json'),sha256=sha(HERE/'IO_AUDIT_CPU_AND_ACTUAL_QUALIFICATION.json')),
 accepted=257,new_accepted=59,reused_raw=198,new_raw_scanned=59,strict_pairs=len(pairs),new_or_newly_matched_pairs=46,identity_errors=0,
 model_starts=0,production_changes=0,old72_raw_scans=0)
put(run/'DELIVERY_MANIFEST.json',manifest);put(HERE/'DELIVERY_MANIFEST.json',manifest)
print(json.dumps(dict(run_path=str(run),review_sha256=sha(run/'REVIEW.md'),pairs_sha256=sha(run/'STRUCTURED_PAIRS.json'),manifest_sha256=sha(run/'DELIVERY_MANIFEST.json'),files=files),indent=2))
