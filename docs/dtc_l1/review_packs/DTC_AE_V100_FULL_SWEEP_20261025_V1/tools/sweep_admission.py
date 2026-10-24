"""Exact per-input spec producer within an immutable finite candidate request."""
import pathlib,json,hashlib,copy,math,importlib.util,os
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');GIB=1024**3;MIB=1024**2
REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def module(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put_once(p,x):
 data=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode();p=P(p)
 if p.exists():assert p.read_bytes()==data,'immutable admission file collision';return
 with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def grouped_candidates():
 grouped={}
 for r in read(T/'control/INTAKE_CANDIDATES.json')['inputs']:grouped.setdefault(r['input_digest'],[]).append(r)
 return grouped
def admit(input_digest,native):
 assert sha(__file__)==native.read_current_authority()[0]['registered_future_requests'][REQ]['spec_producer_sha256'],'unqualified spec producer change'
 group=grouped_candidates()[input_digest];r=group[0];qpath=T/'qualification'/input_digest/'QUALIFICATION.json'
 if not qpath.exists():return {'state':'PENDING_BODY_QUALIFICATION','input_digest':input_digest}
 d=read(qpath);issues=list(d.get('issues',[]));statuses=sorted({s for row in group for s in row['prior_scientific_statuses']})
 if d['status']!='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS':return {'state':'INPUT_HOLD','input_digest':input_digest,'reason':d['status'],'issues':issues,'error':d.get('error')}
 if any('HOLD_SHARED_TRACE_INTERPRETATION' in s or s=='SCIENTIFIC_HOLD_PRESERVED' for s in statuses):return {'state':'INPUT_HOLD','input_digest':input_digest,'reason':'PRIOR_EXACT_CONTENT_HOLD_PRESERVED','original_statuses':statuses}
 for row in d['rows']:
  for item in row.get('width_counts',[]):
   if item['opcode'].split('.')[0] in ['LDG','LDL'] and item['trace_width']!=item['parser_width']:issues.append({'reason':'CACHEABLE_WIDTH_METADATA_MISMATCH','kernel':row['ordinal'],'evidence':item})
 if issues:return {'state':'INPUT_HOLD','input_digest':input_digest,'reason':'CACHEABLE_MEMORY_DOMAIN_REVIEW','issues':issues}
 binding={'input_digest':input_digest,'aliases':group,'asset':r['asset'],'qualification':d,'qualification_source_sha256':sha(qpath),'body_parser_sha256':sha(T/'tools/body_audit_ratebound.py'),'current_source_scope':'Complete declared trace,not certification of native full application/numerical values;old scientific statuses are preserved','prior_scientific_statuses':statuses}
 bp=T/'control/input_bindings'/(input_digest+'.json');put_once(bp,binding)
 expected={'instructions':d['expected_instructions'],'CTA':d['expected_CTA'],'kernels':d['expected_kernels']}
 cap=512*MIB+d['expected_kernels']*256*1024+d['expected_CTA']*64;cap=math.ceil(cap/(16*MIB))*16*MIB
 assert cap<=8*GIB,'per-input native output cap requires resource review'
 candidates=sorted(grouped_candidates());idx=candidates.index(input_digest);cal=read(T/'control/HOST_CALIBRATION.json');cpus=cal['selected_model_CPUs']
 golden=read(T/'control/FOUR_ARM_GOLDEN_TEMPLATES.json');spec_hashes={};specs=[]
 for arm_index,c in enumerate(['DM','DH','CM','CH']):
  cell=f'E2-AEV100-{input_digest[:16]}-{c}';g=golden[c];s=copy.deepcopy(g['original_spec']);s.update(schema='DTC_AE_V100_FULL_SWEEP_CELL_SPEC_V1',cohort=cell,request=REQ,cell=c,workload=input_digest,input_digest=input_digest,program=r['program'],suite=r['suite'],input_binding_sha256=sha(bp),host_cpu=cpus[(idx*4+arm_index)%len(cpus)],expected=expected)
  conf=[]
  for i in range(4):
   p=T/'DTC/env'/c/f'config-{i}.config';conf.append({'path':str(p),'sha256':sha(p)})
  s['configs']=conf;s['native_simulator_argv']=[str(T/'DTC/bin/accel-sim.out'),'-trace',d['trace_entry']]
  for x in conf:s['native_simulator_argv']+=['-config',x['path']]
  s['limits'].update(max_result_directory_bytes=cap,timeout_seconds=90*24*3600)
  s['original_environment']={'DTC_AG7_POLICY_B_PROGRESS':'1','DTC_AG7_INPUT_SHA':input_digest,'DTC_AG7_ROI_SHA':hashlib.sha256(json.dumps({'commands':d['expected_commands'],'expected':expected,'scope':'COMPLETE_DECLARED_INPUT'},sort_keys=True).encode()).hexdigest()}
  runtime=[]
  for row in s['runtime_files']:
   if '/config-' in row['target']:continue
   p=T/row['target'];assert sha(p)==row['sha256'];runtime.append({'target':row['target'],'sha256':row['sha256'],'actual_realpath':str(p.resolve())})
  for row in conf:runtime.append({'target':str(P(row['path']).relative_to(T)),'sha256':row['sha256'],'actual_realpath':str(P(row['path']).resolve())})
  s['runtime_files']=runtime;s['expected_options']=copy.deepcopy(g['golden_effective_options']);s['expected_options']['-trace']=[d['trace_entry']]
  sp=T/'control'/(cell+'_SPEC.json');put_once(sp,s);spec_hashes[cell]=sha(sp);specs.append(s)
 def register(reg):
  q=reg['registered_future_requests'][REQ]
  for cell,h in spec_hashes.items():
   assert cell in q['candidate_cohorts'] and cell not in q['sealed']
   if cell in q['admitted_specs']:assert q['admitted_specs'][cell]==h
   else:assert cell not in q['consumed'];q['admitted_specs'][cell]=h
  q['admitted_inputs'][input_digest]={'binding_sha256':sha(bp),'specs':spec_hashes,'program':r['program'],'logical_bytes':r['asset']['logical_bytes'],'instructions':d['expected_instructions'],'kernels':d['expected_kernels'],'raw_result_cap_per_cell_bytes':cap}
 current=native.read_current_authority()[0]['registered_future_requests'][REQ]
 if not all(current['admitted_specs'].get(c)==h for c,h in spec_hashes.items()):native.update_authority(register)
 return {'state':'ADMITTED_FULL_INPUT','input_digest':input_digest,'program':r['program'],'cells':list(spec_hashes),'instructions':d['expected_instructions'],'kernels':d['expected_kernels'],'cap':cap,'alias_count':len(group)}
