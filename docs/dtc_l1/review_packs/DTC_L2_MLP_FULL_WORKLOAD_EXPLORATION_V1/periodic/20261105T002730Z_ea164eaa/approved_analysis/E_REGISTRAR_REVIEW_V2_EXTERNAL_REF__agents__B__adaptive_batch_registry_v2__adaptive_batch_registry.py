"""Inert additive AD1 batch registry. prepare is read-only; Main commits explicitly.

No dispatcher/scope/consumer/source installation, no automatic selection/retry.
Normalized candidate schema is explicit; an unqualified schema adapter cannot
release production. All authority callbacks use passed q and file CAS only.
"""
import pathlib,json,hashlib,copy,os,sys,threading,types,subprocess,math,importlib.util
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ROLE='ADAPTIVE_PARAMETER_PERFORMANCE_TRIAL'
ID='DTC_ADAPTIVE_BATCH_REGISTRY_V2'
FROZEN_SCOPE_SHA='5f079aed36eca8dd62906bdfaa68006d3b3f27964c506a03361f2fab0908d1d2'
NATIVE_SHA='e8276aadbb243b29166d89e5e937de260e6017061b475b62ac9c6c6f3dc3825a'
OPS_SHA='a53f4933d2f0a7479a15d0e6dd8aa0501c4762d6b2161363b9467472a43fc1dc'
BASE=dict(entries=192,merge=4,miss_queue=32,frfcfs=64)
TARGETS={'-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'}
def read(p):return json.loads(P(p).read_bytes())
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def objsha(v):return hashlib.sha256(raw(v)).hexdigest()
def compactsha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def terminal_adapter(cfg):
 path=cfg['terminal_adapter_path'];assert sha(path)==cfg['terminal_adapter_sha256']and cfg['dependency_pins'][path]==cfg['terminal_adapter_sha256']
 s=importlib.util.spec_from_file_location('source_pinned_terminal_membership_adapter_v2',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def natural_receipt_evolution(initial,current,root):
 """Allow only existing consumed generations to acquire joined natural DONE.
 No changed grant/spec/UUID/new birth/negative closure can pass this recovery.
 """
 a=copy.deepcopy(initial);b=copy.deepcopy(current);assert set(a['consumed'])==set(b['consumed']),'OLD_COHORT_SET_CHANGED_DURING_RECOVERY'
 changed=[]
 for c,old in a['consumed'].items():
  new=b['consumed'][c]
  if new==old:continue
  assert 'execution_receipt'not in old and set(new)==set(old)|{'execution_receipt'}and {k:v for k,v in new.items()if k!='execution_receipt'}==old,'ONLY_NEW_NATURAL_RECEIPT_ALLOWED'
  receipt=new['execution_receipt'];assert receipt['cohort']==c and receipt['uuid']==old['uuid']and receipt['stop_reason']is None and receipt['launcher_wait_returncode']==0
  assert read(P(root)/'control/qualification_ledger'/(c+'.DONE.json'))==receipt,'NATURAL_RECEIPT_MISSING_JOINED_DONE'
  b['consumed'][c]=copy.deepcopy(old);changed.append(c)
 if b.get('state')!=a.get('state'):
  assert changed and b.get('state')=='RUNNING';b['state']=a['state']
 assert b==a,'NON_RECEIPT_Q_EVOLUTION_DURING_PARTIAL_RECOVERY'
 return changed
def immutable(p,b):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,'IMMUTABLE_FILE_CONFLICT';return
 tmp=p.with_name('.'+p.name+'.'+os.urandom(6).hex())
 try:
  with tmp.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
  try:os.link(tmp,p)
  except FileExistsError:assert p.read_bytes()==b
 finally:
  if tmp.exists():tmp.unlink()
 fd=os.open(p.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def resource_independent(s):
 v=copy.deepcopy(s);v.pop('estimated_peak_model_RAM_bytes')
 for k in ['max_process_tree_rss_bytes','max_process_tree_vms_bytes']:v['limits'].pop(k)
 return v
def expected_options(parameters):
 assert set(parameters)==set(BASE)and all(type(v)is int and BASE[k]<=v<=2147483647 for k,v in parameters.items())
 assert parameters['entries']<=1073741823
 return {'-gpgpu_cache:dl2':[f"S:128:128:16,L:B:m:L:L,A:{parameters['entries']}:{parameters['merge']},{parameters['miss_queue']}:0,32"],'-gpgpu_frfcfs_dram_sched_queue_size':[str(parameters['frfcfs'])]}
def validate_new_science(s,base,row):
 assert s['request']==REQ and s['cohort']==row['cohort']and s['host_cpu']is None and s['scientific_role']==ROLE
 assert s['input_digest']==row['input_digest']==base['input_digest']and s['cell']==row['cell']==base['cell']and s['profile']==s['downstream_profile']==row['profile']
 assert s['expected_options']==dict(base['expected_options'],**expected_options(row['parameters']))and len(s['expected_options'])==270
 assert len(s['native_simulator_argv'])==3+2*len(s['configs'])and s['native_simulator_argv'][:3]==base['native_simulator_argv'][:3]
 assert s['native_simulator_argv'][3:]==sum([['-config',x['path']]for x in s['configs']],[])
 allowed={'cohort','profile','downstream_profile','scientific_role','adaptive_trial_lineage','baseline_reference','candidate_only','candidate_status','resource_qualification','expected_options','configs','native_simulator_argv','estimated_peak_model_RAM_bytes','limits'}
 assert {k:v for k,v in s.items()if k not in allowed}=={k:v for k,v in base.items()if k not in allowed},'NON_TARGET_GPU_INPUT_SOURCE_FIELD_CHANGED'
 assert {k:v for k,v in s['limits'].items()if k not in ['max_process_tree_rss_bytes','max_process_tree_vms_bytes']}=={k:v for k,v in base['limits'].items()if k not in ['max_process_tree_rss_bytes','max_process_tree_vms_bytes']}
 assert s['estimated_peak_model_RAM_bytes']>=base['estimated_peak_model_RAM_bytes']and s['limits']['max_process_tree_rss_bytes']>=base['limits']['max_process_tree_rss_bytes']and s['limits']['max_process_tree_vms_bytes']>=base['limits']['max_process_tree_vms_bytes']
 lineage=s['adaptive_trial_lineage'];assert lineage==row['original_candidate_lineage']
 assert lineage['schema']=='AD1_UNIFORM_CH_MATCHING_CANDIDATE_LINEAGE_V1'and lineage['cohort']==s['cohort']and lineage['parent_cohort']==base['cohort']and lineage['parent_spec_sha256']==row['base_spec_sha256']
 assert lineage['uniform_parameters']==row['parameters']and lineage['old_UUID_reused']is False and lineage['union_authorized']is False
 assert lineage['new_model_grants']==lineage['models_started']==0 and lineage['registered']is lineage['selected']is False
 assert s['candidate_only']is True and s['candidate_status']=='PENDING_NOT_REGISTERED_NOT_SELECTED'
 assert s['baseline_reference']['status']=='UNRESOLVED'and s['baseline_reference']['derived_reference_qualified']is False and s['baseline_reference']['accepted_cycles']is None
 assert s['resource_qualification']['source_and_resource_generation_qualified']is False
 return compactsha(resource_independent(s))
def effective(texts):
 v={}
 for text in texts:
  for line in text.splitlines():
   line=line.split('#',1)[0].strip()
   if line:
    k,*rest=line.split(None,1)
    if k.startswith('-'):v[k]=rest[0].strip()if rest else''
 return v
def validate_config(s,base):
 before=effective([P(x['path']).read_text()for x in base['configs']]);after=effective([P(x['path']).read_text()for x in s['configs']])
 assert {k:v for k,v in before.items()if k not in TARGETS}=={k:v for k,v in after.items()if k not in TARGETS},'CONFIG_NON_TARGET_CHANGED'
 for x in s['configs']+base['configs']:assert sha(x['path'])==x['sha256']
 for k in TARGETS:assert s['expected_options'][k]==[after[k]]

class AdaptiveBatchRegistry:
 def __init__(self,root,engine,frame,cfg,fault_hook=None):
  self.root=P(root);self.engine=engine;self.frame=frame;self.cfg=copy.deepcopy(cfg);self.lock=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED.lock;self.fault_hook=fault_hook
 def checkpoint(self,k):
  if self.fault_hook:self.fault_hook(k)
 def owner(self):
  assert threading.current_thread()is threading.main_thread()and self.frame.f_locals['engine']is self.engine and self.frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED.lock is self.lock
  self.engine.assert_parent_lease();reg,epoch,q,plan=self.engine.registered()
  if self.cfg['qualification_only']:assert q.get('qualification_only')is True and self.root!=R
  else:
   assert self.root==R and not q.get('qualification_only',False)and os.getpid()==plan['parent_pid']==1498278
   assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']==977758783
   assert isinstance(self.frame,types.FrameType)and sha(self.frame.f_code.co_filename)==OPS_SHA and sha(self.engine.__file__)==NATIVE_SHA
   assert P(self.engine.update_authority.__code__.co_filename)==R/'tools/l2_native.py'
  assert q['request']==REQ and q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed'])
  return q
 def fresh_sources(self):
  cfg=self.cfg;q=self.owner();assert cfg['schema']=='ADAPTIVE_BATCH_REGISTRY_CONFIGURATION_V1'and cfg['source_sha256']==sha(__file__)
  for k in ['catalog','approval','source_manifest','QA','readback']:assert sha(cfg[k+'_path'])==cfg[k+'_sha256'],'PIN_DRIFT '+k
  for p,h in cfg['dependency_pins'].items():assert sha(p)==h
  terminal=terminal_adapter(cfg)
  for worktree in cfg['source_worktree_checks']:
   result=subprocess.run(['git','-C',worktree['path'],'rev-parse','HEAD'],capture_output=True,text=True,timeout=10,check=True);assert result.stdout.strip()==worktree['commit'],'BUILD_HEAD_DRIFT'
   result=subprocess.run(['git','-C',worktree['path'],'status','--porcelain'],capture_output=True,text=True,timeout=10,check=True);assert not result.stdout.strip(),'DIRTY_SOURCE_WORKTREE'
  qa=read(cfg['QA_path']);rb=read(cfg['readback_path'])
  assert qa['status']=='PASS_ADAPTIVE_BATCH_ISOLATED_TRANSACTION_CPU'and qa['source_sha256']==rb['source_sha256']==cfg['source_sha256']and qa['pure_EX_callback_qualified']is True
  assert rb['verified']is True and rb['QA_sha256']==cfg['QA_sha256']
  if not cfg['qualification_only']:assert qa['actual_candidate_schema_qualified']is True and not qa.get('qualification_only',False)and not rb.get('qualification_only',False)
  source=read(cfg['source_manifest_path'])
  assert source['status']=='PENDING_NOT_REGISTERED_NOT_SELECTED'and source['request']==REQ
  for m in source['members']:assert sha(m['path'])==m['sha256']
  cat=read(cfg['catalog_path']);app=read(cfg['approval_path'])
  assert cat['schema']=='NORMALIZED_ADAPTIVE_CH_AD1_CANDIDATES_V1'and cat['request']==REQ and cat['status']=='PENDING_NOT_REGISTERED_NOT_SELECTED'
  assert app['schema']=='ADAPTIVE_BATCH_STAGE_SELECTION_APPROVAL_V1'and app['request']==REQ and app['approved_for_registration']is True
  assert app['candidate_catalog_sha256']==cfg['catalog_sha256']and app['source_manifest_sha256']==cfg['source_manifest_sha256']and app['registrar_source_sha256']==cfg['source_sha256']
  assert app['same_goal_authorization_path']==cfg['same_goal_authorization_path']and sha(app['same_goal_authorization_path'])==app['same_goal_authorization_sha256']==cfg['same_goal_authorization_sha256']
  authority=read(app['same_goal_authorization_path']);assert authority['adaptive_expansion_and_combinations_authorized']is True and authority['total_start_limit']is None
  assert authority['technical_finite_registration']=='exact matrix starts; extensions receive corresponding additive credits, never reset/refund'
  assert app['new_grants']==len(app['selected_cohorts'])and app['refunds']==0 and app['automatic_retry']is False and app['changes_initial350_membership']is False
  scopepath=P(cat['frozen_scope_path']);assert sha(scopepath)==cat['frozen_scope_sha256']==FROZEN_SCOPE_SHA
  scope=read(scopepath);digests=sorted({p['input_digest']for p in scope['points']});assert len(scope['points'])==350 and len(digests)==35 and cat['frozen_input_digests']==digests
  assert set(digests)==set(authority['input_digests'])and cat['initial350_matrix_sha256']==cfg['initial350_matrix_sha256']==sha(self.root/'control/MATRIX_CURRENT.json')
  selected=set(app['selected_cohorts']);assert len(selected)==app['new_grants']and selected
  rows=[r for r in cat['rows']if r['cohort']in selected];assert len(rows)==len(selected)and len({r['cohort']for r in cat['rows']})==len(cat['rows'])
  vectors={(r['profile'],r['cell'],objsha(r['parameters']))for r in rows}
  assert all({r['input_digest']for r in rows if(r['profile'],r['cell'],objsha(r['parameters']))==v}==set(digests)and sum((r['profile'],r['cell'],objsha(r['parameters']))==v for r in rows)==35 for v in vectors),'NOT_UNIFORM_ALL35_BATCH'
  assert {(r['profile'],r['cell'])for r in rows}<={('F128','CH'),('F256','CH')},'THIS_CANDIDATE_REGISTRAR_LIMITED_TO_PENDING_CH_F128_F256'
  assert app['selected_vectors']==sorted([dict(profile=p,cell=c,parameters=next(r['parameters']for r in rows if r['profile']==p and r['cell']==c))for p,c,_ in vectors],key=lambda x:(x['profile'],x['cell']))
  # Selection kinds have different evidence prerequisites. Necessary matched CH
  # can precede all35 DH completion, but A's old candidate gate is NOT silently
  # waived: an explicit versioned Root supersession record is required below.
  kind=app['selection_kind'];assert kind in['MATCHED_CH_FOLLOWUP','BOUNDARY_OR_COMBINATION'];completion=None
  needs_completion=kind=='BOUNDARY_OR_COMBINATION'or app.get('execution_order_mode')=='ORIGINAL_CANDIDATE_GATE_SATISFIED'
  if needs_completion:
   cp=app['initial_single_factor_completion'];assert sha(cp['path'])==cp['sha256'];completion=read(cp['path'])
   assert completion['schema']=='INITIAL35_SINGLE_FACTOR_TERMINAL_STATUS_EVIDENCE_V1'and completion['request']==REQ and completion['frozen_scope_sha256']==FROZEN_SCOPE_SHA
   assert completion['all_initial350_statuses_terminal']is True and completion['pending_count']==completion['running_count']==completion['unknown_count']==0 and len(completion['cell_evidence'])==350
   assert {r['cohort']for r in completion['cell_evidence']}=={r['cohort']for r in scope['points']}
   for r in completion['cell_evidence']:terminal.validate_row(r,q,self.root)
  if kind=='MATCHED_CH_FOLLOWUP':
   proof=app['matched_DH_evidence'];assert sha(proof['path'])==proof['sha256'];evidence=read(proof['path'])
   assert app['formal_winner_selected']is False and app['formal_adoption_authorized']is False and app['IR_R2_engineering_union_authorized']is False
   for profile in {r['profile']for r in rows}:
    stats=evidence['statistics'][profile]['ALL']['fixed_common'];values=stats['values'];population=stats['population']
    assert set(values)==set(population)and len(population)==stats['n']and set(population)<=set(digests)and len(population)>0
    gm=math.exp(sum(math.log(x)for x in values.values())/len(values));assert all(x>0 for x in values.values())and math.isclose(gm,stats['GM'],rel_tol=1e-12)
    reason=app['matching_purpose'];assert reason in['EFFECTIVE_DIRECTION_MATCH','MODERATE_UNIFORM_RESOURCE_CONTROL']
    if reason=='EFFECTIVE_DIRECTION_MATCH':assert gm>=1.01,'INTERNAL_EFFECT_SCREEN_NOT_MET'
    else:assert isinstance(app['explicit_uniform_control_justification'],str)and app['explicit_uniform_control_justification'].strip()
   if not needs_completion:
    assert app['execution_order_mode']=='EXPLICIT_ROOT_SUPERSESSION_FOR_NECESSARY_CH'
    cp=app['superseding_execution_order_review'];assert sha(cp['path'])==cp['sha256'];review=read(cp['path'])
    assert review['schema']=='DTC_MAIN_AD1_MATCHED_CH_EXECUTION_ORDER_REVIEW_V1'and review['request']==REQ and review['status']=='APPROVED_EXECUTION_ORDER_REVISION_ONLY'
    assert review['owner_pid']==1498278 and review['owner_start_ticks']==977758783 and review['candidate_catalog_sha256']==cfg['catalog_sha256']
    assert set(review['selected_cohorts'])==selected and review['earlier_necessary_CH_matching_approved']is True
    assert review['original_candidate_bytes_unchanged']is True and review['parameter_families_inputs_physics_unchanged']is True and review['formal_adoption_authorized']is False
    assert review['matched_DH_evidence_sha256']==proof['sha256']and review['original_candidate_batch_gates']==cat['candidate_batch_activation_gates']
  frozen_rows=[]
  for row in rows:
   assert row['role']==ROLE and row['candidate_set_id']==cat['candidate_set_id']and sha(row['spec_path'])==row['spec_sha256']
   spec=read(row['spec_path']);base=read(row['base_spec_path']);assert sha(row['base_spec_path'])==row['base_spec_sha256']
   assert row['base_cohort']==base['cohort']and any(p['cohort']==base['cohort']and p['profile']=='P0'and p['input_digest']==spec['input_digest']and p['cell']==spec['cell']for p in scope['points'])
   science=validate_new_science(spec,base,row);validate_config(spec,base)
   admitted=copy.deepcopy(spec);admitted['adaptive_registration_binding']=dict(schema='AD1_SOURCE_BOUND_REGISTRATION_PROVENANCE_V1',original_candidate_spec_sha256=row['spec_sha256'],original_candidate_lineage_sha256=objsha(row['original_candidate_lineage']),stage_selection_approval_sha256=cfg['approval_sha256'],selection_kind=kind,superseding_execution_order_review_sha256=app.get('superseding_execution_order_review',{}).get('sha256'),candidate_flags_and_original_gate_are_immutable_construction_provenance=True,registration_is_not_runtime_activation=True,new_grants=1,refunds=0,automatic_retry=False)
   frozen_rows.append(dict(row=copy.deepcopy(row),spec=admitted,candidate_spec=spec,initial_spec_sha256=objsha(admitted),science_sha256=science))
  if not cfg['qualification_only']:
   required={s['source_worktrees'][k]:s[k+'_commit']for i in frozen_rows for s in[i['spec']]for k in ['core','framework']}
   assert {w['path']:w['commit']for w in cfg['source_worktree_checks']}==required,'EXACT_CURRENT_BUILD_WORKTREE_CHECKS_REQUIRED'
  return q,cat,app,completion,frozen_rows
 def prepare(self):
  """Read-only, including no transaction directory or lockfile creation."""
  with self.lock:
   q,cat,app,completion,rows=self.fresh_sources();batch_id=objsha(dict(schema=ID,catalog_sha256=self.cfg['catalog_sha256'],approval_sha256=self.cfg['approval_sha256'],selected_cohorts=sorted(app['selected_cohorts'])))
   for item in rows:
    c=item['spec']['cohort'];assert c not in q['admitted_specs']and c not in q['consumed']
    for path in[self.root/'control/specs'/(c+'.json'),self.root/'control'/(c+'_SPEC.json'),self.root/'control/qualification_ledger'/(c+'.INTENT.json'),self.root/'control/dispatch_bindings'/(c+'.json')]:assert not path.exists(),'NEW_IDENTITY_ALREADY_PRESENT'
   return dict(schema='ADAPTIVE_BATCH_PREPARED_PROPOSAL_V1',batch_id=batch_id,configuration=copy.deepcopy(self.cfg),rows=rows,initial350_matrix_utf8=(self.root/'control/MATRIX_CURRENT.json').read_text(),initial350_matrix_sha256=self.cfg['initial350_matrix_sha256'],frozen_scope_utf8=P(cat['frozen_scope_path']).read_text(),source_bound_selection=app,selection_sha256=self.cfg['approval_sha256'],new_grants=len(rows),refunds=0,registrar_installs_runtime=False)
 def folder(self,p):return self.root/'control/adaptive_parameter_batches'/p['batch_id']
 def validate_proposal(self,p):
  q,cat,app,completion,rows=self.fresh_sources();assert p['configuration']==self.cfg and p['rows']==rows and p['source_bound_selection']==app and p['selection_sha256']==self.cfg['approval_sha256']
  assert p['new_grants']==len(rows)and p['refunds']==0 and p['schema']=='ADAPTIVE_BATCH_PREPARED_PROPOSAL_V1'
  assert p['batch_id']==objsha(dict(schema=ID,catalog_sha256=self.cfg['catalog_sha256'],approval_sha256=self.cfg['approval_sha256'],selected_cohorts=sorted(app['selected_cohorts'])))and p['registrar_installs_runtime']is False
  assert hashlib.sha256(p['frozen_scope_utf8'].encode()).hexdigest()==FROZEN_SCOPE_SHA,'FROZEN_SCOPE_PREIMAGE_DRIFT'
  assert hashlib.sha256(p['initial350_matrix_utf8'].encode()).hexdigest()==p['initial350_matrix_sha256']==sha(self.root/'control/MATRIX_CURRENT.json')
  return q
 def reconcile(self,p):
  with self.lock:
   q=self.validate_proposal(p);cs={i['spec']['cohort']for i in p['rows']};records=[r for r in q.get('authorized_parameter_batches',[])if r.get('batch_id')==p['batch_id']];present=cs&set(q['admitted_specs'])
   if not present:
    assert not records and not(self.folder(p)/'COMMITTED.json').exists()
    for i in p['rows']:
     c=i['spec']['cohort'];assert c not in q['consumed']and not(self.root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(self.root/'control/dispatch_bindings'/(c+'.json')).exists()
     for path in[self.root/'control/specs'/(c+'.json'),self.root/'control'/(c+'_SPEC.json')]:
      if path.exists():assert sha(path)==i['initial_spec_sha256']
    return dict(state='UNGRANTED_SAFE_TO_CONTINUE',batch_id=p['batch_id'],new_grants=0)
   assert present==cs and len(records)==1;record=records[0];assert record==self.batch_record(p)
   for i in p['rows']:
    c=i['spec']['cohort'];current=self.engine.canonical(c)
    assert resource_independent(current)==resource_independent(i['spec'])and current['estimated_peak_model_RAM_bytes']>=i['spec']['estimated_peak_model_RAM_bytes']
    assert current['limits']['max_process_tree_rss_bytes']>=i['spec']['limits']['max_process_tree_rss_bytes']and current['limits']['max_process_tree_vms_bytes']>=i['spec']['limits']['max_process_tree_vms_bytes']
    assert q['admitted_inputs'][current['input_digest']]['specs'].count(c)==1
   result=dict(state='COMMITTED_RECONCILED',batch_id=p['batch_id'],cohorts=sorted(cs),new_grants=0,committed_grants=len(cs),runtime_scope_installed=False)
   immutable(self.folder(p)/'COMMITTED.json',raw(result));return result
 def batch_record(self,p):
  return dict(batch_id=p['batch_id'],role=ROLE,catalog_sha256=self.cfg['catalog_sha256'],source_manifest_sha256=self.cfg['source_manifest_sha256'],stage_selection_approval_sha256=p['selection_sha256'],selection_kind=p['source_bound_selection']['selection_kind'],superseding_execution_order_review_sha256=p['source_bound_selection'].get('superseding_execution_order_review',{}).get('sha256'),registrar_source_sha256=self.cfg['source_sha256'],cohorts=sorted(i['spec']['cohort']for i in p['rows']),initial_spec_sha256={i['spec']['cohort']:i['initial_spec_sha256']for i in p['rows']},science_sha256={i['spec']['cohort']:i['science_sha256']for i in p['rows']},new_grants=p['new_grants'],refunds=0,automatic_retry=False,initial350_statistics_excluded=True,validated_union_authorized=False,runtime_activation='REQUIRES_SEPARATELY_QUALIFIED_SOURCE_BOUND_STAGE')
 def commit(self,p):
  with self.lock:
   q=self.validate_proposal(p);prior=self.reconcile(p)
   if prior['state']=='COMMITTED_RECONCILED':return prior
   folder=self.folder(p);immutable(folder/'PREPARED.json',raw(p));immutable(folder/'preimages/MATRIX_INITIAL350.json',p['initial350_matrix_utf8'].encode());immutable(folder/'preimages/SCOPE_FROZEN.json',p['frozen_scope_utf8'].encode())
   original=folder/'preimages/Q_BEFORE.json'
   if not original.exists():immutable(original,raw(q))
   natural_receipt_evolution(read(original),q,self.root)
   immutable(folder/'attempts'/(objsha(q)+'.Q_CAS.json'),raw(q));self.checkpoint('AFTER_PREPARED')
   for i in p['rows']:
    c=i['spec']['cohort'];immutable(self.root/'control/specs'/(c+'.json'),raw(i['spec']));self.checkpoint('AFTER_FIRST_SPEC');immutable(self.root/'control'/(c+'_SPEC.json'),raw(i['spec']))
   self.checkpoint('AFTER_SPEC_PUBLICATION');before=self.validate_proposal(p);natural_receipt_evolution(read(original),before,self.root);immutable(folder/'attempts'/(objsha(before)+'.Q_CAS.json'),raw(before));batch=self.batch_record(p)
   def grant(reg):
    # No engine/registered/canonical/authority/forecast calls under EX.
    current=reg['registered_future_requests'][REQ];assert current==before,'AUTHORITY_Q_CAS_CHANGED'
    assert sha(self.root/'control/MATRIX_CURRENT.json')==p['initial350_matrix_sha256']
    assert not any(r.get('batch_id')==p['batch_id']for r in current.get('authorized_parameter_batches',[]))
    for i in p['rows']:
     c=i['spec']['cohort'];assert c not in current['admitted_specs']and c not in current['consumed']and c not in current['admitted_inputs'][i['spec']['input_digest']]['specs']
     assert sha(self.root/'control/specs'/(c+'.json'))==sha(self.root/'control'/(c+'_SPEC.json'))==i['initial_spec_sha256']
     assert not(self.root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(self.root/'control/dispatch_bindings'/(c+'.json')).exists()
    for i in p['rows']:
     s=i['spec'];c=s['cohort'];current['admitted_specs'][c]=i['initial_spec_sha256'];current['admitted_inputs'][s['input_digest']]['specs'].append(c)
    current['budget']+=p['new_grants'];current['remaining']+=p['new_grants'];current.setdefault('authorized_parameter_batches',[]).append(copy.deepcopy(batch))
    stripped=copy.deepcopy(current)
    for i in p['rows']:
     c=i['spec']['cohort'];del stripped['admitted_specs'][c];stripped['admitted_inputs'][i['spec']['input_digest']]['specs'].remove(c)
    stripped['budget']-=p['new_grants'];stripped['remaining']-=p['new_grants'];stripped['authorized_parameter_batches'].remove(batch)
    if'authorized_parameter_batches'not in before:del stripped['authorized_parameter_batches']
    assert stripped==before,'NONALLOWLIST_MUTATION'
   self.engine.update_authority(grant);self.checkpoint('AFTER_AUTHORITY');result=self.reconcile(p);self.checkpoint('AFTER_COMMITTED');return dict(result,new_grants=p['new_grants'])
