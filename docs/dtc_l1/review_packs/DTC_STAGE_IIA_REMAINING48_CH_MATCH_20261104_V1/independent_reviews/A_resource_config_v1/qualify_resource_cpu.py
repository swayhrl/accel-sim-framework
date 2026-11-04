from pathlib import Path
import importlib.util,json,copy,tempfile,math,hashlib,os,time,sys
sys.dont_write_bytecode=True
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/agents/A_resource_config_v1');S=O/'stage2_resources.py';s=importlib.util.spec_from_file_location('remaining48_resource_CPU',S);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);G=m.G;M=m.M;p=m.policy(json.loads((O/'RESOURCE_POLICY.candidate.json').read_text()));checks=[]
def ck(n,v):assert v,n;checks.append(n)
sample=dict(utc='CPU_ONLY',monotonic=100.,host_MemAvailable_bytes=220*G,cgroup_effective_headroom_bytes=220*G,native_free_bytes=20*G,free_inodes=200000,archive_free_bytes=40*1024*G,true164_mount_verified=True,cpu_allowed=list(range(8)),cpu_topology=[dict(cpu=i,node=0,core=i,socket=0)for i in range(8)],cpu_quota_equivalent=8,observed_models=[],observed_affinity_claims=[],cpu_ticks={},host_pswpout_pages=0,host_oom_kill_count=1,cgroup_swap_current_bytes=0,cgroup_memory_events=dict(oom=0,oom_kill=0,max=0))
b=dict(required_free_bytes=40*G,peer_reservations=[dict(request=m.STAGE1_REQ,reserved_write_bytes=24*G),dict(request=m.FIRST16_REQ,reserved_write_bytes=int(2.5*G)),dict(request=m.REQ,reserved_write_bytes=9*G),dict(request='OTHER',reserved_write_bytes=G)],reserved_additional_live_and_candidate_RAM_bytes=G,per_scope_write_ceiling_pass={'ORIG':True},known_remaining_writes_by_request={'ORIG':G});peers={m.STAGE1_REQ:dict(projected_write_bytes=G,additional_RAM_bytes=G,projection_within_registered_ceiling=True),m.FIRST16_REQ:dict(projected_write_bytes=0,additional_RAM_bytes=0,projection_within_registered_ceiling=True)};own=dict(projected_write_bytes=G,actual_unarchived_output_bytes=M,additional_RAM_bytes=4*G,projection_within_registered_ceiling=True,ram=[],writes=[]);q=dict(reserved_write_bytes=9*G);sp=dict(cohort='CPU_ONLY',workload='a',input_digest='a',estimated_peak_model_RAM_bytes=G,limits=dict(max_process_tree_rss_bytes=8*G,max_result_directory_bytes=64*M),historical_elapsed_seconds=100)
x=m._evaluate(sp,True,sample,None,b,peers,own,q,p);ck('replace3_exact_named_peers_not_other',x['required_free_bytes']==int(6.5*G));ck('other_peer_preserved',x['other_peer_reservations']==[dict(request='OTHER',reserved_write_bytes=G)])
for name,kw in [('hostfloor',dict(host_MemAvailable_bytes=7*G)),('cgfloor',dict(cgroup_effective_headroom_bytes=7*G)),('hostmem',dict(host_memory_pressure={'full':{'avg10':.75}})),('cgmem',dict(memory_pressure={'some':{'avg10':3.}})),('hostIO',dict(host_io_pressure={'full':{'avg10':31.}})),('cpu',dict(cpu_pressure={'full':{'avg10':11.}}))]:
 a=m._evaluate(sp,True,dict(sample,**kw),None,b,peers,own,q,p);r=m._evaluate(sp,False,dict(sample,**kw),None,b,peers,own,q,p);ck(name+'_pause_new',not a['physical_RAM_pass']);ck(name+'_runtime_healthy',r['physical_RAM_pass']and r['physical_disk_pass'])
