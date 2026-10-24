from pathlib import Path
import json,gzip,hashlib,collections,csv,datetime
B=Path('/root/data/ep_l2_main_20261023_v1');P=B/'sm70_trace_statistics_20261024_v3';W=B/'worktree'
A=W/'docs/ep_l2/operations/ep_main_account_workload_audit_20261024_v2'
O=W/'docs/ep_l2/operations/ep_main_sm70_trace_statistics_20261024_v3';O.mkdir(exist_ok=True)
def read(p):return json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
def put(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
inputs=read(A/'EXACT_INPUT_INDEX.json.gz');coverage=read(A/'PROGRAM_COVERAGE.json')
headers={h:read(P/(h+'_headers.json.gz')) for h in ['174','174-new']}
maps={h:{r['key']:r for r in d['files']} for h,d in headers.items()}
assert all(r['exists'] and r['stable'] and r['metadata_matches_prior'] and r['binary_version']=='70' for d in headers.values() for r in d['files'])
assert all(all(isinstance(k,str) and k in maps[r['host']] for k in r['member_object_keys']) for r in inputs if r['complete_by_metadata'])
cuda=['BlackScholes','convolutionSeparable','fastWalshTransform','histogram','mergeSort','scalarProd','scan','sortingNetworks','transpose','vectorAdd']
rod=['b+tree','backprop','bfs','cfd','dwt2d','gaussian','heartwall','hotspot','hotspot3d','huffman','hybridsort','kmeans','lavamd','leukocyte','lud','mummergpu','myocyte','nn','nw','particlefilter','pathfinder','srad','streamcluster']
par=['bfs','cutcp','histo','lbm','mri-gridding','mri-q','sad','sgemm','spmv','stencil','tpacf']
poly=['2DCONV','2MM','3DCONV','3MM','ATAX','BICG','CORR','COVAR','FDTD-2D','GEMM','GESUMMV','GRAMSCHM','MVT','SYR2K','SYRK']
accept={'CUDA Samples':{'convolutionSeparable','fastWalshTransform','vectorAdd'},'Rodinia':{'cfd','dwt2d'},'Parboil':{'sad','sgemm'}}
hold={('CUDA Samples','scan'):'HOLD: extended/shared address semantics',('Rodinia','b+tree'):'HOLD: active mask/address record contract',('Parboil','spmv'):'HOLD: missing IADD3 source operand in legacy input'}
def family(s,p):
 if s=='Rodinia':
  if p.startswith('particlefilter'):return 'particlefilter'
  if p.startswith('srad'):return 'srad'
 return p
rows=[]
for su,programs in [('CUDA Samples',cuda),('Rodinia',rod),('Parboil',par),('PolyBench/GPU',poly)]:
 for pr in programs:
  relevant=[c for c in coverage if c['suite']==su and family(su,c['program'])==pr and (su!='Rodinia' or c['version']=='3.1')]
  r={'suite':su,'program':pr,'suite_version':'3.1' if su=='Rodinia' else 'GPU 1.0' if su=='PolyBench/GPU' else 'cudasdk/9.1 capture namespace' if su=='CUDA Samples' else '11-program suite','binary_version':'70' if any(c[h]['complete_path_count'] for c in relevant for h in ['174','174-new']) else 'NOT_OBSERVED','EP_history':'SOURCE_ACCEPTED_EXACT_INPUT_ONLY' if pr in accept.get(su,set()) else hold.get((su,pr),'NOT_ACCEPTED_IN_CURRENT_EP_ROSTER')}
  if su=='CUDA Samples' and pr=='vectorAdd':r['EP_history']='NATIVE_ACCEPTED_size4000000_ONLY'
  if su=='CUDA Samples' and pr=='fastWalshTransform':r['EP_history']='SOURCE_ACCEPTED_logK7_logD21_ONLY; logK11_logD19_LEGACY_BASELINE'
  for h in ['174','174-new']:
   regular=[c for c in relevant if c[h]['nonfraction_label_paths']]
   frac=[c for c in relevant if c[h]['fraction_label_paths']]
   r[h+'_state']='REGULAR_PATH_AVAILABLE' if regular else 'FRACTION_ONLY' if frac else 'NO_COMPLETE_EXPANDED_TRACE_FOUND'
   r[h+'_implementations']=[c['program'] for c in relevant if c[h]['complete_path_count']]
   r[h+'_example_entries']=[c[h]['example_entry'] for c in regular or frac]
  r['notes']=''
  if su=='Rodinia' and pr=='srad':r['notes']='3.1 v1 present; 3.1 v2 only commandlist placeholder; do not substitute 2.0-ft'
  if su=='Rodinia' and pr=='particlefilter':r['notes']='float and naive both present, counted as one family'
  if su=='CUDA Samples':r['notes']='10 captured programs are not the entire CUDA Samples source universe'
  rows.append(r)
summary={}
for su in ['CUDA Samples','Rodinia','Parboil','PolyBench/GPU']:
 rr=[r for r in rows if r['suite']==su]
 summary[su]={'enumerated_program_families':len(rr)}
 for h in ['174','174-new']:
  summary[su][h]={'regular':sum(r[h+'_state']=='REGULAR_PATH_AVAILABLE' for r in rr),'fraction_only':sum(r[h+'_state']=='FRACTION_ONLY' for r in rr),'no_expanded_trace':sum(r[h+'_state']=='NO_COMPLETE_EXPANDED_TRACE_FOUND' for r in rr)}
assert sum(s['174']['regular']+s['174']['fraction_only'] for s in summary.values())==53
assert sum(s['174']['regular'] for s in summary.values())==46
assert sum(s['174']['fraction_only'] for s in summary.values())==7
assert sum(s['174-new']['regular']+s['174-new']['fraction_only'] for s in summary.values())==27
put('PROGRAM_STATISTICS.json',rows);put('SUMMARY.json',summary)
with (O/'PROGRAM_STATISTICS.csv').open('w',newline='') as f:
 cols=['suite','program','suite_version','binary_version','174_state','174-new_state','EP_history','notes','174_example_entries','174-new_example_entries']
 wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader()
 for r in rows:wr.writerow({k:' | '.join(r[k]) if isinstance(r[k],list) else r[k] for k in cols})
dirs=read(A/'SUITE_DIRECTORY_METADATA.json.gz')
sdk=next(d for d in dirs['174'] if d['path'].endswith('/src/cuda/sdk/4.2'))
sdk_rows=[{'source_sample':n,'same_name_trace_found':n in cuda,'source_root':sdk['path'],'source_version':'4.2','capture_namespace_if_present':'cudasdk/9.1' if n in cuda else None,'is_cross_version_source_provenance_certified':False} for n in sorted(sdk['children'])]
assert len(sdk_rows)==73
put('CUDA_SDK42_SOURCE_CANDIDATES_NOT_CAPTURE_DENOMINATOR.json',sdk_rows)
legacy=[r for r in coverage if r['suite']=='Rodinia' and r['version']=='2.0-ft']
put('RODINIA_20FT_SEPARATE_STATISTICS.json',legacy)
proof={h:{'files':len(d['files']),'architecture_counts':d['architecture_counts'],'utc':d['utc'],'hostname':d['hostname'],'namespace':d['namespace'],'physical_prefix_bytes_read':sum(x['physical_prefix_bytes_read'] for x in d['files']),'decoded_prefix_bytes_read':sum(x['decoded_prefix_bytes'] for x in d['files']),'all_stable':True,'all_match_prior_metadata':True,'header_capture_sha256':hashlib.sha256((P/(h+'_headers.json.gz')).read_bytes()).hexdigest()} for h,d in headers.items()}
put('HEADER_VERIFICATION_SUMMARY.json',proof)
for h in headers:(O/(h+'_HEADERS.json.gz')).write_bytes((P/(h+'_headers.json.gz')).read_bytes())
for n in ['header_probe.py','build_statistics.py']:(O/n).write_bytes((P/n).read_bytes())
state={'REGULAR_PATH_AVAILABLE':'常规','FRACTION_ONLY':'仅裁剪','NO_COMPLETE_EXPANDED_TRACE_FOUND':'未找到'}
md=['# EP当前V100/SM70 trace资产全表（2026-10-24）','','当前EP最近正式运行加载V100/Volta基础及EP研究overlay。以下按既有四套资产逐程序家族统计；不是4080资产表，也不表示所有输入已通过EP模拟资格。','','本轮复用0bc1aa9f3bfb3cceccdea32af4af668037769027的双账户文件级清点，并新增逐成员header检查：原174 16,883个文件、174-new 8,641个文件，所有binary version均为70；无读取错误、无文件身份变化。只读取每文件至多2048B解码前缀，不解析指令正文、不重算整个trace SHA；压缩读取实际字节另记。两账户包含共享/重复视图，不相加为独立文件或存储占用。','','**已发现trace：53个suite内程序家族；46个有常规目录版本，7个仅裁剪。174-new目前可读取27个，其中18个常规、9个仅裁剪。** Rodinia3.1的ParticleFilter float/naive合计一个家族，两实现分别保留；与2.0-ft分开。','','“常规”仅表示存在成员齐备、路径未标记裁剪的版本，原始捕获是否完整仍需进一步来源/正文资格；“未找到”只针对已核查展开文件。大型tgz和tar.zst未展开，不能排除另含输入。','','## 总计','','| Suite | 统计口径 | 常规 | 仅裁剪 | 未找到 | 174-new有trace |','|---|---|---:|---:|---:|---:|']
for su,s in summary.items():md.append(f"| {su} | {'已知trace程序，完整SDK分母未冻结' if su=='CUDA Samples' else str(s['enumerated_program_families'])+'个程序家族'} | {s['174']['regular']} | {s['174']['fraction_only']} | {'不作全SDK缺口计数' if su=='CUDA Samples' else s['174']['no_expanded_trace']} | {s['174-new']['regular']+s['174-new']['fraction_only']} |")
for su in summary:
 md+=['',f'## {su}','','| 程序 | 原174 | 174-new | SM | EP历史/备注 |','|---|---|---|---|---|']
 for r in rows:
  if r['suite']!=su:continue
  st=r['EP_history'];note='待EP资格'
  if st.startswith('SOURCE_ACCEPTED'):note='指定旧输入已接受；其余输入不继承'
  if st.startswith('NATIVE_ACCEPTED'):note='Vector 4M原生已接受'
  if st.startswith('HOLD'):note=st
  if r['174_state']=='NO_COMPLETE_EXPANDED_TRACE_FOUND':note='源码/目录存在，未找到齐备展开trace'
  if r['notes'] and su=='Rodinia':note+='；'+r['notes']
  md.append(f"| {r['program']} | {state[r['174_state']]} | {state[r['174-new_state']]} | {'70' if r['binary_version']=='70' else '—'} | {note} |")
md+=['','## 版本、缺口和使用边界','','- CUDA：上表完整列出当前找到trace的10程序；不是完整CUDA Samples只有10程序。实际还存在SDK4.2的73个源码样例目录，其中63个未在本轮trace表找到同名程序；源码4.2与捕获路径9.1不可直接当成同一版本全集。73项另表列出，尚未建立逐项同源捕获关系。','- Rodinia3.1：23个程序家族中19个有trace；缺Heartwall、Huffman、Leukocyte、MUMmerGPU。SRAD已有v1，但v2缺齐备展开trace。ParticleFilter的float/naive两实现均有。','- Parboil：11程序中8个有常规版本，MRI-Gridding仅裁剪；LBM、TPACF未找到齐备展开trace。109新采的SM89 SpMV small不混入此SM70表。','- PolyBench/GPU1.0：15程序全部有SM70 trace；2MM、CORR、COVAR、FDTD-2D、GRAMSCHM、SYR2K当前仅找到裁剪版本。174-new缺3DCONV、MVT的展开输入；其3MM/SYRK只发现裁剪版本。','','## Rodinia2.0-ft另存资产','','174-new另有11个SM70输入：Backprop、BFS、Heartwall、Hotspot、Kmeans、LUD、NN、NW、Pathfinder、SRAD v2、Streamcluster。它们是另外一个版本，不用于填补Rodinia3.1的缺口，也不重复加进53个程序家族。','','## 输入、路径与接受边界','','- 每个程序的双账户绝对入口见PROGRAM_STATISTICS.csv/JSON；所有候选输入尺寸、参数、kernel数和成员元数据仍以父级[完整账户清点](../ep_main_account_workload_audit_20261024_v2/ACCOUNT_WORKLOAD_AUDIT.md)的EXACT_INPUT_INDEX.json.gz为准。路径副本、S/F与多个runtime不重复计程序。','- 旧接受的7程序是Vector、Conv、FWT_7_21、CFD、DWT、SAD及独立SGEMM，限其精确输入和runtime；原MAIN6/7保持。Scan、B+Tree、旧Parboil SpMV仍HOLD。','- 只有Vector的指定4M输入有EP native完整应用证据。当前文件已迁入/可读不等于资格或启动授权。','- 全部核查只读；模拟、编译、采集、输入搬运和科研账本改写均为0。','','## CUDA SDK4.2源码候选附表','','以下仅为73个源码目录的完整名称对照；不把它作为捕获包9.1的覆盖率分母。','','| 源码样例 | 本轮找到同名trace |','|---|---|']
for r in sdk_rows:md.append(f"| {r['source_sample']} | {'有；同源版本未认证' if r['same_name_trace_found'] else '未找到'} |")
(O/'SM70_TRACE_STATISTICS.md').write_text('\n'.join(md)+'\n')
put('VALIDATION.json',{'status':'PASS_ALL_MEMBER_HEADERS_AND_FAMILY_TOTALS','input_index_source_commit':'0bc1aa9f3bfb3cceccdea32af4af668037769027','member_observations':25524,'all_binary_version_70':True,'all_prior_file_identities_match':True,'trace_program_families':53,'regular_program_families':46,'fraction_only_program_families':7,'native_visible_program_families':27,'trace_full_content_sha_verified':False,'workload_or_simulator_invocations':0,'trace_payload_copy_bytes':0,'science_registry_writes':0})
put('DELIVERY_SHA256.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.iterdir()) if p.is_file() and p.name!='DELIVERY_SHA256.json'})
print(json.dumps({'rows':len(rows),'source_sdk_candidates':len(sdk_rows),'summary':summary,'delivery_bytes':sum(p.stat().st_size for p in O.iterdir())}))
