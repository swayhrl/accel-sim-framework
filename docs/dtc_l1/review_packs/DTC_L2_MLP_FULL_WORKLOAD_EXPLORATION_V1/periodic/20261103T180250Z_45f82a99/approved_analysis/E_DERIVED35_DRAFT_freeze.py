"""Freeze a new analysis-only contract candidate; never activates references or GM."""
import pathlib,json,hashlib,datetime
P=pathlib.Path;D=P(__file__).parent;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');O=D/'20261028T232437497897Z'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
summary=read(O/'SUMMARY.json');allrows=read(O/'REFERENCE_MAP_350_DRAFT.json')['rows'];gaps=read(O/'CANDIDATE_REFERENCE_GAPS_12.json')['rows'];coverage=read(O/'PROGRAM_COVERAGE_35.json')['programs']
assert len(allrows)==350 and len(gaps)==12 and summary['input_count']==35
contract=dict(schema='DTC_L2_MLP_DERIVED35_SAME_PHYSICS_REFERENCE_CONTRACT_DRAFT_V1',status='DRAFT_NOT_APPROVED_NOT_APPLIED',analysis_namespace='DTC_L2_MLP_DERIVED35_SAME_PHYSICS_V1',source_snapshot_UTC=summary['UTC'],frozen_scope_path=str(R/'control/SCOPE.json'),frozen_scope_sha256=sha(R/'control/SCOPE.json'),program_input_digests=sorted({r['key']['input_digest']for r in allrows}),slot_count=350,profiles=['P0','E384','E768','M8','M16','Q64','Q128','F128','F256'],reference_key=['input_digest','cell','profile'],source_precedence=[dict(rank=1,source='Existing exact original350 accepted measurement or already ratified matched-P0 reference',rule='Retain it; never replace it by a faster new trial.'),dict(rank=2,source='Only twelve explicitly predeclared engineering-censored original gaps',rule='The fixed one-to-one IR1 eleven or scan/M16 R2 one, conditional on full matching and actual natural strict+archive acceptance.'),dict(rank=3,source='Anything else',rule='MISSING; no zero/one filling, no best-of trial selection, no substitution for currently running/unstarted original slots.')],predeclared_reference_links=[dict(key=r['key'],original_cohort=r['original_cohort'],alternate_cohort=r['predeclared_alternate']['cohort'],alternate_role=r['predeclared_alternate']['role'])for r in gaps],required_identity=['Same frozen complete input digest/input-binding SHA and expected CTA/instruction/kernel counts','Same Core9eed/Framework02775 and actual qualified binary; same design and profile','Exact original-target→new-trial declared configs/native argv/all270 option vectors and frozen science keys; new effective options/counts must be proved by strict receipt','Only officially amended resource/host-CPU/cohort/role/lineage/qualified observation generation may differ; these differences are disclosed','Natural DONE==NATIVE_EXIT==authority execution_receipt; same newUUID through INTENT/launch/PID/strict/result; actual full archive/native restoration','Performance scope true and correctness_validation_only false; no correctness-only repair validation admitted'],forbidden=['Relabeling old negative/pending/HOLD as original accepted','Changing original350/MATRIX/SCOPE, IR/R2 role or existing unionFalse flag','Selecting fastest/newest/best-speedup/PASS trial after looking at performance','Silently relaxing input/full ROI/build/options/design/hash/matching','Using incomplete/pending/failed new measurements or synthetic/CPU fixture data','Giving IR/R2 direct membership in old summary/adaptive original-accepted parents'],statistics=dict(new_named_view_only=True,statistical_combination_if_approved=True,ledger_union=False,role_mutation=False,old_original_summary_unchanged=True,all_source_roles_displayed_side_by_side=True,DH_speedup='DH_P0_reference_cycles / DH_variant_reference_cycles',CH_speedup='CH_P0_reference_cycles / CH_variant_reference_cycles',relative_DTC_improvement='S_DH / S_CH only on identical complete four-cell population',CH_over_DH='same-profile CH_reference_cycles / DH_reference_cycles',GM='exp(mean(log(each matched input ratio))); one input/program and one uniform parameter vector; each available/common/suite population explicit',full35_label_requires='35 valid matched input pairs for the reported metric/profile; a four-way claim also needs all four sources for all35',missing='Remain missing and counted; subset GM must state n/35 and exact population',current_formal_derived_GM_generated=False),authority=dict(user_Goal_frozen35_and_independent_same_physics_engineering_recovery_already_authorized=True,internal_unionFalse_not_a_permanent_user_ban=True,additional_user_permission_not_automatically_required_for_main_reviewed_same_population_same_physics_named_analysis=True,required_before_use='Main scientific review, explicit versioned named statistical contract and public provenance; current candidate is not applied',current_legacy_guard_or_IRplan_changed=False,runtime_parent_or_formal_adoption='Not authorized by this analysis-only draft; separate Main-reviewed, source-qualified consumer/integration contract required, preserving all original records',user_arbitration_required_for=['New/changed input semantics or ROI; promoting unresolved7/fraction/trim/derived models','Different Core/FW/binary or actual non-target physics/config/design/hash/clock/capacity, without a separately approved comparability contract','Performance-driven source choice, dropping regressions/failures, per-program best configuration or weakened strict acceptance','Changing scientific estimand beyond fully qualified same-input same-design measurements, or claiming original first-attempt/full350 acceptance despite preserved negatives']),models_started=0,new_grants=0,production_changes=0,paper_v0_23_unchanged=True)
put(O/'DERIVED35_CONTRACT_DRAFT.json',contract)
# Exact file/line or JSON-pointer evidence, with authorship level explicit.
quotes=[]
def lines(path,start,end,meaning):
 text=P(path).read_text().splitlines();quotes.append(dict(path=str(path),sha256=sha(path),line_start=start,line_end=end,exact_text='\n'.join(text[start-1:end]),authority_level=meaning))
