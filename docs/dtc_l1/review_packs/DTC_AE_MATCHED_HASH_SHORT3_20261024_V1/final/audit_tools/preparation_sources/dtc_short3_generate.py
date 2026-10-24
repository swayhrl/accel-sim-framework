import pathlib,json,hashlib,os,subprocess,ast
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');A=P('/root/data/dtc_main_20261023_v1/ae_fair_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
REQ='DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1'
ids=json.loads((T/'control/INPUT_IDENTITIES.json').read_text())
cells=[f'E2-AEF3-{w}-{c}' for w in ['NN','DWT2D','MRIQ'] for c in ['DM','DH','CM','CH']]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x):
 with P(p).open('x') as f:f.write(x)
def put(p,o):write(p,json.dumps(o,indent=2,ensure_ascii=False)+'\n')
native=(A/'tools/aefair_native.py').read_text().replace(str(A),str(T)).replace('DTC_AEFAIR_EPOCH2_V1',REQ)
native=native.replace("['E2-AEFAIR-CM','E2-AEFAIR-CH','E2-AEFAIR-DM','E2-AEFAIR-DH']",repr(cells))
native=native.replace("glob('E2-AEFAIR-*.INTENT.json')","glob('E2-AEF3-*.INTENT.json')")
native=native.replace('8*64*MIB','24*32*MIB').replace('all4 caps','all12 tightened caps')
native=native.replace("asset=original_native.current_assets(['DTC_AD_GEMM'])","asset=check_input(s)")
native=native.replace("dtc_guard=NativeDTCGuard(channel,{'proven_actual_root':True,'pid':n['pid'],'start_ticks':n['start_ticks'],'generation':ident,'input':env['DTC_AG7_INPUT_SHA'],'roi':env['DTC_AG7_ROI_SHA']},out,began_ns)","dtc_guard=NativeDTCGuard(channel,{'proven_actual_root':True,'pid':n['pid'],'start_ticks':n['start_ticks'],'generation':ident,'input':env['DTC_AG7_INPUT_SHA'],'roi':env['DTC_AG7_ROI_SHA']},out,began_ns);last_full=start-10")
native=native.replace("'AEFAIR_EXACT_UPDATE'","'AEFAIR_SHORT3_EXACT_UPDATE'")
native += '''
def check_input(s):
 p=ROOT/'control/INPUT_IDENTITIES.json'
 require(sha(p)==read(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['input_identities_sha256'],'input manifest changed')
 d=read(p)[s['workload']];a=d['asset']
 require(P(a['source_root']).resolve()==P(a['mount_tree']).resolve(),'trace compatibility path drift')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',a['mount_tree']],text=True))['filesystems'][0]
 require(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','genuine164 input mount changed')
 for r in d['members']:
  p=P(r['path']);st=p.stat();require([st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns]==r['identity'],'full-SHA-qualified input object changed')
  with p.open('rb') as f:require(bool(f.read(1)),'input unreadable')
 return {'status':'FULL_SHA_PREFLIGHT_BOUND_CURRENT_STAT_IDENTITY_PASS','asset_id':a['asset_id'],'members':len(d['members']),'input_manifest_sha256':sha(ROOT/'control/INPUT_IDENTITIES.json'),'full_SHA_repeated_during_prepare':False,'scientific_qualification':'PER_WORKLOAD_WHOLE_INPUT_STRICT_REQUIRED'}
'''
ast.parse(native);write(T/'tools/short3_native.py',native)
base=(A/'tools/aefair_result.py').read_text().replace(str(A),str(T)).replace('20261023_dtc_aefair_epoch2_results','20261024_dtc_aefair_short3_epoch2_results').replace("['E2-AEFAIR-CM','E2-AEFAIR-CH','E2-AEFAIR-DM','E2-AEFAIR-DH']",repr(cells))
write(T/'tools/short3_result_base.py',base)
gate=(A/'tools/aefair_result_gate_v2.py').read_text().replace(str(A),str(T)).replace('DTC_AEFAIR_EPOCH2_V1',REQ).replace("T/'prepared_outbox_revision2'","T/'control/release'").replace("T/'tools/aefair_result.py'","T/'tools/short3_result_base.py'")
write(T/'tools/short3_result.py',gate)
for name in ['RESULT_ENGINE_PIN.json','DTC_NATIVE_GUARD_CONTROL_TESTS.json']:(T/'control'/name).write_bytes((A/'control'/name).read_bytes())
baseopts=json.loads((N/'control/DTC_ORIGINAL_INPUT_RUNTIME_IDENTITY.json').read_text())['options']
specs=[]
for w,short in [('NN','NN'),('DWT2D','DWT2D'),('MRI-Q','MRIQ')]:
 d=ids[w]
 for c in ['DM','DH','CM','CH']:
  cell=f'E2-AEF3-{short}-{c}';s=json.loads((A/'control'/f'E2-AEFAIR-{c}_SPEC.json').read_text())
  oldconfigs=s['configs'];s.update(schema='DTC_AEFAIR_SHORT3_EXACT_CELL_SPEC_V1',cohort=cell,request=REQ,workload=w)
  folder=T/'DTC/env'/cell;folder.mkdir()
  conf=[]
  for i,row in enumerate(oldconfigs):
   p=folder/f'config-{i}.config';p.write_bytes(P(row['path']).read_bytes());conf.append({'path':str(p),'sha256':sha(p)})
  s['configs']=conf;s['native_simulator_argv']=[str(T/'DTC/bin/accel-sim.out'),'-trace',d['asset']['source_root']+'/'+d['asset']['entry_name']]
  for row in conf:s['native_simulator_argv']+=['-config',row['path']]
  s['limits'].update(max_result_directory_bytes=32*1024**2,timeout_seconds=21600)
  s['expected']={'instructions':d['expected_instructions'],'CTA':d['expected_CTA'],'kernels':d['expected_kernels']}
  s['original_environment']={'DTC_AG7_POLICY_B_PROGRESS':'1','DTC_AG7_INPUT_SHA':hashlib.sha256(json.dumps(d['members'],sort_keys=True).encode()).hexdigest(),'DTC_AG7_ROI_SHA':hashlib.sha256(json.dumps({'scope':'FULL_ORIGINAL_INPUT','commands':d['expected_commands'],'expected':s['expected']},sort_keys=True).encode()).hexdigest()}
  runtime=[]
  for row in s['runtime_files']:
   if '/config-' in row['target']:continue
   target=row['target'];p=T/target
   assert sha(p)==row['sha256']
   runtime.append({'target':target,'sha256':sha(p),'actual_realpath':str(p.resolve())})
  for row in conf:
   p=P(row['path']);runtime.append({'target':str(p.relative_to(T)),'sha256':row['sha256'],'actual_realpath':str(p.resolve())})
  s['runtime_files']=runtime
  opts=json.loads(json.dumps(baseopts))
  for row in conf:
   for line in P(row['path']).read_text().splitlines():
    line=line.split('#',1)[0].strip()
    if line.startswith('-'):
     key,*vals=line.split();opts[key]=vals
  assert len(opts)==270
  s['expected_options']=opts;s['input_identities_sha256']=sha(T/'control/INPUT_IDENTITIES.json')
  put(T/'control'/f'{cell}_SPEC.json',s);specs.append({'cohort':cell,'sha256':sha(T/'control'/f'{cell}_SPEC.json')})
