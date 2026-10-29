"""Full pure parser tests on declared synthetic terminal fixtures, not workload performance.
No raw or trace body reused. Small accepted compact structure fields seed geometry.
"""
import pathlib,json,hashlib,importlib.util,copy,datetime,gzip,traceback
P=pathlib.Path;B=P(__file__).resolve().parent;H=B/'host_candidate'
def read(p):return json.loads(P(p).read_bytes())
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(P(p).read_bytes()).hexdigest())
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
mc=load('contract_full_cpu',H/'mode_contract.py');parser=load('parser_full_cpu',H/'mode_aware_terminal.py');hcontrol=read(B/'HOST_NATIVE_T3_ACTUAL_CONTROLS.json');root=P(hcontrol['sandbox_root']);base=read(root/'cases/EP_PERF_SANDBOX_CORRECTED_F_V2/control/FROZEN_SPEC.json');binding=read(base['input_binding_ref']['path']);seed=read(B/'COMPACT_TERMINAL_METADATA_SEED.json');bundle={'model':{'structural_observations':seed['structure']},'application':{'application_scopes':seed['application_scopes']}};_,numeric=parser.numeric_math();parse,_=parser.numeric_math();reasons=parse.__globals__['REASONS'];F=B/'synthetic_parser_fixtures';F.mkdir(exist_ok=True);results=[]
def wire(prefix,kind,row):
 return prefix+'|'+kind+'|'+ '|'.join(k+'='+(','.join(str(x)for x in v)if isinstance(v,list)else str(v))for k,v in row.items())+'\n'
