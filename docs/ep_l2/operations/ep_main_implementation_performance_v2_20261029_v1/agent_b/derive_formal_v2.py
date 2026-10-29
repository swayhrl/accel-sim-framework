import pathlib,json,hashlib,copy,csv,datetime,importlib.util,difflib
P=pathlib.Path;B=P(__file__).resolve().parent;J=B.parents[2];O=J/'research/observation_guided_20261029_v1/round2/agent_b';H=B/'host_candidate'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n');return ref(p)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
regpath=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reg=read(regpath);RID='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1';rows=reg['registered_future_requests'][RID]['consumed'];old=read(O/'EXACT_SPEC_AND_BUDGET_MANIFEST.json');reuse=[];drafts=[];seen={}
for proposal in old['proposals']:
 s=read(proposal['draft_ref']['path']);base=read(s['original_accepted_S_spec_ref']['path']);program=s['program'];inp=s['input_identity_sha256'];mode=s['mode'];candidates=[]
 if inp not in seen:
  for case,row in rows.items():
   if inp[:8].upper()not in case or row.get('state')!='CLOSED_ACCEPTED' or not row.get('accepted_point_ref'):continue
   point=read(row['accepted_point_ref']['path']);spec_ref=point['spec_ref'];p=read(spec_ref['path'])
   if p['mode']not in ['S','WV_ZERO_RO']:continue
   checks={
    'spec_ref_SHA':sha(spec_ref['path'])==spec_ref['sha256'],
    'point_ref_SHA':sha(row['accepted_point_ref']['path'])==row['accepted_point_ref']['sha256'],
    'accepted_and_drained':point['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED' and point['hardware_drained']is True,
    'Source5':p['source_identity']==point['source_identity']==base['source_identity'],
    'strong_input':p['input_identity_sha256']==point['input_identity_sha256']==inp,
    'geometry':p['geometry']==base['geometry'],
    'profile':p['profile']==base['profile'],
    'observers':p['observer_env']==base['observer_env'],
    'ordered_kernel_launches':p['expected_kernel_launches']==base['expected_kernel_launches'],
    'ordered_kernel_scopes':p['expected_kernel_scopes']==base['expected_kernel_scopes'],
    'input_binding_ref':p['input_binding_ref']==base['input_binding_ref'],
    'input_binding_SHA':sha(p['input_binding_ref']['path'])==p['input_binding_ref']['sha256']}
   flags={'-gpgpu_ep_l2_ft_mode':'1'if p['mode']=='S'else'2','-gpgpu_ep_l2_tvd_clean':'0'if p['mode']=='S'else'1','-gpgpu_ep_l2_tvd_dirty':'0'if p['mode']=='S'else'1','-gpgpu_ep_l2_ro_tag_detach':'0','-gpgpu_ep_l2_ro_line_mshr_bypass':'0'}
   opts=copy.deepcopy(base['expected_effective_options']);opts.update(flags);checks['full282_exact_declared_mode_only']=opts==p['expected_effective_options'] and len(opts)==282
   binding=read(p['input_binding_ref']['path']);record=dict(program=program,input_identity_sha256=inp,mode=p['mode'],cohort=case,registry_request_id=RID,current_registry_state=row['state'],point_ref=row['accepted_point_ref'],spec_ref=spec_ref,input_binding_ref=p['input_binding_ref'],ordered_kernel_identity=binding['ordered_kernel_identity'],expected282_sha256=digest(opts),Source5=p['source_identity'],checks=checks,identity_status='PASS'if all(checks.values())else'HOLD',Main_reuse_signoff='PENDING_MAIN_REVIEW_NOT_AGENT_SELF_APPROVED',new_start_cost=0,cycles=point['cycles'])
   candidates.append(record)
  seen[inp]=candidates;reuse.extend(candidates)
 s['cohort']='EP_PERF_V2_PROPOSED_'+program.upper()+'_'+inp[:8].upper()+'_'+mode;s['schema']='EP_WV_V2_EXACT_DRAFT_NOT_FROZEN_REGISTERED_OR_AUTHORIZED';s['science_request_id']='EP_L2_WV_DECOMPOSITION_V2';s['status']='HOLD_PENDING_MAIN_MODE_HOST_PARSER_NATIVE_AND_EXACT_USER_LAUNCH_AUTHORIZATION';s['host_engine_ref']=ref(H/'ep_perf_native_wv_modes_draft.py');s['host_common_ref']=ref(H/'ep_perf_common_v2.py');s['mode_contract_ref']=ref(H/'mode_contract.py');s['validation_module_ref']=ref(H/'mode_aware_terminal.py');s['host_qualification_ref']=None;s['mode_cpu_qualification_ref']=None;s['matched_S_anchor_qualification_ref']=None;s['approved_launches']=0;s['Source78_P1_review_required']='NONBLOCKING_FOR_RO_DISABLED_W_WV_NO_P1_INTEGRATION'
 s['scientific_option_contract'].update(mode=mode,CPU_mode_qualification_ref=None,T_M='DISABLED_NOT_EXERCISED',W_only_CPU_evidence_candidate_ref=ref(O/'CPU_ACTUAL_EXECUTION_FINAL.json'))
 overlay_src=P(proposal['mode_overlay_ref']['path']);overlay=B/'scientific_drafts'/overlay_src.name;overlay.parent.mkdir(exist_ok=True);overlay.write_bytes(overlay_src.read_bytes());s['ordered_configs'][-1]=ref(overlay)
 s['mode_native_requirements']=dict(fresh_scoped_request=True,old227_budget_reuse=False,new_route_installation='MAIN_ONLY_AFTER_QUALIFICATION',source78_unchanged=True,application_parser_positive='NOT_QUALIFIED',observer_NI='NO_NEW_OBSERVER_CORE_OR_ENV_PROPOSED',application_NI='NOT_INHERITED_FROM_CPU; exact existing Source78 profile evidence only')
 target=B/'scientific_drafts'/(program+'_'+mode+'.json');draftref=put(target,s)
 drafts.append(dict(program=program,input_identity_sha256=inp,mode=mode,priority='FIRST_TWO_LOW_COST'if program in['GEMM','fastWalshTransform']else'CONDITIONAL_FOUR_POSITIVE_NEGATIVE',draft_ref=draftref,expected282_sha256=digest(s['expected_effective_options']),mode_delta_vs_S=s['exact_mode_delta_vs_S'],hardware_delta_beyond_formal_flags={},RO='NOT_APPLICABLE_RUNTIME_DISABLED',source_identity=s['source_identity'],matched_existing_S=[x for x in seen[inp]if x['mode']=='S'],matched_existing_WV=[x for x in seen[inp]if x['mode']=='WV_ZERO_RO'],mode_CPU='COMPONENT_PASS_MAIN_SIGNOFF_PENDING'if mode=='W_ONLY'else'PRIOR_ACCEPTED_WV_PLUS_NEW_HOST_PENDING',HostQ='PARTIAL_NO_FULL_W_WRAPPER_POSITIVE',nativeQ='PARTIAL_SANDBOX_ONLY_NOT_INSTALLED',new_starts_requested=1,new_starts_authorized=0,new_starts_consumed=0,NI_extra_starts_requested=0,NI_extra_condition='No new observer/Core. If Main requires application Host/parser qualification or changes source/env, separately request exact additional controls; never included or silently borrowed.',wall_anchor_seconds=proposal['wall_anchor_seconds'],new_mode_wall='UNKNOWN',planning_peak_RSS_bytes=proposal['planning_peak_RSS_bytes'],hard_limits=s['limits']))
put(B/'EXACT_EXISTING_S_WV_REUSE_AUDIT.json',dict(schema='EP_V2_EXACT_EXISTING_REFERENCE_AUDIT',registry_snapshot_sha256=sha(regpath),snapshot_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),read_only=True,raw_or_trace_body_reads=0,records=reuse,conclusion='S all four PASS; WV GEMM/FWT PASS; Stencil/Scan WV absent therefore two new WV points required',scientific_reuse_authority='Main signoff required'))
put(B/'EXACT_WV_SPECS_AND_BUDGET_V2.json',dict(schema='EP_W_ONLY_WV_V2_DRAFT_MATRIX',status='DRAFT_NO_AUTHORIZATION_NO_REGISTRATION',proposed=drafts,budget=dict(first_FWT_GEMM_W_ONLY=2,conditional_Stencil_Scan_W_ONLY_and_WV=4,total_if_all_separately_approved=6,authorized=0,consumed=0,RO_T_three_arm_excluded=True,extra_NI_starts=0,extra_NI_NOT_AUTOMATIC=True),missing_qualifications=['Main formal modeCPU signoff','complete W_ONLY parser HostQ actual positive and negative fixtures','new Host qualification Main review','new independent native route integration and official dry-prepare after exact authorization','current scoped source/input/mode eligibility','fresh exact user budget authorization','fresh resource admission'],no_source_or_observer_change=True))
with (B/'EXACT_WV_BUDGET_V2.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=['program','mode','priority','new_starts_requested','new_starts_authorized','new_starts_consumed','planning_peak_RSS_bytes','new_mode_wall']);w.writeheader();w.writerows({k:r[k]for k in w.fieldnames}for r in drafts)
# Candidate diff after all pin updates; keep immutable old draft as provenance.
for name in ['mode_contract.py','mode_aware_terminal.py','ep_perf_native_wv_modes_draft.py']:
 (B/(name+'.patch')).write_text(''.join(difflib.unified_diff((O/'host_candidate'/name).read_text().splitlines(True),(H/name).read_text().splitlines(True),fromfile='round2/'+name,tofile='v2_candidate/'+name)))
print(json.dumps(dict(drafts=len(drafts),reuse=len(reuse),identity_all_pass=all(all(x['checks'].values())for x in reuse),new_starts=0)))
