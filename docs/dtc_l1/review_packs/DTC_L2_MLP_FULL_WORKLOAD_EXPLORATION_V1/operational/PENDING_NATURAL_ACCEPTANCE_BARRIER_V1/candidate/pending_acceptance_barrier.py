"""Short natural-DONE acceptance barrier for new backfill only; no new money."""
import copy,hashlib,inspect,json,os,pathlib,sys,threading
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
AF_MARKER='DTC_AGING_PRIMARY_TARGET_SELECTOR_V1'
AF_SHA='af09621e85945e489d6022f1b22b6c8702374af8ad81d5e14945977fed039b57'
MARKER='DTC_PENDING_NATURAL_ACCEPTANCE_BARRIER_V1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def observe_result(root,closure,cohort,uuid):
 """Observation only. Negative/unknown never synthesizes accepted or closed."""
 path=closure.get('strict_result_path')
 if path is None:return dict(status='AWAITING_RESULT_OR_STRICT_ACCEPTANCE',accepted=False)
 expected=P(root)/'analysis'/(cohort+'.RESULT.json');assert P(path)==expected
 for _ in range(3):
  with expected.open('rb')as h:a=os.fstat(h.fileno());raw=h.read();z=os.fstat(h.fileno())
  if(a.st_size,a.st_mtime_ns,a.st_ino)==(z.st_size,z.st_mtime_ns,z.st_ino)and len(raw)==z.st_size:break
 else:raise RuntimeError('UNSTABLE_PENDING_ACCEPTANCE_RESULT')
 v=json.loads(raw);assert v['cohort']==cohort and v['uuid']==uuid
 state=v.get('state');status='NATURAL_DONE_WITH_EXPLICIT_NEGATIVE_RESULT_MAIN_REVIEW'if state=='FAIL_L2MLP_ARCHIVED_NO_RETRY'else'RESULT_PRESENT_BUT_NOT_ACCEPTED_BY_ORIGINAL_CONSUMER'
 return dict(status=status,accepted=False,path=str(expected),sha256=hashlib.sha256(raw).hexdigest(),result_state=state,original_consumer_acceptance=False)

def make_wrapper(previous_advance,state,frame_unavailable,root=R,result_reader=None):
 """Exactly one old af096 invocation; only returned backfill eligibility changes."""
 reader=result_reader or(lambda closure,c,u:observe_result(root,closure,c,u))
 def advance(frame):
  try:
   decision=previous_advance(frame) # exactly once; protected/tokens/seen/C unchanged
   result=copy.deepcopy(decision);target=result.get('target');feasible=bool((result.get('feasibility')or{}).get('feasible'))
   backed=result.get('virtual_fence_released_due_full_claim')is True;tokens=[]
   if target and feasible and not backed:
    closures={(x['cohort'],x['uuid']):x for x in frame['closures']}
    for(c,u),token in sorted(state.pending_releases.items()):
     closure=closures.get((c,u))
     if closure is None:raise RuntimeError('PENDING_RELEASE_WITHOUT_AUTHORITATIVE_CURRENT_CLOSURE')
     assert closure['natural_done']is True and closure['accepted_strict_archive_restore']is False
     assert token['raw_release_bytes']>0 and token['realized_credit_bytes']>=0
     observation=reader(closure,c,u)
     tokens.append(dict(cohort=c,uuid=u,raw_release_bytes=token['raw_release_bytes'],realized_credit_bytes=token['realized_credit_bytes'],realized_kind='POSITIVE_REALIZED_PENDING'if token['realized_credit_bytes']else'ZERO_REALIZED_PENDING',acceptance_observation=observation))
   active=bool(tokens)
   result['pending_natural_acceptance_barrier']=dict(schema='DTC_PENDING_NATURAL_ACCEPTANCE_BARRIER_V1',active=active,target=target['cohort']if target else None,own_drain_feasible=feasible,full_target_cost_already_accounted=backed,pending=tokens,original_backfill_cohorts=decision['backfill_cohorts'],provisional_RAM_money_added_bytes=0,strict_credit_added_bytes=0,timeout_based_release=False,original_target_offer_preserved=True,original_protected_bytes_unchanged=result['protected_bytes']==decision['protected_bytes'],prior_advance_called_once=True)
   if active:result['backfill_cohorts']=[]
   state.last_decision=result
   return result
  except frame_unavailable:raise
  except Exception as error:
   raise frame_unavailable(dict(status='PENDING_NATURAL_ACCEPTANCE_OBSERVATION_UNAVAILABLE',error=repr(error),admission_returned_none=True,resource_snapshot_fabricated=False))from error
 return advance

def install_on_existing(aging,owner_assert,frame_unavailable,main=None,root=R,result_reader=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];assert not hasattr(main,MARKER)
 with aging.lock:
  prior=getattr(main,AF_MARKER);state=aging.state;previous=state.advance
  assert prior['state']is state and prior['aging']is aging and prior['wrapper']is previous
  source=P(previous.__code__.co_filename);assert sha(source)==AF_SHA
  refs=(aging.original,aging.frame_provider,aging.wrapper,aging.lock)
  before=copy.deepcopy(state.__dict__);wrapper=make_wrapper(previous,state,frame_unavailable,root,result_reader)
  state.advance=wrapper;assert copy.deepcopy(state.__dict__)['advance']is wrapper
  assert {k:v for k,v in state.__dict__.items()if k!='advance'}=={k:v for k,v in before.items()if k!='advance'}
  assert refs==(aging.original,aging.frame_provider,aging.wrapper,aging.lock)
  setattr(main,MARKER,dict(aging=aging,state=state,previous=previous,wrapper=wrapper,prior_selector=prior,refs=refs,owner_assert=owner_assert,source_path=str(source),source_sha256=AF_SHA))
 return dict(status='PENDING_NATURAL_ACCEPTANCE_BACKFILL_BARRIER_INSTALLED',same_state=id(state),new_grants=0,model_starts=0,protected_or_tokens_or_credit_replayed=False,temporary_25pct_backfill_pause_explicit=True)

def restore_in_owner(owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];v=getattr(main,MARKER);aging=v['aging']
 with aging.lock:
  assert aging.state is v['state']and aging.state.advance is v['wrapper']
  assert v['refs']==(aging.original,aging.frame_provider,aging.wrapper,aging.lock)
  aging.state.advance=v['previous'];assert getattr(main,AF_MARKER)is v['prior_selector'];delattr(main,MARKER)
 return dict(status='EXACT_AF096_ADVANCE_RESTORED',new_grants=0,model_starts=0)

def apply_in_owner():
 assert threading.current_thread()is threading.main_thread();main=sys.modules['__main__'];memory=getattr(main,'DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1');engine=memory['engine'];aging=memory['aging'];engine.assert_parent_lease()
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks'];assert memory['res'].DTC_LARGE_JOB_AGING_INSTALLED is aging
 gate=getattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')['gate'];assert gate.aging is aging
 unavailable=type(gate).choose.__globals__['FrameUnavailable']
 return install_on_existing(aging,engine.assert_parent_lease,unavailable,main,R)
