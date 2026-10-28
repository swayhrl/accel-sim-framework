"""Future-only primary target coverage. No import-time production action."""
import ast,copy,hashlib,inspect,json,pathlib,sys,textwrap,threading,types,os
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
SOURCE=R/'control/operational_amendments/large_job_aging_v1/large_job_aging.py'
SOURCE_SHA='b4e69ea06c017898ce9c5f5fcbb57cfb380ee47942c19cd88520abfaaf07d1ff'
MARKER='DTC_AGING_PRIMARY_TARGET_SELECTOR_V1'
OLD_CHOICES="""choices=[r for r in frame['pending']if r['cell']=='DH'and r['profile']=='P0'and r['cost_bytes']>=p['large_bytes']
            and now-r['first_eligible_monotonic']>=p['wait_seconds']and r['cohort']not in consumed
            and r['cohort']not in claims and r['input_digest']not in active_inputs]"""
NEW_CHOICES="choices=_qualified_primary_choices(frame,p,now,consumed,claims,active_inputs)"
OLD_KEY="(r['program']in started,r['first_eligible_monotonic'],r['input_digest'],r['cohort'])"
NEW_KEY="(r['program']in started,r['first_eligible_monotonic'],r['profile']!='P0',r['input_digest'],r['cohort'])"
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()

def primary_eligible(row,context):
 """Pure identity predicate. All evidence comes from the existing live sources."""
 c=row['cohort'];q=context['registry'];spec=context['specs'].get(c);point=context['matrix_points'].get(c)
 if spec is None or point is None:return False
 if c not in q['admitted_specs']or c in q['consumed']or c in q.get('sealed',[]):return False
 if c not in context['active_memory']['allowed_cohorts']or c in context['preserved_nonprimary']or c in context['initial_references']:return False
 if c in context['INTENT_exists']:return False
 if context['spec_sha256'].get(c)!=q['admitted_specs'][c]:return False
 if spec.get('request')!=REQ or spec.get('schema')!='DTC_L2_MLP_SPEC_V1':return False
 if spec.get('source_kind')!='FROZEN35_WHOLE_DECLARED_TRACE_CONTRACT'or spec.get('performance_scope')!='NEW_L2_MLP_ONLY_NEVER_ORIGINAL':return False
 if spec.get('correctness_validation_only')is not False or spec.get('new_base_reuse')is not False:return False
 if spec.get('cell')not in ['CH','DH']:return False
 if not all(row[k]==spec.get(k)==point.get(k)for k in ['cohort','input_digest','program','cell','profile']):return False
 if row['cost_bytes']<spec['estimated_peak_model_RAM_bytes']:return False
 return True

def choose_candidates(frame,policy,now,consumed,claims,active_inputs,context):
 """Only target selection changes. The original frame/backfill pool is untouched."""
 return [r for r in frame['pending']if r['cost_bytes']>=policy['large_bytes']
  and now-r['first_eligible_monotonic']>=policy['wait_seconds']and r['cohort']not in consumed
  and r['cohort']not in claims and r['input_digest']not in active_inputs and primary_eligible(r,context)]

def build_advance(original_advance,context_provider):
 """Compile exact old advance with only the two reviewed selection substitutions."""
 fn=original_advance.__func__ if hasattr(original_advance,'__func__')else original_advance
 assert sha(SOURCE)==SOURCE_SHA and P(inspect.getsourcefile(fn))==SOURCE
 original=textwrap.dedent(inspect.getsource(fn));assert original.count(OLD_CHOICES)==1 and original.count(OLD_KEY)==1
 changed=original.replace(OLD_CHOICES,NEW_CHOICES).replace(OLD_KEY,NEW_KEY)
 assert changed.replace(NEW_CHOICES,OLD_CHOICES).replace(NEW_KEY,OLD_KEY)==original
 def qualified(frame,p,now,consumed,claims,active_inputs):
  return choose_candidates(frame,p,now,consumed,claims,active_inputs,context_provider(frame))
 namespace=dict(fn.__globals__,_qualified_primary_choices=qualified)
 exec(compile(changed,str(P(__file__).resolve())+'::minimal_advance','exec'),namespace)
 return namespace['advance'],dict(original_advance_utf8=original,modified_advance_utf8=changed,original_module_sha256=SOURCE_SHA,only_target_filter_and_key_changed=True)