prev=dict(sample,monotonic=90.)
for name,kw in [('swapout',dict(host_pswpout_pages=200000)),('cgswap',dict(cgroup_swap_current_bytes=700*M)),('hostOOM',dict(host_oom_kill_count=2)),('cgOOM',dict(cgroup_memory_events=dict(oom=1)))]:ck(name+'_delta_pause',bool(m.pressure_reasons(dict(sample,**kw),prev,p)))
ck('static_old_swap_not_forever_hold',not m.pressure_reasons(dict(sample,host_oom_kill_count=2),dict(prev,host_oom_kill_count=2),p))
ck('native5GiB_stop',not m._evaluate(sp,False,dict(sample,native_free_bytes=5*G),None,b,peers,own,q,p)['physical_disk_pass']);ck('predicted_disk_shortfall_only_admission',not m._evaluate(sp,True,dict(sample,native_free_bytes=6*G),None,b,peers,own,q,p)['physical_disk_pass']and m._evaluate(sp,False,dict(sample,native_free_bytes=6*G),None,b,peers,own,q,p)['physical_disk_pass']);ck('archive_mount_fail_pause_new_not_kill',not m._evaluate(sp,True,dict(sample,true164_mount_verified=False),None,b,peers,own,q,p)['admission_disk_pass']and m._evaluate(sp,False,dict(sample,true164_mount_verified=False),None,b,peers,own,q,p)['physical_disk_pass'])
# Private CPU fixture files only; no production control/registry mutation.
with tempfile.TemporaryDirectory(dir=O)as td:
 root=Path(td);(root/'control/specs').mkdir(parents=True);sp2=dict(sp,cohort='CPU_ONLY');f=root/'control/specs/CPU_ONLY.json';f.write_text(json.dumps(sp2));fq=dict(consumed={},admitted_specs={'CPU_ONLY':m.sha(f)},reserved_write_bytes=9*G)
 class MockPeer:
  def rss(self,root,row):return 0,False
  def archived(self,root,c,row):return False
  def size(self,p):return 0
 peer=MockPeer();d=m._dynamic(peer,root,fq,{},256*M,None,False);ck('unclaimed48_not_reserved',d['projected_write_bytes']==256*M);d=m._dynamic(peer,root,fq,{},256*M,sp2,True);ck('only_current_candidate2cap',d['projected_write_bytes']==384*M)
 fq['consumed']={'CPU_ONLY':{'uuid':'CPU_ONLY_UUID'}};d=m._dynamic(peer,root,fq,{'CPU_ONLY':dict(result_cap_bytes=64*M)},256*M,None,False);ck('consumed_claim_not_doublecounted',len(d['ram'])==1 and len(d['writes'])==1);ck('unresolved_futuregrowth_retained',d['projected_write_bytes']==384*M)
# Disk-before-claim: oversized selected long point does not poison small fit point.
real_resources=m.resources
try:
 large=dict(sp,cohort='CPU_LARGE',workload='large',historical_elapsed_seconds=1000);small=dict(sp,cohort='CPU_SMALL',workload='small',historical_elapsed_seconds=1);claims={}
 m.resources=lambda s,fresh:dict(physical_RAM_pass=True,admission_disk_pass=s['cohort']=='CPU_SMALL',required_free_bytes=G,native_free_bytes=G,admission_decision={'pressure_reasons':[]})
 pick=m.choose_dispatch([large,small],sample,claims,previous=None,policy=p);ck('disk_beforeclaim_finds_alternative_small',pick['cohort']=='CPU_SMALL'and claims=={}and len(m.preclaim_diagnostics())==1)
 m.resources=lambda s,fresh:dict(physical_RAM_pass=True,admission_disk_pass=False,required_free_bytes=G,native_free_bytes=G,admission_decision={'pressure_reasons':[]})
 ck('all_diskhold_no_claim_mutation',m.choose_dispatch([large,small],sample,claims,policy=p)is None and claims=={})
