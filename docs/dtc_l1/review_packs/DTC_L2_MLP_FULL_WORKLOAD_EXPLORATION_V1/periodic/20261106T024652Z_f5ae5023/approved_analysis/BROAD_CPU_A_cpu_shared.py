"""Explicit dynamic CPU timeslicing generation. Import never installs or launches.
The old CPU2 idle-spare policy, global ACTIVE/context and science stay unchanged.
"""
import pathlib,json,hashlib,copy,importlib.util,os,time,sys
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');G=1024**3
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ID='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1';MODE='CPU_SHARED_DYNAMIC_PER_COHORT'
FIELD='additional_cpu_shared_timeslice_binding';PROOF='additional_cpu_shared_timeslice_proof';SNAP='CPU_SHARED_TIMESLICE_SNAPSHOT.json'
INITIAL='E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1'
ORIGINAL_FOUR=(INITIAL,'E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSBPF-V1','E2-DTCL2MLP-16f4c42373e4961e-DH-P0-OBSCTRL-V1','E2-DTCL2MLP-16f4c42373e4961e-DH-P0-OBSBPF-V1')
FIRST_UUID='2d24a1be-db7b-4100-9752-42b16ea46035'
FIRST_RESULT_SHA='5395654775d9760cc777732ff7565f861b840388c3561b7df1dfd88db763b42e'
FIRST_REPLAY_SHA='144ebf9fb1a2b81a93aa4056e3a9846df89673ac365b8fb2a9942765f129b9da'
STAGE2_CERT_SHA='30bd502f7fe6653907b3e835c2b7aee78c780c65ecde758df473942158d1b895'
DESIGN=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/A/broad_shared_cpu_v1/RESOURCE_CONTRACT.json')
DESIGN_SHA='a8c7446a0edaeb166402400f6a8efbf558e54aac690d26dccfda5bbc63a3edc9'
ROLES=['library','owner','frontend','extra_strict','consumer']
POLICY=dict(min_sample_seconds=.5,max_sample_seconds=10.,max_evidence_age_seconds=2.,visible_quota_fraction=.75,prospective_cpu_threads=1,max_shared_running=None,reserve_all_other_claim_threads=True,require_idle_physical_cores=False,max_sibling_busy_threshold=None,only_ignored_pressure_reason='cpu_pressure_full',selected_cpu_original_legal_required=True,hidden_ancestor_limits_excluded=False)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def objsha(v):return hashlib.sha256(js(v)).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError('RESOURCE_HOLD_CPU_SHARED: '+msg)
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
_CPU2=load('timeslice_frozen_CPU2',R/'control/operational_amendments/cpu_spare_memory_v2/cpu_memory.py');_OLD=_CPU2._OLD
RES=R/'tools/l2_resources.py';RPOLICY=R/'control/RESOURCE_POLICY.json'
def atomic(p,v):return _OLD.atomic(p,v)
def budget(base):return _OLD.budget(base)
def validate_broad_approval(cfg,q=None,approval_utf8=None,gate_utf8=None,source_artifacts_utf8=None,scope_contract_utf8=None):
 """Hash-bound actual mixed4 evidence plus separate Main scope authorization.
 No raw replay/authority read occurs in this function; offline replay uses UTF8.
 """
 text=P(cfg['broad_approval_path']).read_text()if approval_utf8 is None else approval_utf8
 need(hashlib.sha256(text.encode()).hexdigest()==cfg['broad_approval_sha256'],'broad approval SHA')
 app=json.loads(text);need(app['schema']=='DTC_MAIN_BROAD_SHARED_CPU_PREREQUISITE_APPROVAL_V1'and app['Main_broad_operational_rollout_approved']is True and app['eligible_conditional_new_operational_registration']is True and app['new_grants']==0,'Main broad approval absent')
 need(app['qualification_only']is False or cfg['qualification_only'],'fixture approval cannot release production')
 need(len(set(cfg['allowed_cohorts']))==len(cfg['allowed_cohorts'])and set(app['allowed_cohorts'])==set(cfg['allowed_cohorts']),'approval/finite explicit scope mismatch')
 ref=app['scope_contract'];need(ref['path']==cfg['scope_contract_path']and ref['sha256']==cfg['scope_contract_sha256'],'scope contract reference mismatch')
 st=P(ref['path']).read_text()if scope_contract_utf8 is None else scope_contract_utf8
 need(hashlib.sha256(st.encode()).hexdigest()==ref['sha256'],'scope contract SHA');sc=json.loads(st)
 need(sc['schema']=='DTC_MAIN_BROAD_CPU_CURRENT_UNUSED_SCOPE_CANDIDATE_V1'and sc['request']==REQ and sc['new_model_grants']==0 and sc['engineering_excluded']is True and sc['supplemental_R2_excluded']is True,'wrong scientific scope contract')
 need({x['cohort']for x in sc['rows']}==set(cfg['allowed_cohorts'])and len(sc['rows'])==len(cfg['allowed_cohorts']),'scope contract cohort mismatch')
 gr=app['actual_gate'];gt=P(gr['path']).read_text()if gate_utf8 is None else gate_utf8
 need(hashlib.sha256(gt.encode()).hexdigest()==gr['sha256'],'actual4 gate SHA');gate=json.loads(gt)
 need(cfg['expected_pins'][gr['source_path']]==gr['source_sha256']==sha(gr['source_path'])and gate['gate_source_sha256']==gr['source_sha256'],'actual gate source lineage drift')
 need(gate['status']=='PASS_REAL_MIXED_GENERATION_ENGINEERING_FOUR_FULL_CHAIN'and gate['accepted_real_count']==4 and gate['four_point_qualified']is True and (gate.get('qualification_only',False)is False or cfg['qualification_only']),'actual mixed4 gate missing')
 rows=gate['rows'];need(len(rows)==4 and {r['cohort']for r in rows}==set(ORIGINAL_FOUR)and all(r['actual_full_chain_replayed']is True for r in rows),'not actual exact4 fullchain')
 need(gate['primary_rollout_eligible']is False and gate['IR_rollout_eligible']is False,'gate itself is not rollout authority')
 need(gate['actual_owner_pid']==1498278 and gate['actual_owner_start_ticks']==977758783,'wrong actual gate owner generation')
 refs=app['source_artifacts'];need(set(refs)>={r['cohort']+'.RESULT'for r in rows}|{r['cohort']+'.DONE'for r in rows},'four RESULT/DONE references required')
 texts={};docs={}
 for key,ref in refs.items():
  body=P(ref['path']).read_text()if source_artifacts_utf8 is None else source_artifacts_utf8[key]
  need(hashlib.sha256(body.encode()).hexdigest()==ref['sha256'],'gate source artifact SHA '+key);texts[key]=body;docs[key]=json.loads(body)
 for row in rows:
  c=row['cohort'];result=docs[c+'.RESULT'];done=docs[c+'.DONE'];need(refs[c+'.RESULT']['sha256']==row['RESULT_sha256'],'gate RESULT SHA mismatch')
  need(result['cohort']==done['cohort']==c and result['uuid']==done['uuid']==row['uuid']and result['cycles']==row['cycles']and done['stop_reason']is None and done['launcher_wait_returncode']==0,'gate closure UUID/natural exit mismatch')
  need(result['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and result['archive']['receipt']['archive_sha256']==row['archive_sha256']and result['archive']['receipt']['manifest_sha256']==row['archive_manifest_sha256'],'gate archive closure mismatch')
  if not cfg['qualification_only']:
   proof=result['proof'];need({k:proof[k]for k in ['CTA','instructions','kernel_count']}==row['counts']and proof['performance_accepted']is True,'gate/fullcounts mismatch')
 if q is not None:
  need(set(cfg['allowed_cohorts'])<=set(q['admitted_specs']),'unregistered scope')
  current={x['cohort']:x for x in q.get('authorized_incident_recovery_trials',[])}
  for row in sc['rows']:
   if row['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':need(current.get(row['cohort'])==row['incident_authorization_record'],'IR11 grant/oldnegative lineage changed')
 return dict(status='PASS_EXPLICIT_MAIN_BROAD_SCOPE_AND_ACTUAL_MIXED_FOUR',certificate_utf8=text,gate_utf8=gt,source_artifacts_utf8=texts,scope_contract_utf8=st)
def _scope(cfg,q):
 need(cfg['scope_mode']=='ALL_ALLOWED_ADMITTED_UNSPENT'and cfg['qualification_stage']=='AFTER_REAL_ENGINEERING4_GATE','unapproved broad scope/stage')
 allowed=cfg['allowed_cohorts'];need(allowed and len(set(allowed))==len(allowed)and set(allowed)<=set(q['admitted_specs']),'unknown/duplicate/unadmitted scope')
 validate_broad_approval(cfg,q);return allowed
def record(cfg):
 keys=['request','overlay_id','scope_mode','qualification_stage','allowed_cohorts','max_shared_running','memory_utilization_fraction','host_floor_bytes','cgroup_floor_bytes','cpu_shared_policy','source_paths','qualified_sources','expected_pins','QA_sha256','readback_sha256','io_active_sha256','design_contract_sha256','scope_contract_path','scope_contract_sha256','broad_approval_path','broad_approval_sha256']
 return dict({k:copy.deepcopy(cfg[k])for k in keys},configuration_sha256=objsha(cfg),shared_CPU_is_not_idle_spare=True)
def validate(cfg,q):
 need(cfg['schema']==cfg['overlay_id']==ID and cfg['request']==q['request']==REQ and cfg['status']=='ACTIVE_FUTURE_ONLY','wrong shared generation/config')
 _scope(cfg,q);need(cfg['max_shared_running']is None and cfg['cpu_shared_policy']==POLICY,'shared policy/cap drift')
 need(cfg['memory_utilization_fraction']==.95 and cfg['host_floor_bytes']==cfg['cgroup_floor_bytes']==10*G,'RAM policy drift')
 need(sha(cfg['design_contract_path'])==cfg['design_contract_sha256']==DESIGN_SHA,'Main design contract drift')
 need(cfg['qualification_only']is True and q.get('qualification_only')is True and P(cfg['root']).resolve()!=R if cfg['qualification_only']else not q.get('qualification_only',False)and P(cfg['root']).resolve()==R,'qualification/production context mismatch')
 need(set(cfg['source_paths'])==set(cfg['qualified_sources'])==set(ROLES),'resource source roles mismatch')
 need(cfg['library_path']==cfg['source_paths']['library'],'generic fa3 library path mismatch')
 for role in ROLES:need(sha(cfg['source_paths'][role])==cfg['qualified_sources'][role],'shared source drift '+role)
 need(cfg['qualified_sources']['library']==sha(__file__),'wrong shared library')
 for p,h in cfg['expected_pins'].items():need(sha(p)==h,'frozen dependency drift '+p)
 need(cfg['expected_pins'][str(RES)]==sha(RES)and cfg['expected_pins'][str(RPOLICY)]==sha(RPOLICY)and cfg['expected_pins'][str(P(_CPU2.__file__))]==sha(_CPU2.__file__),'required frozen resource pins absent')
 need(sha(cfg['io_active_path'])==cfg['io_active_sha256'],'IO configuration drift')
 for k in ['QA','readback']:need(sha(cfg[k+'_path'])==cfg[k+'_sha256'],'qualification/readback drift '+k)
 qa=read(cfg['QA_path']);rb=read(cfg['readback_path']);need(qa['status']=='PASS'and all(qa[k]is True for k in['cpu_shared_resource_qualified','native_binding_qualified','dynamic_concurrency_qualified']),'shared resource unqualified')
 need(rb['verified']is True and rb['QA_sha256']==cfg['QA_sha256']and qa['qualified_sources']==rb['qualified_sources']==cfg['qualified_sources']and qa['expected_pins']==rb['expected_pins']==cfg['expected_pins'],'qualification/publication source mismatch')
 if qa.get('qualification_only')or rb.get('qualification_only'):need(cfg['qualification_only']and q.get('qualification_only')is True,'CPU stand-in cannot authorize Main')
 row=q['additional_operational_overlays'][ID];need(row['status']=='ACTIVE'and all(row.get(k)==v for k,v in record(cfg).items()),'shared overlay authority mismatch')
 return row
def eligible_cohort(cfg,q,c,stage,claims=None):
 need(stage in['OWNER_FRAME','OWNER_CHOOSE','NATIVE'],'unknown stage')
 return c in _scope(cfg,q)and c not in q['consumed']and c not in q.get('sealed',[])and not(stage=='OWNER_CHOOSE'and c in(claims or{}))
def wrap_cpu_evidence(raw,prospective_cpu_threads=1):
 need(type(prospective_cpu_threads)is int and prospective_cpu_threads>=1,'invalid reserved prospective threads')
 return dict(schema=ID+'_CPU_DOUBLE_SAMPLE',reserved_prospective_cpu_threads=prospective_cpu_threads,raw_cpu2_evidence=copy.deepcopy(raw),shared_sampler_source_sha256=sha(__file__),created_monotonic=time.monotonic(),CPU2_spare_PASS_claimed=False)
def sample_cpu_evidence(selected_cpu=None,sample_seconds=.5,prospective_cpu_threads=1):
 need(type(prospective_cpu_threads)is int and prospective_cpu_threads>=1,'invalid reserved prospective threads')
 return wrap_cpu_evidence(_CPU2.sample_cpu_evidence(selected_cpu,sample_seconds,1),prospective_cpu_threads)
def verify_cpu_evidence(e,selected_cpu=None,prospective_cpu_threads=None):
 prospective_cpu_threads=e['reserved_prospective_cpu_threads']if prospective_cpu_threads is None else prospective_cpu_threads
 need(type(prospective_cpu_threads)is int and prospective_cpu_threads>=1 and e['reserved_prospective_cpu_threads']==prospective_cpu_threads,'reserved prospective CPU threads mismatch')
 need(e['schema']==ID+'_CPU_DOUBLE_SAMPLE'and e['shared_sampler_source_sha256']==sha(__file__)and e['CPU2_spare_PASS_claimed']is False,'wrong shared CPU evidence')
 raw=e['raw_cpu2_evidence'];need(raw['schema']==_CPU2.ID+'_CPU_DOUBLE_SAMPLE'and raw['policy']==_CPU2.POLICY and raw['sampler_source_sha256']==sha(_CPU2.__file__)and raw['prospective_cpu_threads']==1,'old raw sampler evidence changed')
 a,b=raw['first'],raw['second'];dt=b['monotonic']-a['monotonic'];need(.5<=dt<=10.,'CPU double sample interval')
 need(a['boot_id']==b['boot_id']and all(a[k]==b[k]for k in['sampler_pid','sampler_start_ticks','sampler_uid','sampler_ppid','allowed','topology']),'CPU generation/topology changed')
 need(not a['unreadable_tasks']and not b['unreadable_tasks'],'unknown affinity read')
 need(0<=e['created_monotonic']-b['completed_monotonic']<=2.,'CPU evidence age at capture')
 if selected_cpu is not None:need(type(selected_cpu)is int and selected_cpu in b['allowed']and(raw['selected_cpu']is None or raw['selected_cpu']==selected_cpu),'selected CPU not allowed/bound')
 ca,cb=a['cgroups'],b['cgroups'];need(all(ca[k]==cb[k]for k in['process_cgroup','mount_root','mount_point']),'cgroup namespace changed')
 need([x['path']for x in ca['visible']]==[x['path']for x in cb['visible']],'visible ancestor set changed')
 for s in[a,b]:need(s['cgroups']['hidden_ancestor_status']=='UNKNOWN'and s['cgroups']['hidden_ancestor_limits_excluded']is False,'hidden ancestors falsely excluded')
 cgdt=cb['sample_monotonic']-ca['sample_monotonic'];need(.5<=cgdt<=10.,'quota sample interval');quota=[]
 for x,y in zip(ca['visible'],cb['visible']):
  need(x['quota']==y['quota'],'quota changed');s0,s1=x['stat'],y['stat'];need(all(k in s0 and k in s1 for k in['usage_usec','nr_throttled','throttled_usec']),'missing quota counters')
  need(all(s1[k]>=s0[k]for k in['usage_usec','nr_throttled','throttled_usec']),'quota counter reset');need(s1['nr_throttled']==s0['nr_throttled']and s1['throttled_usec']==s0['throttled_usec'],'visible quota throttled')
  if y['quota'][0]!='max':
   limit=int(y['quota'][0])/int(y['quota'][1]);used=(s1['usage_usec']-s0['usage_usec'])/cgdt/1e6;need(used+prospective_cpu_threads<=.75*limit,'used+reserved+candidate exceeds .75 quota');quota.append(dict(path=y['path'],quota_cores=limit,used_cores=used,prospective_threads=prospective_cpu_threads))
 need(quota,'no finite visible quota');busy={}
 for cpu in b['allowed']:
  x=a['cpu_ticks'].get(str(cpu));y=b['cpu_ticks'].get(str(cpu));need(x is not None and y is not None and len(x)==len(y)==8,'missing ticks');delta=[v-u for u,v in zip(x,y)];need(min(delta)>=0 and sum(delta)>0,'invalid tick delta');busy[str(cpu)]=(sum(delta)-delta[3]-delta[4])/sum(delta)
 return dict(status='PASS_VISIBLE_QUOTA_FOR_CPU_TIMESHARING_NOT_IDLE_SPARE',selected_cpu=selected_cpu,quota_checks=quota,host_mean_busy=sum(busy.values())/len(busy),selected_cpu_busy=None if selected_cpu is None else busy[str(selected_cpu)],min_idle_core_rule_applied=False,sibling_idle_threshold_applied=False,hidden_ancestor_status='UNKNOWN',hidden_ancestor_limits_excluded=False)
def _proc(pid):
 try:
  a=P('/proc')/str(pid)/'stat';text=a.read_text();f=text.rsplit(')',1)[1].split();return dict(pid=pid,start_ticks=int(f[19]),state=f[0],stat_sha256=hashlib.sha256(text.encode()).hexdigest())
 except(FileNotFoundError,ProcessLookupError):return dict(pid=pid,missing=True)
def capture_slot_evidence(cfg,q,cohort,selected_cpu=None,root=None,proc_reader=None):
 root=P(root or cfg['root']);proc_reader=proc_reader or _proc;claims_path=root/'control/POOL_DISPATCH_RESERVATIONS.json';claims_utf8=claims_path.read_text();claims=json.loads(claims_utf8)['claims'];allowed=set(_scope(cfg,q));rows=[];unknown=[];inspections=[]
 for c,claim in claims.items():
  tagged=claim.get('cpu_shared_timeslice_overlay_id')==ID
  if tagged and c not in allowed:unknown.append(c)
  if c!=cohort and(c in allowed or tagged):rows.append(dict(cohort=c,kind='SHARED_UNSPENT_OR_MODEL_CLAIM',claim=copy.deepcopy(claim)))
 # Ordinary CPU2 spent rows, including old scan/M16 without receipt, never
 # occupy a shared slot. Inspect only allowed shared rows or unclosed rows
 # whose actual INTENT explicitly carries this new shared binding.
 for c,row in q['consumed'].items():
  if c not in allowed and row.get('execution_receipt'):continue
  ip=root/'control/qualification_ledger'/(c+'.INTENT.json')
  if not ip.exists():
   inspections.append(dict(cohort=c,row=copy.deepcopy(row),INTENT_utf8=None,DONE_utf8=None))
   if c in allowed:unknown.append(c)
   continue
  itext=ip.read_text();intent=json.loads(itext);donepath=root/'control/qualification_ledger'/(c+'.DONE.json');inspections.append(dict(cohort=c,row=copy.deepcopy(row),INTENT_utf8=itext,DONE_utf8=donepath.read_text()if donepath.exists()else None));binding=intent.get(FIELD)
  if not binding:
   if c in allowed:unknown.append(c)
   continue
  if binding.get('schema')!=ID or c not in allowed:unknown.append(c);continue
  need(intent['cohort']==c and intent['uuid']==row['uuid'],'shared generation UUID mismatch')
  output=P(intent['output']);done=root/'control/qualification_ledger'/(c+'.DONE.json');receipt=row.get('execution_receipt');closed=bool(receipt and done.exists()and read(done)==receipt and receipt.get('uuid')==row['uuid'])
  if closed:continue
  observed=dict(status='UNOBSERVED_CONSUMED_WITHOUT_JOINED_DONE')
  pp=output/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
  if pp.exists():
   proof=read(pp);observed=proc_reader(proof['pid']);observed['expected_start_ticks']=proof['start_ticks'];observed['same_live_birth']=not observed.get('missing')and observed.get('start_ticks')==proof['start_ticks']and observed.get('state')not in['Z','X'];observed['pid_proof_sha256']=sha(pp)
  rows.append(dict(cohort=c,kind='SHARED_CONSUMED_AWAITING_JOINED_DONE',uuid=row['uuid'],INTENT_sha256=hashlib.sha256(itext.encode()).hexdigest(),generation_observation=observed,missing_DONE_never_refunds_slot=True))
 claim_costs={}
 for c in claims:
  if c in q['consumed']:continue
  path=root/'control/specs'/(c+'.json');spec=read(path);need(sha(path)==q['admitted_specs'][c]and spec['cohort']==c and spec['host_cpu']is None,'claim canonical/authority mismatch');claim_costs[c]=dict(canonical_spec_utf8=path.read_text(),canonical_spec_sha256=sha(path),estimated_peak_model_RAM_bytes=spec['estimated_peak_model_RAM_bytes'])
 other_claims={c:v for c,v in claims.items()if c!=cohort};collisions=[c for c,v in other_claims.items()if v.get('host_cpu')==selected_cpu]if selected_cpu is not None else[]
 return dict(schema=ID+'_DYNAMIC_RESERVATION_EVIDENCE',cohort=cohort,selected_cpu=selected_cpu,allowed_cohorts=sorted(allowed),current_admitted_spec_sha256=q['admitted_specs'][cohort],candidate_consumed=cohort in q['consumed'],consumed_inspections=inspections,consumed_cohorts=sorted(q['consumed']),unspent_claim_canonical_costs=claim_costs,claims_utf8=claims_utf8,claims_sha256=hashlib.sha256(claims_utf8.encode()).hexdigest(),other_shared_reservations=rows,unknown_shared_cohorts=sorted(set(unknown)),other_claim_CPU_collisions=collisions,prospective_shared_count=1+len({x['cohort']for x in rows if x['cohort']!=cohort}),max_shared_running=None,prospective_cpu_threads=1+len(set(other_claims)|{x['cohort']for x in rows if x['cohort']!=cohort}),created_monotonic=time.monotonic(),ordinary_CPU2_rows_counted_as_shared=False)
def verify_slot_evidence(e,cfg,cohort,selected_cpu=None):
 need(e['schema']==ID+'_DYNAMIC_RESERVATION_EVIDENCE'and e['cohort']==cohort and e['selected_cpu']==selected_cpu,'slot identity mismatch')
 need(e['allowed_cohorts']==sorted(cfg['allowed_cohorts'])and not e['unknown_shared_cohorts'],'unknown shared generation')
 need(hashlib.sha256(e['claims_utf8'].encode()).hexdigest()==e['claims_sha256'],'claim snapshot changed');claims=json.loads(e['claims_utf8'])['claims']
 need(e['candidate_consumed']is False,'candidate already consumed')
 need(cohort not in e['consumed_cohorts']and set(e['unspent_claim_canonical_costs'])==set(claims)-set(e['consumed_cohorts']),'claim consumption/cost evidence omitted')
 for claim_c,cost in e['unspent_claim_canonical_costs'].items():
  sp=json.loads(cost['canonical_spec_utf8']);need(hashlib.sha256(cost['canonical_spec_utf8'].encode()).hexdigest()==cost['canonical_spec_sha256']and sp['cohort']==claim_c and sp['host_cpu']is None and sp['estimated_peak_model_RAM_bytes']==cost['estimated_peak_model_RAM_bytes'],'claim canonical cost snapshot changed')
 reserved={(c,'SHARED_UNSPENT_OR_MODEL_CLAIM')for c,v in claims.items()if c!=cohort and(c in cfg['allowed_cohorts']or v.get('cpu_shared_timeslice_overlay_id')==ID)};unknown={c for c,v in claims.items()if v.get('cpu_shared_timeslice_overlay_id')==ID and c not in cfg['allowed_cohorts']}
 for x in e['consumed_inspections']:
  c=x['cohort'];r=x['row'];intent=None if x['INTENT_utf8']is None else json.loads(x['INTENT_utf8']);binding=None if intent is None else intent.get(FIELD)
  if not binding:
   if c in cfg['allowed_cohorts']:unknown.add(c)
   continue
  if binding.get('schema')!=ID or c not in cfg['allowed_cohorts']:unknown.add(c);continue
  need(intent['cohort']==c and intent['uuid']==r['uuid'],'consumed shared UUID mismatch')
  done=None if x['DONE_utf8']is None else json.loads(x['DONE_utf8']);receipt=r.get('execution_receipt');closed=bool(receipt and done==receipt and receipt.get('uuid')==r['uuid'])
  if not closed:reserved.add((c,'SHARED_CONSUMED_AWAITING_JOINED_DONE'))
 need(not unknown and set(e['unknown_shared_cohorts'])==unknown,'unknown shared consumption/claim')
 need({(x['cohort'],x['kind'])for x in e['other_shared_reservations']}==reserved,'shared reservation omitted/fabricated')
 expected=[c for c,v in claims.items()if c!=cohort and v.get('host_cpu')==selected_cpu]if selected_cpu is not None else[]
 need(e['other_claim_CPU_collisions']==expected and not expected,'selected CPU collides with own other claim')
 need(e['prospective_shared_count']==1+len({r['cohort']for r in e['other_shared_reservations']if r['cohort']!=cohort})and cfg['max_shared_running']is None and e['max_shared_running']is None,'dynamic shared count mismatch')
 expected_threads=1+len({k for k in claims if k!=cohort}|{r['cohort']for r in e['other_shared_reservations']if r['cohort']!=cohort});need(e['prospective_cpu_threads']==expected_threads,'future CPU claim reservation omitted')
 need(e['ordinary_CPU2_rows_counted_as_shared']is False,'ordinary jobs count as shared')
 return dict(status='PASS_DYNAMIC_SHARED_RESERVATIONS_NO_FIXED_JOBCAP',prospective_shared_count=e['prospective_shared_count'])
def capture_legal_cpu_evidence(cfg,claims,cohort,selected_cpu=None):
 mod=load('shared_original_CPU_allocator',RES);sample=mod.resource_sample(True,read(RPOLICY));others={c:v for c,v in claims.items()if c!=cohort};return dict(schema=ID+'_LEGAL_CPU',source_sha256=sha(RES),sample=sample,other_claims=copy.deepcopy(others),candidate_cohort=cohort,selected_cpu=selected_cpu,legal_cpu_candidates=mod.cpu_candidates(sample,others,None),created_monotonic=time.monotonic())
def verify_legal_cpu_evidence(e,cfg,cohort,selected_cpu=None):
 need(e['schema']==ID+'_LEGAL_CPU'and e['candidate_cohort']==cohort and e['selected_cpu']==selected_cpu,'allocator evidence identity');need(e['source_sha256']==cfg['expected_pins'][str(RES)]==sha(RES),'allocator source mismatch')
 mod=load('shared_offline_original_CPU_allocator',RES);legal=mod.cpu_candidates(e['sample'],e['other_claims'],None);need(legal==e['legal_cpu_candidates']and legal,'original CPU allocator empty/changed')
 if selected_cpu is not None:need(selected_cpu in legal,'selected CPU not original legal candidate')
 need(0<=e['created_monotonic']-e['sample']['monotonic']<=2.,'allocator sample stale at capture')
 return dict(status='PASS_ORIGINAL_CPU_ALLOCATOR_MEMBERSHIP',selected_cpu=selected_cpu)
def project(base,cfg=None):return _OLD.project(_CPU2._raw(base))
def verify_science_scope(spec,cohort,contract):
 row=next((r for r in contract['rows']if r['cohort']==cohort),None);need(row is not None and {k:spec[k]for k in contract['scientific_projection_keys']}==row['science_projection'],'GPU science changed from explicit scope')
 role='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'if row['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'else None;need(spec.get('scientific_role')==role,'scientific role changed')
 if role:
  lineage=spec['incident_recovery_trial_lineage'];auth=row['incident_authorization_record']
  for k in ['incident_id','original_cohort','original_uuid','original_negative_RESULT_sha256','original_DONE_sha256','science_projection_sha256','primary_statistics_excluded','validated_union_authorized']:need(lineage[k]==auth[k],'IR lineage drift '+k)
  need(lineage['reuse_old_UUID']is False and lineage['automatic_retry']is False and lineage['refunds']==0 and lineage['new_grants']==1,'IR no retry/refund boundary')
 return row
def _canonical(cfg,c,slot):
 root=P(cfg['root']);path=root/'control/specs'/(c+'.json');alias=root/'control'/(c+'_SPEC.json');s=read(path);need(s['cohort']==c and s['host_cpu']is None and sha(path)==sha(alias)==slot['current_admitted_spec_sha256'],'canonical/alias/current grant mismatch')
 contract=read(cfg['scope_contract_path']);verify_science_scope(s,c,contract)
 return s,sha(path),path.read_text()
def project_for_candidate(base,cfg,cohort,selected_cpu=None,evidence=None,slot_evidence=None,context=None,legal_cpu_evidence=None):
 need(cohort in cfg['allowed_cohorts'],'outside shared scope');kind=(context or{}).get('kind','NATIVE'if selected_cpu is not None else'OWNER_FRAME');need(kind in['OWNER_FRAME','OWNER_CHOOSE','NATIVE']and(kind!='NATIVE'or type(selected_cpu)is int),'context/selected CPU')
 need(slot_evidence is not None,'fresh shared slot evidence required');verify_slot_evidence(slot_evidence,cfg,cohort,selected_cpu);spec,h,canonical_utf8=_canonical(cfg,cohort,slot_evidence)
 evidence=evidence or sample_cpu_evidence(selected_cpu,prospective_cpu_threads=slot_evidence['prospective_cpu_threads']);cpu=verify_cpu_evidence(evidence,selected_cpu,slot_evidence['prospective_cpu_threads']);need(legal_cpu_evidence is not None,'original legal CPU evidence required');verify_legal_cpu_evidence(legal_cpu_evidence,cfg,cohort,selected_cpu)
 now=time.monotonic();raw=copy.deepcopy(_CPU2._raw(base));need(evidence['raw_cpu2_evidence']['second']['boot_id']==raw['boot_id'],'CPU/memory boot mismatch')
 for stamp in[evidence['raw_cpu2_evidence']['second']['completed_monotonic'],slot_evidence['created_monotonic'],legal_cpu_evidence['sample']['monotonic'],raw['monotonic']]:need(0<=now-stamp<=2.,'fresh admission evidence expired')
 old95=_OLD.project(raw);reasons=old95['admission_decision']['pressure_reasons'];effective=[r for r in reasons if r!='cpu_pressure_full'];total=old95['total_projected_additional_RAM_bytes'];decision=dict(old95['admission_decision'],pressure_reasons=effective,pressure_pause_new=bool(effective),pass_admission=not effective and total<=budget(old95))
 certificate=validate_broad_approval(cfg)
 proof=dict(schema=ID,mode=MODE,config=copy.deepcopy(cfg),context=dict(kind=kind,cohort=cohort,selected_cpu=selected_cpu),base_resource_snapshot=raw,old95_resource_snapshot=old95,cpu_evidence=copy.deepcopy(evidence),cpu_assessment=cpu,slot_evidence=copy.deepcopy(slot_evidence),legal_cpu_evidence=copy.deepcopy(legal_cpu_evidence),canonical_spec_utf8=canonical_utf8,canonical_spec_sha256=h,raw_pressure_reasons=copy.deepcopy(reasons),effective_pressure_reasons=effective,effective_decision=decision,growth_unchanged_bytes=total,created_monotonic=now,CPU2_spare_PASS_claimed=False,shared_CPU_is_idle_spare=False,design_contract_utf8=P(cfg['design_contract_path']).read_text(),broad_approval_utf8=certificate['certificate_utf8'],broad_gate_utf8=certificate['gate_utf8'],broad_source_artifacts_utf8=certificate['source_artifacts_utf8'],scope_contract_utf8=certificate['scope_contract_utf8'])
 verify_proof(proof,require_native=False);return dict(old95,physical_RAM_pass=decision['pass_admission'],admission_decision=decision,**{PROOF:proof})
def verify_proof(p,require_native=False):
 need(p['schema']==ID and p['mode']==MODE and p['CPU2_spare_PASS_claimed']is False and p['shared_CPU_is_idle_spare']is False,'wrong shared proof')
 cfg=p['config'];c=p['context'];need(hashlib.sha256(p['design_contract_utf8'].encode()).hexdigest()==cfg['design_contract_sha256']==DESIGN_SHA,'design snapshot mismatch');need(cfg['cpu_shared_policy']==POLICY and cfg['max_shared_running']is None,'proof policy drift')
 need(cfg['schema']==cfg['overlay_id']==ID and cfg['request']==REQ and cfg['scope_mode']=='ALL_ALLOWED_ADMITTED_UNSPENT'and cfg['memory_utilization_fraction']==.95 and cfg['host_floor_bytes']==cfg['cgroup_floor_bytes']==10*G,'proof generation/RAM policy drift')
 need(cfg['qualification_stage']=='AFTER_REAL_ENGINEERING4_GATE','unknown broad proof stage');validate_broad_approval(cfg,None,p['broad_approval_utf8'],p['broad_gate_utf8'],p['broad_source_artifacts_utf8'],p['scope_contract_utf8'])
 need(c['cohort']in cfg['allowed_cohorts']and c['kind']in['OWNER_FRAME','OWNER_CHOOSE','NATIVE'],'proof scope/context');spec=json.loads(p['canonical_spec_utf8']);need(hashlib.sha256(p['canonical_spec_utf8'].encode()).hexdigest()==p['canonical_spec_sha256']==p['slot_evidence']['current_admitted_spec_sha256']and spec['cohort']==c['cohort']and spec['host_cpu']is None,'proof canonical identity')
 contract=json.loads(p['scope_contract_utf8']);verify_science_scope(spec,c['cohort'],contract)
 raw=p['base_resource_snapshot'];need(raw['source_module_sha256']==cfg['expected_pins'][str(RES)]and raw['policy_sha256']==cfg['expected_pins'][str(RPOLICY)],'raw source/policy mismatch');need('additional_padding_admission_proof'not in raw,'shared mode requires NOFLAG full cost')
 rows=raw['RAM_reservation_entries']+raw['own_ram_forecasts'];need(all(type(x['additional_reserved_bytes'])is int and x['additional_reserved_bytes']>=0 for x in rows)and sum(x['additional_reserved_bytes']for x in rows)==raw['total_projected_additional_RAM_bytes'],'full peer/own/claim growth sum')
 old95=_OLD.project(raw);need(objsha(old95)==objsha(p['old95_resource_snapshot']),'raw/old95 modified');need(raw['total_projected_additional_RAM_bytes']==p['growth_unchanged_bytes'],'growth changed')
 cpu=verify_cpu_evidence(p['cpu_evidence'],c['selected_cpu'],p['slot_evidence']['prospective_cpu_threads']);need(cpu==p['cpu_assessment'],'CPU assessment changed');verify_slot_evidence(p['slot_evidence'],cfg,c['cohort'],c['selected_cpu']);verify_legal_cpu_evidence(p['legal_cpu_evidence'],cfg,c['cohort'],c['selected_cpu'])
 claims=json.loads(p['slot_evidence']['claims_utf8'])['claims']
 for claim_c,cost in p['slot_evidence']['unspent_claim_canonical_costs'].items():
  own=[r for r in raw['own_ram_forecasts']if r['cohort']==claim_c];need(len(own)==1 and own[0]['kind']=='CLAIM_OR_CANDIDATE'and own[0]['RSS_bytes']==0 and own[0]['additional_reserved_bytes']==cost['estimated_peak_model_RAM_bytes'],'other claim full RAM omitted/discounted')
 need(p['legal_cpu_evidence']['other_claims']=={k:v for k,v in claims.items()if k!=c['cohort']},'original allocator dropped other claims')
 need(p['cpu_evidence']['raw_cpu2_evidence']['second']['boot_id']==raw['boot_id']==p['legal_cpu_evidence']['sample']['boot_id'],'resource/CPU/allocator boot mismatch')
 for stamp in[p['cpu_evidence']['raw_cpu2_evidence']['second']['completed_monotonic'],p['slot_evidence']['created_monotonic'],p['legal_cpu_evidence']['sample']['monotonic'],raw['monotonic']]:need(0<=p['created_monotonic']-stamp<=2.,'evidence stale at proof')
 effective=[x for x in old95['admission_decision']['pressure_reasons']if x!='cpu_pressure_full'];decision=dict(old95['admission_decision'],pressure_reasons=effective,pressure_pause_new=bool(effective),pass_admission=not effective and raw['total_projected_additional_RAM_bytes']<=budget(old95))
 need(p['raw_pressure_reasons']==old95['admission_decision']['pressure_reasons']and p['effective_pressure_reasons']==effective and p['effective_decision']==decision,'pressure changed beyond explicit sharedCPUfull')
 need(decision['pass_admission']and old95['physical_disk_pass']and old95['own_write_ceiling_pass']and old95['native_free_bytes']>old95['required_free_bytes']and old95['free_inodes']>=100000,'other physical/pressure gate HOLD')
 if c['kind']!='OWNER_FRAME':
  candidate=[r for r in raw['own_ram_forecasts']if r['cohort']==c['cohort']];need(len(candidate)==1 and candidate[0]['kind']=='CLAIM_OR_CANDIDATE'and candidate[0]['RSS_bytes']==0 and candidate[0]['additional_reserved_bytes']==spec['estimated_peak_model_RAM_bytes'],'candidate missing/discounted/duplicate')
 if require_native:
  need(c['kind']=='NATIVE'and type(c['selected_cpu'])is int,'native requires selected CPU/NATIVE context');f=p['native_full_forecast'];need(f['cohort']==c['cohort']and f['selected_cpu']==c['selected_cpu']and f['canonical_spec_sha256']==p['canonical_spec_sha256'],'forecast identity mismatch')
  need(f['canonical_estimated_peak_model_RAM_bytes']==spec['estimated_peak_model_RAM_bytes']and f['forecast_input_spec']==dict(spec,host_cpu=c['selected_cpu'])and f['forecast']['predicted_peak_RAM_bytes']<=spec['estimated_peak_model_RAM_bytes'],'full forecast/canonical underbound')
  need(hashlib.sha256(f['history_utf8'].encode()).hexdigest()==f['history_sha256']and hashlib.sha256(f['resource_policy_utf8'].encode()).hexdigest()==f['resource_policy_sha256']==cfg['expected_pins'][str(RPOLICY)],'forecast inputs SHA')
  mod=load('shared_offline_full_forecast',RES);need(f['forecast_source_sha256']==cfg['expected_pins'][str(RES)]==sha(RES)and mod.forecast(f['forecast_input_spec'],json.loads(f['history_utf8']),json.loads(f['resource_policy_utf8']))==f['forecast'],'full forecast recomputation')
 return dict(status='PASS_CPU_SHARED_TIMESLICE_RESOURCE_NOT_CPU2_SPARE',cohort=c['cohort'],selected_cpu=c['selected_cpu'],CPU2_spare_PASS_claimed=False,full_growth_bytes=p['growth_unchanged_bytes'],budget_bytes=budget(old95),cpu_assessment=cpu)
verify_memory_proof=verify_proof
def _invocation():
 a=sys.argv[1:];need(len(a)>=5 and a[:2]in[['experiment','prepare'],['experiment','run-native'],['experiment','inspect']]and a[3:5]==['--project','DTC_L1'],'unbound invocation');return a[2],a
def _forecast(native,c):
 spec=native.spec_for(c);hp=R/'control/HISTORICAL_RSS.json';history=hp.read_text();policy=RPOLICY.read_text();mod=load('shared_original_full_forecast',RES);forecast=mod.forecast(spec,json.loads(history),json.loads(policy));need(forecast['predicted_peak_RAM_bytes']<=spec['estimated_peak_model_RAM_bytes'],'CANONICAL_FULL_FORECAST_REFRESH_REQUIRED')
 return dict(cohort=c,selected_cpu=spec['host_cpu'],canonical_spec_sha256=native.registered()[2]['admitted_specs'][c],canonical_estimated_peak_model_RAM_bytes=spec['estimated_peak_model_RAM_bytes'],forecast_input_spec=spec,forecast=forecast,history_utf8=history,history_sha256=hashlib.sha256(history.encode()).hexdigest(),resource_policy_utf8=policy,resource_policy_sha256=hashlib.sha256(policy.encode()).hexdigest(),forecast_source_sha256=sha(RES))
def install_future_native(native,cfg,padding=False,invocation_cohort=None):
 q=native.registered()[2];validate(cfg,q);cohort,argv=_invocation()if invocation_cohort is None else(invocation_cohort,['CPU_FIXTURE_EXPLICIT_INVOCATION',invocation_cohort]);need(eligible_cohort(cfg,q,cohort,'NATIVE')and not padding,'not unused approved NOFLAG shared cohort');need(not hasattr(native,'_CPU_SHARED_BINDING'),'shared overlay already installed')
 need(invocation_cohort is None or cfg['qualification_only']and q.get('qualification_only')is True,'explicit invocation fixture only')
 parent=copy.deepcopy(native.assert_parent_lease());original=native.resources;proofs=[];forecasts=[]
 def resources(spec,fresh_source=False):
  if not fresh_source:return original(spec,False)
  q=native.registered()[2];validate(cfg,q);need(eligible_cohort(cfg,q,cohort,'NATIVE'),'shared cohort spent/sealed');selected=native.spec_for(cohort)['host_cpu'];forecasts.append(_forecast(native,cohort));slot=capture_slot_evidence(cfg,q,cohort,selected,root=native.R);cpu=sample_cpu_evidence(selected,prospective_cpu_threads=slot['prospective_cpu_threads']);claims=json.loads(slot['claims_utf8'])['claims'];legal=capture_legal_cpu_evidence(cfg,claims,cohort,selected)
  value=project_for_candidate(original(spec,True),cfg,cohort,selected,cpu,slot,{'kind':'NATIVE'},legal);value[PROOF]['native_full_forecast']=copy.deepcopy(forecasts[-1]);verify_proof(value[PROOF],True);proofs.append(copy.deepcopy(value[PROOF]));return value
 native.resources=resources;old_engine=native.engine
 def engine():
  n=old_engine();old=n.exclusive;binding=dict(schema=ID,request=REQ,cohort=cohort,mode=MODE,padding_optin=False,qualified_sources=cfg['qualified_sources'],config_sha256=objsha(cfg),QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],snapshot_sha256=None,selected_cpu=None,final_cpu_evidence_sha256=None,final_slot_evidence_sha256=None,CPU2_spare_PASS_claimed=False)
  def exclusive(path,obj):
   path=P(path)
   if path.name.endswith('.INTENT.json'):
    validate(cfg,native.registered()[2]);need(obj['cohort']==cohort and native.assert_parent_lease()==parent,'intent/lease changed');resources(native.spec_for(cohort),True);[verify_proof(p,True)for p in proofs];final=proofs[-1];out=P(obj['output']);cp=native.R/'control/specs'/(cohort+'.json');db=native.R/'control/dispatch_bindings'/(cohort+'.json');row=copy.deepcopy(native.registered()[2]['additional_operational_overlays'][ID])
    snapshot=dict(schema=ID,mode=MODE,padding_optin=False,config=copy.deepcopy(cfg),record=row,overlay_record=copy.deepcopy(row),fresh_preflights=proofs,full_forecast_preflights=forecasts,invocation=dict(argv=argv,cohort=cohort,selected_cpu=final['context']['selected_cpu'],parent_lease=parent,native_source_path=str(native.__file__),native_source_sha256=sha(native.__file__)),canonical_spec_utf8=cp.read_text(),canonical_spec_sha256=sha(cp),dispatch_binding_utf8=db.read_text(),dispatch_binding_sha256=sha(db),source_snapshots={r:dict(path=cfg['source_paths'][r],sha256=cfg['qualified_sources'][r],utf8=P(cfg['source_paths'][r]).read_text())for r in ROLES},QA_utf8=P(cfg['QA_path']).read_text(),readback_utf8=P(cfg['readback_path']).read_text(),io_active_utf8=P(cfg['io_active_path']).read_text(),design_contract_utf8=P(cfg['design_contract_path']).read_text(),CPU2_spare_PASS_claimed=False)
    snapshot['broad_approval_utf8']=final['broad_approval_utf8'];snapshot['broad_gate_utf8']=final['broad_gate_utf8'];snapshot['broad_source_artifacts_utf8']=copy.deepcopy(final['broad_source_artifacts_utf8']);snapshot['scope_contract_utf8']=final['scope_contract_utf8']
    atomic(out/SNAP,snapshot);binding.update(snapshot_sha256=sha(out/SNAP),selected_cpu=final['context']['selected_cpu'],final_cpu_evidence_sha256=objsha(final['cpu_evidence']),final_slot_evidence_sha256=objsha(final['slot_evidence']))
   if path.name.endswith('.INTENT.json')or path.name in['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
    need(binding['snapshot_sha256'],'shared INTENT snapshot absent');obj=dict(obj,**{FIELD:copy.deepcopy(binding)})
   return old(path,obj)
  n.exclusive=exclusive;return n
 native.engine=engine;native._CPU_SHARED_BINDING=dict(schema=ID,cohort=cohort,config_sha256=objsha(cfg),source_sha256=sha(__file__));return native