def build(s):
 lines=['# TEST_ONLY_SYNTHETIC_TERMINAL_NOT_A_SIMULATION_OR_PERFORMANCE_RESULT\n','gpgpu-sim_git-commit-'+s['source_identity']['core_source_commit']+'\n','accelsim-commit-'+s['source_identity']['framework_source_commit']+'\n']
 lines += [k+' '+v+' # synthetic exact options\n'for k,v in s['expected_effective_options'].items()]
 for cmd in binding.get('expectedcommands',binding.get('all_commands')):
  lines.append(('Processing kernel /TEST_ONLY_SYNTHETIC/'+cmd if cmd.endswith('.traceg')else'launching memcpy command : '+cmd)+'\n')
 for k in s['expected_kernel_launches']:lines.append('launching kernel name: '+k['name']+' uid: '+str(k['uid'])+' cuda_stream_id: 0\n')
 lines += ['EPL2ROV1|COMMANDLIST_BEGIN|commands='+str(len(binding.get('expectedcommands',binding.get('all_commands'))))+'\n','gpu_tot_sim_cycle = 99\n']+[wire('EPL2STRUCTV1',kind,records[str(sid)])for sid in range(64)for kind,records in bundle['model']['structural_observations'].items()]+['EPL2ROV1|COMMANDLIST_END|complete=1|commands='+str(len(binding.get('expectedcommands',binding.get('all_commands'))))+'\n','gpu_tot_sim_cycle = 100\n','gpu_tot_sim_insn = '+str(s['expected_instructions'])+'\n','gpu_tot_issued_cta = '+str(s['expected_CTA'])+'\n']
 for sid in range(64):
  summary=dict(slice=sid,mode=int(s['expected_effective_options']['-gpgpu_ep_l2_ft_mode']),observed_cycles=100,descriptor_responses=0,wbuf=16,physical_slots=1168,role_free=1168,role_resident=0,role_bypass=0,wb_slots=0,ownership_consistent=1,reserved=0,read_refs=0,wb_live=0,wb_created=0,wb_lower_accept=0,wb_completed=0)
  terminal=dict(slice=sid,requester_exact_once=1,hardware_drained=1,unique_requesters=0,responses=0,pending_lower_reads=0,pending_returns=0,pending_responses=0)
  invariant=dict(slice=sid,kernel_uid=(1<<64)-1,bank_pending=0,terminal_clean=1,resident_tag_payload_consistent=1,payload_double_owner=0,line_mshr_capacity=128,descriptor_capacity=512,descriptor_free=512,wad_capacity=128,descriptor_used=0,line_mshr_used=0,wad_live=0,resident_pending=0,bypass_live=0)
  obs=dict(slice=sid,enabled=1,sampled_cycles=100,unfinished_head=0,head_changes_without_admission=0,lower_reads=0,lower_read_bytes=0,lower_write_bytes=0,lower_wb_bytes=0,unclassified_refusal_observations=0)
  diag=dict(slice=sid,copy_free=0,l2_data_free=0,hardware_P1_throughput_eligible=1,physical_grants=0,logical_copy_reads=0,logical_copy_writes=0,**{'exempt_'+k:0 for k in parse.__globals__['EXEMPT']})
  for pref,kind,v in [('EPL2FTV1','SUMMARY',summary),('EPL2FTV1','TERMINAL',terminal),('EPL2B0V1','INVARIANT',invariant),('EPL2MSV1','OBSERVER',obs),('EPL2MSV1','LOCAL_DIAGNOSTIC',diag)]:lines.append(wire(pref,kind,v))
  for reason in range(len(reasons)):
   wait=dict(slice=sid,reason=reason,hist_log2=[0]*65,resolved=0,requests=0,observations=0,sum=0,max=0,unknown_while_unresolved=0)
   lines.append(wire('EPL2MSV1'if reason<15 else'EPL2MSV2','WAIT',wait))
  for kind,records in bundle['model']['structural_observations'].items():lines.append(wire('EPL2STRUCTV1',kind,records[str(sid)]))
  if True:
   lines.append(wire('EPL2TVDV2','SUMMARY',dict(slice=sid,mandatory=0,live=0,role_tvd=0,served_sector_bytes=0,served_sectors=0,dirty_forward_responses=0,read_responses=0)))
   lines.append(wire('EPL2TVDV3','METADATA_COST',dict(slice=sid,frontend_cam_ports=1,completion_cam_ports=1,directory_bound_wb_uid_bits=32,extra_packet_identity_bits=0,indexed_control_read_views=3,indexed_control_update_lanes=3,metadata_PPA='UNKNOWN',metadata_clock_closure='UNKNOWN')))
  # Entirely synthetic drained zero-RO population, not copied performance counters.
  rs=dict(slice=sid,live=0,accepted_global_reads=0,accepted_oracle_candidates=0,accepted_ro=0,transactions=0,merges=0,responses=0,lower_sectors=0,concurrent_duplicate_sectors=0,detached=0,detach=int(s['T']),bypass=1,manifest=s['expected_effective_options']['-gpgpu_ep_l2_ro_manifest_sha256'],scope='TRACE_MODEL_CLOSED_WORLD')
  close=dict(slice=sid,ro_live=0,shared_descriptor_used=0,shared_line_used=0,epoch_closed=1,ro_descriptor_responses=0,native_descriptor_responses=0,scope='NATIVE_AND_RO_DISTINCT_SUBCOUNTERS_NOT_ALL_FRONTEND_REQUESTS')
  resource=dict(slice=sid,shared_descriptor_capacity=512,payload_capacity=1168,line_capacity=128,query_ports_per_slice=1,query_latency_gpu_cycles=1,peak_shared_descriptors=0,peak_shared_lines=0,peak_transactions=0,lower_read_bytes=0,concurrent_duplicate_read_bytes=0,query_count=0,query_wait_cycles=0,query_port_wait_attempts=0,oracle='TRACE_MODEL_CLOSED_WORLD')
  conc=dict(slice=sid,completed_ro_requesters=0,scope='RO_ISSUED_NOT_RETURNED_PER_SLICE',measurement='OBSERVER_ONLY_NO_ADMISSION_LOOKUP',epoch_begin_gpu_cycle=0,epoch_end_gpu_cycle=100,last_response_gpu_cycle=0,peak_lower_transactions=0,peak_independent_lower_lines=0)
  for pref,kind,v in [('EPL2ROV1','SUMMARY',rs),('EPL2ROC1','CLOSURE',close),('EPL2ROC1','RESOURCE',resource),('EPL2ROC1','LOWER_CONCURRENCY',conc)]:lines.append(wire(pref,kind,v))
  lines.append(wire('EPL2P1V2','SET_ELIGIBILITY_QUERY',dict(slice=sid,enabled=int(s['ordinary_ro_tag_relief']),T=int(s['T']),issued=0,paid_wait_gpu_cycles=0,port_wait_attempts=0,query_ports_per_slice=1,query_latency_gpu_cycles=1,population='ordinary_raw_full_frontend_head',shared_with='RO_frontend_query',physical_timing_and_PPA='UNKNOWN')))
  for reason in ['TAG_SET_ALL_PENDING','LINE_MSHR_FULL','SHARED_DESCRIPTOR_FULL','PER_ADDRESS_FULL']:
   lines.append(wire('EPL2ROC1','WAIT',dict(slice=sid,reason=reason,scope='SLICE_FRONTEND_HEAD_NONEXCLUSIVE_WAIT',pending_head=0,hist_log2=[0]*16,unique_head_requests=0)))
 for pref,rows in bundle['application']['application_scopes'].items():
  for row in rows.values():
   row=dict(row)
   if 'completion_cycle'in row:row['completion_cycle']='100'
   lines.append(pref+'|'+'|'.join(k+'='+str(v)for k,v in sorted(row.items(),key=lambda kv:0 if kv[0]=='scope'else 1))+'\n')
 lines.append('GPGPU-Sim: *** exit detected ***\n');return ''.join(lines)
