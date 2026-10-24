import pathlib,json,importlib.util,csv,types,copy,ast,hashlib
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');A=P('/root/data/dtc_main_20261023_v1/ae_fair_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
read=lambda p:json.loads(P(p).read_bytes())
strict=load('new_strict',T/'tools/short3_strict.py');m=strict.legacy();tests=[]
audit=N/'DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/identity_metadata/KERNEL_BODY_AUDIT.tsv'
rows=[r for r in csv.DictReader(audit.open(),delimiter='\t') if r['workload'].lower()=='gemm']
d=read(N/'control/DTC_ORIGINAL_INPUT_RUNTIME_IDENTITY.json');d['rows']=rows;d['expected_kernels']=1
for c in ['DM','DH','CM','CH']:
 cohort='E2-AEFAIR-'+c;ss=read(A/'control'/(cohort+'_SPEC.json'));ss['expected_options']=read(P(read(A/'control/qualification_ledger'/(cohort+'.INTENT.json'))['output'])/'AEFAIR_STRICT.json')['effective_options']
 raw=P(read(A/'control/qualification_ledger'/(cohort+'.INTENT.json'))['output'])/'raw.log'
 x=strict.population(raw.read_text(),ss,d,m)
 assert x['cycles']=={'CM':1511333,'CH':1395216,'DM':1071405,'DH':826089}[c]
 tests.append({'test':'actual_completed_GEMM_'+c,'status':'PASS','cycles':x['cycles'],'new_models':0})
opts=ss['expected_options'];head='\n'.join(k+' '+' '.join(v)+' # fixture' for k,v in opts.items())+'\nperformance model initialization complete.\n'
def block(i,name,path,insn,total,cta):
 return f'Processing kernel {path}\nkernel_name = {name}\nDTC_L1_mode = PAPER_BASE\nkernel_launch_uid = {i}\ngpu_sim_insn = {insn}\ngpu_tot_sim_insn = {total}\ngpu_tot_issued_cta = {cta}\ngpu_sim_cycle = 100\ngpu_tot_sim_cycle = {100*i}\nDTC_L1_pib_occupancy = 0\nDTC_L1_lower_outstanding = 0\nDTC_L1_pib_admits = 2\nDTC_L1_pib_retires = 2\nDTC_L1_lower_requests_acquired = 1\nDTC_L1_lower_requests_released = 1\nDTC_L1_baseline_mshr_entries = 512\n'
fixture=head+block(1,'a','/synthetic/a.traceg',10,10,2)+block(2,'b','/synthetic/b.traceg',20,30,5)+'GPGPU-Sim: *** exit detected ***\nGPGPU-Sim: *** simulation thread exiting ***\n'
fs={'cell':'CM','expected_options':opts,'expected':{'instructions':30,'CTA':5,'kernels':2}}
fd={'rows':[{'kernel':'a','path':'/synthetic/a.traceg','active_thread_instructions':'10','complete_ctas':'2'},{'kernel':'b','path':'/synthetic/b.traceg','active_thread_instructions':'20','complete_ctas':'3'}],'expected_commands':['a.traceg','b.traceg'],'expected_instructions':30,'expected_CTA':5}
fm=types.SimpleNamespace(FORBIDDEN=m.FORBIDDEN,echo=m.echo,numeric=m.numeric,traffic=lambda x:{})
assert strict.population(fixture,fs,fd,fm)['kernel_count']==2;tests.append({'test':'synthetic_two_kernel_population','status':'PASS','scope':'Parser boundaries only, no traffic qualification or scientific result'})
mutations={'missing_kernel':fixture.replace('kernel_name = b','other_name = b'),'reordered_name':fixture.replace('kernel_name = a','kernel_name = b'),'wrong_UID':fixture.replace('kernel_launch_uid = 2','kernel_launch_uid = 3'),'wrong_cumulative_insn':fixture.replace('gpu_tot_sim_insn = 30','gpu_tot_sim_insn = 29'),'wrong_CTA':fixture.replace('gpu_tot_issued_cta = 5','gpu_tot_issued_cta = 4'),'undrained_PIB':fixture.replace('DTC_L1_pib_occupancy = 0','DTC_L1_pib_occupancy = 1'),'wrong_mode':fixture.replace('DTC_L1_mode = PAPER_BASE','DTC_L1_mode = PAPER_IO'),'missing_natural':fixture.replace('GPGPU-Sim: *** exit detected ***',''),'partial_insn':fixture.replace('gpu_sim_insn = 20','gpu_sim_insn = 19'),'AD_on':fixture+'DTC_PROGRESSIVE_WAKE_V1\n','conflicting_option':fixture+'-gpgpu_n_clusters 63 # mutation\n'}
for name,text in mutations.items():
 try:strict.population(text,fs,fd,fm)
 except (ValueError,RuntimeError):tests.append({'test':'reject_'+name,'status':'PASS_EXPECTED_REJECTION'})
 else:raise AssertionError('accepted mutation '+name)
native=load('new_native',T/'tools/short3_native.py');req=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');assert len(req['matrix_order'])==12
for c in req['matrix_order']:native.check_input(native.spec_for(c))
for w in ['NN','DWT2D','MRIQ']:
 ss={c:native.spec_for(f'E2-AEF3-{w}-{c}') for c in ['CM','CH','DM','DH']}
 for a,b,keys in [('CM','CH',{'-gpgpu_cache:dl1'}),('DM','DH',{'-gpgpu_dtc_l1_tag_hash_bankrow'})]:
  diff={k for k in ss[a]['expected_options'] if ss[a]['expected_options'][k]!=ss[b]['expected_options'][k]};assert diff==keys
 for c in ss:
  old=read(A/'control'/f'E2-AEFAIR-{c}_SPEC.json');assert [r['sha256'] for r in old['configs']]==[r['sha256'] for r in ss[c]['configs']]
tests.append({'test':'all12_spec_input_config_source_and_paired_options','status':'PASS','same_config_bytes_as_GEMM':True})
gate=load('new_gate',T/'tools/short3_result.py');own={'reserved_write_bytes':1024**3};reg={'registered_future_requests':{native.REQUEST:own,'active_peer':{'state':'RUNNING','reserved_write_bytes':123}}};assert gate.peer_basis(reg)['registered_peer_bytes']==123
for amount in [None,-1,'123']:
 reg['registered_future_requests']['active_peer']['reserved_write_bytes']=amount
 try:gate.peer_basis(reg)
 except RuntimeError:tests.append({'test':'reject_unknown_negative_or_string_peer_'+str(amount),'status':'PASS_EXPECTED_REJECTION'})
 else:raise AssertionError('peer accepted')
for p in (T/'tools').glob('*.py'):ast.parse(p.read_text())
r=native.resources(native.spec_for('E2-AEF3-NN-DM'));assert r['physical_RAM_pass'] and r['physical_disk_pass']
out={'schema':'DTC_SHORT3_ZERO_MODEL_QUALIFICATION_V1','status':'PASS_ZERO_MODEL_STARTS','tests':tests,'resources':r,'limits':'Synthetic fixtures are parser tests only; actual GEMM replay verifies real full scientific parser. New workloads require fresh exact terminal acceptance. No simulator build, constructor, canary, trace execution or model start during qualification.','tool_sha256':{p.name:sha(p) for p in sorted((T/'tools').glob('*.py'))}}
with (T/'control/QUALIFICATION.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'status':out['status'],'tests':len(tests),'resources':r},indent=2))
