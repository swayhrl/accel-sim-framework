"""Read-only actual scientific view/installed-source transition review. No tests or writes outside E."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys,collections
P=pathlib.Path;H=P(__file__).resolve().parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
gp=R/'control/operational_amendments/typed_negative_full35_v2/terminal_gate.py';gate=load('terminal_gate',gp)
vp=gp.with_name('typed_analysis_view.py');viewmod=load('actual_typed_view',vp)
cfgpath=R/'control/operational_amendments/typed_negative_transport_v3/INSTALL_CONFIG.json';cfg=read(cfgpath)
pp=A/'agents/E/interaction_policy_v3/interaction_policy.py';policy=load('actual_interaction_c69',pp)
ip=R/'control/operational_amendments/interaction_policy_v3';ack=read(ip/'ACK.json')
for n,pin in ack['source_pins'].items():assert sha(A/'agents/E/interaction_policy_v3'/n)==pin
rawp=R/'analysis/AUTO_SUMMARY.json';rawbytes=rawp.read_bytes();raw=json.loads(rawbytes)
matrixp=R/'control/MATRIX_CURRENT.json';matrixbytes=matrixp.read_bytes();matrix=json.loads(matrixbytes);history=read(R/'control/SEARCH_HISTORY.json')
assert len(matrix['points'])==350
before=copy.deepcopy(raw)
view,proofs=viewmod.project(raw,cfg['bindings'],cfg['verifier']['path'],cfg['verifier']['sha256'])
def genuine_this_call(row,proof):assert proof is proofs[row['cohort']];return proof
previous=gate.recommend(view,matrix,history,cfg['source_paths'],cfg['source_pins'],proofs,genuine_this_call)
decision=policy.augment(previous,view,matrix,history)
decision=policy.validate_new_phases(decision,view,matrix,history,proofs)
assert raw==before and matrixp.read_bytes()==matrixbytes
ev=policy.Evidence(view,matrix,history,proofs)
initial_missing=[dict(profile=n,cell=c,input_digest=d,program=view['programs'][d]['program'],state=ev.row(d,n,c).get('state'))for n in policy.INITIAL for c in(('CH','DH')if n=='P0'else('DH',))for d in ev.ids if not ev.terminal(d,n,c)]
seedparents=[]
for label,over in policy.SEEDS:
 p=policy.normalize(over);parents=ev.parents([ev.resolve(dict(policy.BASE,**{k:p[k]}))for k in policy.AXES if p[k]!=policy.BASE[k]])
 seedparents.append(dict(seed=policy.name(p),parents=parents,requires_original_M16='M16'in parents,requires_R2=False,
  currently_missing_full35={n:len(ids)for n,ids in ev.missing(parents).items()}))
profiles={n:dict(DH_accepted=sum(ev.good(d,n)for d in ev.ids),CH_accepted=sum(ev.good(d,n,'CH')for d in ev.ids),DH_full35=ev.full(n))for n in policy.INITIAL}
negative=cfg['bindings'][0];cell=view['table'][negative['input_digest']]['M16']['DH'];rp=R/'analysis'/(negative['cohort']+'.RESULT.json')
batch=read(R/'analysis/BATCH_STATE.json');r2='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2'
cpuack=read(R/'control/operational_amendments/cpu_spare_memory_v2/ACK.json');syncack=read(R/'control/operational_amendments/future_memory_scope_sync_v1/ACK.json')
oldqa=A/'agents/E/interaction_policy_v3/CPU_QUALIFICATION.json';journalqa=A/'agents/E/interaction_policy_v3/JOURNAL_CPU_QUALIFICATION.json'
requiredpaths=[pp,A/'agents/E/interaction_policy_v3/owner_adapter.py',A/'agents/E/interaction_policy_v3/resource_qualifier.py',gp,vp,cfgpath,
 P(cfg['source_paths']['base']),P(cfg['source_paths']['supplement']),P(cfg['verifier']['path']),R/'tools/l2_ops.py',
 R/'control/operational_amendments/registry_journal_v1/l2_registry_journal.py',
 R/'control/operational_amendments/future_memory_scope_sync_v1/scope_sync.py',
 R/'control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py']
out=dict(schema='CPU2_SCIENTIFIC_TRANSITION_READONLY_REVIEW_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 actual_summary_sha256=hashlib.sha256(rawbytes).hexdigest(),primary_matrix_sha256=hashlib.sha256(matrixbytes).hexdigest(),
 source_pins=[dict(path=str(p),sha256=sha(p))for p in requiredpaths],
 actual_decision=dict(interaction_phase=decision['interaction_search']['phase'],proposal_count=len(decision['proposals']),
  requires_engineering_review=decision.get('requires_engineering_review'),negative_review_disposition_required=decision.get('negative_review_disposition_required'),
  scientific_stage_complete=decision['scientific_stage_complete'],adoption_ready=decision['adoption_ready']),
 original350=dict(total=350,nonterminal=len(initial_missing),terminal=350-len(initial_missing),accepted=sum(ev.good(d,n,c)for n in policy.INITIAL for c in(('CH','DH')if n=='P0'else('DH',))for d in ev.ids),
  nonterminal_by_program=dict(collections.Counter(x['program']for x in initial_missing)),missing=initial_missing),
 original_scan_M16=dict(cohort=negative['cohort'],uuid=cell['uuid'],state=cell['state'],accepted=cell['accepted'],cycles=cell['cycles'],
  verified_typed_proof=proofs[negative['cohort']],original_RESULT_exists=rp.exists(),is_terminal=ev.terminal(negative['input_digest'],'M16'),is_full35_parent=ev.full('M16')),
 original_profile_coverage=profiles,structural_seed_actual_parent_sets=seedparents,
 supplemental_R2=dict(cohort=r2,in_primary_matrix=any(p['cohort']==r2 for p in matrix['points']),running=r2 in batch.get('running',[]),
  in_postprocess=r2 in batch.get('postprocess',[]),automatic_union=False),
 installation_evidence=dict(interaction_ACK_sha256=sha(ip/'ACK.json'),interaction_commit=ack['publication_commit'],
  interaction_same_journal_id=ack['journal_object_id'],sync_same_journal_id=syncack['same_journal_object_id'],
  sync_outer=syncack['actual_registry_outer_is_scope_sync'],inner_E_preserved=syncack['actual_E_resource_guard_preserved_inside'],
  cpu2_ACK_sha256=sha(R/'control/operational_amendments/cpu_spare_memory_v2/ACK.json'),cpu2_same_memory_dict=cpuack['same_memory_dictionary'],
  cpu2_old_records_unchanged=cpuack['old_memory_and_CPU1_records_unchanged'],cpu2_no_science_grant=not cpuack['automatic_new_scientific_grants']),
 prior_CPU_coverage_reused=[dict(path=str(p),sha256=sha(p),status=read(p)['status'],count=read(p)['count'])for p in(oldqa,journalqa)],
 findings=dict(initial_typed_negative_permanent_block=False,original_M16_OFAT_extension_hold=True,entire_merge_direction_blocked=False,
  structural_seeds_blocked_by_original_M16=False,forced_uniform_CH_missing_M16_block=False,
  global_scheduler_waits_R2_before_adaptive=True,final_manual_negative_disposition_is_not_implemented=True),
 source_statement='Actual pinned typed archive view and recommendation read only; same live owner/journal object identities are from installed ACKs, not new owner introspection.',
 model_starts=0,new_grants=0,production_changes=0,scientific_semantics_changed=False,old_CPU_tests_rerun=False)
(H/'REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status='PASS_READONLY',review_sha256=sha(H/'REVIEW.json'),actual_phase=out['actual_decision'],initial=out['original350']['nonterminal'],original_negative_terminal=out['original_scan_M16']['is_terminal'],seed_parents=seedparents)))
