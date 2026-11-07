"""Private new96 runtime candidate. Import inert; actual entry Main-only.

The complete independently reviewed new-root artifact finalizer is a mandatory
input. This file does not supply an actual release. No old request is attached.
"""
from pathlib import Path
import ast,contextlib,copy,hashlib,json,os,sys,threading,time,types
READINESS='PASS_CPU_EQUIVALENT_CLEAN_RUNTIME_ADAPTER'
REQUEST='DTC_ORACLE_REMAINING24_20261106_V1'
AUTHORITY='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
B2_SHA='d3ad4b880753a9bf42e91858743bdae9f657a63e578be4bc5180d8b3b44c6bc1'
RSS_SHA='d10e7691ccd0b87b223cfd32a4651a256ec8c0bf1caf377ae360edbfaaed3d64'
ALIAS_SHA='5525945a40de4b28a9c28382bdb5829747d277413518f7250c74606c78c8c3f3'
SPARSE_SHA='dc00fb7a0435c85dd0b377ead470df58ce9127d6bc1ef32b7ec69ad5a5885c6d'
OLD32_ENGINE_SHA='5f978c77586f3be030ca0295adb6eec09d8152254df1f88f85becb45588850d9'
MATRIX_SHA='11d5bfc7642a6262fde719119603c940ca64eb98de69d2554124f24b2302a3ee'
MARKER='DTC_ORACLE_CLEAN_MAIN_SINGLE_POOL_V1'
def need(x,why):
 if not x:raise RuntimeError(why)
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def pinned(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p));return p
def load(ref,name):
 p=pinned(ref);m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as h:h.write(encoded(v));h.flush();os.fsync(h.fileno())
def validate_candidate(candidate,plan,parent):
 need(plan['request']==candidate['request']==REQUEST and plan['stage']=='remaining24','ONLY_ORIGINAL_REMAINING96')
 need(plan['preparation_phase']=='SCIENCE_FINAL_FROZEN'and candidate['ready_for_registration']is True,'CPU_DRAFT_IS_NOT_SCIENCE')
 need(plan['expected_new_starts']==candidate['budget']==candidate['remaining']==96
      and candidate['consumed']=={} and candidate['sealed']=={},'EXACT_UNUSED96_ONLY')
 need(len(candidate['admitted_specs'])==96 and set(candidate['admitted_specs'])==set(plan['authorized_cohorts']),
      'EXACT_COHORT_DOMAIN96')
 need(plan['authority_commit']==candidate['approved_contract_commit']==AUTHORITY,'FROZEN_AUTHORITY')
 need(candidate['owner_pid']==plan['parent_pid']==parent['pid']and
      candidate['owner_start_ticks']==plan['parent_start_ticks']==parent['start_ticks'],'TRUE_NEW_OPERATIONAL_OWNER')
 need((parent['pid'],parent['start_ticks'])not in[(1498278,977758783),(438646,1072993843)]
      and parent['request']==REQUEST,'NOT_OLD_EXEC_IMAGE')
 need(candidate['model_automatic_retries']==0 and candidate['new_registration_only']is True
      and candidate['old_request_budget_reused']is False and plan['CH_budget']==0,'NO_RETRY_REUSE_OR_CH')
 need(set(plan['qualified_modes'])=={'M_DATAREAD','L2_DATAREAD','L1_DATAREADY'},'FROZEN_Q3')
 return 96
def register_exact_request(current,candidate,plan,parent,evidence):
 """Pure EX callback: all IO, source/lease/locks/gates checked beforehand."""
 validate_candidate(candidate,plan,parent)
 need(evidence['authority_commit']==AUTHORITY and evidence['exact_candidate_count']==96
      and evidence['Gate0_CPU_source_strict_independent_review']=='PASS'
      and evidence['Gate2_any_mode_fixed8_and_shared_OFF_accepted_independently_reviewed']=='PASS'
      and set(evidence['Gate2_released_modes'])and set(evidence['Gate2_released_modes'])<=set(plan['qualified_modes']),
      'GENUINE_INDEPENDENT_RELEASE_GATES')
 need(REQUEST not in current['registered_future_requests'],'REQUEST_ALREADY_REGISTERED_FORWARD_HOLD')
 peers=copy.deepcopy(current['registered_future_requests']);historical=copy.deepcopy({k:v for k,v in current.items()if k!='registered_future_requests'})
 new=copy.deepcopy(candidate);new['runtime_release_evidence']=copy.deepcopy(evidence)
 current['registered_future_requests'][REQUEST]=new
 need(all(current['registered_future_requests'][k]==v for k,v in peers.items()),'ANY_OLD_REQUEST_MUTATION')
 need({k:v for k,v in current.items()if k!='registered_future_requests'}==historical,'ANY_HISTORY_OR_BUDGET_COUNTER_MUTATION_IN_CALLBACK')
 return 96
