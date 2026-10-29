"""Full pure parser tests on declared synthetic terminal fixtures, not workload performance.
No raw or trace body reused. Small accepted compact structure fields seed geometry.
"""
import pathlib,json,hashlib,importlib.util,copy,datetime,gzip,traceback
P=pathlib.Path;B=P(__file__).resolve().parent;H=B/'host_candidate'
def read(p):return json.loads(P(p).read_bytes())
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(P(p).read_bytes()).hexdigest())
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
mc=load('contract_full_cpu',H/'mode_contract.py');parser=load('parser_full_cpu',H/'mode_aware_terminal.py');hcontrol=read(B/'HOST_NATIVE_V2_ACTUAL_CONTROLS.json');root=P(hcontrol['sandbox_root']);base=read(root/'cases/EP_PERF_SANDBOX_W_ONLY_V2/control/FROZEN_SPEC.json');binding=read(base['input_binding_ref']['path']);reg=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');row=reg['registered_future_requests'][base['goal']]['consumed']['EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1'];bundle=read(row['validation_ref']['path']);_,numeric=parser.numeric_math();parse,_=parser.numeric_math();reasons=parse.__globals__['REASONS'];F=B/'synthetic_parser_fixtures';F.mkdir(exist_ok=True);results=[]
def wire(prefix,kind,row):
 return prefix+'|'+kind+'|'+ '|'.join(k+'='+(','.join(str(x)for x in v)if isinstance(v,list)else str(v))for k,v in row.items())+'\n'