def pointer(path,ptr,meaning):
 v=read(path)
 for key in ptr.strip('/').split('/'):v=v[key]
 quotes.append(dict(path=str(path),sha256=sha(path),JSON_pointer=ptr,exact_value=v,authority_level=meaning))
irp=A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json';r2r=A/'agents/E/supplemental_scan_m16_v2/README.md';pol=A/'agents/E/strace_bpf_future_policy_v3/future_policy.py';op=A/'coordinator/BROAD_SHARED_CPU_PREREQUISITE_APPROVAL_V1/APPROVAL.json'
for ptr in ['/contract/primary_statistics_excluded','/contract/validated_union_authorized','/contract/union_into_effective35_GM_parent_or_adoption_requires_explicit_user_confirmation','/selection_rule']:
 pointer(irp,ptr,'Agent/Main-created incident recovery contract, not verbatim user prohibition. Current execution guard remains unchanged.')
lines(r2r,10,14,'Frozen supplemental R2 contract; original350 and old M16 HOLD stay untouched.')
lines(A/'agents/E/supplemental_scan_m16_v2/supplemental_trial.py',192,203,'Actual old adaptive adapter strips R2 before original parent inference.')
lines(A/'agents/E/supplemental_scan_m16_v2/supplemental_trial.py',240,245,'Actual supplemental table GM=None/automatic_union=False, unchanged.')
lines(pol,103,134,'Qualified scope policy preserves IR role/exclusion and separate actual performance identity; not an inherent data-quality rejection.')
lines(R/'tools/l2_results.py',67,79,'Existing accepted() recognizes strict measurement quality; summary membership is separate.')
lines(R/'tools/l2_results.py',124,141,'Actual primary summary enumerates only real matrix cohort paths; no glob/IR/R2 substitution.')
opdoc=read(op)
for key,value in opdoc.items():
 if 'union'in key.lower():pointer(op,'/'+key,'Main operational rollout restriction, not an external user ban on a future named statistical contract.')