def helpers_from_B2(source,environment):
 need(hashlib.sha256(source).hexdigest()==B2_SHA,'ONLY_QUALIFIED_B2_OPERATIONAL_HELPERS')
 tree=ast.parse(source);apply=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='apply')
 nodes=[copy.deepcopy(x)for tr in apply.body if isinstance(tr,ast.Try)for x in tr.body
        if isinstance(x,ast.FunctionDef)and x.name in['fresh','harvest','cycle_error']]
 need({x.name for x in nodes}=={'fresh','harvest','cycle_error'},'EXACT_QUALIFIED_ERROR_HELPERS')
 exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<PRIVATE_REVIEWED_B2_HELPERS>','exec'),environment)
 return environment
def bind_private_pool(release,parent,locks,root,plan):
 """Create one pool context, no new process/model starts in this function."""
 root=Path(root);base=root.parent;main=sys.modules['__main__']
 need(threading.current_thread()is threading.main_thread()and not hasattr(main,MARKER),'ONE_TRUE_CLEAN_MAIN_POOL')
 review=read(pinned(release['independent_live_review']))
 for key in ['RSS_history_adapter','B2_helpers','alias_hook','sparse_hook','artifact_finalizer']:
  need(review[key+'_sha256']==release[key]['sha256'],'D_REVIEW_COMPONENT_BINDING:'+key)
 need(release['RSS_history_adapter']['sha256']==RSS_SHA and release['B2_helpers']['sha256']==B2_SHA
      and release['alias_hook']['sha256']==ALIAS_SHA and release['sparse_hook']['sha256']==SPARSE_SHA,
      'ONLY_FROZEN_POSTPROCESS_AND_RSS_HELPERS')
 guard=load(release['guard'],'CLEAN_RUNTIME_TRUE_PARENT_GUARD')
 verify=lambda:guard.verify_parent_lease(plan)
 verify();b2=load(release['B2_helpers'],'CLEAN_RUNTIME_QUALIFIED_B2_HELPERS_ONLY')
 history=load(release['RSS_history_adapter'],'CLEAN_RUNTIME_EXACT_RSS')
 alias=load(release['alias_hook'],'CLEAN_RUNTIME_EXACT_ALIAS552')
 sparse=load(release['sparse_hook'],'CLEAN_RUNTIME_PROVEN_SPARSE_DC00')
 ops=load(dict(path=str(root/'tools/oracle_ops.py'),sha256=sha(root/'tools/oracle_ops.py')),'CLEAN_MAIN_PRIVATE_UNIQUE_POOL')
 ops.BASE=base;ops.R=root;ops._C_execution_root=root;ops._C_owner_pid=parent['pid'];ops._C_owner_start=parent['start_ticks'];ops._C_request=REQUEST
 ops._C_assert_clean_owner=verify
 def command(ctx,c,operation):
  need(Path(ctx['root'])==root and operation in['prepare','run-native'],'ONLY_NEW96_NATIVE_ROUTE')
  need(c in plan['authorized_cohorts'],'ONLY_FROZEN_NEW96_NATIVE_ROUTE')
  route=pinned(plan['installed_native_route'])
  need(route==Path('/root/data/ep_l2_dtc_l1_native_v2/bin/native'),'ACTUAL_NATIVE_EPOCH2_ROUTE')
  return ['/root/data/ep_l2_dtc_l1_native_v2/bin/experiment',operation,c,'--project','DTC_L1']
 ops._C_native_command=command
 original_load=ops.load
 def private_load(name,path):
  m=original_load(name,path)
  if Path(path).name=='oracle_results.py':m=sparse.wrap_consumer(alias.wrap_consumer(m,root),root)
  return m
 ops.load=private_load;ops.attach_registered_request(str(root));state=getattr(main,MARKER)
 need(set(state['contexts'])=={str(root)}and state['claims']=={},'ONLY_NEW96_NO_OLD32_ATTACH')
 shared=next(x for x in parent['locks']if x['role']=='shared')
 @contextlib.contextmanager
 def shared_scope(state):
  guard.verify_lock(shared,parent['pid']);yield shared['fd']
 ops._B_inherited_shared_scope=shared_scope
 def verify_shared(state,fd):
  need(fd==shared['fd'],'EXACT_ACTUALLY_HELD_SHARED_FD');return guard.verify_lock(shared,parent['pid'])
 ops._B_verify_shared_scope=verify_shared
 ops._B_reconcile_inherited_claims=lambda *unused:verify()
 gen=root/'control/CLEAN_OPERATIONAL_GENERATION';gen.mkdir(exist_ok=True)
 ops._B_generation_root=gen;ops._B_generation=sha(release['guard']['path'])+':'+str(parent['pid'])+':'+str(parent['start_ticks'])
 @contextlib.contextmanager
 def review_scope():
  with Path('/root/data/dtc_controlled_oracle_20261106_v1/control/ORACLE_INDEPENDENT_ACTUAL_REVIEW_JOB.lock').open('a+b')as h:
   import fcntl
   fcntl.flock(h,fcntl.LOCK_EX);yield h
 ops._B_review_scope=review_scope
 env=dict(b2.__dict__,BASE=base,generation_root=gen,generation=ops._B_generation,put=put,state=state)
 helpers_from_B2(pinned(release['B2_helpers']).read_bytes(),env)
 ops._B_resource=env['fresh'];ops._B_harvest=env['harvest'];ops._B_cycle_error=env['cycle_error']
 ops._B_unused_identity=b2.unused_identity;ops._B_closed_receipt=b2.closed_receipt;ops._B_launch_phase_ready=b2.launch_phase_ready
 ops._B_cleanup=lambda running,post,reviews:b2.cleanup_unused_claims(state,running,post,reviews,env['cycle_error'])
 need(release['frozen_matrix']['sha256']==MATRIX_SHA,'ORIGINAL_FROZEN128_MATRIX')
 matrix=read(pinned(release['frozen_matrix']));allowed={r['input_digest']for r in matrix['rows']};need(len(allowed)==32,'EXACT_CORE32_RSS_INPUT_DOMAIN')
 oldroot=Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8')
 need(release['old32_readonly_engine']['sha256']==OLD32_ENGINE_SHA,'EXACT_OLD32_READONLY_ENGINE_SOURCE')
 oldengine=load(release['old32_readonly_engine'],'CLEAN_READONLY_OLD32_NO_ATTACH')
 oldctx=dict(root=oldroot,request='DTC_ORACLE_INITIAL8_20261106_V1',e=oldengine)
 def refresh(state,contexts):
  snapshot=history.capture([oldctx]+contexts,allowed)
  p=gen/'RSS_history_snapshots'/(snapshot['snapshot_sha256']+'.json')
  if p.exists():need(read(p)==snapshot,'EXACT_RSS_SNAPSHOT_CONFLICT')
  else:put(p,snapshot)
  state['B_exact_RSS_snapshot']=snapshot
  for ctx in contexts:history.bind_forecast(ctx['res'],lambda:state.get('B_exact_RSS_snapshot'))
 ops._B_refresh_RSS_history=refresh
 ops._B_choose_with_RSS_history=lambda res,*a,**kw:history.choose(res,state['B_exact_RSS_snapshot'],*a,**kw)
 return ops,state
