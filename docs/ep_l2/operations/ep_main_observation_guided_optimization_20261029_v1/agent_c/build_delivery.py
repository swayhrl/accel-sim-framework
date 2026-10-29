from pathlib import Path
import json, csv, hashlib, datetime

J = Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
OUT = J / 'research/observation_guided_20261029_v1/agent_c'
LANE = J / 'receipts/lane_o_v1r2_20261029/review/docs/ep_l2/operations/ep_lane_o_workload_memory_characterization_20261028_v1'
DOC = J / 'review/docs/ep_l2/operations/ep_full_workload_performance_20261027_v1'
OUT.mkdir(parents=True, exist_ok=True)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path': str(p), 'sha256': sha(p), 'bytes': Path(p).stat().st_size}
def load(p): return json.loads(Path(p).read_text())
def put(name, obj):
    p = OUT / name
    with p.open('x') as f: json.dump(obj, f, ensure_ascii=False, indent=2); f.write('\n')

source = load(J/'control/SOURCE_QUALIFICATION.json')['source_identity']
analysis_path = DOC/'results_analysis/RESULTS_ANALYSIS_CURRENT.json'
analysis = load(analysis_path)
ms_path = DOC/'ACCEPTED_REFERENCE_MSHR_SUMMARY.json'
ms = {x['cohort']: x for x in load(ms_path)['cases']}
cohorts = {
 'EP_PERF_SCAN_CF8D1C4D_S_REF_V1','EP_PERF_SCAN_CF8D1C4D_F_REF_V1',
 'EP_PERF_CONV_S_REF_V1','EP_PERF_CONV_F_REF_V1',
 'EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1',
 'EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1',
 'EP_PERF_VECTOR6M_S_REF_V1','EP_PERF_VECTOR6M_F_REF_V1',
 'EP_PERF_SGEMM_S_REF_V1','EP_PERF_SGEMM_F_REF_V1',
 'EP_PERF_VECTOR4M_S_REF_V1','EP_PERF_VECTOR4M_F_REF_V1',
 'EP_PERF_CONV_F_G16_W8_V1','EP_PERF_CONV_F_G32_W4_V1',
 'EP_PERF_VECTOR4M_F_G32_W4_V1',
}
selected = [x for x in analysis['endpoints'] if x['cohort'] in cohorts]
assert {x['cohort'] for x in selected} == cohorts, cohorts - {x['cohort'] for x in selected}
rows = []
for e in selected:
    assert e['accepted'] and e['state'] == 'CLOSED_ACCEPTED'
    assert e['source_identity'] == source
    for k in ('validation_ref','point_ref','archive_ref','done_ref'):
        r=e[k]; assert sha(r['path'])==r['sha256'], (e['cohort'], k)
    b = load(e['validation_ref']['path'])
    assert b['source_identity'] == source and b['input_identity_sha256']==e['input_identity_sha256']
    fm=b['model']['mechanism_metrics']['full_mechanism_records']
    ro=fm.get('readonly', {})
    roinfo={'status':'NOT_APPLICABLE' if not e['M'] else 'OBSERVED'}
    if e['M']:
        assert len(ro)==64
        for field in ('accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions','merges','detached','responses'):
            roinfo[field]=sum(v['summary'][field] for v in ro.values())
        assert roinfo['transactions']+roinfo['merges']==roinfo['accepted_ro']==roinfo['responses']
        roinfo['max_over_slice_pending_unique_lines']=max(v['lower_concurrency']['peak_independent_lower_lines'] for v in ro.values())
        roinfo['max_over_slice_live_transactions']=max(v['resource']['peak_transactions'] for v in ro.values())
        roinfo['merge_fraction_of_accepted_ro']={
          'numerator':roinfo['merges'], 'denominator':roinfo['accepted_ro'],
          'boundary':'RO accepted successful requester population',
          'class':'exact certified GLOBAL_ACC_R nonwrite nonatom admitted to RO runtime',
          'meaning':'live transaction merge, NOT strict fill-before-ready',
          'value':roinfo['merges']/roinfo['accepted_ro'] if roinfo['accepted_ro'] else None}
    bottleneck={k:b['model']['mechanism_metrics']['bottleneck'].get(k, {'status':'NOT_EMITTED'})
      for k in ('LINE_MSHR_FULL','PER_LINE_CAP','DESCRIPTOR_FULL','TAG_SET_PENDING')}
    rows.append({
      'cohort':e['cohort'],'program':e['program'],'input_identity_sha256':e['input_identity_sha256'],
      'mode':e['mode'],'profile':e['profile'],'geometry':e['geometry'],'cycles':e['cycles'],
      'M':e['M'],'T':e['T'],'observer':e['observer'],'source_identity':source,
      'bundle_ref':e['validation_ref'],'point_ref':e['point_ref'],'archive_ref':e['archive_ref'],
      'done_ref':e['done_ref'],'spec_ref':e['spec_ref'],'option282_digest':e['option282_digest'],
      'semantic_population_digest':e['semantic_population_digest'],
      'RO':roinfo,'ordinary_MSHR':ms.get(e['cohort'],{'status':'NOT_PROJECTED_IN_44_REF_SUBSET'}),
      'MS_first_wait_population':bottleneck,
      'strict_required_sector_before_ready':'NOT_COLLECTED',
      'normal_RO_union_time_distribution':'NOT_COLLECTED',
      'actual_ingress_gap':'NOT_COLLECTED',
      'same_NEW_set_tick_full_structural_joint':'NOT_COLLECTED',
      'full_LIFE_NEW_at_R_current_endpoint':'NOT_COLLECTED',
      'T_independent_cycles_contribution':'UNKNOWN_NO_MATCHED_F_MINUS_T_POINT',
    })

