"""Independent CPU candidate: typed terminal membership + full35 inference fence.
No installation, grants, model runs, result writing or mutation of supplied data.
"""
import copy,hashlib,importlib.util,pathlib,uuid
P=pathlib.Path
TYPED='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY'
POLICY={
 'schema':'DTC_L2_MLP_TYPED_ENGINEERING_TERMINAL_FULL35_POLICY_V1',
 'status':'CPU_CANDIDATE_NOT_APPLIED_REQUIRES_VERSIONED_MAIN_ANNOUNCEMENT',
 'typed_terminal_is_not_standard_native_FAIL':True,
 'acceptance_unchanged':True,
 'terminal_membership':'only independently verified engineering-negative archive certificate',
 'inference':'full35 accepted source profiles and P0 only; no original V1 common34 proposal pass-through',
 'final_completion':'never clear existing engineering-review/finalguard flags; reviewed-negative completion needs explicit separate disposition',
}

def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def private_module(path,pin):
 assert sha(path)==pin,'Frozen source pin mismatch'
 sp=importlib.util.spec_from_file_location('isolated_terminal_'+uuid.uuid4().hex,path)
 m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def recommend(summary,scope,history,source_paths,source_pins,certificates,verify_certificate,final_guard=None):
 before=copy.deepcopy(summary);ids=sorted({p['input_digest']for p in scope['points']})
 assert len(ids)==35 and set(ids)==set(summary['table'])
 verified=[]
 for digest,profiles in summary['table'].items():
  for profile,designs in profiles.items():
   for design,row in designs.items():
    if row.get('state')!=TYPED:continue
    assert row.get('accepted')is False and row.get('cycles')is None,'Typed negative cannot supply performance'
    c=row['cohort'];cert=certificates[c]
    proof=verify_certificate(dict(row,input_digest=digest,profile=profile,cell=design),cert)
    assert proof.get('verified')is True and proof.get('cohort')==c and proof.get('uuid')==row['uuid']
    assert proof.get('performance_accepted')is False and proof.get('cycles')is None
    for key in ('source_identity_verified','archive_verified','no_model_retry_verified','missing_done_exit_disclosed'):
     assert proof.get(key)is True,key
    verified.append(proof)
 base=private_module(source_paths['base'],source_pins['base'])
 supplement=private_module(source_paths['supplement'],source_pins['supplement'])
 # Fresh private module globals only; existing active/frozen instances untouched.
 base.TERMINAL_NEGATIVE=set(base.TERMINAL_NEGATIVE)|{TYPED}
 supplement.NEGATIVE=set(supplement.NEGATIVE)|{TYPED}
 original=base.recommend(summary,scope,history)
 gated=copy.deepcopy(original);kept=[];blocked=[]
 def full(profile):
  return all(summary['table'][d].get(profile,{}).get('DH',{}).get('accepted')is True
   and type(summary['table'][d][profile]['DH'].get('cycles'))is int
   and summary['table'][d][profile]['DH']['cycles']>0 for d in ids)
 for proposal in original.get('proposals',[]):
  phase=proposal['phase'];evidence=proposal.get('evidence',{});reason=None
  if phase in ('BOUNDARY_EXTENSION','PAIR_COMBINATION','MULTI_COMBINATION'):
   parents=list(evidence.get('negatives',{}))
   if evidence.get('n')!=35 or evidence.get('population')!=ids or not parents or not all(full(p)for p in parents):
    reason='INFERENCE_SOURCE_NOT_FULL35_ACCEPTED'
  elif phase=='CH_MATCH':
   if not full('P0')or not full(proposal['profile']):reason='CH_CANDIDATE_NOT_FULL35_DH'
  elif phase!='INITIAL':reason='UNKNOWN_BASE_INFERENCE_PHASE_REQUIRES_REVIEW'
  if reason:blocked.append(dict(proposal=proposal,reason=reason))
  else:kept.append(proposal)
 gated['proposals']=kept
 result=supplement.augment(gated,summary,scope,history)
 result['typed_engineering_terminal_policy']=dict(POLICY,source_pins=source_pins)
 result['verified_typed_engineering_negatives']=verified
 result['blocked_common_subset_proposals']=blocked
 result['original_base_recommendation_retained']=original
 # A disclosed engineering negative remains visible for manual scientific review.
 if verified:
  result['requires_engineering_review']=True
  result['scientific_stage_complete']=False
  result['adoption_ready']=False
  result['negative_review_disposition_required']=True
 if final_guard is not None:result=final_guard(result)
 assert summary==before,'Supplied original summary mutated'
 return result