pointer(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','/user_instruction','Native Main transcription/summary of the user Goal, not claimed as a verbatim chat quotation.')
pointer(R/'control/SCIENCE_AUTHORIZATION.json','/scope','Native start/registration authority; start authority alone does not silently revise statistics.')
put(O/'CONTRACT_EVIDENCE_QUOTES.json',dict(schema='DTC_DERIVED35_AUTHORITY_AND_ROLE_EVIDENCE_V1',evidence=quotes,user_conversation_basis=['用户全工作负载 Goal 覆盖全部冻结35输入，并授权四因素扫描、合理扩展、组合、CH匹配及普通工程 solve-and-continue。','用户要求保留历史失败/修复身份，不得把它们替换成原accepted；这不等于禁止另名统计引用合法独立严格新测量。'],interpretation='Existing Goal permits Main to review a transparent same-population/same-physics derived analysis contract. Agent-authored unionFalse guards must remain intact; this draft never silently bypasses them. Material input/physics/selection/estimand changes need user scientific disposition.'))
gaplines=[]
for r in gaps:
 c=r['predeclared_alternate'];m=c['measurement'];state='strict/natural/archive ready'if c['strict_natural_archive_ready']else('consumed, no accepted RESULT'if m['consumed']else'not consumed')
 gaplines.append('| '+r['key']['program']+' | '+r['key']['cell']+'-'+r['key']['profile']+' | '+c['role']+' | '+c['cohort']+' | '+state+' |')
incomplete=[x for x in coverage if x['original_accepted']<10]
report='''# Derived35 同物理测量引用：未应用候选

快照时间：'''+summary['UTC']+'''。原始350格仍为 **323 accepted、27缺口**，31个程序原始10格全齐。原始缺口中12格有预先指定的新试验来源（IR11+scan/M16 R2），其余15格继续等待原身份的首次自然完成。当前12个候选仅R2一个已有严格、自然、归档回执；没有生成派生GM，更没有宣称完整35覆盖。

**不能冒充原accepted，不等于严格新测量永远不可用。** 当前IRplan72ce、R2合同与Main operational approval5c51规定了排除/unionFalse；这些是我们既有内部合同和运行guard，不是用户原文永久禁止新派生分析。用户已授权全35与同物理普通工程恢复。Main可在既有Goal范围内审定、显式版本化另名统计合同，逐格引用合法新测量并完整披露原角色；无需仅因内部guard再制造外部许可门。当前草稿不执行该决定，也不改变任何旧角色、unionFalse、旧summary或旧adaptive。

正式新统计若保持同35输入、同设计/统一配置、严格匹配、非按性能选源，应先冻结本候选的来源与分析口径，由Main审读并公开版本；后续source-bound消费者另行资格验证。若要改变输入/ROI/未决7身份、构建或实际物理参数、按收益挑trial/删负例、弱化严格证据或改变科学估计对象，则是真正需要用户裁决的科学边界。当前只读的各角色侧表、单项严格新测量及明确同物理成对诊断可继续，不得偷算并声称旧350/旧full35已完整。

## 确定性引用规则

1. 原格已有合法严格accepted或已批准匹配P0 reference时，永远优先保留，不用更快的新trial替换。
2. 仅针对下表12个已确定工程删失缺口，使用唯一预指定IR1或R2；选择与cycles/收益/是否漂亮无关。
3. 原target与新trial的冻结input/binding、Core9eed/FW02775/binary、配置和all270声明、完整ROI必须相同。新trial还须实际effective270/完整计数、自然DONE/EXIT/authority、strict与真164/native归档全齐。旧失败的实际完整物理执行从未被声称已验证。
4. pending/失败/缺失继续missing，不填0/1。全部来源保留原role并列展示；IR/R2只成为新命名派生视图的measurement reference，不成为旧格的original accepted。
5. 每个配置以固定输入集合报告available/common/suite覆盖；只有某指标35个真实配对都齐，才可称该指标full35 GM。CH非P0仍缺时，不能推断相对DTC改善或正式统一胜者。

## 12格预指定引用与P0缺口

| 程序 | 原格 | 新来源角色 | 精确新cohort | 当前证据 |
|---|---|---|---|---|
'''+ '\n'.join(gaplines)+'''

SYRK 的 CH-P0、DH-P0 都是原负例，对应独立IR1；因此SYRK的基线对也必须等新严格测量完成，不能以variant代P0。lavamd 缺 CH-P0 是原身份仍在执行，**不建替代引用**。hybridsort和scan的P0原始配对齐。除这4个程序外，另外31程序的原始10格齐。

当前原始缺口明细：
'''+ '\n'.join('- '+x['program']+'：'+str(x['original_accepted'])+'/10原accepted；'+', '.join(y['cell']+'-'+y['profile']for y in x['original_missing_cells'])for x in incomplete)+'''

## 可复核数据与边界

`REFERENCE_MAP_350_DRAFT.json` 给出全部350格及逐格来源逻辑，`CANDIDATE_REFERENCE_GAPS_12.json` 给出12个alternate的spec/RESULT/DONE路径SHA、输入SHA、构建/270/ROI匹配、自然及归档状态。`PROGRAM_COVERAGE_35.json` 给出全35覆盖/P0依赖；`ORIGINAL_MISSING_CELLS.json` 保留全部原缺失。qualified generator9c22仅做只读向量转换核对，350个same-design P0→profile均保留非目标选项/固定容量/时钟；不是新模拟或旧native审计。缺证据用null保留，没有重新扫描大raw或旧工程四点归档。

`CONTRACT_EVIDENCE_QUOTES.json` 给出精确文件SHA、行号或JSON pointer原文，并区分用户Goal、Main转录、agent合同和运行guard；`DERIVED35_CONTRACT_DRAFT.json` 是待Main审定的显式新统计合同。原350、11negative、R2/IR台账及角色全部未改，英文v0.23未动。正式parent/adoption接线不由本分析草稿授权，不能直接让旧V3 accepted门接受IR/R2。
'''
(O/'REPORT.md').write_text(report)
members=sorted(p for p in O.iterdir()if p.is_file())
put(O/'MANIFEST.json',dict(schema='DTC_DERIVED35_CANDIDATE_REVIEW_IMMUTABLE_MANIFEST_V1',status='DRAFT_NOT_APPROVED_NOT_APPLIED',source_collector_sha256=sha(D/'collect.py'),source_freezer_sha256=sha(__file__),members=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in members],new_models_started=0,new_grants=0,production_changes=0,formal_GM_generated=False))
print(json.dumps(dict(directory=str(O),MANIFEST_sha256=sha(O/'MANIFEST.json'),REPORT_sha256=sha(O/'REPORT.md'),contract_sha256=sha(O/'DERIVED35_CONTRACT_DRAFT.json'),map350_sha256=sha(O/'REFERENCE_MAP_350_DRAFT.json'),gap12_sha256=sha(O/'CANDIDATE_REFERENCE_GAPS_12.json'),summary=summary)))