def live_context(root,engine,sync,memory,frame):
 """One current authority/matrix view. No duplicate cohort allowlist."""
 root=P(root);q,active=sync.stable_memory();assert active==memory['context']['cfg']
 matrix=read(root/'control/MATRIX_CURRENT.json');scope=read(root/'control/SCOPE.json')
 assert matrix['request']==REQ and matrix['base_scope_sha256']==sha(root/'control/SCOPE.json')
 points={p['cohort']:p for p in matrix['points']};assert len(points)==len(matrix['points'])
 specs={};hashes={};intents=set()
 for row in frame['pending']:
  c=row['cohort']
  if c not in q['admitted_specs']or c not in points:continue
  path=root/'control/specs'/(c+'.json');raw=path.read_bytes();spec=json.loads(raw)
  assert spec==engine.canonical(c);specs[c]=spec;hashes[c]=hashlib.sha256(raw).hexdigest()
  if(root/'control/qualification_ledger'/(c+'.INTENT.json')).exists():intents.add(c)
 return dict(registry=q,active_memory=active,matrix_points=points,specs=specs,spec_sha256=hashes,
  preserved_nonprimary=set(sync.cfg['preserved_nonprimary_cohorts']),initial_references=set(scope['initial_references']),INTENT_exists=intents)

def install_on_existing(aging,context_provider,owner_assert,frame_unavailable,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];assert not hasattr(main,MARKER)
 with aging.lock:
  state=aging.state;assert 'advance'not in state.__dict__,'Do not override another instance selector'
  original=state.advance;compiled,source=build_advance(original,context_provider)
  before=copy.deepcopy(state.__dict__);refs=(aging.original,aging.frame_provider,aging.wrapper,aging.lock)
  # A plain function remains identity-stable under FrameGuard deepcopy/rollback.
  # A MethodType would deepcopy its self and can silently bind a cloned state.
  def advance(frame):
   try:return compiled(state,frame)
   except Exception as error:
    raise frame_unavailable(dict(status='PRIMARY_TARGET_IDENTITY_READ_UNAVAILABLE',error=repr(error),source_sha256=sha(__file__),admission_returned_none=True,resource_snapshot_fabricated=False))from error
  state.advance=advance
  assert copy.deepcopy(state.__dict__)['advance']is advance
  assert {k:v for k,v in state.__dict__.items()if k!='advance'}==before
  assert refs==(aging.original,aging.frame_provider,aging.wrapper,aging.lock)
  marker=dict(aging=aging,state=state,original=original,wrapper=advance,source=source,context_provider=context_provider,owner_assert=owner_assert,refs=refs)
  setattr(main,MARKER,marker)
 return dict(status='PRIMARY_TARGET_SELECTOR_ONLY_INSTALLED',same_state=id(state),same_aging=id(aging),new_grants=0,model_starts=0,reservation_credit_changed_on_install=False)

def restore_in_owner(owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];v=getattr(main,MARKER);aging=v['aging']
 with aging.lock:
  assert aging.state is v['state']and aging.state.advance is v['wrapper']
  assert v['refs']==(aging.original,aging.frame_provider,aging.wrapper,aging.lock)
  del aging.state.advance;assert aging.state.advance==v['original'];delattr(main,MARKER)
 return dict(status='ORIGINAL_CLASS_ADVANCE_RESTORED',new_grants=0,model_starts=0)

def apply_in_owner():
 assert threading.current_thread()is threading.main_thread();main=sys.modules['__main__'];memory=getattr(main,'DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1');engine=memory['engine'];aging=memory['aging'];sync=getattr(main,'DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1')
 engine.assert_parent_lease();plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']
 assert memory['res'].DTC_LARGE_JOB_AGING_INSTALLED is aging and sync.memory is memory
 gate=getattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')['gate'];assert gate.aging is aging
 unavailable=type(gate).choose.__globals__['FrameUnavailable']
 return install_on_existing(aging,lambda frame:live_context(R,engine,sync,memory,frame),engine.assert_parent_lease,unavailable,main)