finally:m.resources=real_resources
fields=json.loads((O/'RESOURCE_SPEC_FIELDS.json').read_text());ck('48_mapping_pairs',len(fields['points'])==48 and len({x['input_digest']for x in fields['points']})==24);ck('no_uniform4GiB_forecast',len({x['estimated_peak_model_RAM_bytes']for x in fields['points']})>10);ck('RSS_cap_above16_supported',max(x['limits']['max_process_tree_rss_bytes']for x in fields['points'])>16*G);ck('RSS_prediction_not_cap',all(x['estimated_peak_model_RAM_bytes']<x['limits']['max_process_tree_rss_bytes']for x in fields['points']));ck('VMS_not_RSS',all(x['limits']['max_process_tree_vms_bytes']>=4*x['limits']['max_process_tree_rss_bytes']for x in fields['points']));ck('heterogeneous_outputcaps',set(x['limits']['max_result_directory_bytes']for x in fields['points'])=={64*M,256*M,512*M});ck('myocyte_historical_not_truncated',all(x['limits']['max_result_directory_bytes']>x['observed_max_result_logical_bytes']for x in fields['points']));ck('8point5GiB_lifetime_upper',2*sum(x['limits']['max_result_directory_bytes']for x in fields['points'])==int(8.5*G))
# Actual source-pinned read-only peer evidence and fresh real measurements.
peer=m._peer();reg,ep=peer.authority();base=peer.resources({'request':peer.ORIG,'cohort':'R48_CPU_ONLY_QUALIFICATION'},False);first16=m._closed_first16(peer,reg);stage1=m._dynamic(peer,m.STAGE1,reg['registered_future_requests'][m.STAGE1_REQ],peer.claims(m.STAGE1),G);actual=m.sample_system();ck('actual_closed16_zero_future_writes',first16['projected_write_bytes']==0 and first16['exact_archived_nonlive_count']==16);ck('actual_oldscan_not_zeroed',stage1['projected_write_bytes']>G and len(stage1['writes'])==1);ck('actual_genuine164',actual['true164_mount_verified']);ck('hostPSI_and_swap_fields',all(k in actual for k in ['host_memory_pressure','host_io_pressure','host_cpu_pressure','cgroup_swap_current_bytes']))
cert=m._closed_known_metadata(peer,reg,base);base['remaining48_closed_metadata_forward_projection']=cert
ck('actual3closed_metadata_scopes',cert['released_future_metadata_bytes']==3*G and sum(x['released_future_metadata_bytes']>0 for x in cert['proofs'].values())==3)
ck('actual18exactclosedjoins',sum(len(x['points'])for x in cert['proofs'].values())==18)
ck('closedprojection_changes_no_existing_bytes',cert['existing_df_bytes_removed']==0 and not cert['old_registry_or_source_modified'])
with tempfile.TemporaryDirectory(dir=O)as td:
 root=Path(td);c='C';row=dict(uuid='U',intent_sha256='fixture',execution_receipt={'uuid':'U'});paths=[root/'control/qualification_ledger/C.INTENT.json',root/'control/qualification_ledger/C.DONE.json',root/'DTC/run/results/U/NATIVE_EXIT.json',root/'control/C_ARCHIVE_RECEIPT.json',root/'DTC/run/results/U/NATIVE_SIMULATOR_PID_AND_MAPS.json']
 for x in paths:x.parent.mkdir(parents=True,exist_ok=True);x.write_text(json.dumps(dict(pid=123,start_ticks=456)))
 class ClosedPeer:
  ROOTS={'KNOWN':root}
  def archived(self,*a):return self.archive_ok
  def rss(self,*a):return 0,self.live
  archive_ok=True;live=False
 cp=ClosedPeer();cq=dict(state='CLOSED',remaining=0,budget=1,consumed={c:row},reserved_write_bytes=G)
 def verify(q=cq,cl=None,amount=G,entries=None,request='KNOWN'):
  m._JOIN.clear();return m._closed_metadata_scope(cp,request,root,q,cl or {},amount,[]if entries is None else entries)['released_future_metadata_bytes']
 ck('closed_complete_metadata_release',verify()==G)
 for name,delta in [('running',{'state':'RUNNING'}),('remaining',{'remaining':1}),('budget_gap',{'budget':2}),('missing_state',{'state':None})]:ck('closed_negative_'+name,verify(dict(cq,**delta))==0)
 ck('closed_negative_unusedclaim',verify(cl={'UNUSED':{}})==0)
 ck('closed_negative_nonempty_writeentry',verify(entries=[{}])==0)
 ck('closed_negative_other_amount',verify(amount=2*G)==0)
 ck('closed_negative_unknownscope',verify(request='UNKNOWN')==0)
 cp.live=True;ck('closed_negative_livegeneration',verify()==0);cp.live=False
 cp.archive_ok=False;ck('closed_negative_missingjoin',verify()==0);cp.archive_ok=True
 paths[-1].unlink();ck('closed_negative_missingPIDwitness',verify()==0)
 paths[-1].write_text('{}');ck('closed_negative_incompletePIDgeneration',verify()==0)
(O/'CLOSED_METADATA_JOIN_CERTIFICATE.json').write_text(json.dumps(cert,indent=2)+'\n')
projections=[]
for n in [0,1,8,16,24,48]:
 selected=fields['points'][:n];ow=dict(own,projected_write_bytes=256*M+2*sum(x['limits']['max_result_directory_bytes']for x in selected),actual_unarchived_output_bytes=256*M,additional_RAM_bytes=sum(x['estimated_peak_model_RAM_bytes']for x in selected));rr=m._evaluate(sp,True,actual,None,base,{m.STAGE1_REQ:stage1,m.FIRST16_REQ:first16},ow,dict(reserved_write_bytes=int(8.75*G)),p);projections.append(dict(qualification_only_n_claims=n,required_free_bytes=rr['required_free_bytes'],native_free_bytes=rr['native_free_bytes'],RAM_admission_pass=rr['physical_RAM_pass'],disk_admission_pass=rr['admission_disk_pass'],additional_RAM_bytes=rr['total_projected_additional_RAM_bytes']))
result=dict(schema='DTC_REMAINING48_RESOURCE_CPU_QUALIFICATION_V1',status='PASS',source_sha256=m.sha(S),policy_sha256=m.sha(O/'RESOURCE_POLICY.candidate.json'),resource_fields_sha256=m.sha(O/'RESOURCE_SPEC_FIELDS.json'),assertions=len(checks),checks=checks,actual_closed_first16=first16,actual_stage1_dynamic=stage1,qualification_only_unregistered_claim_projections=projections,new_models_started=0,new_scientific_registrations=0,no_production_files_changed=True);(O/'CPU_RESOURCE_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','assertions':len(checks),'source':m.sha(S),'closed16write':first16['projected_write_bytes'],'projections':projections}))