gaps = [
 {'metric':'RO accepted/candidates/live merges/retirement','status':'REUSE_EXISTING','action':'no new application'},
 {'metric':'ordinary line-MSHR/per-address/D512 first blocked UID, retry checks and reason waits','status':'REUSE_EXISTING','action':'do not infer full demand incidence without matching class denominator'},
 {'metric':'actual production detached','status':'REUSE_EXISTING','action':'retain 27/237/1141; no detailed TagFAIL or lifetime inferred'},
 {'metric':'strict requested-sector before-ready at ingress and first-head','status':'NOT_COLLECTED','action':'only if needed for a chosen M policy; boundary-labelled live/prestate hook'},
 {'metric':'normal+RO pending/live independent-address union','status':'NOT_COLLECTED','action':'event-based refcounts, no peak addition; optional until policy needs union'},
 {'metric':'same firstNEW/ever-full UID,set,tick full AND structural RO','status':'NOT_COLLECTED','action':'minimal highest-value T hook; candidate predicate excludes T enable bit'},
 {'metric':'T independent cycle contribution','status':'UNKNOWN','action':'same accepted Source78 F_MINUS_T/F causal pair is different from new collector NI'},
]
put('MT_OPPORTUNITY_AND_GAPS.json', {
 'schema':'EP_OBSERVATION_GUIDED_MT_COMPACT_ONLY_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'15 selected CLOSED_ACCEPTED Source78 points; not 35/42/96 coverage census',
 'source_identity':source,'new_models':0,'new_trace_body_reads':0,'new_raw_body_reads':0,
 'new_scientific_acceptance':False,'join':'reuse Main sealed endpoint acceptance/identity; reverify selected compact bundle/point/archive/DONE bytes only',
 'inputs':[ref(J/'control/SOURCE_QUALIFICATION.json'),ref(analysis_path),ref(ms_path),
           ref(LANE/'MEASUREMENT_CONTRACT.md'),ref(LANE/'NI_MATRIX.md'),ref(LANE/'PILOT_GAPS.json')],
 'rows':rows,'gaps':gaps,
 'production_collector':'NOT_IMPLEMENTED_NOT_QUALIFIED',
 'pure_reference':'13 synthetic local Windows Python tests passed; no simulator code/lib linkage; no native or app NI claim',
 'cost':'C++ state/serialized output/host overhead UNMEASURED; design caps are targets only',
})