def check(name,fn,reject=False,match=None):
 try:v=fn();ok=not reject;err=None
 except Exception as e:v=None;err=type(e).__name__+':'+str(e);ok=reject and(match is None or match in err)
 results.append(dict(label=name,PASS=ok,error=err,expected='REJECT'if reject else'PASS'))
 if not ok:raise AssertionError(results[-1])
 return v
fixtures={}
for mode in ['F_MINUS_T','LEGACY_F','CORRECTED_F']:
 s=copy.deepcopy(base);s['mode']=mode;s['T']=mode!='F_MINUS_T';s['M']=True;s['ordinary_ro_tag_relief']=mode=='CORRECTED_F';s['cohort']='EP_PERF_SANDBOX_'+mode+'_V2';s['expected_effective_options'].update(mc.flags(mode));q=dict(formal_mode=mode,mode_contract_ref=s['mode_contract_ref'],validation_module_ref=s['validation_module_ref'],mode_cpu_qualification_ref=s['mode_cpu_qualification_ref'],source_identity=s['source_identity']);p=F/(mode+'_TEST_ONLY_SYNTHETIC.log');p.write_text(build(s));fixtures[mode]=(s,q,p)
 value=check(mode+'_actual_full_pure_parser_positive_synthetic',lambda s=s,q=q,p=p:parser.validate_case(p,s,q,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']))
 check(mode+'_no_acceptance_permission',lambda:mc.need(value['scientific_acceptance_granted']is False,'parser accepted fixture'))
 check(mode+'_profile_preserved',lambda mode=mode:mc.need(value['formal_history_profile']==mc.MODES[mode][5],'relabelled mode'))
# P1 cost model emitted in all M1 arms: full presence/flag/port/subset controls.
s,q,p=fixtures['CORRECTED_F'];original=p.read_text()
for name,transform,msg in [
 ('missing_P1',lambda t:'\n'.join(l for l in t.split('\n')if not l.startswith('EPL2P1V2|')),'exact64 final P1'),
 ('P1_wrong_mode',lambda t:t.replace('enabled=1|T=1|issued','enabled=0|T=1|issued'),'P1 actualmode'),
 ('P1_free_latency',lambda t:t.replace('query_latency_gpu_cycles=1|population','query_latency_gpu_cycles=0|population'),'P1 port/latency'),
 ('P1_excess_sharedsubset',lambda t:t.replace('T=1|issued=0','T=1|issued=1'),'ordinarysubset'),
 ('RO_wrong_T',lambda t:t.replace('detach=1|bypass=1','detach=0|bypass=1'),'RO actual T/M'),
 ('missing_correction_option',lambda t:'\n'.join(l for l in t.split('\n')if not l.startswith('-gpgpu_ep_l2_ordinary_ro_tag_relief ')),'all283'),
 ('correction_option_mismatch',lambda t:t.replace('-gpgpu_ep_l2_ordinary_ro_tag_relief 1 #','-gpgpu_ep_l2_ordinary_ro_tag_relief 0 #'),'all283')]:
 pp=F/('NEG_T3_'+name+'.log');pp.write_text(transform(original));check('T3_'+name,lambda pp=pp:parser.validate_case(pp,s,q,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']),True,msg)
# SameSource ON counterparts are parser controls, not applicationNI.
for mode in mc.MODES:
 s0,q0,p0=fixtures[mode];so=copy.deepcopy(s0);so['observer_profile']='T3_DIAG_ON';so['observer_env'].update(EPL2_DETACH_DIAG='1',EPL2_TAGPRESSURE_DIAG='1');matrix=mc.exact(so['three_arm_matrix_ref'])
 for row in matrix['arms'].values():row['observer_env']=so['observer_env']
 mp=F/('TEST_ONLY_ON_MATRIX_'+mode+'.json');mp.write_text(json.dumps(matrix,sort_keys=True,indent=2)+'\n');so['three_arm_matrix_ref']=ref(mp)
 rows=[]
 for sid in list(range(64))+[64]:
  row=dict(record='SLICE'if sid<64 else'GLOBAL',schema_id='EPL2_TAGPRESSURE_GEOMETRY_V2_CANDIDATE',schema_sha256='e9869eddb1c5d7c497f45f4cd19e08ba3b687fbd843704d8debf09bc042147b6',source_base_core='9243f769620653f2a9d4df5599e9581e9dae6067',slice=sid,cycle=100,sets=16,assoc=8,T=so['T'],M=True,ro_runtime=True,epoch_closed=True,overflow_invalid=False,output_invalid=False,closure_ok=True,counters=dict(observed_heads=0,covered=0,probe_skipped=0,ro_observed=0,ro_na=0),histograms={k:[]for k in ['heads_raw_reserved','heads_raw_reserved_eligible','heads_raw_reserved_reasonmask','ways_raw_reserved_predmask','ways_raw_reserved_class','heads_raw_reserved_invalid']},route_joint=[]);rows.append('EPL2TAGPRESSUREV1|'+json.dumps(row)+'\n')
 rows.append('EPL2DETACH_DIAG_V1|'+json.dumps(dict(record='GLOBAL',slice=64,cycle=100,overflow_invalid=False,output_invalid=False,closure_ok=True,epoch_closed=True))+'\n')
 text=build(so)+''.join(rows);on=F/('ON_'+mode+'_TEST_ONLY.log');on.write_text(text);check('T3_ON_full_parser_'+mode,lambda so=so,q0=q0,on=on:parser.validate_case(on,so,q0,so['source_qualification_ref']['path'],so['source_qualification_ref']['sha256']))
 if mode=='CORRECTED_F':
  for name,fn,msg in [('TP_invalid',lambda t:t+'EPL2TAGPRESSUREV1|'+json.dumps(dict(record='OUTPUT_INVALID'))+'\n','TP OUTPUT_INVALID'),('TP_overflow',lambda t:t.replace('"overflow_invalid": false','"overflow_invalid": true'),'TP invalid/overflow'),('TP_closurefalse',lambda t:t.replace('"closure_ok": true','"closure_ok": false'),'TP invalid/overflow'),('TP_wrong_schema',lambda t:t.replace('e9869eddb1c5d7c497f45f4cd19e08ba3b687fbd843704d8debf09bc042147b6','0'*64),'geometry schemaSHA'),('TP_wrong_geometry',lambda t:t.replace('"sets": 16','"sets": 32'),'TP16x8'),('TP_false_counter_closure',lambda t:t.replace('"covered": 0','"covered": 1'),'TP observed/covered')]:
   bad=F/(name+'_TEST_ONLY.log');bad.write_text(fn(text));check(name,lambda bad=bad,so=so,q0=q0:parser.validate_case(bad,so,q0,so['source_qualification_ref']['path'],so['source_qualification_ref']['sha256']),True,msg)
s,q,p=fixtures['CORRECTED_F'];original=p.read_text()

mutations=[('wrong_FT_mode',lambda x:x.replace('mode=2|observed_cycles','mode=1|observed_cycles'),'actual FT layout'),('missing_B0_invariant',lambda x:'\n'.join(l for l in x.split('\n')if not l.startswith('EPL2B0V1|INVARIANT|')),'FT/B0 terminal'),('live_descriptor',lambda x:x.replace('descriptor_used=0','descriptor_used=1'),'not drained'),('bank_P2',lambda x:x.replace('bank0=1','bank0=2'),'bank service'),('WB_not_drained',lambda x:x.replace('wb_live=0','wb_live=1'),'live FT transient'),('source_banner',lambda x:x.replace(s['source_identity']['core_source_commit'],'0'*40),'actual Source'),('config283',lambda x:x.replace('-dram_latency 100 #','-dram_latency 101 #'),'all283'),('extra_RO_population',lambda x:x+'EPL2ROV1|SUMMARY|slice=0|live=0\n','conflicting physical terminal'),('optional_on_wire',lambda x:x+'EPL2LIFEV1|anything\n','fourOFF'),('truncated_exit',lambda x:x.replace('GPGPU-Sim: *** exit detected ***',''),'natural complete'),('MS_wait_wrong_hist',lambda x:x.replace('hist_log2='+','.join(['0']*65),'hist_log2=0'),'65bin'),('instruction_count',lambda x:x.replace('gpu_tot_sim_insn = '+str(s['expected_instructions']),'gpu_tot_sim_insn = 1'),'instruction/CTA')]
for name,fn,match in mutations:
 pp=F/('NEG_'+name+'.log');pp.write_text(fn(original));check('W_FULL_NEG_'+name,lambda pp=pp:parser.validate_case(pp,s,q,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']),True,match)
# Lossless gzip path must produce the same model counters as plain fixture; not NI evidence.
gz=F/'W_ONLY_TEST_ONLY_SYNTHETIC.log.gz'
with gzip.open(gz,'wb')as out:out.write(original.encode())
a=check('W_FULL_lossless_gzip_positive',lambda:parser.validate_case(gz,s,q,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']))
check('W_FULL_gzip_logical_census_equal',lambda:mc.need(a['raw_logical_sha256']==hashlib.sha256(original.encode()).hexdigest(),'gzip logical census'))
out=dict(schema='EP_T3_NEW_SOURCE_FULL_PARSER_SYNTHETIC_CONTROLS',status='PASS_PURE_FULL_WRAPPER_SYNTHETIC_NOT_APPLICATION_ACCEPTANCE_OR_NI',count=len(results),controls=results,model_starts=0,Trace_raw_body_scans=0,fixture_provenance='synthesized zero-requester drained terminal + exact S Source/options/command metadata and small compact STRUCT/scoped row seed, with requested formal mode; no measured W_ONLY cycles',fixture_cycles='TEST_ONLY_SYNTHETIC_100_NOT_PERFORMANCE',small_bundle_seed_ref=seed['source_ref'],new_parser_module_ref=ref(H/'mode_aware_terminal.py'),numeric_body_sha256=numeric['numeric_body_sha256'],frozen_final_suffix_sha256=numeric['frozen_final_suffix_sha256'],production_Source_changed=False,science_granted=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixtures=[dict(ref(p),TEST_ONLY=True)for p in F.iterdir()])
(B/'FULL_PARSER_T3_ACTUAL_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],count=len(results))))