def run_released_new96(release,parent,locks):
 """Actual dormant entry. Main must independently release this full contract."""
 need(release['actual_execution_authorized']is True,'NO_ACTUAL_SCIENTIFIC_RELEASE')
 review=read(pinned(release['independent_live_review']))
 need(review['runtime_adapter_sha256']==sha(__file__)and review['artifact_finalizer_sha256']==release['artifact_finalizer']['sha256'],
      'REVIEWED_FINALIZER_BEFORE_DYNAMIC_LOAD')
 finalizer=load(release['artifact_finalizer'],'CLEAN_MAIN_PRIVATE_ARTIFACT_FINALIZER')
 # No old lease append. The genuine new lease is a new immutable private file.
 root=Path(release['execution_root'])
 need(root==Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24'),
      'ONLY_NEW_PRIVATE_GENERATION_BEFORE_ANY_WRITE')
 lease_path=root/'control/CLEAN_MAIN_PRIVATE_LEASE.fixed.json'
 put(lease_path,parent);lease_ref=dict(path=str(lease_path),sha256=sha(lease_path))
 result=finalizer.finalize_and_qualify_parent(release,parent,lease_ref)
 need(result['status']=='PASS_NEW_PRIVATE_CPU_LAYOUT_SOURCE_RESOURCE_QUALIFICATION'
      and Path(result['root'])==root,'COMPLETE_NEW_PRIVATE_RUNTIME_NOT_QUALIFIED')
 plan=read(root/'control/EXECUTION_PLAN.json');candidate=read(root/'control/REGISTRY_REQUEST_CANDIDATE.json')
 guard=load(release['guard'],'CLEAN_RUNTIME_REGISTRATION_GUARD');guard.verify_parent_lease(plan)
 validate_candidate(candidate,plan,parent)
 e=load(dict(path=str(root/'tools/oracle_native.py'),sha256=sha(root/'tools/oracle_native.py')),'CLEAN_MAIN_NEW96_ENGINE')
 res=load(dict(path=str(root/'tools/oracle_resources.py'),sha256=sha(root/'tools/oracle_resources.py')),'CLEAN_MAIN_NEW96_RESOURCES')
 # Heavy resource/source checks occur outside registry EX. Passed evidence and
 # candidate/plan/parent snapshots are the pure mutator's only dependencies.
 evidence=res.verify_registration_release(plan,candidate)
 evidence['actual_serial_operational_owner']=dict(pid=parent['pid'],start_ticks=parent['start_ticks'],controller=parent['controller'],
      private_lease=lease_ref,old32_no_new_starts=True,old32_no_lease_or_registry_changes=True)
 e.update_authority(lambda current:register_exact_request(current,candidate,plan,parent,evidence))
 # Main-reviewed finalizer installs the additive exact native route only after
 # registration. It must conserve all preceding bytes and cannot widen96 rows.
 route=finalizer.install_reviewed_native_route(release,parent)
 need(route['status']=='PASS_ADDITIVE_EXACT_NEW96_NATIVE_ROUTE','NATIVE_ROUTE_FORWARD_HOLD')
 # Route's immutable pin is an independently registered source pin, never a
 # post-registration rewrite of plan. Finalizer must have precomputed it.
 need(sha(plan['installed_native_route']['path'])==plan['installed_native_route']['sha256'],'ACTUAL_NATIVE_ROUTE_PIN')
 ops,state=bind_private_pool(release,parent,locks,root,plan)
 failed=[]
 def run():
  try:ops.run_scheduler()
  except BaseException as error:failed.append(repr(error))
 worker=threading.Thread(target=run,name='DTC_CLEAN_MAIN_UNIQUE_96_DISPATCH_POOL',daemon=False);state['worker']=worker;worker.start()
 worker.join() # TPE lifetime and locks remain owned even on routine HOLD.
 # Never let a new controller leave its lock context with an unclosed consumed
 # child, irrespective of logging availability. This is a conservative hold;
 # there is no signalling, restart, reset or second dispatcher.
 while True:
  q=e.registered()[2]
  if all(row.get('execution_receipt')is not None for row in q['consumed'].values()):break
  state['B_admission_paused_in_memory']=True;time.sleep(2)
 need(not failed,'UNEXPECTED_PRIVATE_POOL_STOPPED_FORWARD_HOLD:'+repr(failed))
 return dict(status='NEW96_UNIQUE_CLEAN_OWNER_POOL_RETURNED',request=REQUEST,pid=parent['pid'],start_ticks=parent['start_ticks'])

if __name__=='__main__':print(json.dumps(dict(status='CPU_RUNTIME_CANDIDATE_ONLY',models=0,registrations=0)))