ni_fields=['path','mode','input','candidate_source','CPU_status','application_OFF_ON_status','minimum_controls','NI_inheritance']
ni=[
 ['ingress_child/queue_enter/first_head','S','Conv or Scan','NOT_FROZEN','13 reference tests subset only; production CPU NOT_PREPARED','NOT_QUALIFIED','parent/sector closure; ROP+texture; successor-before-head; UID generation; tail; order','old S observer does not cover new hooks'],
 ['ingress_child/queue_enter/first_head','F','Vector6M or Conv','NOT_FROZEN','NOT_PREPARED','NOT_QUALIFIED','same as S plus actual RO/partial-ready path','S NI does not cover F'],
 ['RO required-sector ready/merge/retire','F','Vector6M then Conv/SGEMM if enabled','NOT_FROZEN','pure mask reference only; production NOT_PREPARED','NOT_QUALIFIED','partial ready; issued vs not-yet-issued; ready-only drain; last waiter; reject before admit','old Source78 Vector4M ETNI only old observer'],
 ['normal+RO address union','F','Conv or Vector6M','NOT_FROZEN','pure set reference only; production NOT_PREPARED','NOT_QUALIFIED','same line normal+RO refcounts; multiple transactions; return reorder; zero-tail; overflow invalidation','separate peak maxima are not union evidence'],
 ['T full AND structural candidates','F and F_MINUS_T','Conv G16W8 first; G32W4 optional','NOT_FROZEN','pure event reference only; production NOT_PREPARED','NOT_QUALIFIED','enable-independent structural predicate; firstNEW vs everfull; pin/reuse/generation; detach guard stays','constructed candidate not application opportunity or performance'],
 ['WV-specific ingress/V service','WV_ZERO_RO','FWT','NOT_FROZEN','NOT_PREPARED','NOT_QUALIFIED','only if chosen new counter reaches WV; actual victim/dirty-forward commit','S/F NI cannot transfer to WV; RO/T N/A'],
 ['S static RO-membership optional','S','exact chosen input','NOT_FROZEN','NOT_PREPARED','NOT_QUALIFIED','explicit correct-input certificate; readonly membership no production RO, ports or timing','dormant S manifest may name Vector4M; never inherit it'],
 ['bounded state/serializer','all actual new schemas','maximum commandlist metadata stress','NOT_FROZEN','NOT_PREPARED','NOT_QUALIFIED','actual sizeof/padding; overflow/censor; max bins; bounded output; no per-kernel Cartesian dump','Python reference not C++ memory/output bound'],
]
with (OUT/'NEW_OBSERVER_NI_MATRIX.csv').open('x',newline='') as f:
 w=csv.writer(f);w.writerow(ni_fields);w.writerows(ni)

spec_fields=['priority','input','input_identity_sha256','geometry','parent_F_cohort','parent_F_spec_SHA256','parent_F_cycles','parent_F_detach','candidate_mode','candidate_M','candidate_T','observer','source_core','ELF_SHA256','point_count_if_parent_F_reuse_qualified','point_count_if_new_ELF_or_observer','missing_gates','authorization']
plans=[]
for priority,cohort in enumerate(['EP_PERF_CONV_F_G16_W8_V1','EP_PERF_VECTOR4M_F_G32_W4_V1','EP_PERF_CONV_F_G32_W4_V1'],1):
 e=next(x for x in rows if x['cohort']==cohort)
 plans.append([priority,e['program'],e['input_identity_sha256'],str(e['geometry']),cohort,e['spec_ref']['sha256'],e['cycles'],e['RO']['detached'],
  'F_MINUS_T (not WV_ZERO_RO)',1,0,'all heavy OFF exactly parent; MS/B0/M0a unchanged',source['core_source_commit'],source['binary_sha256'],1,
  '2 causal points plus any missing exact OFF/ON controls; cannot reuse old ELF F as new ELF control',
  'same-source legal mode host/native qualification; exact 282 only T allowed delta; same RO certificate; scope exact geometry; fresh goal budget and sole-entry',
  'DRAFT_ONLY_0_NEW_START_AUTHORIZATION'])
with (OUT/'F_MINUS_T_F_DRAFT_SPEC_MATRIX.csv').open('x',newline='') as f:
 w=csv.writer(f);w.writerow(spec_fields);w.writerows(plans)