def build(s):
 lines=['# TEST_ONLY_SYNTHETIC_TERMINAL_NOT_A_SIMULATION_OR_PERFORMANCE_RESULT\n','gpgpu-sim_git-commit-'+s['source_identity']['core_source_commit']+'\n','accelsim-commit-'+s['source_identity']['framework_source_commit']+'\n']
 lines += [k+' '+v+' # synthetic exact options\n'for k,v in s['expected_effective_options'].items()]
 for cmd in binding.get('expectedcommands',binding.get('all_commands')):
  lines.append(('Processing kernel /TEST_ONLY_SYNTHETIC/'+cmd if cmd.endswith('.traceg')else'launching memcpy command : '+cmd)+'\n')
 for k in s['expected_kernel_launches']:lines.append('launching kernel name: '+k['name']+' uid: '+str(k['uid'])+' cuda_stream_id: 0\n')
 lines += ['gpu_tot_sim_cycle = 100\n','gpu_tot_sim_insn = '+str(s['expected_instructions'])+'\n','gpu_tot_issued_cta = '+str(s['expected_CTA'])+'\n']
 for sid in range(64):
  summary=dict(slice=sid,mode=int(s['expected_effective_options']['-gpgpu_ep_l2_ft_mode']),observed_cycles=100,wbuf=16,physical_slots=1168,role_free=1168,role_resident=0,role_bypass=0,wb_slots=0,ownership_consistent=1,reserved=0,read_refs=0,wb_live=0,wb_created=0,wb_lower_accept=0,wb_completed=0)
  terminal=dict(slice=sid,requester_exact_once=1,hardware_drained=1,unique_requesters=0,responses=0,pending_lower_reads=0,pending_returns=0,pending_responses=0)
  invariant=dict(slice=sid,kernel_uid=(1<<64)-1,bank_pending=0,terminal_clean=1,resident_tag_payload_consistent=1,payload_double_owner=0,line_mshr_capacity=128,descriptor_capacity=512,descriptor_free=512,wad_capacity=128,descriptor_used=0,line_mshr_used=0,wad_live=0,resident_pending=0,bypass_live=0)
  obs=dict(slice=sid,enabled=1,sampled_cycles=100,unfinished_head=0,head_changes_without_admission=0,lower_reads=0,lower_read_bytes=0,lower_write_bytes=0,lower_wb_bytes=0,unclassified_refusal_observations=0)
  diag=dict(slice=sid,copy_free=0,l2_data_free=0,hardware_P1_throughput_eligible=1,physical_grants=0,logical_copy_reads=0,logical_copy_writes=0,**{'exempt_'+k:0 for k in parse.__globals__['EXEMPT']})
  for pref,kind,v in [('EPL2FTV1','SUMMARY',summary),('EPL2FTV1','TERMINAL',terminal),('EPL2B0V1','INVARIANT',invariant),('EPL2MSV1','OBSERVER',obs),('EPL2MSV1','LOCAL_DIAGNOSTIC',diag)]:lines.append(wire(pref,kind,v))
  for reason in range(len(reasons)):
   wait=dict(slice=sid,reason=reason,hist_log2=[0]*65,resolved=0,requests=0,observations=0,sum=0,max=0,unknown_while_unresolved=0)
   lines.append(wire('EPL2MSV1'if reason<15 else'EPL2MSV2','WAIT',wait))
  for kind,records in bundle['model']['structural_observations'].items():lines.append(wire('EPL2STRUCTV1',kind,records[str(sid)]))
  if s['mode']=='WV_ZERO_RO':
   lines.append(wire('EPL2TVDV2','SUMMARY',dict(slice=sid,mandatory=0,live=0,role_tvd=0,served_sector_bytes=0,served_sectors=0,dirty_forward_responses=0,read_responses=0)))
   lines.append(wire('EPL2TVDV3','METADATA_COST',dict(slice=sid,frontend_cam_ports=1,completion_cam_ports=1,directory_bound_wb_uid_bits=32,extra_packet_identity_bits=0,indexed_control_read_views=3,indexed_control_update_lanes=3,metadata_PPA='UNKNOWN',metadata_clock_closure='UNKNOWN')))
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
for mode in ['S','W_ONLY','WV_ZERO_RO']:
 s=copy.deepcopy(base);s['mode']=mode;s['T']=False;s['M']=False;s['expected_effective_options'].update(mc.flags(mode));q=dict(formal_mode=mode,mode_contract_ref=s['mode_contract_ref'],validation_module_ref=s['validation_module_ref'],mode_cpu_qualification_ref=s['mode_cpu_qualification_ref'],source_identity=s['source_identity']);p=F/(mode+'_TEST_ONLY_SYNTHETIC.log');p.write_text(build(s));fixtures[mode]=(s,q,p)
 value=check(mode+'_actual_full_pure_parser_positive_synthetic',lambda s=s,q=q,p=p:parser.validate_case(p,s,q,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']))
 check(mode+'_no_acceptance_permission',lambda:mc.need(value['scientific_acceptance_granted']is False,'parser accepted fixture'))
 check(mode+'_profile_preserved',lambda mode=mode:mc.need(value['formal_history_profile']==mc.MODES[mode][5],'relabelled mode'))
s,q,p=fixtures['W_ONLY'];original=p.read_text()
mutations=[('wrong_FT_mode',lambda x:x.replace('mode=2|observed_cycles','mode=1|observed_cycles'),'actual FT layout'),('missing_B0_invariant',lambda x:'\n'.join(l for l in x.split('\n')if not l.startswith('EPL2B0V1|INVARIANT|')),'FT/B0 terminal'),('live_descriptor',lambda x:x.replace('descriptor_used=0','descriptor_used=1'),'nonempty terminal'),('bank_P2',lambda x:x.replace('bank0=1','bank0=2'),'bank service'),('WB_not_drained',lambda x:x.replace('wb_live=0','wb_live=1'),'live FT transient'),('source_banner',lambda x:x.replace(s['source_identity']['core_source_commit'],'0'*40),'actual Source'),('config282',lambda x:x.replace('-dram_latency 100 #','-dram_latency 101 #'),'all282'),('extra_RO_population',lambda x:x+'EPL2ROV1|SUMMARY|slice=0|live=0\n','TVD/RO scope'),('optional_on_wire',lambda x:x+'EPL2LIFEV1|anything\n','fourOFF'),('truncated_exit',lambda x:x.replace('GPGPU-Sim: *** exit detected ***',''),'natural complete'),('MS_wait_wrong_hist',lambda x:x.replace('hist_log2='+','.join(['0']*65),'hist_log2=0'),'65bin'),('instruction_count',lambda x:x.replace('gpu_tot_sim_insn = '+str(s['expected_instructions']),'gpu_tot_sim_insn = 1'),'instruction/CTA')]
for name,fn,match in mutations:
 pp=F/('NEG_'+name+'.log');pp.write_text(fn(original));check('W_FULL_NEG_'+name,lambda pp=pp:parser.validate_case(pp,s,q,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']),True,match)
# Lossless gzip path must produce the same model counters as plain fixture; not NI evidence.
gz=F/'W_ONLY_TEST_ONLY_SYNTHETIC.log.gz'
with gzip.open(gz,'wb')as out:out.write(original.encode())
a=check('W_FULL_lossless_gzip_positive',lambda:parser.validate_case(gz,s,q,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']))
check('W_FULL_gzip_logical_census_equal',lambda:mc.need(a['raw_logical_sha256']==hashlib.sha256(original.encode()).hexdigest(),'gzip logical census'))
out=dict(schema='EP_W_ONLY_V2_FULL_PARSER_SYNTHETIC_CONTROLS',status='PASS_PURE_FULL_WRAPPER_SYNTHETIC_NOT_APPLICATION_ACCEPTANCE_OR_NI',count=len(results),controls=results,model_starts=0,Trace_raw_body_scans=0,fixture_provenance='synthesized zero-requester drained terminal + exact S Source/options/command metadata and small compact STRUCT/scoped row seed, with requested formal mode; no measured W_ONLY cycles',fixture_cycles='TEST_ONLY_SYNTHETIC_100_NOT_PERFORMANCE',small_bundle_seed_ref=row['validation_ref'] if False else reg['registered_future_requests'][base['goal']]['consumed']['EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1']['validation_ref'],new_parser_module_ref=ref(H/'mode_aware_terminal.py'),numeric_body_sha256=numeric['numeric_body_sha256'],frozen_final_suffix_sha256=numeric['frozen_final_suffix_sha256'],production_Source_changed=False,science_granted=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixtures=[dict(ref(p),TEST_ONLY=True)for p in F.iterdir()])
(B/'FULL_PARSER_SYNTHETIC_V2_ACTUAL_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],count=len(results))))
