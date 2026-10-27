from pathlib import Path
import json, hashlib, datetime, math, re, difflib

OUT = Path(__file__).resolve().parent
TMP = Path('D:/repo/tmp')
BASELINE_COMMIT = '71584878be0c80375f9d25bcd80e171b7bf4478d'
UPSTREAM_COMMIT = 'b059fdae25c2aabf737486aada743fca114469ce'
FREEZE_SHA = 'a4157b56b48d8d8df048b9f64e62d54b091e80176d7a05169ef9c64b0c06da9d'
APPS = ['backprop','cfd','kmeans','nn','nw','pathfinder','streamcluster']
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
write = lambda name, x: (OUT/name).write_text(json.dumps(x, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
freeze_path = TMP/'DTC_P42_REPRESENTATIVE_FREEZE.json'
assert sha(freeze_path.read_bytes()) == FREEZE_SHA
freeze = read(freeze_path)
dedup = read(TMP/'DTC_PAPER_DEDUP_EVIDENCE_20261027_V2.json')
sources = read(OUT/'SOURCE_IDENTITY_EVIDENCE.json')
current = read(OUT/'CURRENT_READONLY_VERIFICATION.json')
upstream = read(OUT/'UPSTREAM_PINNED_EVIDENCE.json') + read(OUT/'UPSTREAM_PINNED_EVIDENCE_2.json')
prior = read(TMP/'DTC_P42_ADJUDICATION_EVIDENCE.json')
assert len(current['commandlists']) == 21 and all(x['matches_expected'] for x in current['commandlists'])
assert any(x.get('sha256') == FREEZE_SHA for x in current['freeze_checks'])

def source(app, file, version='3.1'):
    return next(s for s in sources['sources'] if s['program'] == app and s.get('version') == version and Path(s['path']).name == file)

def ref(app, file, lo, hi, version='3.1'):
    s = source(app,file,version)
    return {'path':s['path'], 'sha256':s['sha256'], 'lines':[lo,hi],
            'excerpt':'\n'.join(f'{i}: {t}' for i,t in enumerate(s['text'].splitlines(),1) if lo <= i <= hi)}

upstream_checks = []
for u in upstream:
    if not u.get('content'): continue
    s = next(s for s in sources['sources'] if s['path'].endswith('/'+u['rel']))
    exact = s['text'] == u['content']
    upstream_checks.append({'relative_path':u['rel'],'pinned_url':u['url'],
        'pinned_utf8_sha256':sha(u['content'].encode()),'deployed_path':s['path'],
        'deployed_sha256':s['sha256'],'exact_match':exact,
        'difference':None if exact else ''.join(difflib.unified_diff(u['content'].splitlines(True),s['text'].splitlines(True),fromfile='pinned',tofile='deployed'))})
assert len(upstream_checks) == 18
assert sum(x['exact_match'] for x in upstream_checks) == 16

inputs = []
for m in freeze['mapping_72_to_42']:
    if m['program'] not in APPS: continue
    r = next(r for r in dedup['rows'] if r['intake']['input_digest'] == m['input_digest'])
    i = r['intake']
    scripts = {s['sha256']:s for a in i['asset']['source_aliases'] for s in a.get('capture_scripts',[])}
    for s in scripts.values():
        assert sha(s['text'].encode()) == s['sha256']
    inputs.append({k:m[k] for k in ['program','input_digest','bundle_id','trace_entry','source_version','parameters','source_members_sha256']} | {
        'v1_decision':m['decision'], 'original_commands':i['expected_commands'],
        'capture_scripts':list(scripts.values()),'source_aliases':i['asset']['source_aliases'],
        'prior_contexts':i['asset']['prior_scientific_contexts'],
        'kernel_scope':[{'ordinal':g['ordinal'],'kernel':g['kernel'],'complete_ctas':g['complete_ctas'],
            'complete_warps':g['complete_warps'],'trace_version':g['trace_version'],
            'binary_version':g['binary_version']} for g in r['kernel_geometry']],
        'expected_kernel_launches':len(i['ordered_kernels']),
        'declared_kernel_population_evidence':{
            'qualification_status':r['qualification']['status'],
            'capture_complete_native_input':r['qualification']['capture_complete_native_input'],
            'native_numerical_correctness':r['qualification']['native_numerical_correctness'],
            'caution':'This pre-existing trace-population qualification is not whole-application capture or numerical validation.'},
        'raw_dataset_content_sha256':None,'capture_executable_sha256':None,
        'read_scope':'Current commandlist SHA rechecked; existing whole-body member SHA receipts reused without trace scans.'})
assert len(inputs) == 21
write('INPUT_IDENTITY_CATALOG.json', inputs)
write('UPSTREAM_SOURCE_VERIFICATION.json',upstream_checks)

excerpts = {
    'backprop':[ref('backprop','facetrain.c',14,52),ref('backprop','backprop_cuda.cu',80,84),ref('backprop','backprop_cuda.cu',118,128),ref('backprop','backprop.c',132,136),ref('backprop','imagenet.c',8,23),ref('backprop','run',1,2)],
    'cfd':[ref('cfd','euler3d.cu',17,27),ref('cfd','euler3d.cu',499,507),ref('cfd','euler3d.cu',555,566),ref('cfd','euler3d.cu',580,596),ref('cfd','run',1,10)],
    'kmeans':[ref('kmeans','kmeans.c',108,123),ref('kmeans','kmeans.c',190,220),ref('kmeans','kmeans_clustering.c',133,171),ref('kmeans','kmeans_cuda.cu',47,80),ref('kmeans','kmeans_cuda.cu',152,156),ref('kmeans','kmeans_cuda.cu',228,245),ref('kmeans','run',1,2)],
    'nn':[ref('nn','nn_cuda.cu',20,30),ref('nn','nn_cuda.cu',143,162),ref('nn','nn_cuda.cu',176,223),ref('nn','run',1,2),ref('nn','nn_cuda.cu',13,32,'2.0-ft'),ref('nn','nn_cuda.cu',147,208,'2.0-ft')],
    'nw':[ref('nw','needle.cu',83,109),ref('nw','needle.cu',147,165),ref('nw','needle.h',1,20),ref('nw','run',1,2)],
    'pathfinder':[ref('pathfinder','pathfinder.cu',19,65),ref('pathfinder','pathfinder.cu',188,204),ref('pathfinder','run',1,2)],
    'streamcluster':[ref('streamcluster','streamcluster_cuda_cpu.cpp',20,23),ref('streamcluster','streamcluster_cuda_cpu.cpp',329,348),ref('streamcluster','streamcluster_cuda_cpu.cpp',565,585),ref('streamcluster','streamcluster_cuda_cpu.cpp',887,903),ref('streamcluster','streamcluster_cuda.cu',132,174),ref('streamcluster','streamcluster_cuda.cu',239,257),ref('streamcluster','run',1,2)]}
write('SOURCE_EXCERPTS.json',excerpts)

def proposal(prefix):
    return next(x['input_digest'] for x in inputs if x['input_digest'].startswith(prefix))

decisions = [
 {'program':'backprop','status':'UNRESOLVED_V1_UNCHANGED','scope':'SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED',
  'new_findings':['Both versions train one network once; hidden/output sizes are 16/1 and the initialization seed is 7.',
      '3.1 packaged run specifies 65536. Its two captured kernels and HtoD sizes 262148 and 4456516 bytes agree with (65536+1)*4 and (65536+1)*17*4.',
      '2.0-ft is explicitly a modified functional-regression collection; its 4096 input is not an alias of the 3.1 65536 input. Two 4096 captures have different trace-format identities and member SHAs.'],
  'v2_proposal':{'input_digest':proposal('5fa6'),'rule':'Prefer the 3.1 release run command over small 2.0-ft regression variants, if this outcome-independent suite policy is adopted explicitly for V2.','conditional':True},
  'remaining_evidence':['42-suite source-version precedence not approved/frozen','Capture executable/build/tracer linkage','Generated input content or capture-time generator/runtime binding; source seed alone is insufficient']},
 {'program':'cfd','status':'UNRESOLVED_V1_UNCHANGED','scope':'STANDARD_FULL_APPLICATION_SCOPE_CONTRADICTION',
  'new_findings':['Pinned and deployed euler3d retain iterations=2000 and RK=3. Three initialization launches plus 2000*(one step-factor + three flux + three time-step)=14003 GPU launches are expected.',
      'All three available candidates contain only three initialize + one step-factor + one flux kernel; no time-step occurs. Even a complete first iteration would require 10 kernels.',
      'The local source differs from pinned b059fdae only by CUDA error-check wrapper removal; this does not explain five captured kernels.',
      '193K grid1008*192 describes padded nelr=193536, not exact mesh nel. A historical 097K E1 reference input SHA exists, but is not bound to the capture contents.'],
  'v2_proposal':{'input_digest':None,'rule':'Do not promote any five-kernel candidate as a full CFD application. Recover capture executable and documented ROI/early-stop evidence first. An explicit partial-region suite would be a different scientific contract.','conditional':True},
  'remaining_evidence':['Capture-time source/binary identity and truncation/ROI configuration','Raw mesh contents, exact nel and capture-linked SHA','Full time-step/iteration capture or approved bounded-region contract; neither is granted by current authorization']},
 {'program':'kmeans','status':'UNRESOLVED_V1_UNCHANGED','scope':'DATA_DEPENDENT_CONVERGENCE_NOT_CERTIFIED',
  'new_findings':['The 3.1 packaged run uses kdd_cup; source defaults are kmin=kmax=5, threshold=0.001 and one outer run.',
      'All three 3.1 captures contain invert_mapping plus two kmeansPoint launches. This can be a two-iteration convergence, but neither a fixed two-iteration application nor truncation is proven from kernel count.',
      'Source-layout conditional dimensions from independent HtoD matrix/membership/center sizes are 819200x34, 494020x34 (kdd_cup), 28672x138 (28k_4x_features), and 400x34 (2.0-ft). These are not certified raw dataset identities.',
      'The existing official 400 capture data symlink is broken on 174-new. A result file is not the original input data.'],
  'v2_proposal':{'input_digest':proposal('2315'),'rule':'kdd_cup is the source-packaged run candidate; do not freeze until dataset and convergence/capture-completeness evidence close.','conditional':True},
  'remaining_evidence':['Actual dataset bytes/SHA and row/feature parser result','Capture stdout final iterated-N/convergence result plus tracer scope','Source-version precedence and capture binary/source/build binding']},
 {'program':'nn','status':'UNRESOLVED_V1_UNCHANGED','scope':'SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED',
  'new_findings':['3.1 packaged run matches filelist_4 -r 5 -lat 30 -lng 90 and emits one euclid GPU kernel after reading all records; -r selects the CPU-side top-N result count, not an euclid GPU argument.',
      'The 342112-byte HtoD coordinate buffer implies 42764 LatLong records under the 3.1 two-float layout. The 2.0-ft candidates instead use four 735000-byte character-record batches. Same filelist_4 spelling is not proof of the same files or records.',
      '3.1 has a DTC_LEGACY_NN pointer to three historical cohorts under commit b2d6121e169dd0605d3e3c51cd010e7e77effd49. Their recorded status is checked terminal scope only until comparison complete, not approval of whole-app input identity for the 42-suite.',
      'Deployed nn_cuda.cu additionally has an emulation-only memory-size branch absent at pinned b059fdae; GPU kernel and host read/launch scope match in the inspected diff, but exact capture compile flags remain unknown.'],
  'v2_proposal':{'input_digest':proposal('8df9'),'rule':'3.1 packaged run plus historical named reference provides the strongest provenance candidate, subject to dataset and source-version-policy closure.','conditional':True},
  'remaining_evidence':['filelist bytes plus ordered constituent data files and capture-linked SHAs','Capture executable/build/tracer identity including emulation macro state','Explicit V2 version-policy adoption; historical terminal-scope receipts are not full-app certification']},
 {'program':'nw','status':'UNRESOLVED_V1_UNCHANGED','scope':'SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED',
  'new_findings':['3.1 packaged run specifies 2048 10. Source generates equal-length sequences using seed7 and accepts a single dimension and penalty; the README usage is stale and should not override the parser.',
      'With BLOCK_SIZE=16 the two wavefront loops emit 2*(2048/16)-1=255 launches, exactly the captured count. The 2.0-ft 128 case correspondingly emits15 launches.',
      '2.0-ft kernel signatures include an additional output matrix pointer, so matching application name is not identical kernel implementation. Its two captures differ in format/body SHAs.'],
  'v2_proposal':{'input_digest':proposal('cf56'),'rule':'Use 3.1 packaged run command if the V2 source-version policy is adopted. This is not a performance-based size choice.','conditional':True},
  'remaining_evidence':['Capture executable/compiler/tracer linkage','Generated sequence content binding to generator and C-library behavior','Explicit V2 version policy; whole-app numerical correctness remains separate']},
 {'program':'pathfinder','status':'UNRESOLVED_V1_UNCHANGED','scope':'SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED',
  'new_findings':['Parser binds argv1=cols, argv2=rows and argv3=pyramid_height; the packaged run is 100000 100 20 > result.txt. The output redirection is not a fourth application argument.',
      'Source seed is9. Source loop ceil((rows-1)/height) predicts5 launches for 100000x100,height20 and4 for1000x20,height5, agreeing with the trace commandlists.',
      'The two same-argument 2.0-ft captures differ in trace-format identity and member SHAs; no duplicate elimination by program name or outcome is justified.'],
  'v2_proposal':{'input_digest':proposal('ccdd'),'rule':'Use the 3.1 packaged run if the V2 source-version policy is adopted; retain output redirection as shell semantics.','conditional':True},
  'remaining_evidence':['Capture executable/compiler/tracer binding','Capture-time generated wall contents or exact generator/runtime binding','Explicit V2 source-version precedence']},
 {'program':'streamcluster','status':'UNRESOLVED_V1_UNCHANGED','scope':'STANDARD_FULL_APPLICATION_SCOPE_CONTRADICTION',
  'new_findings':['3.1 packaged run is 10 20 256 65536 65536 1000 none output.txt 1. For positive n, source generates coordinates with SimStream seeded by srand48(1); none is not an external dataset filename in this case.',
      'The 3/6/16 candidate adds an extra output.txt argument. The inspected 3.1 parser accepts argc>=10 and reads only argv1..9, so the trailing argument is ignored under this source; it does not restore a goldfile check.',
      'The CPU pFL path uses ITER=3 and emits floor(3*kmax*ln(kmax)) pgain calls in every entered sweep; each pgain unconditionally launches one kernel_compute_cost. This is32 calls for kmax6 or179 calls for kmax20. Five captured kernels cannot be a complete sweep under the inspected standard source.',
      'Both candidates have exactly five complete kernels. Their missing HtoD entries also cannot certify host initialization. Capture binary/ROI or early termination must explain this before whole-application use.'],
  'v2_proposal':{'input_digest':None,'blocked_packaged_run_candidate':proposal('f7d6'),'rule':'The 10/20/256 tuple matches the packaged command, but do not freeze a five-kernel capture as complete streamcluster. Resolve the source/capture scope mismatch before a V2 identity decision.','conditional':True},
  'remaining_evidence':['Capture binary/source/compile flags and tracer kernel-window rules','Capture completion/host convergence log and complete launch range','Generated coordinate content/runtime binding; explicit parameter-policy decision']}
]

shape = []
for x in inputs:
    if x['program'] != 'kmeans': continue
    copies = [int(c.rsplit(',',1)[1]) for c in x['original_commands'] if c.startswith('MemcpyHtoD,')]
    n = copies[1]//4; f = copies[0]//copies[1]
    assert n*4 == copies[1] and n*f*4 == copies[0]
    assert copies[2] == 5*f*4
    shape.append({'input_digest':x['input_digest'],'matrix_HtoD_bytes':copies[0], 'membership_HtoD_bytes':copies[1], 'center_HtoD_bytes':copies[2],
        'source_layout_conditional_npoints':n,'source_layout_conditional_features':f,'inferred_clusters':5,
        'actual_dataset_bytes_certified':False,'assumptions':'Observed copies correspond to the inspected source feature/membership/center allocations, with 4-byte float/int; capture binary identity not recovered.'})

prior_refs = [r for r in prior['records'] if r['path'].endswith(('M5_EXTENDED20_APPROVAL.md','M5_E1_EXTENDED20_FORMALIZATION.md'))]
write('HISTORICAL_REFERENCE_EVIDENCE.json',{'prior_records':prior_refs,
    'nn_contexts':next(x['prior_contexts'] for x in inputs if x['input_digest'].startswith('8df9')),
    'cfd_contexts':next(x['prior_contexts'] for x in inputs if x['input_digest'].startswith('f9ed')),
    'cfd097k_historical_candidate_mesh_sha256':'43534e58454ba8baf95253e14d3b07150b9960577e922a954d6e51142a27abfa',
    'caution':'The historical canonical-mesh SHA is not an assertion that current captured 097K bytes are bound to it.'})

report = {'schema':'DTC_P42_SEVEN_UNRESOLVED_READONLY_V1','agent':'F','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'baseline_framework_commit':BASELINE_COMMIT,'upstream_source_commit':UPSTREAM_COMMIT,'v1_freeze_sha256':FREEZE_SHA,
 'freeze_unchanged_verified':True,'frozen_count_unchanged':35,'unresolved_count_unchanged':7,'newly_frozen_inputs':0,
 'source_scope_consistent_proposal_count':4,'source_scope_contradiction_count':2,'convergence_data_unproven_count':1,
 'input_count':21,'current_commandlist_sha_matches':21,'deployed_source_records':len(sources['sources']),
 'pinned_upstream_files_checked':len(upstream_checks),'pinned_exact_matches':sum(x['exact_match'] for x in upstream_checks),
 'selection_independent_of_results':{'performance_fields_accessed':False,'embedded_original_modes_ignored':True,'strict_PASS_used':False,'runtime_used':False,'speedup_used':False,'repair_cycles_used':False},
 'no_new_simulations':True,'no_trace_body_scans':True,'no_capture_execution':True,'no_science_or_controller_mutation':True,
 'ATAX_prefix_exclusion_unchanged':True,'paper_master':'English v0.23 unchanged',
 'decisions':decisions,'source_layout_conditional_kmeans_shapes':shape,
 'streamcluster_sweep_call_counts':{str(k):math.floor(3*k*math.log(k)) for k in [6,20]},
 'cfd_expected_standard_launches':3+2000*(1+3+3),
 'evidence_files':['SOURCE_IDENTITY_EVIDENCE.json','SOURCE_EXCERPTS.json','UPSTREAM_SOURCE_VERIFICATION.json','INPUT_IDENTITY_CATALOG.json','CURRENT_READONLY_VERIFICATION.json','BOUNDED_DATASET_INVENTORY.json','HISTORICAL_REFERENCE_EVIDENCE.json'],
 'v2_policy_proposal':'An explicit release-command policy may prioritize 3.1 packaged run examples over 2.0-ft functional-regression inputs, provided capture scope is consistent. This is a recommendation, not an existing approved rule or a V1 freeze mutation.',
 'followups':[{'mode':'READ_ONLY','priority':1,'action':'Recover capture-time executable/build/tracer and any kernel-window limits for CFD and streamcluster; explain five-kernel scopes before whole-application claims.'},
  {'mode':'READ_ONLY','priority':2,'action':'Locate existing raw kmeans and NN dataset manifests/files; bind row/feature or ordered records and SHA to the actual captures, then recover convergence/completion logs.'},
  {'mode':'SCIENTIFIC_IDENTITY_POLICY_DECISION_REQUIRED','priority':3,'action':'Review a V2 source-release/run-command precedence policy for backprop, NW, pathfinder and NN; preserve old 35 identities and all 72 history rows.'},
  {'mode':'NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED','priority':4,'action':'Only if existing capture provenance cannot close: propose a separately approved capture/completeness validation. No recapture, new simulation or replay is launched by this report.'}]}
write('SEVEN_UNRESOLVED_ADJUDICATION_REPORT.json',report)

md = ['# 七项输入身份与完整性只读收敛报告（Agent F）','',
 '结论：V1 仍为 **35 项冻结、7 项 UNRESOLVED**，本轮没有新增冻结。21 份当前 kernelslist.g 的 SHA 全部与 V1 相符。四项可形成基于 Rodinia 3.1 发布 `run` 命令的 V2 条件建议；CFD、streamcluster 存在标准应用范围矛盾；kmeans 的输入内容和收敛范围仍缺证据。', '',
 '本报告不读取 cycles、加速比、模拟耗时或修复性能，也不按 PASS 选择。没有新模拟、捕获、trace 主体扫描或运行中任务改动。英文 v0.23、原 35 项及 ATAX 前缀排除证据保持不变。','',
 '| 程序 | V2 条件候选 | 本轮明确的范围判断 | 尚缺的关键证据 |','|---|---|---|---|']
labels={'backprop':'3.1 / 65536','cfd':'无','kmeans':'3.1 / kdd_cup（暂不可冻结）','nn':'3.1 / filelist_4 -r 5 -lat 30 -lng 90','nw':'3.1 / 2048 10','pathfinder':'3.1 / 100000 100 20','streamcluster':'无；10/20/256 仅命令候选'}
scope_labels={'backprop':'单次训练的两个 kernel 与源码一致','cfd':'5 个 kernel 缺 time_step，标准应为 14003 个','kmeans':'invert + 两次迭代；不能由数量判定收敛/截断','nn':'读入全部记录后一次 GPU 距离计算，top-N 在 CPU','nw':'255 次波前 launch 与源码公式一致','pathfinder':'5 次金字塔 launch 与源码公式一致','streamcluster':'5 次 launch 少于一次标准搜索 sweep 的 32/179 次'}
for d in decisions:md.append('| '+d['program']+' | '+labels[d['program']]+' | '+scope_labels[d['program']]+' | '+'；'.join(d['remaining_evidence'])+' |')
md += ['', '这里的 V2 候选是审阅建议，**不是已批准的版本优先级，也不是完整应用/数值正确性的认证**。仅“新版参数更大”不足以构成选择理由；建议依据是可核验的发布 run 命令、源码 parser 与捕获范围。', '',
 '## 最重要的新增发现','',
 '1. **streamcluster 也有范围阻断。** 已与固定上游 commit 核对一致的 `streamcluster_cuda_cpu.cpp` 中，`ITER=3`；每个实际进入的 pFL sweep 固定调用 `floor(3*kmax*ln(kmax))` 次 pgain。每次 pgain 无条件发一个 `kernel_compute_cost`。kmax=6/20 时分别为 32/179 次，现有两份只有 5 次。必须先找出 capture 二进制、ROI/窗口限制或提前退出证据。不能称为完整 streamcluster。', '',
 '2. **CFD 的缺口被再次锁定，不能靠本地源码差异解释。** 本地与上游的差异集中在 CUDA 错误检查包装，二者仍保持 2000 次外迭代、每次三阶段 RK。标准完整 launch 数为 `3+2000×(1+3+3)=14003`；当前 5 个 kernel 连第一次 time_step 都没有。193K 对应的 `193536` 仅是 padded nelr，真实 nel 和 mesh SHA 未与捕获绑定。', '',
 '3. **kmeans 同名数据集不是一维大小序列。** 按源码矩阵/成员/中心复制布局条件推导：', '',
 '| 捕获参数 | npoints（条件推导） | nfeatures（条件推导） | 原始输入内容 SHA |','|---|---:|---:|---|']
for s in shape:
    x = next(x for x in inputs if x['input_digest']==s['input_digest'])
    md.append(f"| {' '.join(x['parameters'])} | {s['source_layout_conditional_npoints']} | {s['source_layout_conditional_features']} | 未绑定 |")
md += ['', '这些维度由真实 commandlist 复制字节数和已读源码公式交叉约束；由于 capture 二进制尚未绑定，它们不是数据内容认证。`28k_4x_features` 的条件推导是 28672×138，不能直接按名字解释为任意其他输入的四倍。三个 3.1 输入都捕获两次 kmeansPoint：可能是两次收敛，也可能受捕获窗口影响，必须用已有 convergence/capture 日志判定。', '',
 '4. **NN 的 filelist_4 名字不构成同数据证据。** 3.1 HtoD 坐标缓存 342112 字节，在两个 float 的 LatLong 布局下对应 42764 条记录；2.0-ft 使用四批 735000 字节字符记录。3.1 的 `-r 5` 是 CPU top-N 返回数量，不传给 GPU euclid。历史 DTC_LEGACY_NN 三个 cohort 有精确 provenance 指针，但其 terminal-scope 状态不能冒充 42-suite 的整应用认证。', '',
 '5. **2.0-ft 和 3.1 不能当重复 capture 直接合并。** 2.0-ft 上游 README 明确其目的是缩小规模的功能回归，且版本内同参数的 format0/format3 捕获 SHA 不同。NW 还存在 kernel 参数签名差异。旧捕获全部保留；不根据哪个更快、成功或省时来选择。', '',
 '## 七项逐项证据与建议']
for d in decisions:
    md += ['', '### '+d['program'], '', '状态：`'+d['status']+'`；范围：`'+d['scope']+'`。', '']
    md += ['- '+t for t in d['new_findings']]
    md += ['', '建议：'+d['v2_proposal']['rule'], '', '仍缺：'+ '；'.join(d['remaining_evidence'])+'。', '', '源码位置：']
    for e in excerpts[d['program']]:
        md.append(f"- `{e['path']}:{e['lines'][0]}–{e['lines'][1]}`，SHA256 `{e['sha256']}`。")
    md += ['', '候选输入身份：']
    for x in [x for x in inputs if x['program']==d['program']]:
        cmdsha=next(z['sha256'] for z in x['source_members_sha256'] if z['relative_path']=='kernelslist.g')
        md.append(f"- `{x['input_digest']}`；bundle `{x['bundle_id']}`；`{x['trace_entry']}`；commandlist SHA `{cmdsha}`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。")
md += ['', '## 来源核验与未解决边界','',
 f'- 基准审阅 commit：`{BASELINE_COMMIT}`，目录 `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/`。',
 f'- 当前164冻结文件 `/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1/analysis/REPRESENTATIVE_FREEZE.json` 的 SHA256 仍为 `{FREEZE_SHA}`；local副本一致。',
 f'- 固定上游源码：`accel-sim/gpu-app-collection@{UPSTREAM_COMMIT}`；18份文件独立读取，16份与部署字节相同；另外2份为 CFD 的错误检查包装修改和 NN 的 emulation-only 内存分支。逐文件 URL、SHA、diff 见 `UPSTREAM_SOURCE_VERIFICATION.json`。',
 '- 112份小源码/命令文件约765KB；无仓库 Git 元数据，不能把部署目录整体冒充一个已验证 commit。已读具体文件均保留路径、SHA与内容；未比较的文件不宣称等价。',
 '- `get_data.sh` 指向的数据目录在本机指定位置不存在，5个官方2.0-ft capture目录的 data symlink均为历史服务器绝对路径且当前失效。这只是有界路径核查，不宣称数据在所有服务器上不存在；也没有下载、重构或重新采集输入。',
 '- 历史 M5 E1 表记载 097K candidate mesh SHA `43534e58454ba8baf95253e14d3b07150b9960577e922a954d6e51142a27abfa`，但其 executable/PTX/完整 capture 仍未绑定，故不用于绕过 CFD 范围阻断。',
 '- 每份 trace 的已声明 grid/warp 完整性与应用全部 host 迭代完整性是不同层次。已有 accepted、负例、修复、HOLD 身份均不作替换；本报告没有重新计算性能。', '',
 '## 后续最小动作','',
 '1. 只读恢复 CFD、streamcluster 的捕获二进制/源码/启动环境与 kernel 窗口参数，首先解释为何恰为5个kernel。',
 '2. 只读定位已有 kmeans/NN 原始数据及 manifest、收敛与捕获退出日志，按输入SHA和有序文件清单绑定，不用文件名替代内容。',
 '3. 审阅 V2 的“Rodinia3.1发布run优先于2.0-ft功能回归”统一身份规则；若采纳，backprop/NW/pathfinder/NN已有命令与范围依据。CFD、streamcluster仍不得因此晋升。',
 '4. 只有现有证据无法闭合时，另行提出 `NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED` 的捕获完整性验证合同；本轮不执行。', '',
 '分析代码 `build_identity_report.py` 只消费已有身份/源码/commandlist证据，不加载 PERFORMANCE.json、cycles、模拟耗时或strict结果来选择代表。']
(OUT/'SEVEN_UNRESOLVED_ADJUDICATION_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
assert sha(freeze_path.read_bytes()) == FREEZE_SHA
checks={'passed':True,'checks':['21 current commandlists match V1 SHA','local+164 V1 freeze SHA unchanged','all recovered historical run.sh text hashes match original receipts','18 pinned-source comparisons:16 exact,2 explicit diffs','21 inputs retained with full digests/bundles/member SHA','7 decisions remain UNRESOLVED and 35 identities unchanged','no performance/strict/runtime data used for representative selection','4 matrix/membership/center byte-count identities consistent','CFD standard launch formula14003','streamcluster sweep32/179 and5-kernel scope mismatch'],
 'generated_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
write('VALIDATION.json',checks)
manifest = {p.name:{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ['MANIFEST.json','ARCHIVE_RECEIPT.json']}
write('MANIFEST.json',{'schema':'DTC_AGENT_F_MANIFEST_V1','baseline_commit':BASELINE_COMMIT,'v1_freeze_sha256':FREEZE_SHA,'files':manifest})
print(json.dumps({'output':str(OUT),'decisions':len(decisions),'inputs':len(inputs),'files':len(manifest),'new_frozen':0,'validation':True},ensure_ascii=False))