readme='''# M/T机会、缺口与最小验证

本交付只复用15个Main已封存接受端点的小JSON；逐一回读bundle、point、archive和DONE的SHA。没有Trace/raw正文扫描、模型启动、注册表/Git写入，也不重新授予旧端点科学资格。精确来源与整数在MT_OPPORTUNITY_AND_GAPS.json。本表不是35/42/96全体覆盖；全体由Agent A/Main统一表维护。

## 结论与候选优先级

**PROVEN**：Vector6M efced2c… F有1,500,000个accepted RO requester、375,109个事务、1,124,891个live merge（74.9927%）。普通line-MSHR峰0与RO issued-not-ready独立line峰70/slice并存，前者不能解释为没有访存并发。Vector4M ddf26d…是另一个输入，不能以其时间线或sector复用直接填Vector6M。

**PROVEN**：SGEMM有1,135,915个accepted RO requester、81,582事务、1,054,333个live merge（92.8179%）；S每地址32限制有1,738次重复head检查、55个首次受阻UID。Conv S普通line-MSHR峰128，6,499次检查、696个UID；F仍有2,986次检查、337个UID。这表明M的独立line容量机会与同址merge限制应分别设计，不能统一用扩容line-MSHR解决所有情况。原因等待只到first-known-clear（ANY例外），不称独占GPU stall。

**PROVEN**：Vector4M32×4实际detach27；Conv16×8实际237、32×4实际1,141。对应F均慢于同几何S，仍**UNKNOWN** T自身收益。当前REF四pilot heavy全部OFF，LIFE_WIRE=SUMMARY_STAGE不提供完整NEW-at-R或Tag寿命。现有MS TAG_SET_PENDING不是生产TagFAIL。Source78旧timeline Conv-S的289 firstNEW-at-R8/42,717 preview是另一个开启observer的接受点；本文不把它塞进当前REF的联合格。

**UNKNOWN**：live merge里多少发生于本请求所需sector未ready、多少只是ready/draining；有多少事务首次merge置reuse_seen；正常与RO同时独立地址并集；同一新UID、同Set、同刻R==ways且结构eligible的机会。不能把RO merge边际和S满路边际相乘。RO pending峰、descriptor峰均为各slice最大值，不相加成GPU同步峰。

**HYPOTHESIS**：对Conv先判断独立line-MSHR等待是否实质改善，再考虑M资源；对SGEMM应先检查每地址merge与ready-only drain，不能从92.8%live merge推断严格Fill前复用；对Vector6M不优先增加普通line-MSHR，因为F已绕过它且现有数据未证明该处饱和。高merge对reuse_seen保护的限制只作假说，尚无同事件共现。

**建议**：总体先W/V（由Agent B交付）；M/T不启动新大矩阵。若用户审查后只批准一个T因果点，首选Conv16×8同Source78/ELF的F_MINUS_T，用已有合法F母点控制，保留完整硬件与证书。可验证T cycles贡献且不需要先造新collector。第二候选Vector4M32×4，Conv32×4仅作为更强压力备选，不为了detach继续缩容。新mode host/native/geometry资格尚未闭合，表中每行都是0授权候选，不自动累计成3次预算。WV=M0/T0不等于F_MINUS_T=M1/T0；无需为T单项控制另跑S。

## 最小新增计量工程：设计与纯参考，不接生产

新增指标的价值必须对应选定策略，不能先实现全功能地址分析器。建议分两档：

1. **T-only小钩子**：现有first-head/preview快照里读出真实UID、generation、目标set、R、结构候选数，结构谓词独立于T位；记录firstNEW、ever-full、repeat checks、真实Tag拒绝distinct ticks、head→admission和right-censor。guard不变，不新增probe/目录/银行动作。由已有RO mutation维护结构候选shadow，不能为观察周期扫way或复用含T开关的can_detach。必须审查attached、owner/generation、reuse_seen、required-not-ready、pin与实际协议保护的完整对应。
2. **仅若M策略需要**：真实push的parent/sector child身份、queue_enter、first-head分开。读到达前required-sector ready及issued状态，分别报requested-not-ready、issued-not-ready、ready-only-drain、line其他sector pending；normal/RO独立地址用事件refcount并集，overflow使exact失效。不能扫描FIFO倒推ingress，也不需要先做全地址reuse距离表。S不运行RO，静态membership只能绑定本输入已资格证书，禁止使用其可能指向Vector4M的dormant配置。

`mt_contract_reference.py`及13项测试是**纯计量语义参考**，已在本地Windows/Python3.12.10执行；没有链接任何Core/ELF/.a、没有生产hook，也没有宣称本地执行等于174 native资格。测试覆盖defaultOFF、边界去重、后继先到、firstNEW与everfull、T关闭仍有结构事件、结构UNKNOWN、generation/epoch保留、跨clock拒绝相减、同tick多child、overflow失效、部分sector ready、地址并集、同人口分母。未覆盖真实parent-child闭合、ROP/texture、生产mutation/生命周期/顺序和应用NI。

参考代码中的Python字典、set与线性遍历不是最终低开销实现，不允许接入生产。生产C++候选仍NOT_IMPLEMENTED、没有新Core/ELF。新hooks每路径CPU正确性、真实sizeof/对齐/输出上界和应用OFF/ON均NOT_QUALIFIED；≤16MiB状态、≤8MiBcompact、≤5%host overhead均为未测目标，不能用13项纯测试背书。

## NI与点数

先冻结实际启用路径：只采head的方案不用承诺ingress；不用V/RO的S不被迫做全部F/WV测试。若采集Conv/Scan-S需求、Conv/Vector6M-F实际M/T、FWT-WV的实际路径，则每一个启用模式分别需要CPU路径和同新ELF/同输入/同硬件/同模式OFF/ON控制。S不能覆盖F/WV，FWT不自动换RO-F。旧Source78 Vector4M ETNI只资格旧observer，不覆盖本参考或新hook。

新采集点数=N_ON+N_missing_exact_OFF；不能直接说4ON+1OFF足够。如新ELF四候选各一模式且无任何同ELF OFF控制，则四对=8点只是条件算例，非计划预算；如果只实现T-only，可收缩为一个合法F的2点OFF/ON，再另审因果F_MINUS_T/F。collecting NI和性能因果是两件事，若复用同一模式ON点，必须精确冻结共同配置/资格后才能合并计数。Stage C/D正式预算由Main另列、用户审查，本文无任何新增启动授权。

## 工程与旧资产边界

可复用科学底：Core78f4b59…/FW9dd1ee57…/ELF78d4e96…，完整Source5见JSON。主机写入V3的800纯协议+10生产CPU不等于native应用资格；MSHR64、native/merge-aware T候选各保留独立工程身份，均不自动集成。新源码不得链接旧.a冒称生产正确性。大Trace和永久raw继续真164，本文只有小型派生文档和参考代码。
'''
(OUT/'MT_OPPORTUNITY_AND_GAPS.md').write_text(readme)
put('PURE_REFERENCE_EXECUTION.json', {
 'schema':'EP_MT_CONTRACT_PURE_WINDOWS_REFERENCE_EXECUTION_V1',
 'execution_utc':'2026-10-29; exact tool receipt retained in Main conversation',
 'platform':'Windows local host; Python 3.12.10',
 'command':'python -B -m unittest -v test_mt_contract_reference.py',
 'working_directory':'D:/repo/.ep_observation_agent_c_20261029',
 'tests':13,'failures':0,'returncode':0,'unittest_reported_seconds':0.001,
 'tool_wall_seconds':0.7590282,
 'fresh_local_preflight':{'available_physical_KiB':3238176,'D_free_bytes':65841299456},
 'execution_kind':'PURE_SYNTHETIC_METERING_REFERENCE_ONLY',
 'production_compile':False,'simulator_library_linked':False,'application_NI':'NOT_EXECUTED',
 'native174_CPU':'NOT_EXECUTED','host_model_overhead':'NOT_MEASURED',
 'peak_RSS':'NOT_INSTRUMENTED','CXX_state_size':'NOT_IMPLEMENTED_NOT_MEASURED',
 'files':[ref(OUT/'mt_contract_reference.py'),ref(OUT/'test_mt_contract_reference.py')],
})
put('DELIVERY_MANIFEST.json', {
 'schema':'EP_OBSERVATION_GUIDED_AGENT_C_DELIVERY_V1',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'READY_FOR_MAIN_REVIEW_NO_SCIENTIFIC_STARTS',
 'files':[ref(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='DELIVERY_MANIFEST.json'],
 'immutable_old_sources':True,'new_simulations':0,'trace_raw_body_scans':0,
 'remote_Git_or_registry_mutations':0,
})
print(json.dumps({'manifest':ref(OUT/'DELIVERY_MANIFEST.json'),'rows':len(rows)},indent=2))