auth={'schema':'DTC_AEFAIR_SHORT3_USER_AUTHORIZATION_V1','user_instruction':'我建议你先把一些短的workload的也同理跑一遍，另外我正在并行做多个测试集的workload整理，做完后应该都能跑。你先跑3个较小的整理下流程吧。','interpretation':'Exactly three short complete non-GEMM workloads, same four-config matched hash design, at most12 new native starts; no auto retry, no additional workload','prior_session_authorization':'DTC-MAIN sole resident lane;174-new epoch2 entry, true164 result archive, preserve old AG8R1 and historical ledgers','selected':['NN','DWT2D','MRI-Q'],'max_starts':12,'old_GEMM_request':'COMPLETE_UNCHANGED','paper_mother':'English v0.23 remains last user-confirmed mother; actual package unavailable','numerical_correctness_PPA':'UNPROVEN'}
put(T/'control/USER_GOAL_AUTHORIZATION.json',auth)
request={'schema':'DTC_AEFAIR_SHORT3_EXACT_REQUEST_V1','request_id':REQ,'specs':specs,'matrix_order':cells,'max_starts':12,'one_worker':True,'no_retry':True,'on_first_safety_or_strict_failure':'STOP_COHORT_SEAL_REMAINING','source':'174-new native only','inputs':list(ids),'input_identities_sha256':sha(T/'control/INPUT_IDENTITIES.json'),'native_output_root':str(T/'DTC/run/results'),'true164_archive_increment':'20261024_dtc_aefair_short3_epoch2_results','result_cap_per_cell_bytes':32*1024**2,'wall_per_cell_seconds':21600,'user_authorization_sha256':sha(T/'control/USER_GOAL_AUTHORIZATION.json'),'same_binary_and_config_bytes_as_completed_GEMM':True,'resource_reservation':'12 x32MiB results plus12 x32MiB independent restores plus256MiB spool =1GiB own, all reserved;7GiB floor+1GiB unknown+active registered peers','scope_limits':'Small fixed historical inputs, no inference of suite representativeness, native numerical correctness, hardware timing or PPA; cross-design geometry limits unchanged'}
put(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',request)
put(T/'control/SCIENCE_AUTHORIZATION.json',{'explicit_user_approval':True,'owner_bindings_ratified':True,'target_resource_policy_ratified':True,'approval_request_sha256':sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'budgets':{c:1 for c in cells},'basis':'User requested three short workloads same design;12 exact fresh native starts; prior target resource policy retained,32MiB cap tighter than64MiB.'})
q=json.loads((A/'control/REGISTRATION_CANDIDATE.json').read_text());q.update(request_id=REQ,budget=12,remaining=12,consumed={},state='ARMED',reserved_write_bytes=1024**3,spec_request_sha256=sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),spec_path=str(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),authorization_path=str(T/'control/USER_GOAL_AUTHORIZATION.json'),authorization_sha256=sha(T/'control/USER_GOAL_AUTHORIZATION.json'),controller_sha256=sha(T/'tools/short3_native.py'),scope='Twelve fresh whole-input cells:NN,DWT2D,MRI-Q each DM,DH,CM,CH; old GEMM and history preserved')
for row in q['shared_tool_pins']:assert sha(row['path'])==row['sha256']
put(T/'control/REGISTRATION_CANDIDATE.json',q)
print('EXACT_12_SPECS_PREPARED_ZERO_STARTS')
